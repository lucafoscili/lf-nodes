from pathlib import Path
from typing import Any, Dict

from ..registry import WorkflowCell, WorkflowNode
from .utils import resolve_upload_paths


# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "10":  # Image loader
            resolved_paths = resolve_upload_paths(inputs, "source_path", allow_multiple=True)
            inputs_map["file_names"] = (
                resolved_paths[0] if len(resolved_paths) == 1 else ";".join(resolved_paths)
            )
# endregion

# region Inputs
input_upload = WorkflowCell(
    node_id="10",
    id="source_path",
    value="Source image",
    shape="upload",
    props={
        "lfHtmlAttributes": {
            "accept": "image/*"
        },
        "lfLabel": "Source image",
    },
)
# endregion

# region Outputs
output_json = WorkflowCell(
    id="metadata",
    node_id="10",
    shape="code",
    description="Metadata",
    props={
        "lfLanguage": "json",
    }
)
# endregion

# region Workflow Definition
id = "load_metadata"
category = "JSON"
value = "Load metadata"
description = "Loads metadata from an image."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_upload,
    ],
    outputs=[
        output_json,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
