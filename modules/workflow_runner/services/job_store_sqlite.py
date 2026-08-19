import aiosqlite
import asyncio
import json
import logging
import time

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from .input_snapshot import sanitize_input_snapshot

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
        _conn = await aiosqlite.connect(db_path, timeout=30.0)  # longer busy timeout
        # Pragmas for durability + fewer locks in WAL mode
        await _conn.execute("PRAGMA journal_mode=WAL;")
        await _conn.execute("PRAGMA synchronous=NORMAL;")
        await _conn.execute("PRAGMA busy_timeout=30000;")  # 30s

        # Schema (note: your code uses 'runs' as the table name)
        await _conn.execute("""
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
                inputs TEXT
            )
        """)

        # Existing installations predate durable remix inputs.  Migrate in
        # place without rewriting or invalidating any historical rows.
        columns_cur = await _conn.execute("PRAGMA table_info(runs)")
        columns = {row[1] for row in await columns_cur.fetchall()}
        if "inputs" not in columns:
            await _conn.execute("ALTER TABLE runs ADD COLUMN inputs TEXT")

        # Indexes to support owner filters + active lookups
        await _conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_runs_owner_status
            ON runs(owner_id, status)
        """)
        await _conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_runs_active
            ON runs(status, updated_at DESC)
        """)

        await _conn.commit()
    return _conn

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
) -> JobRecord:
    conn = await _ensure_conn()
    now = time.time()
    # Upsert logic: if the row already exists (likely created by a prior status update before
    # we had workflow_id/owner_id), update those columns ONLY if they are currently NULL.
    # Preserve existing status/created_at/seq/result/error fields.
    await conn.execute(
        """
        INSERT INTO runs (run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id, inputs)
        VALUES (?, ?, 'pending', ?, ?, NULL, NULL, 0, ?, ?)
        ON CONFLICT(run_id) DO UPDATE SET
          workflow_id = COALESCE(runs.workflow_id, excluded.workflow_id),
          owner_id    = COALESCE(runs.owner_id,    excluded.owner_id),
          inputs      = COALESCE(runs.inputs,      excluded.inputs)
        """,
        (run_id, workflow_id, now, now, owner_id, json.dumps(sanitize_input_snapshot(inputs), ensure_ascii=False, separators=(",", ":"))),
    )
    await conn.commit()

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
        )
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
    cur = await conn.execute("SELECT run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id, inputs FROM runs WHERE run_id = ?", (run_id,))
    row = await cur.fetchone()
    if not row:
        return None
    result = None
    try:
        # result column is at index 5
        result = json.loads(row[5]) if row[5] else None
    except Exception:
        result = row[5]

    inputs = {}
    try:
        inputs = json.loads(row[9]) if row[9] else {}
    except Exception:
        inputs = {}
    return JobRecord(run_id=row[0], workflow_id=row[1], status=row[2], created_at=row[3], updated_at=row[4], result=result, error=row[6], seq=row[7] or 0, owner_id=row[8], inputs=inputs if isinstance(inputs, dict) else {})
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
# endregion

# region List
async def list_jobs(owner_id: Optional[str] = None, status: Optional[str] = None) -> Dict[str, JobRecord]:
    """List jobs optionally filtered by owner_id and/or status.

    Returns a dict keyed by run_id mapping to JobRecord instances.
    """
    conn = await _ensure_conn()
    out: Dict[str, JobRecord] = {}
    q = "SELECT run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id, inputs FROM runs"
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
        result = None
        try:
            # result column is at index 5
            result = json.loads(row[5]) if row[5] else None
        except Exception:
            result = row[5]
        inputs = {}
        try:
            inputs = json.loads(row[9]) if row[9] else {}
        except Exception:
            inputs = {}
        out[row[0]] = JobRecord(run_id=row[0], workflow_id=row[1], status=row[2], created_at=row[3], updated_at=row[4], result=result, error=row[6], seq=row[7] or 0, owner_id=row[8], inputs=inputs if isinstance(inputs, dict) else {})
    return out
# endregion

# region Delete
async def remove_job(run_id: str) -> Optional[JobRecord]:
    # Soft delete: mark deleted + bump seq
    rec = await set_job_status(run_id, "deleted")
    return rec
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
    "set_job_status",
    "list_jobs",
    "remove_job",
    "subscribe_events",
    "unsubscribe_events",
    "publish_event",
    "close",
]
