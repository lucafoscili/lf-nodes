import aiosqlite
import asyncio
import json
import logging
import time

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from .input_snapshot import sanitize_input_snapshot
from .job_contracts import validate_submission_identity as _validate_submission_identity

LOG = logging.getLogger(__name__)

# Path to sqlite DB file (set via configure).
_DB_PATH: Optional[str] = None

# region Configuration
def configure(db_path: Optional[str]) -> None:
    """Configure the adapter with a database file path.

    Pass None to let the adapter choose a default file under the module folder.
    """
    global _DB_PATH
    _DB_PATH = db_path

_conn: Optional[aiosqlite.Connection] = None
_conn_lock = asyncio.Lock()

# in-memory pubsub (subscribers receive event dicts)
_subscribers: list[asyncio.Queue] = []
# endregion

@dataclass
class JobRecord:
    run_id: str
    workflow_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    seq: int = 0
    owner_id: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    submission_id: Optional[str] = None
    request_fingerprint: Optional[str] = None
    comfy_url: Optional[str] = None


_SELECT_COLUMNS = (
    "run_id, workflow_id, status, created_at, updated_at, result, error, seq, "
    "owner_id, inputs, submission_id, request_fingerprint, comfy_url"
)


def _record_from_row(row: Any) -> JobRecord:
    result = None
    try:
        result = json.loads(row[5]) if row[5] else None
    except Exception:
        result = row[5]
    inputs = {}
    try:
        inputs = json.loads(row[9]) if row[9] else {}
    except Exception:
        inputs = {}
    return JobRecord(
        run_id=row[0],
        workflow_id=row[1],
        status=row[2],
        created_at=row[3],
        updated_at=row[4],
        result=result,
        error=row[6],
        seq=row[7] or 0,
        owner_id=row[8],
        inputs=inputs if isinstance(inputs, dict) else {},
        submission_id=row[10] if len(row) > 10 else None,
        request_fingerprint=row[11] if len(row) > 11 else None,
        comfy_url=row[12] if len(row) > 12 else None,
    )


# region Connection
def _build_event(rec: JobRecord) -> dict:
    # Preserve the historical SSE contract.  Bounded summary projection is an
    # explicit HTTP/SSE caller choice, not a storage-layer default.
    from ..utils.serialize import serialize_job

    return serialize_job(rec, include_result_for_terminal=True)

