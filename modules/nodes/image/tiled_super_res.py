import time
from typing import List

from PIL import Image, ImageDraw, ImageFont

import torch
import torch.nn.functional as F

from comfy import model_management
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters.unsharp_mask import unsharp_mask_effect
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
)
from ...utils.helpers.torch import TilePlan, blend_upscaled_tiles, plan_input_tiles
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.ui import create_compare_node

# region LF_TiledSuperRes
class LF_TiledSuperRes:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Image or image list to upscale."}),
                "upscale_model": (Input.UPSCALE_MODEL, {"tooltip": "Preloaded spandrel upscaling model."}),
                "target_long_edge": (Input.INTEGER, {
                    "default": 2048,
                    "max": 16384,
                    "min": 0,
                    "step": 64,
                    "tooltip": "Desired longest edge after upscaling. Set 0 to use the model's native scale.",
                }),
                "tile_count": (Input.INTEGER, {
                    "default": 4,
                    "min": 1,
                    "max": 32,
                    "tooltip": "Approximate number of tiles to process. Collapses to a single tile when the whole image fits in memory.",
                }),
                "sharpen": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Optional unsharp-mask amount applied after blending.",
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, False, False, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_TYPES = ("IMAGE", "IMAGE", "JSON")
    RETURN_NAMES = ("image", "image_list", "stats")

    def on_exec(self, **kwargs: dict):
        images = normalize_input_image(kwargs.get("image"))
        upscale_model = normalize_list_to_value(kwargs.get("upscale_model"))
        target_long_edge = int(normalize_list_to_value(kwargs.get("target_long_edge")))
        tile_count = int(normalize_list_to_value(kwargs.get("tile_count")))
        sharpen_amount = float(normalize_list_to_value(kwargs.get("sharpen")))

        if upscale_model is None:
            raise RuntimeError("Upscale model is required.")

        if tile_count < 1:
            tile_count = 1
        if tile_count % 2 != 0 and tile_count > 1:
            tile_count += 1

        if not images:
            raise RuntimeError("No images provided for super-resolution.")

        device = model_management.get_torch_device()

        dtype_bytes = images[0].element_size()
        channels = images[0].shape[-1]
        max_h = max(int(img.shape[1]) for img in images)
        max_w = max(int(img.shape[2]) for img in images)
        sample_plan = plan_input_tiles(max_w, max_h, tile_count)
        max_tile_pixels = max(spec.width * spec.height for spec in sample_plan.tiles)
        max_input_tile_bytes = max_tile_pixels * channels * dtype_bytes
        scale = float(getattr(upscale_model, "scale", 1.0))
        max_upscaled_tile_pixels = int(round(max_tile_pixels * (scale ** 2)))
        max_upscaled_tile_bytes = max_upscaled_tile_pixels * channels * dtype_bytes

        canvas_h = int(round(max_h * scale))
        canvas_w = int(round(max_w * scale))
        canvas_bytes = canvas_h * canvas_w * channels * dtype_bytes

        if target_long_edge > 0 and max(max_h, max_w) > 0:
            target_scale = target_long_edge / max(max_h, max_w)
            effective_scale = max(scale, target_scale)
        else:
            effective_scale = scale

        output_h = int(round(max_h * effective_scale))
        output_w = int(round(max_w * effective_scale))
        output_bytes = output_h * output_w * channels * dtype_bytes

        safety_margin = 64 * 1024 * 1024
        model_module = getattr(upscale_model, "model", upscale_model)
        try:
            model_bytes = model_management.module_size(model_module)
        except Exception:
            model_bytes = 0

        memory_required = (
            model_bytes
            + max_input_tile_bytes
            + max_upscaled_tile_bytes
            + (canvas_bytes * 2)
            + output_bytes
            + safety_margin
        )

        if model_management.get_free_memory(device) < memory_required:
            model_management.free_memory(memory_required, device)

        if hasattr(upscale_model, "to"):
            upscale_model.to(device)

        upscaled_images: List[torch.Tensor] = []
        stats_rows: List[dict] = []
        compare_nodes: List[dict] = []

        for index, image in enumerate(images):
            start = time.perf_counter()
            h, w = image.shape[1], image.shape[2]
            plan = plan_input_tiles(w, h, tile_count)

            tiles_out: List[torch.Tensor] = []
            for spec in plan.tiles:
                patch = image[:, spec.y0:spec.y1, spec.x0:spec.x1, :]
                patch_chw = patch.permute(0, 3, 1, 2).to(device)
                with torch.autocast(device.type, enabled=device.type == "cuda"):
                    upscaled = upscale_model(patch_chw)
                upscaled = upscaled.clamp(0.0, 1.0)
                tiles_out.append(upscaled.permute(0, 2, 3, 1).detach())

            blended = blend_upscaled_tiles(
                tiles_out,
                plan.tiles,
                scale=scale,
                device=device,
                channels=image.shape[-1],
            )

            if target_long_edge > 0:
                final_long_edge = max(h, w) * scale
                if abs(final_long_edge - target_long_edge) > 1:
                    target_scale = target_long_edge / max(h, w)
                    target_h = int(round(h * target_scale))
                    target_w = int(round(w * target_scale))
                    blended = F.interpolate(
                        blended.permute(0, 3, 1, 2),
                        size=(target_h, target_w),
                        mode="bicubic",
                        align_corners=False,
                        antialias=True,
                    ).permute(0, 2, 3, 1)

            if sharpen_amount > 0:
                sharpened_samples: List[torch.Tensor] = []
                original_device = blended.device
                original_dtype = blended.dtype
                blended_cpu = blended.detach().to(torch.float32).cpu()

                for sample in blended_cpu:
                    sample_batch = sample.unsqueeze(0)
                    sharpened = unsharp_mask_effect(
                        sample_batch,
                        amount=sharpen_amount,
                        radius=5,
                        sigma=1.0,
                        threshold=0.0,
                    )

                    if sharpened.dim() == 3:
                        sharpened = sharpened.unsqueeze(0)
                    sharpened_samples.append(sharpened)

                if sharpened_samples:
                    blended = torch.cat(sharpened_samples, dim=0).to(
                        device=original_device,
                        dtype=original_dtype,
                    )

            blended = blended.clamp(0.0, 1.0).to(image.dtype).cpu()
            upscaled_images.append(blended)

            clean_url, debug_url = self._save_compare_images(
                blended,
                plan,
                base_width=w,
                base_height=h,
            )
            compare_nodes.append(create_compare_node(clean_url, debug_url, index))

            elapsed = time.perf_counter() - start
            stats_rows.append({
                "index": index,
                "input_size": [int(h), int(w)],
                "output_size": [int(blended.shape[1]), int(blended.shape[2])],
                "tiles": len(plan.tiles),
                "grid": [plan.cols, plan.rows],
                "model_scale": scale,
                "duration": elapsed,
            })

        if hasattr(upscale_model, "to"):
            upscale_model.to("cpu")

        batch_list, image_list = normalize_output_image(upscaled_images)

        dataset = {
            "nodes": compare_nodes,
        }

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}tiledsuperres",
            {
                "node": kwargs.get("node_id"),
                "dataset": dataset,
            },
        )

        return batch_list[0], image_list, {"runs": stats_rows}

    def _save_compare_images(
        self,
        image: torch.Tensor,
        plan: TilePlan,
        *,
        base_width: int,
        base_height: int,
    ) -> tuple[str, str]:
        clean_pil = tensor_to_pil(image)
        debug_image = self._render_tile_overlay(
            clean_pil.copy(),
            plan,
            base_width=base_width,
            base_height=base_height,
        )

        output_file_clean, subfolder_clean, filename_clean = resolve_filepath(
            filename_prefix="tiled_super_res",
            image=image,
        )
        clean_pil.save(output_file_clean, format="PNG")
        clean_url = get_resource_url(subfolder_clean, filename_clean, "temp")

        output_file_debug, subfolder_debug, filename_debug = resolve_filepath(
            filename_prefix="tiled_super_res_debug",
            image=image,
        )
        debug_image.save(output_file_debug, format="PNG")
        debug_url = get_resource_url(subfolder_debug, filename_debug, "temp")

        return clean_url, debug_url

    @staticmethod
    def _render_tile_overlay(
        base_image: Image.Image,
        plan: TilePlan,
        *,
        base_width: int,
        base_height: int,
    ) -> Image.Image:
        rgba_base = base_image.convert("RGBA")
        overlay = Image.new("RGBA", rgba_base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        width, height = rgba_base.size
        scale_x = width / float(base_width if base_width > 0 else 1)
        scale_y = height / float(base_height if base_height > 0 else 1)
        font = ImageFont.load_default()

        for idx, spec in enumerate(plan.tiles):
            outer = [
                int(round(spec.x0 * scale_x)),
                int(round(spec.y0 * scale_y)),
                int(round(spec.x1 * scale_x)),
                int(round(spec.y1 * scale_y)),
            ]
            inner = [
                int(round(spec.inner_x0 * scale_x)),
                int(round(spec.inner_y0 * scale_y)),
                int(round(spec.inner_x1 * scale_x)),
                int(round(spec.inner_y1 * scale_y)),
            ]

            outer = LF_TiledSuperRes._clamp_rect(outer, width, height)
            inner = LF_TiledSuperRes._clamp_rect(inner, width, height)

            draw.rectangle(outer, outline=(255, 80, 80, 220), width=2, fill=(255, 64, 64, 48))
            if outer != inner:
                draw.rectangle(inner, outline=(64, 255, 128, 220), width=1)

            if len(plan.tiles) > 1:
                label = str(idx + 1)
                if hasattr(draw, "textbbox"):
                    bbox = draw.textbbox((0, 0), label, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                else:
                    text_w, text_h = draw.textsize(label, font=font)
                text_x = min(max(outer[0] + 6, 0), max(0, width - text_w - 1))
                text_y = min(max(outer[1] + 6, 0), max(0, height - text_h - 1))
                bg_rect = (
                    text_x - 4,
                    text_y - 4,
                    text_x + text_w + 4,
                    text_y + text_h + 4,
                )
                draw.rectangle(bg_rect, fill=(0, 0, 0, 160))
                draw.text((text_x, text_y), label, fill=(255, 255, 255, 230), font=font)

        combined = Image.alpha_composite(rgba_base, overlay)
        return combined.convert("RGB")

    @staticmethod
    def _clamp_rect(rect: list[int], width: int, height: int) -> list[int]:
        x0, y0, x1, y1 = rect
        x0 = max(0, min(width - 1, x0))
        y0 = max(0, min(height - 1, y0))
        x1 = max(0, min(width, x1))
        y1 = max(0, min(height, y1))
        if x1 <= x0:
            x1 = min(width, x0 + 1)
        if y1 <= y0:
            y1 = min(height, y0 + 1)
        return [x0, y0, x1, y1]

# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_TiledSuperRes": LF_TiledSuperRes,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_TiledSuperRes": "Tiled Super Resolution",
}
# endregion


