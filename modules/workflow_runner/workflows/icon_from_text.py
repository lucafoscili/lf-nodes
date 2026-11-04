"""Icon from Text: a square, framed game-style icon from a prompt and optional style images.

Krea 2 Turbo paints the subject at 1024 px. With one to three style images the
community style-reference adapter carries their visual language; without any,
the adapter is removed and the prompt alone guides the painting. Background
Remover then finds the subject, and Icon Framer fits it into a square with a
backdrop, glow, outline, vignette and bevelled rim, saved at a master size and
at a small display size beside the painting itself.

One submission paints one candidate: submit several seeds for several
candidates, so each can be reproduced from its own seed.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from ..services.registry import WorkflowCell, WorkflowNode
from .krea2 import (
    _LOCAL_MAX_SEED,
    _OFFICIAL_KREA2_MODEL,
    _KREA2_MODELS,
    _STYLE_LORA,
    _number,
    _number_cell,
    _prompt_cell,
    _select_cell,
    _upload_cell,
)
from .utils import (
    choice as _choice,
    has_input_value as _has_value,
    integer as _integer,
    required_text as _required_text,
    resolve_load_image_reference,
)

_WORKFLOW_PATH = Path(__file__).resolve().with_suffix(".json")
_STYLE_SLOTS = ("style_1", "style_2", "style_3")
_DEFAULT_FOLDER = "LF_Nodes/IconFromText"
_FOLDER = re.compile(r"^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*$")
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_BACKDROPS = (
    ("color", "Flat colour", "The subject sits on the backdrop colour."),
    ("source", "Painted surroundings", "The subject keeps the painting's own surroundings."),
)


def _colour(inputs: Dict[str, Any], name: str, default: str) -> str:
    value = inputs.get(name, default)
    if value in (None, ""):
        value = default
    if not isinstance(value, str) or not _HEX.match(value.strip()):
        raise ValueError(f"{name} must be a colour in the format #RRGGBB.")
    return value.strip()


def _folder(inputs: Dict[str, Any]) -> str:
    value = inputs.get("output_folder", _DEFAULT_FOLDER)
    if value in (None, ""):
        value = _DEFAULT_FOLDER
    if not isinstance(value, str) or not _FOLDER.match(value.strip()):
        raise ValueError(
            "output_folder must be relative folder names of letters, digits, '_' or '-', separated by '/'."
        )
    return value.strip()


def _style_inputs(inputs: Dict[str, Any]) -> list[str]:
    """The style image inputs given, which must fill the slots from the first."""

    given = [f"{slot}_image" for slot in _STYLE_SLOTS if _has_value(inputs, f"{slot}_image")]
    expected = [f"{slot}_image" for slot in _STYLE_SLOTS[: len(given)]]
    if given != expected:
        raise ValueError("Style images fill their slots in order: give style_1_image before style_2_image.")
    return given


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any], *, stage_uploads: bool = True) -> None:
    text = _required_text(inputs, "prompt")
    model_name = _choice(inputs, "model_name", _OFFICIAL_KREA2_MODEL, _KREA2_MODELS)
    seed = _integer(inputs, "seed", 42, minimum=0, maximum=_LOCAL_MAX_SEED)
    steps = _integer(inputs, "steps", 8, minimum=4, maximum=20)
    style_strength = _number(inputs, "style_strength", 1.0, minimum=0.0, maximum=2.0)
    master_size = _integer(inputs, "master_size", 512, minimum=64, maximum=1024)
    icon_size = _integer(inputs, "icon_size", 64, minimum=16, maximum=master_size)
    fill = _number(inputs, "fill", 0.86, minimum=0.3, maximum=1.0)
    backdrop = _choice(inputs, "backdrop", "color", (option[0] for option in _BACKDROPS))
    backdrop_color = _colour(inputs, "backdrop_color", "#000000")
    glow_color = _colour(inputs, "glow_color", "#000000")
    glow_strength = _number(inputs, "glow_strength", 0.0, minimum=0.0, maximum=1.0)
    bevel = _number(inputs, "bevel", 0.05, minimum=0.0, maximum=0.2)
    folder = _folder(inputs)
    styles = _style_inputs(inputs)

    prompt["unet"]["inputs"]["unet_name"] = model_name
    prompt["positive"]["inputs"]["prompt"] = text
    prompt["sampler"]["inputs"].update({"seed": seed, "steps": steps})
    prompt["frame"]["inputs"].update(
        {
            "master_size": master_size,
            "icon_size": icon_size,
            "fill": fill,
            "backdrop": backdrop,
            "backdrop_color": backdrop_color,
            "glow_color": glow_color,
            "glow_strength": glow_strength,
            "bevel": bevel,
        }
    )

    if styles:
        prompt["lora"]["inputs"].update({"lora_name": _STYLE_LORA, "strength_model": style_strength})
    else:
        # Without a style image the adapter has nothing to read: paint from the prompt alone.
        prompt.pop("lora")
        prompt["patch"]["inputs"]["model"] = ["unet", 0]
    for index, slot in enumerate(_STYLE_SLOTS):
        name = f"{slot}_image"
        if name in styles:
            if stage_uploads:
                prompt[slot]["inputs"]["image"] = resolve_load_image_reference(inputs, name)
        else:
            prompt.pop(slot)
            prompt["positive"]["inputs"].pop(f"image{index + 1}")

    for node_id, part in (("save_source", "source"), ("save_master", "master"), ("save_icon", "icon")):
        prompt[node_id]["inputs"]["filename_prefix"] = f"{folder}/{part}/seed-{seed}"


def _configure_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    _configure(prompt, inputs, stage_uploads=False)


def _text_cell(node_id: str, cell_id: str, label: str, default: str, description: str) -> WorkflowCell:
    return WorkflowCell(
        node_id=node_id,
        id=cell_id,
        shape="textfield",
        value=label,
        description=description,
        props={
            "lfHtmlAttributes": {"autocomplete": "off", "name": cell_id, "type": "text"},
            "lfLabel": label,
            "lfHelper": {"showWhenFocused": False, "value": description},
            "lfValue": default,
        },
    )


WORKFLOW = WorkflowNode(
    id="icon_from_text",
    value="Icon from Text",
    description=(
        "Paint one object from a prompt with Krea 2 Turbo, optionally in the visual language of up to "
        "three style images, then cut it out and frame it as a square icon: a backdrop, an optional "
        "glow, a dark outline, darkened corners and a bevelled rim. Saves the painting, a master-size "
        "icon and a small icon. One run is one candidate; vary the seed for more."
    ),
    category="Image",
    inputs=[
        _prompt_cell(
            default=(
                "A single brass oil lantern with a glowing flame behind amber glass panes, centred, "
                "filling the frame, on a plain flat black background."
            ),
            description=(
                "Describe the one object: its material, colours and pose. Ask for it centred on a plain, "
                "flat background so the cut-out is clean; the style images carry the painting style."
            ),
        ),
        *(
            _upload_cell(
                slot,
                f"{slot}_image",
                f"Style image {index + 1}",
                "Optional: an icon or painting whose style the result should follow. Fill the slots in order.",
                required=False,
            )
            for index, slot in enumerate(_STYLE_SLOTS)
        ),
        _number_cell(
            node_id="lora",
            cell_id="style_strength",
            label="Style adapter strength",
            default="1",
            minimum=0,
            maximum=2,
            step=0.05,
            description="Strength of the style-reference adapter when style images are given.",
        ),
        _number_cell(
            node_id="sampler",
            cell_id="seed",
            label="Seed",
            default="42",
            minimum=0,
            maximum=_LOCAL_MAX_SEED,
            step=1,
            description="The candidate's seed; the same seed and inputs paint the same picture.",
        ),
        _number_cell(
            node_id="sampler",
            cell_id="steps",
            label="Steps",
            default="8",
            minimum=4,
            maximum=20,
            step=1,
            description="Denoising passes; 8 is the Turbo baseline.",
        ),
        _number_cell(
            node_id="frame",
            cell_id="master_size",
            label="Master size",
            default="512",
            minimum=64,
            maximum=1024,
            step=1,
            description="Edge of the large icon, in pixels.",
        ),
        _number_cell(
            node_id="frame",
            cell_id="icon_size",
            label="Icon size",
            default="64",
            minimum=16,
            maximum=1024,
            step=1,
            description="Edge of the small icon, in pixels, downscaled from the master.",
        ),
        _number_cell(
            node_id="frame",
            cell_id="fill",
            label="Fill",
            default="0.86",
            minimum=0.3,
            maximum=1,
            step=0.01,
            description="Share of the area inside the rim that the object's longer side fills.",
        ),
        _select_cell(
            node_id="frame",
            cell_id="backdrop",
            label="Backdrop",
            default="color",
            description="What sits behind the object.",
            options=_BACKDROPS,
        ),
        _text_cell("frame", "backdrop_color", "Backdrop colour", "#000000", "The backdrop colour, #RRGGBB."),
        _text_cell("frame", "glow_color", "Glow colour", "#000000", "The glow behind the object, #RRGGBB."),
        _number_cell(
            node_id="frame",
            cell_id="glow_strength",
            label="Glow strength",
            default="0",
            minimum=0,
            maximum=1,
            step=0.05,
            description="How strongly the glow lights the backdrop; 0 turns it off.",
        ),
        _number_cell(
            node_id="frame",
            cell_id="bevel",
            label="Rim width",
            default="0.05",
            minimum=0,
            maximum=0.2,
            step=0.005,
            description="Width of the bevelled rim as a share of the edge; 0 draws none.",
        ),
        _text_cell(
            "save_icon",
            "output_folder",
            "Output folder",
            _DEFAULT_FOLDER,
            "Folder under ComfyUI's output for the three images (source, master, icon).",
        ),
        _select_cell(
            node_id="unet",
            cell_id="model_name",
            label="Krea 2 model",
            default=_OFFICIAL_KREA2_MODEL,
            description="The Krea 2 diffusion model; the official Turbo base is the tested default.",
            options=tuple(
                (model, Path(model).stem, "An installed Krea 2 model from diffusion_models/KR2.")
                for model in _KREA2_MODELS
            ),
        ),
    ],
    outputs=[
        WorkflowCell(node_id="save_icon", id="icon", shape="masonry", description="The small framed icon."),
        WorkflowCell(node_id="save_master", id="master", shape="masonry", description="The master-size framed icon."),
        WorkflowCell(node_id="save_source", id="source", shape="masonry", description="The painting before framing."),
    ],
    configure_prompt=_configure,
    configure_download=_configure_download,
    workflow_path=_WORKFLOW_PATH,
)

__all__ = ["WORKFLOW"]