async def _ensure_conn():
    global _conn
    if _conn is not None:
        return _conn
    async with _conn_lock:
        if _conn is not None:
            return _conn
        # select DB path: if not configured, default to a file beside this module
        db_path = _DB_PATH
        if not db_path:
            db_path = str(Path(__file__).resolve().parent / "workflow_runner_history.db")
        LOG.info("Opening workflow-runner sqlite DB at %s", db_path)
        conn = await aiosqlite.connect(db_path, timeout=30.0)  # longer busy timeout
        try:
            # Keep the connection private until its schema is ready. Startup
            # readers may otherwise select newly-added columns while a legacy
            # database is still between ALTER TABLE statements.
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA synchronous=NORMAL;")
            await conn.execute("PRAGMA busy_timeout=30000;")  # 30s

            # Schema (note: your code uses 'runs' as the table name)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    status TEXT,
                    created_at REAL,
                    updated_at REAL,
                    result TEXT,
                    error TEXT,
                    seq INTEGER NOT NULL DEFAULT 0,
                    owner_id TEXT,
                    inputs TEXT,
                    submission_id TEXT,
                    request_fingerprint TEXT,
                    comfy_url TEXT
                )
            """)

            # Existing installations predate durable remix inputs.  Migrate in
            # place without rewriting or invalidating any historical rows.
            columns_cur = await conn.execute("PRAGMA table_info(runs)")
            columns = {row[1] for row in await columns_cur.fetchall()}
            if "inputs" not in columns:
                await conn.execute("ALTER TABLE runs ADD COLUMN inputs TEXT")
            if "submission_id" not in columns:
                await conn.execute("ALTER TABLE runs ADD COLUMN submission_id TEXT")
            if "request_fingerprint" not in columns:
                await conn.execute("ALTER TABLE runs ADD COLUMN request_fingerprint TEXT")
            if "comfy_url" not in columns:
                await conn.execute("ALTER TABLE runs ADD COLUMN comfy_url TEXT")

            # Indexes to support owner filters + active lookups
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_owner_status
                ON runs(owner_id, status)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_active
                ON runs(status, updated_at DESC)
            """)
            await conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_runs_submission_id
                ON runs(submission_id)
                WHERE submission_id IS NOT NULL
            """)

            await conn.commit()
        except BaseException:
            await conn.close()
            raise
        _conn = conn
        return conn

async def close() -> None:
    """Close the adapter connection if open. Safe to call on shutdown.

    This helps tests and interactive sessions avoid leaving a locked DB file.
    """
    global _conn
    if _conn is not None:
        try:
            await _conn.close()
        except Exception:
            LOG.exception("Error closing sqlite connection")
        finally:
            _conn = None
# endregion

# region Create
async def create_job(
    run_id: str,
    workflow_id: str,
    owner_id: Optional[str] = None,
    *,
    inputs: Optional[Dict[str, Any]] = None,
    submission_id: Optional[str] = None,
    request_fingerprint: Optional[str] = None,
    comfy_url: Optional[str] = None,
) -> JobRecord:
    _validate_submission_identity(submission_id, request_fingerprint, comfy_url)
    conn = await _ensure_conn()
    now = time.time()
    try:
        values = (
            run_id,
            workflow_id,
            now,
            now,
            owner_id,
            json.dumps(
                sanitize_input_snapshot(inputs),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            submission_id,
            request_fingerprint,
            comfy_url,
        )
        if submission_id is not None:
            # A stable prompt identity is an owner-bound authority.  Never
            # enrich or adopt an existing run row: an exact idempotent match is
            # accepted only after readback, while every other collision leaves
            # the original row byte-for-byte authoritative.
            await conn.execute(
                """
                INSERT INTO runs (
                  run_id, workflow_id, status, created_at, updated_at, result, error,
                  seq, owner_id, inputs, submission_id, request_fingerprint, comfy_url
                )
                VALUES (?, ?, 'pending', ?, ?, NULL, NULL, 0, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO NOTHING
                """,
                values,
            )
        else:
            # Legacy rows can predate workflow/owner registration because the
            # historical status API could create a placeholder first.
            await conn.execute(
                """
                INSERT INTO runs (
                  run_id, workflow_id, status, created_at, updated_at, result, error,
                  seq, owner_id, inputs, submission_id, request_fingerprint, comfy_url
                )
                VALUES (?, ?, 'pending', ?, ?, NULL, NULL, 0, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                  workflow_id = COALESCE(runs.workflow_id, excluded.workflow_id),
                  owner_id    = COALESCE(runs.owner_id,    excluded.owner_id),
                  inputs      = COALESCE(runs.inputs,      excluded.inputs)
                """,
                values,
            )
        await conn.commit()
    except BaseException:
        await conn.rollback()
        raise

    # Read back the row (may have pre-existed)
    rec = await get_job(run_id)
    if rec is None:
        rec = JobRecord(
            run_id=run_id,
            workflow_id=workflow_id,
            created_at=now,
            updated_at=now,
            status="pending",
            seq=0,
            owner_id=owner_id,
            inputs=sanitize_input_snapshot(inputs),
            submission_id=submission_id,
            request_fingerprint=request_fingerprint,
            comfy_url=comfy_url,
        )
    if submission_id is not None and (
        rec.workflow_id != workflow_id
        or rec.owner_id != owner_id
        or rec.submission_id != submission_id
        or rec.request_fingerprint != request_fingerprint
        or rec.comfy_url != comfy_url
    ):
        raise ValueError("run is already bound to another submission identity")
    event = _build_event(rec)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            pass
    return rec
# endregion

# region Read
async def get_job(run_id: str) -> Optional[JobRecord]:
    conn = await _ensure_conn()
    cur = await conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM runs WHERE run_id = ?",
        (run_id,),
    )
    row = await cur.fetchone()
    if not row:
        return None
    return _record_from_row(row)


async def get_job_by_submission_id(submission_id: str) -> Optional[JobRecord]:
    conn = await _ensure_conn()
    cur = await conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM runs WHERE submission_id = ?",
        (submission_id,),
    )
    row = await cur.fetchone()
    return _record_from_row(row) if row else None
# endregion

# region Update
async def set_job_status(run_id: str, status: str, *, result: Optional[Any] = None, error: Optional[str] = None) -> Optional[JobRecord]:
    conn = await _ensure_conn()
    now = time.time()

    if result is not None:
        try:
            result_json = json.dumps(result)
        except Exception:
            result_json = json.dumps({"_repr": str(result)})
    else:
        result_json = None

    # Single atomic statement; no explicit BEGIN
    await conn.execute(
        """
        INSERT INTO runs (run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id, inputs)
        VALUES (?, NULL, ?, ?, ?, ?, ?, 1, NULL, NULL)
        ON CONFLICT(run_id) DO UPDATE SET
          status      = excluded.status,
          updated_at  = excluded.updated_at,
          result      = excluded.result,
          error       = excluded.error,
          seq         = COALESCE(runs.seq, 0) + 1,
          owner_id    = COALESCE(runs.owner_id, excluded.owner_id),
          workflow_id = COALESCE(runs.workflow_id, excluded.workflow_id)
        """,
        (run_id, status, now, now, result_json, error),
    )
    await conn.commit()

    rec = await get_job(run_id)
    if not rec:
        return None
    event = _build_event(rec)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            pass
    return rec


async def set_job_status_if_unchanged(
    run_id: str,
    new_status: str,
    *,
    owner_id: Optional[str],
    expected_status: str,
    seq: int,
    updated_at: Optional[float],
    result: Optional[Any] = None,
    error: Optional[str] = None,
    clear_error: bool = False,
) -> Optional[JobRecord]:
    """Atomically update and return one exact previously-scanned row."""

    conn = await _ensure_conn()
    now = time.time()
    result_supplied = result is not None
    if result_supplied:
        try:
            result_json = json.dumps(result)
        except Exception:
            result_json = json.dumps({"_repr": str(result)})
    else:
        result_json = None

    cur = await conn.execute(
        """
        UPDATE runs
        SET status = ?,
            updated_at = ?,
            result = CASE WHEN ? THEN ? ELSE result END,
            error = CASE
                      WHEN ? THEN NULL
                      WHEN ? THEN ?
                      ELSE error
                    END,
            seq = COALESCE(seq, 0) + 1
        WHERE run_id = ?
          AND status = ?
          AND COALESCE(seq, 0) = ?
          AND owner_id IS ?
          AND updated_at IS ?
        RETURNING run_id, workflow_id, status, created_at, updated_at,
                  result, error, seq, owner_id, inputs, submission_id,
                  request_fingerprint, comfy_url
        """,
        (
            new_status,
            now,
            int(result_supplied),
            result_json,
            int(clear_error),
            int(error is not None),
            error,
            run_id,
            expected_status,
            int(seq),
            owner_id,
            updated_at,
        ),
    )
    row = await cur.fetchone()
    await conn.commit()
    if row is None:
        return None

    rec = _record_from_row(row)
    event = _build_event(rec)
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            pass
    return rec
# endregion

# region List
async def list_jobs(owner_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, JobRecord]:
    """List jobs optionally filtered by owner_id and/or status.

    Returns a dict keyed by run_id mapping to JobRecord instances.
    """
    conn = await _ensure_conn()
    out: Dict[str, JobRecord] = {}
    q = f"SELECT {_SELECT_COLUMNS} FROM runs"
    params: list = []
    clauses: list = []
    if owner_id is not None:
        clauses.append("owner_id = ?")
        params.append(owner_id)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    cur = await conn.execute(q, params)
    rows = await cur.fetchall()
    for row in rows:
        out[row[0]] = _record_from_row(row)
    return out
# endregion

# region Delete
async def remove_job(run_id: str) -> Optional[JobRecord]:
    # Soft delete: mark deleted + bump seq
    rec = await set_job_status(run_id, "deleted")
    return rec


async def hard_delete_job_if_unchanged(
    run_id: str,
    *,
    owner_id: Optional[str],
    status: str,
    seq: int,
    updated_at: Optional[float],
) -> bool:
    """Hard-delete one row only when its scanned snapshot is still current."""

    conn = await _ensure_conn()
    cur = await conn.execute(
        """
        DELETE FROM runs
        WHERE run_id = ?
          AND status = ?
          AND COALESCE(seq, 0) = ?
          AND ((owner_id IS NULL AND ? IS NULL) OR owner_id = ?)
          AND ((updated_at IS NULL AND ? IS NULL) OR updated_at = ?)
        """,
        (run_id, status, int(seq), owner_id, owner_id, updated_at, updated_at),
    )
    await conn.commit()
    return cur.rowcount == 1
# endregion

# region PubSub
def subscribe_events() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q

def unsubscribe_events(q: asyncio.Queue) -> None:
    try:
        _subscribers.remove(q)
    except ValueError:
        pass

def publish_event(event: Dict[str, Any]) -> None:
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            LOG.exception("Failed to enqueue event to subscriber queue")
# endregion

__all__ = [
    "create_job",
    "get_job",
    "get_job_by_submission_id",
    "set_job_status",
    "set_job_status_if_unchanged",
    "list_jobs",
    "remove_job",
    "hard_delete_job_if_unchanged",
    "subscribe_events",
    "unsubscribe_events",
    "publish_event",
    "close",
]
