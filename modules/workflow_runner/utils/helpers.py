"""Utility helpers for workflow-runner.

Note: the `_emit_run_progress` helper was moved into
`services/run_service.py` where it's used. This module is kept as a
placeholder for other small helpers and to avoid breaking imports.
"""

import logging
from typing import Any

# Other helper functions may live here in future. The progress-emitting
# helper is intentionally colocated with the run orchestration logic.
