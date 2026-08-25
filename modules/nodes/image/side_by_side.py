from __future__ import annotations

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch.image_composite import (
    MAX_COMPOSITE_PIXELS,
    promote_to_rgba,
    render_label_chip,
    resize_composite_image,
    validate_composite_image,
    validate_composite_integer,
)
from ...utils.helpers.ui import create_masonry_node


def _scaled_width(width: int, height: int, target_height: int) -> int:
    """Round a positive scaled width to nearest integer, with halves rounded up."""
    return max(1, (width * target_height + height // 2) // height)


def _burn_label(
    image: torch.Tensor,
    label: str,
    *,
    pane_x: int,
    pane_width: int,
) -> None:
    height = int(image.shape[1])
    margin = max(1, min(8, height // 40))
    available_width = pane_width - margin * 2
    available_height = height - margin * 2
    chip = render_label_chip(
        label,
        max_width=available_width,
        max_height=available_height,
        channels=int(image.shape[-1]),
    )
    if chip is None:
        return

    chip = chip.to(device=image.device, dtype=image.dtype)
    chip_height, chip_width = chip.shape[:2]
    x = pane_x + margin
    y = margin
    image[:, y : y + chip_height, x : x + chip_width, :] = chip.unsqueeze(0)


def compose_side_by_side(
    image_a: torch.Tensor,
    image_b: torch.Tensor,
    *,
    gap_px: int = 8,
    max_height: int = 0,
    show_labels: bool = False,
    label_a: str = "A",
    label_b: str = "B",
) -> torch.Tensor:
    """Build an alpha-safe horizontal composite from two Comfy IMAGE tensors."""
    gap_px = validate_composite_integer(gap_px, "gap_px", minimum=0)
    max_height = validate_composite_integer(max_height, "max_height", minimum=0)
    if not isinstance(show_labels, bool):
        raise ValueError("show_labels must be a boolean.")

    image_a = validate_composite_image(image_a, "image_a")
    image_b = validate_composite_image(image_b, "image_b")
    image_b = image_b.to(device=image_a.device)

    batch_a, height_a, width_a, _ = image_a.shape
    batch_b, height_b, width_b, _ = image_b.shape
    if batch_a != batch_b and batch_a != 1 and batch_b != 1:
        raise ValueError(
            "image_a and image_b batch sizes must match, or one batch must contain "
            "exactly one image."
        )
    batch_size = max(batch_a, batch_b)

    target_height = max(height_a, height_b)
    if max_height > 0:
        target_height = min(target_height, max_height)
    target_width_a = _scaled_width(width_a, height_a, target_height)
    target_width_b = _scaled_width(width_b, height_b, target_height)
    output_width = target_width_a + gap_px + target_width_b
    if target_height * output_width * batch_size > MAX_COMPOSITE_PIXELS:
        raise ValueError(
            "LF_SideBySide output exceeds the 64-megapixel safety limit; set a "
            "smaller max_height."
        )

    resized_a = resize_composite_image(image_a, target_height, target_width_a)
    resized_b = resize_composite_image(image_b, target_height, target_width_b)
    if batch_a == 1 and batch_size > 1:
        resized_a = resized_a.expand(batch_size, -1, -1, -1)
    if batch_b == 1 and batch_size > 1:
        resized_b = resized_b.expand(batch_size, -1, -1, -1)

    channels = 4 if resized_a.shape[-1] == 4 or resized_b.shape[-1] == 4 else 3
    if channels == 4:
        resized_a = promote_to_rgba(resized_a)
        resized_b = promote_to_rgba(resized_b)

    if gap_px:
        gap = torch.zeros(
            (batch_size, target_height, gap_px, channels),
            device=image_a.device,
            dtype=image_a.dtype,
        )
        if channels == 4:
            gap[..., 3] = 1.0
        composite = torch.cat((resized_a, gap, resized_b), dim=2)
    else:
        composite = torch.cat((resized_a, resized_b), dim=2)

    if show_labels:
        composite = composite.clone()
        _burn_label(composite, label_a, pane_x=0, pane_width=target_width_a)
        _burn_label(
            composite,
            label_b,
            pane_x=target_width_a + gap_px,
            pane_width=target_width_b,
        )

    return composite


# region LF_SideBySide
class LF_SideBySide:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": (
                    Input.IMAGE,
                    {"tooltip": "Image shown in the left pane."},
                ),
                "image_b": (
                    Input.IMAGE,
                    {"tooltip": "Image shown in the right pane."},
                ),
                "gap_px": (
                    Input.INTEGER,
                    {
                        "default": 8,
                        "min": 0,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Opaque black divider width in pixels. Set 0 for no divider.",
                    },
                ),
                "max_height": (
                    Input.INTEGER,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 16384,
                        "step": 1,
                        "tooltip": "Maximum composite height. Set 0 to use the taller input's height.",
                    },
                ),
                "show_labels": (
                    Input.BOOLEAN,
                    {
                        "default": False,
                        "tooltip": "Burn the two labels into the upper-left corner of their panes.",
                    },
                ),
                "label_a": (
                    Input.STRING,
                    {
                        "default": "A",
                        "tooltip": "Left-pane label, used only when show_labels is enabled.",
                    },
                ),
                "label_b": (
                    Input.STRING,
                    {
                        "default": "B",
                        "tooltip": "Right-pane label, used only when show_labels is enabled.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = ("Horizontally stitched image batch.",)
    RETURN_NAMES = ("image",)
    RETURN_TYPES = (Input.IMAGE,)

    def on_exec(
        self,
        image_a: torch.Tensor,
        image_b: torch.Tensor,
        gap_px: int = 8,
        max_height: int = 0,
        show_labels: bool = False,
        label_a: str = "A",
        label_b: str = "B",
        **kwargs: dict,
    ) -> dict:
        self._temp_cache.cleanup()
        composite = compose_side_by_side(
            image_a,
            image_b,
            gap_px=gap_px,
            max_height=max_height,
            show_labels=show_labels,
            label_a=label_a,
            label_b=label_b,
        )

        nodes: list[dict] = []
        dataset = {"nodes": nodes}
        for index, image in enumerate(composite):
            single_image = image.unsqueeze(0)
            preview = tensor_to_pil(single_image)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix="side_by_side",
                image=single_image,
                temp_cache=self._temp_cache,
            )
            preview.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")
            nodes.append(create_masonry_node(filename, url, index))

        safe_send_sync(
            "sidebyside",
            {"dataset": dataset},
            kwargs.get("node_id"),
        )
        return {
            "ui": {"lf_output": [{"dataset": dataset}]},
            "result": (composite,),
        }


# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SideBySide": LF_SideBySide,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SideBySide": "Side by side",
}
# endregion
