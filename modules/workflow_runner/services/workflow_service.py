import json
import logging

from typing import Any, Dict, List, Optional

from .definition_inputs import default_input_values

from .registry import (
    WorkflowOrchestraNode,
    get_workflow as _get_workflow,
    list_workflows as _list_workflows,
)


class WorkflowHasNoDownloadableGraphError(LookupError):
    """Raised when a registered orchestra is requested as a Comfy graph."""

    code = "workflow_has_no_downloadable_graph"

    def __init__(self, workflow_id: str) -> None:
        self.workflow_id = workflow_id
        super().__init__(self.code)


# region List/Get Workflows
def list_workflows() -> List[Dict[str, Any]]:
    """Return the list of available workflows from the registry."""
    try:
        return _list_workflows()
    except Exception:
        logging.exception("Failed to list workflows")
        return []

def get_workflow_content(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Return a block's JSON graph, or ``None`` when the ID is unknown.

    Raises ``WorkflowHasNoDownloadableGraphError`` when the ID names a
    registered graph-free orchestra.
    """
    if not workflow_id:
        return None

    try:
        workflow = _get_workflow(workflow_id)
        if not workflow:
            return None
        if isinstance(workflow, WorkflowOrchestraNode):
            # An orchestra has no graph of its own; its declared blocks remain
            # the only downloadable graph authorities.
            raise WorkflowHasNoDownloadableGraphError(workflow_id)
        configure_download = getattr(workflow, "configure_download", None)
        if callable(configure_download):
            prompt = workflow.load_prompt()
            configure_download(prompt, default_input_values(workflow))
            return prompt
        with workflow.workflow_path.open("r", encoding="utf-8") as wf:
            return json.load(wf)
    except FileNotFoundError:
        logging.exception("Workflow file not found: %s", workflow_id)
        return None
    except WorkflowHasNoDownloadableGraphError:
        raise
    except Exception:
        logging.exception("Error loading workflow %s", workflow_id)
        return None
# endregion
