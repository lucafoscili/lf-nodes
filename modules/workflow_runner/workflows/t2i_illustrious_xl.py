from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "3":  # Positive CLIPTextEncode
            name = "prompt"
            prompt_value = inputs.get(name)
            if prompt_value:
                inputs_map["text"] = str(prompt_value)
            else:
                raise InputValidationError(name)

        if node_id == "6":  # KSampler seed (Optional)
            name = "seed"
            seed = inputs.get(name)
            if seed is not None and seed != "":
                inputs_map["seed"] = int(seed)

        if node_id == "1":  # CheckpointLoaderSimple (Optional)
            name = "checkpoint"
            ckpt = inputs.get(name)
            if ckpt:
                inputs_map["ckpt_name"] = str(ckpt)
# endregion

# region Inputs
input_prompt = WorkflowCell(
    node_id="3",
    id="prompt",
    value="Prompt",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "prompt",
            "type": "text",
        },
        "lfLabel": "Prompt",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Illustrious/SDXL anime models work best with Danbooru-style tags and quality boosters (i.e.: 'masterpiece, best quality, 1girl, solo').",
        },
        "lfStyling": "textarea",
        "lfValue": "masterpiece, best quality, 1girl, solo, full body, standing",
    },
)
input_seed = WorkflowCell(
    node_id="6",
    id="seed",
    value="Seed",
    shape="textfield",
    required=False,
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "min": 0,
            "step": 1,
            "name": "seed",
            "type": "number",
        },
        "lfLabel": "Seed",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: the seed for generation. Same seed reproduces an image.",
        },
        "lfValue": "42",
    },
)
input_checkpoint = WorkflowCell(
    node_id="1",
    id="checkpoint",
    value="Checkpoint",
    shape="textfield",
    required=False,
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "checkpoint",
            "type": "text",
        },
        "lfLabel": "Checkpoint",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Optional: override the checkpoint (e.g. 'IL1\\\\novaAnimeXL_ilV120.safetensors'). Defaults to Genesis v0.10.",
        },
        "lfValue": "Genesis v0.10.safetensors",
    },
)
# endregion

# region Outputs
output_png = WorkflowCell(
    node_id="7",
    id="png_file",
    shape="masonry",
    description="PNG File",
)
# endregion

# region Workflow Definition
id = "t2i_illustrious_xl"
category = "Text to Image"
value = "Illustrious XL Anime Portrait"
description = "Text-to-image workflow for Illustrious/SDXL anime portraits at 832x1216. Illustrious-family checkpoints work best with English Danbooru-style tags and quality boosters (i.e.: 'masterpiece, best quality, amazing quality, very aesthetic, absurdres'). Default checkpoint: Genesis v0.10; override via the Checkpoint input."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_prompt,
        input_seed,
        input_checkpoint,
    ],
    outputs=[
        output_png,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
