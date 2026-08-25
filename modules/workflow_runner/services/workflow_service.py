import json
import logging

from typing import Any, Dict, List, Optional

from .registry import get_workflow as _get_workflow, list_workflows as _list_workflows


def _default_input_values(workflow: object) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for cell in getattr(workflow, "inputs", ()):
        props = getattr(cell, "props", None)
        if isinstance(props, dict) and "lfValue" in props:
            values[getattr(cell, "id")] = props["lfValue"]
    return values

# region List/Get Workflows
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
        configure_download = getattr(workflow, "configure_download", None)
        if callable(configure_download):
            prompt = workflow.load_prompt()
            configure_download(prompt, _default_input_values(workflow))
            return prompt
        with workflow.workflow_path.open("r", encoding="utf-8") as wf:
            return json.load(wf)
    except FileNotFoundError:
        logging.exception("Workflow file not found: %s", workflow_id)
        return None
    except Exception:
        logging.exception("Error loading workflow %s", workflow_id)
        return None
# endregion
