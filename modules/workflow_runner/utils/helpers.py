"""Utility helpers moved from the module root into `utils` for SoC.

This module provides small helpers used across the workflow_runner package.
"""
import logging
from typing import Any

from server import PromptServer


def _emit_run_progress(run_id: str, message: str, **extra: Any) -> None:
    payload = {"run_id": run_id, "message": message}
    if extra:
        payload.update(extra)
    try:
        PromptServer.instance.send_sync("lf-runner:progress", payload)
    except Exception:
        logging.exception("Failed to send progress event for run %s", run_id)
