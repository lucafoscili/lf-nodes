"""Service layer for workflow listing and retrieval.

Thin wrappers around the existing registry functions. Keeps file-loading
and JSON parsing in one place so controllers remain simple.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from ..registry import get_workflow as _get_workflow, list_workflows as _list_workflows


def list_workflows() -> List[Dict[str, Any]]:
    """Return the list of available workflows from the registry."""
    try:
        return _list_workflows()
    except Exception:
        logging.exception("Failed to list workflows")
        return []


def get_workflow_content(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Return the JSON content of a workflow or None if not found.

    This mirrors the behaviour previously in handlers.route_get_workflow.
    """
    if not workflow_id:
        return None

    try:
        workflow = _get_workflow(workflow_id)
        if not workflow:
            return None
        with workflow.workflow_path.open("r", encoding="utf-8") as wf:
            return json.load(wf)
    except FileNotFoundError:
        logging.exception("Workflow file not found: %s", workflow_id)
        return None
    except Exception:
        logging.exception("Error loading workflow %s", workflow_id)
        return None
