"""Compatibility shim for the job store.

The real implementation has moved to `services.job_store`. This module keeps a
thin re-export shim so existing imports that reference `workflow_runner.job_manager`
continue to work during the refactor.
"""

from .services.job_store import *  # type: ignore

__all__ = [
    "Job",
    "JobStatus",
    "create_job",
    "get_job",
    "list_jobs",
    "remove_job",
    "set_job_status",
]
