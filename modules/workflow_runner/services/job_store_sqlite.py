import aiosqlite
import asyncio
import json
import logging
import time

from typing import Any, Dict, Optional

from dataclasses import dataclass, field

LOG = logging.getLogger(__name__)

from pathlib import Path

# Path to sqlite DB file (set via configure). If None, a sensible default under the
# module directory will be used when initializing the connection.
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

def _build_event(rec: JobRecord) -> dict:
    # SSE resume-friendly id: "<run_id>:<seq>"
    return {
        "id": f"{rec.run_id}:{rec.seq}",
        "run_id": rec.run_id,
        "workflow_id": getattr(rec, "workflow_id", None),
        "status": rec.status,
        "created_at": rec.created_at,
        "updated_at": rec.updated_at,
        "error": rec.error,
        "result": rec.result if rec.status in ("succeeded", "failed", "cancelled") else None,
        "seq": rec.seq,
        "owner_id": rec.owner_id,
    }

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
                owner_id TEXT
            )
        """)

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

# region Create
async def create_job(run_id: str, workflow_id: str, owner_id: Optional[str] = None) -> JobRecord:
    conn = await _ensure_conn()
    now = time.time()
    # Upsert logic: if the row already exists (likely created by a prior status update before
    # we had workflow_id/owner_id), update those columns ONLY if they are currently NULL.
    # Preserve existing status/created_at/seq/result/error fields.
    await conn.execute(
        """
        INSERT INTO runs (run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id)
        VALUES (?, ?, 'pending', ?, ?, NULL, NULL, 0, ?)
        ON CONFLICT(run_id) DO UPDATE SET
          workflow_id = COALESCE(runs.workflow_id, excluded.workflow_id),
          owner_id    = COALESCE(runs.owner_id,    excluded.owner_id)
        """,
        (run_id, workflow_id, now, now, owner_id),
    )
    await conn.commit()

    # Read back the row (may have pre-existed)
    rec = await get_job(run_id)
    if rec is None:
        rec = JobRecord(run_id=run_id, workflow_id=workflow_id, created_at=now, updated_at=now,
                        status="pending", seq=0, owner_id=owner_id)
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
    cur = await conn.execute("SELECT run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id FROM runs WHERE run_id = ?", (run_id,))
    row = await cur.fetchone()
    if not row:
        return None
    result = None
    try:
        # result column is at index 5
        result = json.loads(row[5]) if row[5] else None
    except Exception:
        result = row[5]
    # row mapping: 0=run_id,1=workflow_id,2=status,3=created_at,4=updated_at,5=result,6=error,7=seq,8=owner_id
    return JobRecord(run_id=row[0], workflow_id=row[1], status=row[2], created_at=row[3], updated_at=row[4], result=result, error=row[6], seq=row[7] or 0, owner_id=row[8])
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
        INSERT INTO runs (run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id)
        VALUES (?, NULL, ?, ?, ?, ?, ?, 1, NULL)
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
    q = "SELECT run_id, workflow_id, status, created_at, updated_at, result, error, seq, owner_id FROM runs"
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
        # row mapping: 0=run_id,1=workflow_id,2=status,3=created_at,4=updated_at,5=result,6=error,7=seq,8=owner_id
        out[row[0]] = JobRecord(run_id=row[0], workflow_id=row[1], status=row[2], created_at=row[3], updated_at=row[4], result=result, error=row[6], seq=row[7] or 0, owner_id=row[8])
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
