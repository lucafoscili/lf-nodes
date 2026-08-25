from pathlib import Path
from typing import Any, Dict

from ..services.registry import WorkflowCell, WorkflowNode
from .utils import resolve_load_image_reference


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    before_reference = resolve_load_image_reference(inputs, "before_path")
    after_reference = resolve_load_image_reference(inputs, "after_path")

    prompt["load_before"]["inputs"]["image"] = before_reference
    prompt["load_after"]["inputs"]["image"] = after_reference


input_before = WorkflowCell(
    node_id="load_before",
    id="before_path",
    value="Original image",
    shape="upload",
    description=(
        "Choose the original or reference image. It appears on the left side of "
        "the comparison. PNG, JPEG, and WebP are good choices."
    ),
    props={
        "lfHtmlAttributes": {
            "accept": "image/*",
        },
        "lfLabel": "1. Choose the original image",
    },
)

input_after = WorkflowCell(
    node_id="load_after",
    id="after_path",
    value="Changed image",
    shape="upload",
    description=(
        "Choose the changed image you want to inspect. It appears on the right "
        "side. Different dimensions are allowed, and transparency is preserved."
    ),
    props={
        "lfHtmlAttributes": {
            "accept": "image/*",
        },
        "lfLabel": "2. Choose the changed image",
    },
)

output_comparison = WorkflowCell(
    node_id="display_comparison",
    id="comparison",
    shape="compare",
    description=(
        "Drag across the image to reveal either version, or switch to the split "
        "view when you want both images side by side."
    ),
    props={
        "lfShape": "image",
        "lfView": "main",
    },
)


id = "compare_images"
node = WorkflowNode(
    id=id,
    value="Compare Images",
    description=(
        "Inspect one original image against one changed image with an interactive "
        "before-and-after view. Both files keep their original dimensions and transparency."
    ),
    category="Image Processing",
    inputs=[input_before, input_after],
    outputs=[output_comparison],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
)


WORKFLOW = node
