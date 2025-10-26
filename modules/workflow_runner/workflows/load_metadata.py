from pathlib import Path
from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, WorkflowNode

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "10":  # Image loader
            name = "source_path"
            source_path = inputs.get(name)
            if not source_path:
                raise InputValidationError(name)

            if isinstance(source_path, (list, tuple)):
                source_path = next((v for v in source_path if v), source_path[0] if len(source_path) > 0 else None)

            if isinstance(source_path, dict):
                source_path = source_path.get('path') or source_path.get('file') or source_path.get('name')

            if isinstance(source_path, str) and ';' in source_path:
                parts = [p for p in (s.strip() for s in source_path.split(';')) if p]
                source_path = parts[0] if parts else source_path

            resolved_path = Path(source_path).expanduser()
            if not resolved_path.exists():
                raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

            resolved_str = str(resolved_path)
            inputs_map["file_names"] = resolved_str
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
