import logging
from typing import Any, Optional

LOG = logging.getLogger(__name__)


def serialize_job(job: Any, include_result_for_terminal: bool = False) -> dict:
    """Serialize a Job-like object into the JSON-friendly dict used by APIs and SSE.

    Accepts either the in-memory `Job` dataclass, adapter record objects from
    persistence layers, or simple dict-like objects.
    """
    try:
        run_id = getattr(job, "id", None) or getattr(job, "run_id", None)
        workflow_id = getattr(job, "workflow_id", None)
        status_raw = getattr(job, "status", None)
        if hasattr(status_raw, "value"):
            status = status_raw.value
        else:
            status = str(status_raw) if status_raw is not None else None

        created_at = getattr(job, "created_at", None)
        updated_at = getattr(job, "updated_at", None)
        error = getattr(job, "error", None)
        result = getattr(job, "result", None)
        owner_id = getattr(job, "owner_id", None)
        seq = getattr(job, "seq", 0) or 0

        # Only include result for terminal statuses unless caller requests otherwise
        terminal_statuses = {"succeeded", "failed", "cancelled"}
        if not include_result_for_terminal and (status not in terminal_statuses):
            result = None

        return {
            "id": f"{run_id}:{seq}",
            "run_id": run_id,
            "workflow_id": workflow_id,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
            "error": error,
            "result": result,
            "owner_id": owner_id,
            "seq": seq,
        }
    except Exception:
        LOG.exception("serialize_job: failed to serialize job")
        return {}


__all__ = ["serialize_job"]
