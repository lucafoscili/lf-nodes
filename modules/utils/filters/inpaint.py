from typing import Dict, Tuple

import math
import os
import random
import torch
import torch.nn.functional as F

import comfy.sample
import nodes

from .unsharp_mask import unsharp_mask_effect
from ..constants import SAMPLERS, SCHEDULERS
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.conversion import base64_to_tensor, convert_to_boolean, convert_to_float, convert_to_int, tensor_to_pil
from ...utils.helpers.editing import get_editing_context
from ...utils.helpers.tagging import apply_wd14_tagging_to_prompt

# region Debug Preview Save
DEBUG_PREVIEW_SAVES = True # Toggle debug preview saves. Hardwired to False for normal runs; set True when debugging.

FilterResult = Tuple[torch.Tensor, Dict[str, str]]

# Sorted by area (ascending), expressed as (long_side, short_side)
MAX_UPSAMPLE_ASPECT_RATIO = 3.0
SDXL_RESOLUTION_PRESETS: tuple[tuple[int, int], ...] = (
    (1024, 1024),
    (1088, 960),
    (1152, 896),
    (1216, 832),
    (1280, 768),
    (1344, 768),
    (1344, 704),
    (1408, 704),
    (1472, 704),
    (1536, 640),
    (1600, 640),
    (1664, 576),
    (1728, 576),
)

def _save_tensor_preview(tensor: torch.Tensor, filename_prefix: str, save_type: str = "temp") -> str | None:
    """
    Saves a tensor as a preview image for debugging purposes if DEBUG_PREVIEW_SAVES is enabled.
    This function detaches the tensor, moves it to CPU, adjusts dimensions if necessary (e.g., adds batch dimension,
    permutes channels from first to last if in (B, C, H, W) format), clamps values to [0, 1], converts to a PIL image,
    and saves it as a PNG file. Only the first batch is processed and saved.

    Args:
        tensor (torch.Tensor): The input tensor to save as an image. Should be in shape (C, H, W) or (B, C, H, W).
        filename_prefix (str): Prefix for the output filename.
        save_type (str, optional): The type of save location (e.g., "temp"). Defaults to "temp".

    Returns:
        str | None: The URL of the saved image if successful and DEBUG_PREVIEW_SAVES is True, otherwise None.
                    Returns None if an exception occurs or if DEBUG_PREVIEW_SAVES is False.
    """
    if not DEBUG_PREVIEW_SAVES:
        return None

    try:
        dbg_tensor = tensor.detach().cpu()
        if dbg_tensor.ndim == 3:
            dbg_tensor = dbg_tensor.unsqueeze(0)
        if dbg_tensor.ndim == 4:
            # if channels-first (B,C,H,W) move to last
            if dbg_tensor.shape[1] in (1, 3, 4) and dbg_tensor.shape[-1] not in (1, 3, 4):
                dbg_tensor = dbg_tensor.permute(0, 2, 3, 1).contiguous()
        dbg_tensor = dbg_tensor.clamp(0.0, 1.0)
        dbg_to_save = dbg_tensor[0:1]
        dbg_image = tensor_to_pil(dbg_to_save)

        dbg_base = get_comfy_dir(save_type)
        dbg_out_file, dbg_sub, dbg_name = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=dbg_base,
            image=dbg_to_save,
        )
        dbg_image.save(dbg_out_file, format="PNG")
        return get_resource_url((dbg_sub or "").replace("\\", "/"), dbg_name, save_type)
    except Exception:
        return None
# endregion

# region Upsample Planning
def _align_up(value: int, alignment: int) -> int:
    """
    Aligns the given value up to the nearest multiple of the specified alignment.

    This function ensures that the returned value is at least 1 and is a multiple of the alignment.
    If alignment is less than or equal to 1, it simply returns the maximum of 1 and the integer value of the input.
    Otherwise, it calculates the smallest multiple of alignment that is greater than or equal to the value.

    Args:
        value (int): The value to be aligned. It will be converted to an integer.
        alignment (int): The alignment boundary. Must be an integer.

    Returns:
        int: The aligned value, which is a multiple of alignment and at least 1.
    """
    if alignment <= 1:
        return max(1, int(value))
    return max(alignment, ((int(value) + alignment - 1) // alignment) * alignment)


def _select_preset_dimensions(longer: int, shorter: int, area_limit: int) -> tuple[int, int] | None:
    """
    Selects the best preset dimensions from SDXL_RESOLUTION_PRESETS that meet the given constraints.
    This function iterates through predefined resolution presets and selects the one that:
    - Has dimensions at least as large as the provided longer and shorter sides.
    - Does not exceed the specified area limit.
    - Provides the smallest aspect ratio error compared to the desired ratio (longer/shorter).
    - Maximizes the area gain (among those with the same ratio error and area gain).

    Args:
        longer (int): The minimum required length for the longer dimension.
        shorter (int): The minimum required length for the shorter dimension.
        area_limit (int): The maximum allowed area (product of dimensions).

    Returns:
        tuple[int, int] | None: A tuple of (preset_long, preset_short) representing the best matching preset dimensions,
        or None if no valid preset is found or if any input is non-positive.
    """
    if longer <= 0 or shorter <= 0 or area_limit <= 0:
        return None

    orig_area = longer * shorter
    best_score: tuple[float, float, int] | None = None
    best_dims: tuple[int, int] | None = None
    desired_ratio = longer / shorter

    for preset_long, preset_short in SDXL_RESOLUTION_PRESETS:
        preset_area = preset_long * preset_short
        if preset_area > area_limit:
            continue
        if preset_long < longer or preset_short < shorter:
            continue
        area_gain = preset_area - orig_area
        if area_gain <= 0:
            continue
        ratio_error = abs((preset_long / preset_short) - desired_ratio)
        score = (ratio_error, -area_gain, preset_long)
        if best_score is None or score < best_score:
            best_score = score
            best_dims = (preset_long, preset_short)

    return best_dims

def _select_upsample_plan(
    orig_h: int,
    orig_w: int,
    upsample_target: int | None,
    align_multiple: int,
) -> dict | None:
    """
    Selects an upsampling plan for image dimensions based on original height and width,
    an optional upsample target, and an alignment multiple.
    This function determines new dimensions for upsampling an image while respecting
    constraints such as maximum aspect ratio (defined by MAX_UPSAMPLE_ASPECT_RATIO),
    area limits, and alignment requirements. It prioritizes preset dimensions if available,
    otherwise scales based on the upsample target. If the plan is invalid or no upsampling
    is needed, it returns None.

    Args:
        orig_h (int): The original height of the image.
        orig_w (int): The original width of the image.
        upsample_target (int | None): The target size for the longer dimension after upsampling.
                                      If None or <= 0, no upsampling plan is selected.
        align_multiple (int): The multiple to which dimensions must be aligned (e.g., for hardware constraints).

    Returns:
        dict | None: A dictionary containing the upsampling plan with keys:
            - "height" (int): The new height.
            - "width" (int): The new width.
            - "source" (str): The source of the dimensions ("preset" or "target").
            - "ratio" (float): The aspect ratio of the new dimensions.
            - "preset" (tuple[int, int] | None): The preset dimensions used, if applicable.
            - "area" (int): The area of the new dimensions.
        Returns None if no valid upsampling plan can be created (e.g., due to aspect ratio limits,
        invalid inputs, or no upsampling needed).

    Notes:
        - The function uses helper functions like _select_preset_dimensions and _align_up (assumed to be defined elsewhere).
        - Aspect ratio is calculated as max_dim / min_dim and must not exceed MAX_UPSAMPLE_ASPECT_RATIO.
        - Dimensions are aligned upwards to the nearest multiple of align_multiple.
        - If preset dimensions are selected, they take precedence over target-based scaling.
    """
    if not upsample_target or upsample_target <= 0:
        return None

    longer = max(orig_h, orig_w)
    shorter = min(orig_h, orig_w)
    if shorter <= 0:
        return None

    aspect_ratio = longer / shorter
    if aspect_ratio > MAX_UPSAMPLE_ASPECT_RATIO + 1e-6:
        return None

    area_limit = int(upsample_target) * int(upsample_target)
    preset_dims = _select_preset_dimensions(longer, shorter, area_limit)

    new_long: int | None = None
    new_short: int | None = None
    source: str | None = None

    if preset_dims:
        new_long, new_short = preset_dims
        source = "preset"
    else:
        if longer >= upsample_target:
            return None
        scale = upsample_target / float(longer)
        if scale <= 1.0:
            return None
        new_long = max(longer, int(round(longer * scale)))
        new_short = max(shorter, int(round(shorter * scale)))
        source = "target"

    new_long = _align_up(new_long, align_multiple)
    new_short = _align_up(new_short, align_multiple)
    if new_short <= 0 or new_long <= 0:
        return None

    new_ratio = max(new_long, new_short) / min(new_long, new_short)
    if new_ratio > MAX_UPSAMPLE_ASPECT_RATIO + 1e-6:
        if new_long >= new_short:
            min_short = _align_up(int(math.ceil(new_long / MAX_UPSAMPLE_ASPECT_RATIO)), align_multiple)
            new_short = max(new_short, min_short)
        else:
            min_long = _align_up(int(math.ceil(new_short / MAX_UPSAMPLE_ASPECT_RATIO)), align_multiple)
            new_long = max(new_long, min_long)

    if new_long <= longer and new_short <= shorter:
        return None

    if orig_h >= orig_w:
        new_height, new_width = new_long, new_short
        preset_ref = (new_long, new_short)
    else:
        new_height, new_width = new_short, new_long
        preset_ref = (new_long, new_short)

    final_ratio = max(new_height, new_width) / min(new_height, new_width)
    if final_ratio > MAX_UPSAMPLE_ASPECT_RATIO + 1e-6:
        return None

    area = new_height * new_width

    return {
        "height": new_height,
        "width": new_width,
        "source": source or "target",
        "ratio": final_ratio,
        "preset": preset_ref if source == "preset" else None,
        "area": area,
    }
# endregion

# region Sample Without Preview
def sample_without_preview(
    model,
    positive,
    negative,
    latent,
    seed,
    steps,
    cfg,
    sampler_name,
    scheduler_name,
    denoise_value,
):
    """
    Generates a new latent sample using the provided model and parameters, without generating a preview image.

    Args:
        model: The diffusion model used for sampling.
        positive: Conditioning information for positive prompts.
        negative: Conditioning information for negative prompts.
        latent (dict): Dictionary containing latent image data and optional batch index and noise mask.
        seed (int): Random seed for noise generation.
        steps (int): Number of sampling steps to perform.
        cfg (float): Classifier-free guidance scale.
        sampler_name (str): Name of the sampler to use.
        scheduler_name (str): Name of the scheduler to use.
        denoise_value (float): Denoising strength for the sampling process.

    Returns:
        dict: A copy of the input latent dictionary with the "samples" key updated to the newly generated latent samples.
    """
    latent_image = latent["samples"]
    latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)

    batch_inds = latent.get("batch_index")
    noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

    noise_mask = latent.get("noise_mask")

    samples = comfy.sample.sample(
        model,
        noise,
        steps,
        cfg,
        sampler_name,
        scheduler_name,
        positive,
        negative,
        latent_image,
        denoise=denoise_value,
        disable_noise=False,
        start_step=None,
        last_step=None,
        force_full_denoise=False,
        noise_mask=noise_mask,
        callback=None,
        disable_pbar=True,
        seed=seed,
    )

    out_latent = latent.copy()
    out_latent["samples"] = samples

    return out_latent
# endregion

# region Perform Inpaint
def perform_inpaint(
    *,
    model,
    clip,
    vae,
    image: torch.Tensor,
    mask: torch.Tensor,
    positive_prompt: str,
    negative_prompt: str,
    sampler_name: str,
    scheduler_name: str,
    steps: int,
    denoise: float,
    cfg: float,
    seed: int,
    disable_preview: bool = True,
    positive_conditioning=None,
    negative_conditioning=None,
    conditioning_mix: float = 0.0,
    conditioning_mode: str | None = None,
) -> torch.Tensor:
    """
    Performs inpainting on the given image using the specified model, mask, and prompts.

    Args:
        model: The diffusion model used for inpainting.
        clip: The CLIP model for text encoding.
        vae: The VAE model for encoding and decoding images.
        image (torch.Tensor): The input image tensor to be inpainted.
        mask (torch.Tensor): The mask tensor indicating regions to inpaint (1=inpaint, 0=keep original).
        positive_prompt (str): The positive text prompt guiding the inpainting.
        negative_prompt (str): The negative text prompt for undesired features.
        sampler_name (str): The name of the sampler to use for generation.
        scheduler_name (str): The name of the scheduler to use for generation.
        steps (int): Number of sampling steps.
        denoise (float): Denoising strength for inpainting.
        cfg (float): Classifier-free guidance scale.
        seed (int): Random seed for reproducibility.
        disable_preview (bool, optional): If True, disables preview sampling for efficiency. Defaults to True.
        positive_conditioning: Optional additional conditioning for the positive prompt.
        negative_conditioning: Optional additional conditioning for the negative prompt.
        conditioning_mix (float, optional): Blend factor between -1 (context conditioning only) and 1 (prompt only).
        conditioning_mode (str, optional): Optional high-level mode override. When provided:
            - "context_only": use only context conditioning when available.
            - "concat": concatenate context + prompt conditioning.
            - "prompts_only": ignore context conditioning and rely on prompts.
            - "blend": blend according to conditioning_mix.

    Returns:
        torch.Tensor: The inpainted image tensor, blended with the original image according to the mask.
    """
    with torch.inference_mode():
        clip_encoder = nodes.CLIPTextEncode()
        positive = clip_encoder.encode(clip, positive_prompt)[0]
        negative = clip_encoder.encode(clip, negative_prompt)[0]

        has_context = positive_conditioning is not None or negative_conditioning is not None
        mode = conditioning_mode or ""

        if has_context and mode != "prompts_only":
            mix_value = float(conditioning_mix if conditioning_mix is not None else 0.0)
            if mix_value > 1.0:
                mix_value = 1.0
            if mix_value < -1.0:
                mix_value = -1.0

            if mode == "context_only":
                if positive_conditioning is not None:
                    positive = positive_conditioning
                if negative_conditioning is not None:
                    negative = negative_conditioning
            elif mode == "concat":
                concat_node = nodes.ConditioningConcat()
                if positive_conditioning is not None:
                    positive = concat_node.concat(positive_conditioning, positive)[0]
                if negative_conditioning is not None:
                    negative = concat_node.concat(negative_conditioning, negative)[0]
            else:
                # Default and "blend" mode: fall back to weighted average behaviour.
                prompt_weight = 0.5 * (mix_value + 1.0)
                context_weight = 1.0 - prompt_weight
                average_node = nodes.ConditioningAverage()

                if positive_conditioning is not None:
                    if context_weight >= 1.0 and prompt_weight <= 0.0:
                        positive = positive_conditioning
                    elif prompt_weight >= 1.0 and context_weight <= 0.0:
                        pass
                    elif context_weight <= 0.0:
                        pass
                    else:
                        positive = average_node.addWeighted(
                            positive,
                            positive_conditioning,
                            float(prompt_weight),
                        )[0]
                elif context_weight >= 1.0 and prompt_weight <= 0.0:
                    # No prompt weight but context conditioning missing; fallback to prompts.
                    pass

                if negative_conditioning is not None:
                    if context_weight >= 1.0 and prompt_weight <= 0.0:
                        negative = negative_conditioning
                    elif prompt_weight >= 1.0 and context_weight <= 0.0:
                        pass
                    elif context_weight <= 0.0:
                        pass
                    else:
                        negative = average_node.addWeighted(
                            negative,
                            negative_conditioning,
                            float(prompt_weight),
                        )[0]
                elif context_weight >= 1.0 and prompt_weight <= 0.0:
                    pass

        conditioning_node = nodes.InpaintModelConditioning()
        pos_cond, neg_cond, latent = conditioning_node.encode(
            positive,
            negative,
            image,
            vae,
            mask,
            True,
        )

        if disable_preview:
            latent_result = sample_without_preview(
                model=model,
                positive=pos_cond,
                negative=neg_cond,
                latent=latent,
                seed=seed,
                steps=steps,
                cfg=cfg,
                sampler_name=sampler_name,
                scheduler_name=scheduler_name,
                denoise_value=denoise,
            )
        else:
            sampler = nodes.KSampler()
            latent_result = sampler.sample(
                model,
                seed,
                steps,
                cfg,
                sampler_name,
                scheduler_name,
                pos_cond,
                neg_cond,
                latent,
                denoise,
            )[0]

        decoded = nodes.VAEDecode().decode(vae, latent_result)[0].to(
            device=image.device,
            dtype=torch.float32,
        )

    if decoded.shape != image.shape:
        decoded = decoded.reshape_as(image)

    mask_to_blend = mask
    if mask_to_blend.dim() == 4:
        mask_to_blend = mask_to_blend[..., 0]
    if mask_to_blend.dim() == 3:
        mask_to_blend = mask_to_blend.unsqueeze(-1)
    if mask_to_blend.shape[-1] != decoded.shape[-1]:
        mask_to_blend = mask_to_blend.expand(-1, -1, -1, decoded.shape[-1])

    return decoded * mask_to_blend + image * (1.0 - mask_to_blend)
# endregion

# region Helpers
def _prepare_inpaint_region(
    base_image: torch.Tensor,
    mask_tensor: torch.Tensor,
    *,
    vae,
    settings: dict,
):
    """
    Prepares the region of interest (ROI) and mask for inpainting by normalizing the ROI, processing mask edges, and optionally upsampling the region.

    Args:
        base_image (torch.Tensor): The input image tensor of shape (B, H, W, C).
        mask_tensor (torch.Tensor): The mask tensor of shape (B, H, W).
        vae: VAE model instance, used for determining alignment factors.
        settings (dict): Dictionary of settings controlling ROI, mask, and upsampling behavior.

    Returns:
        Tuple[
            torch.Tensor,      # work_image: Cropped and optionally upsampled image tensor.
            torch.Tensor,      # work_mask_soft: Processed mask tensor (dilated/feathered/upsampled).
            Tuple[int, int, int, int],  # paste_roi: Coordinates (y0, x0, y1, x1) of the ROI in the original image.
            dict               # meta: Metadata about the processing (dilate/feather px, upsample info, image shape).

    Settings Keys:
        roi_auto (bool): Whether to automatically detect and crop the ROI based on the mask.
        roi_padding (int): Padding added around the detected ROI.
        roi_align (int): Alignment multiple for ROI cropping.
        roi_align_auto (bool): Whether to automatically determine alignment from VAE.
        roi_min_size (int): Minimum size for the cropped ROI.
        dilate (int): Number of pixels to dilate the mask.
        feather (int): Number of pixels to feather (blur) the mask.
        upsample (int or str): Target size for upsampling the longest side of the ROI.
        upsample_target (int or str): Alternative key for upsampling target.

    Notes:
        - The function crops the image and mask to the smallest bounding box containing the mask, with optional padding and alignment.
        - Mask edges can be dilated and feathered for smoother transitions.
        - If upsampling is requested, the cropped region is resized so its longest side matches the target, maintaining alignment.
    """
    h = int(base_image.shape[1])
    w = int(base_image.shape[2])

    roi_auto = convert_to_boolean(settings.get("roi_auto", True))
    if roi_auto is None:
        roi_auto = True
    roi_padding = _normalize_int_setting(settings.get("roi_padding", None), 32, min_value=0)
    roi_align = _normalize_int_setting(settings.get("roi_align", None), 8, min_value=1)
    roi_align_auto = convert_to_boolean(settings.get("roi_align_auto", False)) or False
    roi_min_size = _normalize_int_setting(settings.get("roi_min_size", None), 64, min_value=1)

    raw_upsample = settings.get("upsample")
    if raw_upsample is None or raw_upsample == "":
        raw_upsample = settings.get("upsample_target")
    upsample_target = convert_to_int(raw_upsample) if raw_upsample is not None else None
    if upsample_target is not None:
        upsample_target = max(0, int(upsample_target))

    align_multiple = roi_align
    if roi_align_auto:
        candidates = [
            getattr(vae, "downscale_factor", None),
            getattr(vae, "downsample_factor", None),
            getattr(getattr(vae, "first_stage_model", None), "downscale_factor", None),
            getattr(getattr(vae, "first_stage_model", None), "downsample_factor", None),
        ]
        for candidate in candidates:
            if isinstance(candidate, int) and candidate > 0:
                align_multiple = candidate
                break

    work_image = base_image
    work_mask = mask_tensor
    paste_roi = (0, 0, h, w)
    base_roi_original = None
    mask_roi_original = None

    if roi_auto:
        mask_any = (mask_tensor > 0.5).any(dim=0)
        rows = mask_any.any(dim=1)
        cols = mask_any.any(dim=0)
        if bool(rows.any()) and bool(cols.any()):
            ys = torch.where(rows)[0]
            xs = torch.where(cols)[0]
            y0 = int(ys.min().item())
            y1 = int(ys.max().item()) + 1
            x0 = int(xs.min().item())
            x1 = int(xs.max().item()) + 1

            y0 = max(0, y0 - roi_padding)
            x0 = max(0, x0 - roi_padding)
            y1 = min(h, y1 + roi_padding)
            x1 = min(w, x1 + roi_padding)

            def align_down(value: int, alignment: int) -> int:
                return (value // alignment) * alignment

            def align_up(value: int, alignment: int) -> int:
                return ((value + alignment - 1) // alignment) * alignment

            y0 = align_down(y0, align_multiple)
            x0 = align_down(x0, align_multiple)
            y1 = align_up(y1, align_multiple)
            x1 = align_up(x1, align_multiple)

            y0 = max(0, min(y0, h))
            x0 = max(0, min(x0, w))
            y1 = max(0, min(y1, h))
            x1 = max(0, min(x1, w))

            height = y1 - y0
            width = x1 - x0
            if height < roi_min_size:
                delta = roi_min_size - height
                y0 = max(0, y0 - delta // 2)
                y1 = min(h, y0 + roi_min_size)
            if width < roi_min_size:
                delta = roi_min_size - width
                x0 = max(0, x0 - delta // 2)
                x1 = min(w, x0 + roi_min_size)

            paste_roi = (y0, x0, y1, x1)
            work_image = base_image[:, y0:y1, x0:x1, :]
            work_mask = mask_tensor[:, y0:y1, x0:x1]

    # Track whether the user brush actually touches an image edge so we can avoid
    # introducing a soft falloff along the border (which can look like a white halo).
    mask_touches_top = paste_roi[0] == 0 and bool((work_mask[:, 0:1, :] > 0.5).any())
    mask_touches_bottom = paste_roi[2] == h and bool((work_mask[:, -1:, :] > 0.5).any())
    mask_touches_left = paste_roi[1] == 0 and bool((work_mask[:, :, 0:1] > 0.5).any())
    mask_touches_right = paste_roi[3] == w and bool((work_mask[:, :, -1:] > 0.5).any())

    # Preserve explicit 0 values from settings. Only fall back to defaults when
    # the setting is missing or convert_to_int returns None.
    raw_dilate = settings.get("dilate", None)
    dilate_val = convert_to_int(raw_dilate) if raw_dilate is not None else None
    if dilate_val is None:
        dilate_px = 4
    else:
        dilate_px = int(dilate_val)
    dilate_px = max(0, dilate_px)

    raw_feather = settings.get("feather", None)
    feather_val = convert_to_int(raw_feather) if raw_feather is not None else None
    if feather_val is None:
        feather_px = 2
    else:
        feather_px = int(feather_val)
    feather_px = max(0, feather_px)

    work_mask_soft = work_mask
    if dilate_px > 0:
        kernel = dilate_px * 2 + 1
        wm = work_mask_soft.unsqueeze(1)
        wm = F.max_pool2d(wm, kernel_size=kernel, stride=1, padding=dilate_px)
        work_mask_soft = wm.squeeze(1)
    if feather_px > 0:
        kernel = feather_px * 2 + 1
        wm = work_mask_soft.unsqueeze(1)
        wm = F.avg_pool2d(
            wm,
            kernel_size=kernel,
            stride=1,
            padding=feather_px,
            count_include_pad=False,
        )
        work_mask_soft = wm.squeeze(1)
    work_mask_soft = work_mask_soft.clamp(0.0, 1.0)

    # Track whether the softened mask touches the cropped ROI edges (not just image edges).
    roi_edge_touch = {
        "top": bool((work_mask_soft[:, 0:1, :] > 0).any()),
        "bottom": bool((work_mask_soft[:, -1:, :] > 0).any()),
        "left": bool((work_mask_soft[:, :, 0:1] > 0).any()),
        "right": bool((work_mask_soft[:, :, -1:] > 0).any()),
    }

    # If the mask touches an image border, keep the corresponding band fully opaque
    # to avoid partially transparent edges when the brush is dragged out of bounds.
    edge_band = max(dilate_px + feather_px, 1)
    if mask_touches_top:
        band = min(edge_band, work_mask_soft.shape[1])
        top_cols = (work_mask[:, 0:1, :] > 0.5).expand(-1, band, -1)
        work_mask_soft[:, :band, :] = torch.where(
            top_cols,
            torch.ones_like(work_mask_soft[:, :band, :]),
            work_mask_soft[:, :band, :],
        )
    if mask_touches_bottom:
        band = min(edge_band, work_mask_soft.shape[1])
        bottom_cols = (work_mask[:, -1:, :] > 0.5).expand(-1, band, -1)
        work_mask_soft[:, -band:, :] = torch.where(
            bottom_cols,
            torch.ones_like(work_mask_soft[:, -band:, :]),
            work_mask_soft[:, -band:, :],
        )
    if mask_touches_left:
        band = min(edge_band, work_mask_soft.shape[2])
        left_rows = (work_mask[:, :, 0:1] > 0.5).expand(-1, -1, band)
        work_mask_soft[:, :, :band] = torch.where(
            left_rows,
            torch.ones_like(work_mask_soft[:, :, :band]),
            work_mask_soft[:, :, :band],
        )
    if mask_touches_right:
        band = min(edge_band, work_mask_soft.shape[2])
        right_rows = (work_mask[:, :, -1:] > 0.5).expand(-1, -1, band)
        work_mask_soft[:, :, -band:] = torch.where(
            right_rows,
            torch.ones_like(work_mask_soft[:, :, -band:]),
            work_mask_soft[:, :, -band:],
        )
    work_mask_soft = work_mask_soft.clamp(0.0, 1.0)

    upsample_applied = False
    upsample_info: dict | None = None
    if upsample_target and upsample_target > 0:
        orig_h, orig_w = int(work_image.shape[1]), int(work_image.shape[2])
        plan = _select_upsample_plan(orig_h, orig_w, upsample_target, align_multiple)
        if plan:
            base_roi_original = work_image.clone()
            mask_roi_original = work_mask_soft.clone()

            new_h = int(plan["height"])
            new_w = int(plan["width"])

            wi = work_image.permute(0, 3, 1, 2)
            wi = F.interpolate(wi, size=(new_h, new_w), mode="bicubic", align_corners=False)
            work_image = wi.permute(0, 2, 3, 1).contiguous()

            wm = work_mask_soft.unsqueeze(1)
            wm = F.interpolate(wm, size=(new_h, new_w), mode="nearest")
            work_mask_soft = wm.squeeze(1).contiguous()

            upsample_applied = True
            upsample_info = {
                "orig_height": orig_h,
                "orig_width": orig_w,
                "new_height": new_h,
                "new_width": new_w,
                "source": plan.get("source"),
                "ratio": plan.get("ratio"),
                "preset": plan.get("preset"),
                "area": int(plan.get("area", new_h * new_w)),
            }
            preset = plan.get("preset")
            ratio_val = plan.get("ratio")
            preset_str = f"{preset[0]}x{preset[1]}" if preset else f"{new_w}x{new_h}"
            ratio_str = f"{ratio_val:.2f}:1" if ratio_val else "n/a"
            print(
                f"[LF Inpaint] Upsample preset selected: {preset_str} "
                f"(target={upsample_target}, source={plan.get('source')}, ratio={ratio_str})"
            )

    meta = {
        "dilate_px": dilate_px,
        "feather_px": feather_px,
        "edge_touch": {
            "top": mask_touches_top,
            "bottom": mask_touches_bottom,
            "left": mask_touches_left,
            "right": mask_touches_right,
        },
        "roi_edge_touch": roi_edge_touch,
        "upsample_applied": upsample_applied,
        "upsample_info": upsample_info,
        "image_shape": (h, w),
        "base_roi": base_roi_original,
        "mask_roi": mask_roi_original,
        "mask_for_paste": work_mask_soft.detach(),
    }

    return work_image, work_mask_soft, paste_roi, meta

def _finalize_inpaint_output(
    processed_region: torch.Tensor,
    base_image: torch.Tensor,
    paste_roi: tuple[int, int, int, int],
    *,
    meta: dict,
):
    """
    Finalize the output of an inpainting operation by optionally downscaling, pasting the processed region into the base image, clamping values, and emitting metadata.

    Args:
        processed_region (torch.Tensor): The inpainted region tensor of shape (batch, height, width, channels).
        base_image (torch.Tensor): The original image tensor of shape (batch, height, width, channels).
        paste_roi (tuple[int, int, int, int]): The region of interest (y0, x0, y1, x1) where the processed region should be pasted.
        meta (dict): Metadata containing optional keys:
            - "upsample_applied" (bool): Whether upsampling was applied.
            - "upsample_info" (tuple): Information about upsampling (orig_h, orig_w, new_h, new_w).
            - "dilate_px" (int): Number of pixels for dilation.
            - "feather_px" (int): Number of pixels for feathering.
            - "image_shape" (tuple): Shape of the image (height, width).

    Returns:
        Tuple[torch.Tensor, Dict[str, str]]:
            - The finalized image tensor on CPU, clamped to [0, 1].
            - A dictionary with metadata about the operation (ROI, upsampling, edge processing).
    """
    base_roi = meta.pop("base_roi", None)
    mask_roi = meta.pop("mask_roi", None)

    upsample_applied = bool(meta.get("upsample_applied"))
    upsample_info = meta.get("upsample_info") or {}
    dilate_px = int(meta.get("dilate_px", 4))
    feather_px = int(meta.get("feather_px", 2))
    apply_unsharp_mask = meta.get("apply_unsharp_mask")
    if apply_unsharp_mask is None:
        apply_unsharp_mask = True
    else:
        apply_unsharp_mask = bool(apply_unsharp_mask)

    # Debug helpers: save intermediate previews to temp so user can compare
    debug_files: dict = {}

    orig_h = 0
    orig_w = 0
    if upsample_applied:
        orig_h = int(upsample_info.get("orig_height", 0))
        orig_w = int(upsample_info.get("orig_width", 0))
        new_h = int(upsample_info.get("new_height", 0))
        new_w = int(upsample_info.get("new_width", 0))
        if orig_h <= 0 or orig_w <= 0 or new_h <= 0 or new_w <= 0:
            orig_h = orig_w = 0
        if orig_h and orig_w:
            # Save region before downscale (this is what the preview image was taken from)
            url = _save_tensor_preview(processed_region, "inpaint_region_before_downscale", "temp")
            if url:
                debug_files["region_before_downscale"] = url
            pr = processed_region.permute(0, 3, 1, 2)
            # Use bicubic with antialias to preserve high-frequency detail when downscaling.
            pr = F.interpolate(pr, size=(orig_h, orig_w), mode="bicubic", align_corners=False, antialias=True)
            processed_region = pr.permute(0, 2, 3, 1).contiguous()
            processed_region = processed_region.clamp(0.0, 1.0)

            # Optionally apply a conservative unsharp mask to restore perceived sharpness
            if apply_unsharp_mask:
                try:
                    us_amount = 0.3
                    us_radius = 3
                    us_sigma = 1.0
                    us_threshold = 0.0
                    sharpened = unsharp_mask_effect(processed_region, us_amount, us_radius, us_sigma, us_threshold)
                    # Normalize returned tensor to float [0,1] and move to the processed_region device
                    if not torch.is_floating_point(sharpened):
                        # assume uint8 [0,255]
                        sharpened = sharpened.to(dtype=torch.float32) / 255.0
                    else:
                        sharpened = sharpened.to(dtype=torch.float32)
                    sharpened = sharpened.clamp(0.0, 1.0).to(device=processed_region.device, dtype=processed_region.dtype)
                    processed_region = sharpened
                except Exception:
                    # sharpening is best-effort and non-fatal
                    pass

            # Save region after downscale
            url = _save_tensor_preview(processed_region, "inpaint_region_after_downscale", "temp")
            if url:
                debug_files["region_after_downscale"] = url

    if base_roi is not None and mask_roi is not None:
        mask_roi = mask_roi.to(dtype=processed_region.dtype, device=processed_region.device)
        if mask_roi.dim() == 3:
            mask_roi = mask_roi.unsqueeze(-1)
        processed_region = processed_region * mask_roi + base_roi.to(
            dtype=processed_region.dtype,
            device=processed_region.device,
        ) * (1.0 - mask_roi)

    h, w = meta.get("image_shape", (int(base_image.shape[1]), int(base_image.shape[2])))
    if paste_roi != (0, 0, h, w):
        y0, x0, y1, x1 = paste_roi
        result_full = base_image.clone()
        result_full[:, y0:y1, x0:x1, :] = processed_region
        processed = result_full
        # Save the stitched-full result prior to clamp/move to CPU for debugging
        url = _save_tensor_preview(result_full, "inpaint_final_stitched", "temp")
        if url:
            debug_files["final_stitched"] = url
    else:
        processed = processed_region

    processed = processed.detach().clamp(0.0, 1.0).to(torch.float32).cpu().contiguous()

    # Optionally re-composite with the processed mask so any residual changes outside the mask are removed.
    mask_for_paste = meta.pop("mask_for_paste", None)
    if mask_for_paste is not None:
        mask_for_paste = mask_for_paste.to(dtype=processed.dtype, device=processed.device)
        if mask_for_paste.dim() == 3:
            mask_for_paste = mask_for_paste.unsqueeze(-1)
        # If the mask was upsampled earlier, downscale to match the processed_region before stitching.
        if mask_for_paste.shape[1] != processed_region.shape[1] or mask_for_paste.shape[2] != processed_region.shape[2]:
            mf = mask_for_paste.permute(0, 3, 1, 2)
            mf = F.interpolate(mf, size=(processed_region.shape[1], processed_region.shape[2]), mode="nearest")
            mask_for_paste = mf.permute(0, 2, 3, 1)

        mask_for_paste = mask_for_paste.clamp(0.0, 1.0)
        mask_for_paste_bin = (mask_for_paste > 0.5).to(dtype=processed.dtype, device=processed.device)

        if paste_roi != (0, 0, h, w):
            y0, x0, y1, x1 = paste_roi
            full_mask = torch.zeros_like(processed)
            full_mask[:, y0:y1, x0:x1, :] = mask_for_paste_bin
            processed = processed * full_mask + base_image.cpu().to(dtype=processed.dtype) * (1.0 - full_mask)
        else:
            processed = processed * mask_for_paste_bin + base_image.cpu().to(dtype=processed.dtype) * (1.0 - mask_for_paste_bin)

    # Seam detection + conditional “darker/lighter” edge merge.
    # This only activates near edges where the mask/ROI actually touched,
    # and only when a visible step between edge and interior is detected.
    edge_touch = meta.get("edge_touch", {}) or {}
    roi_edge_touch = meta.get("roi_edge_touch", {}) or {}
    if any(edge_touch.values()) or any(roi_edge_touch.values()):
        base_full = base_image.cpu().to(dtype=processed.dtype)
        band = 1
        thresh = 0.03

        def _analyze_edge(edge_slice, inner_slice, base_slice, label: str):
            # Convert to approximate luminance
            edge_l = edge_slice.mean(dim=-1)
            inner_l = inner_slice.mean(dim=-1)
            base_l = base_slice.mean(dim=-1)

            edge_mean = float(edge_l.mean().item())
            inner_mean = float(inner_l.mean().item())
            base_mean = float(base_l.mean().item())

            if max(abs(edge_mean - inner_mean), abs(edge_mean - base_mean)) < thresh:
                return None  # no visible seam

            # Decide whether the seam band is brighter or darker than both neighbors.
            if edge_mean > inner_mean and edge_mean > base_mean:
                return "brighter"
            if edge_mean < inner_mean and edge_mean < base_mean:
                return "darker"
            return None

        # Top edge
        if (edge_touch.get("top") or roi_edge_touch.get("top")) and processed.shape[1] > band + 1:
            edge = processed[:, :band, :, :]
            inner = processed[:, band : band + 1, :, :]
            base_edge = base_full[:, :band, :, :]
            mode = _analyze_edge(edge, inner, base_edge, "top")
            if mode == "brighter":
                processed[:, :band, :, :] = torch.minimum(inner, base_edge)
            elif mode == "darker":
                processed[:, :band, :, :] = torch.maximum(inner, base_edge)

        # Bottom edge
        if (edge_touch.get("bottom") or roi_edge_touch.get("bottom")) and processed.shape[1] > band + 1:
            edge = processed[:, -band:, :, :]
            inner = processed[:, -band - 1 : -band, :, :]
            base_edge = base_full[:, -band:, :, :]
            mode = _analyze_edge(edge, inner, base_edge, "bottom")
            if mode == "brighter":
                processed[:, -band:, :, :] = torch.minimum(inner, base_edge)
            elif mode == "darker":
                processed[:, -band:, :, :] = torch.maximum(inner, base_edge)

        # Left edge
        if (edge_touch.get("left") or roi_edge_touch.get("left")) and processed.shape[2] > band + 1:
            edge = processed[:, :, :band, :]
            inner = processed[:, :, band : band + 1, :]
            base_edge = base_full[:, :, :band, :]
            mode = _analyze_edge(edge, inner, base_edge, "left")
            if mode == "brighter":
                processed[:, :, :band, :] = torch.minimum(inner, base_edge)
            elif mode == "darker":
                processed[:, :, :band, :] = torch.maximum(inner, base_edge)

        # Right edge
        if (edge_touch.get("right") or roi_edge_touch.get("right")) and processed.shape[2] > band + 1:
            edge = processed[:, :, -band:, :]
            inner = processed[:, :, -band - 1 : -band, :]
            base_edge = base_full[:, :, -band:, :]
            mode = _analyze_edge(edge, inner, base_edge, "right")
            if mode == "brighter":
                processed[:, :, -band:, :] = torch.minimum(inner, base_edge)
            elif mode == "darker":
                processed[:, :, -band:, :] = torch.maximum(inner, base_edge)

    info: Dict[str, str] = {}
    # merge any debug file URLs collected earlier
    if debug_files:
        info.update(debug_files)
    if paste_roi != (0, 0, h, w):
        y0, x0, y1, x1 = paste_roi
        info["roi"] = f"y0={y0},x0={x0},y1={y1},x1={x1}"
    if upsample_applied and orig_h and orig_w:
        nh = int(upsample_info.get("new_height", 0))
        nw = int(upsample_info.get("new_width", 0))
        info["upsample"] = f"{orig_w}x{orig_h} -> {nw}x{nh}"
        preset = upsample_info.get("preset")
        if preset:
            preset_long, preset_short = preset
            info["upsample_preset"] = f"{preset_long}x{preset_short}"
        ratio = upsample_info.get("ratio")
        if ratio:
            info["upsample_ratio"] = f"{ratio:.2f}:1"
        source = upsample_info.get("source")
        if source:
            info["upsample_source"] = str(source)
        area = upsample_info.get("area")
        if area:
            info["upsample_pixels"] = str(area)
    if dilate_px or feather_px:
        info["edges"] = f"dilate={dilate_px},feather={feather_px}"

    return processed, info

def _normalize_steps(raw_value):
    """
    Normalizes the input value to a valid number of steps for inpainting.

    Parameters:
        raw_value (Any): The raw input value representing the number of steps. Can be None or any type convertible to int.

    Returns:
        int: The normalized number of steps, rounded to the nearest integer, with a minimum value of 1. Defaults to 20 if input is None or invalid.
    """
    value = convert_to_int(raw_value) if raw_value is not None else None
    if value is None:
        value = 20

    return max(1, int(round(value)))

def _normalize_denoise(raw_value):
    """
    Normalizes the input value to a valid denoise strength for inpainting.

    Parameters:
        raw_value (Any): The raw input value representing the denoise strength. Can be None or any type convertible to float.

    Returns:
        float: The normalized denoise strength, clamped to [0, 1]. Defaults to 1.0 if input is None or invalid.
    """
    value = convert_to_float(raw_value) if raw_value is not None else None
    if value is None:
        value = 1.0

    return max(0.0, min(1.0, float(value)))

def _normalize_cfg(raw_value):
    """
    Normalizes the input value to a valid classifier-free guidance scale for inpainting.

    Parameters:
        raw_value (Any): The raw input value representing the CFG scale. Can be None or any type convertible to float.

    Returns:
        float: The normalized CFG scale, clamped to [0, 20]. Defaults to 7.0 if input is None or invalid.
    """
    value = convert_to_float(raw_value) if raw_value is not None else None
    if value is None:
        value = 7.0

    return float(value)

def _normalize_conditioning_mix(raw_value):
    """
    Normalize the conditioning mix slider to [-1.0, 1.0].

    -1.0 => input conditioning only, 0.0 => balanced, 1.0 => prompt only.
    """
    value = convert_to_float(raw_value) if raw_value is not None else None
    if value is None:
        value = 0.0
    value = float(value)
    if value > 1.0:
        return 1.0
    if value < -1.0:
        return -1.0
    return value

def _normalize_seed(raw_value):
    """
    Normalizes the input value to a valid random seed for inpainting.

    Parameters:
        raw_value (Any): The raw input value representing the random seed. Can be None or any type convertible to int.

    Returns:
        int: The normalized random seed, with a default value of -1 if input is None or invalid.
    """
    value = convert_to_int(raw_value) if raw_value is not None else None
    if value is None:
        value = -1

    return int(value)


def _normalize_int_setting(raw_value, default, min_value=None, max_value=None):
    """
    Normalize an integer-like setting value while preserving explicit zeros.

    - raw_value: the raw value (may be None)
    - default: the fallback integer when raw_value is None or conversion fails
    - min_value, max_value: optional clamps applied after conversion

    Returns an int.
    """
    val = convert_to_int(raw_value) if raw_value is not None else None
    if val is None:
        val = default
    val = int(val)
    if min_value is not None:
        val = max(min_value, val)
    if max_value is not None:
        val = min(max_value, val)
    return val
# endregion

# region Apply Inpaint Filter
def apply_inpaint_filter(image: torch.Tensor, settings: dict) -> FilterResult:
    """
    Applies an inpainting filter to the given image using the provided settings and editing context.

    Args:
        image (torch.Tensor): The input image tensor to be inpainted. Expected shape: (batch, channels, height, width).
        settings (dict): Dictionary containing filter settings and context information. Must include:
            - "context_id" or "dataset_path": Identifier for the editing session.
            - "model", "clip", "vae": Model components required for inpainting.
            - "b64_canvas", "mask_canvas", or "mask": Base64-encoded mask for inpainting.
            - "steps" (optional): Number of inpainting steps (default: 20).
            - "denoise" or "denoise_percentage" (optional): Denoising strength (default: 100.0).
            - "cfg" (optional): Classifier-free guidance scale (default: 7.0).
            - "sampler" (optional): Sampler name (default: "dpmpp_2m").
            - "scheduler" (optional): Scheduler name (default: "karras").
            - "seed" (optional): Random seed for generation.
            - "positive_prompt" (optional): Positive prompt for inpainting.
            - "negative_prompt" (optional): Negative prompt for inpainting.
            - ROI optimization (optional):
              - "roi_auto": Enable automatic ROI cropping around the mask (default: true)
              - "roi_padding": Pixels of padding around the mask bbox (default: 32)
              - "roi_align": Align ROI size/position to multiple (latent-friendly, default: 8)
              - "roi_align_auto": If true, try to infer alignment from VAE/model downscale factor (fallback 8)
              - "roi_min_size": Minimum ROI width/height (default: 64)
            - Mask edges (optional):
              - "dilate": Integer pixels to dilate mask before feathering (default: 4)
              - "feather": Integer feather radius in pixels (default: 2)
            - Upsample detail (optional):
              - "upsample" or "upsample_target": Target size for the longer side of the ROI; if > current, upsample ROI before inpaint and downscale after (disabled by default)

    Returns:
        FilterResult: A tuple containing:
            - processed (torch.Tensor): The inpainted image tensor.
            - info (dict): Dictionary with additional information, including the mask URL and ROI/upsample info.

    Raises:
        ValueError: If required context, model components, or mask are missing, or if the mask is empty.
    """
    context_id = settings.get("context_id") or settings.get("dataset_path")
    if not context_id:
        raise ValueError("Inpaint filter requires a context_id referencing the editing session.")

    context = get_editing_context(context_id)
    if not context:
        raise ValueError(f"No active editing session for '{context_id}'.")

    model = context.get("model")
    clip = context.get("clip")
    vae = context.get("vae") or getattr(model, "vae", None)
    if model is None or clip is None or vae is None:
        raise ValueError(
            "Inpaint filter requires model, clip, and vae inputs. Connect them to LF_ImagesEditingBreakpoint."
        )

    sampler_default = context.get("sampler")
    scheduler_default = context.get("scheduler")
    cfg_default = context.get("cfg")
    seed_default = -1
    context_positive_prompt = str(context.get("positive_prompt") or "")
    context_negative_prompt = str(context.get("negative_prompt") or "")
    context_positive_conditioning = context.get("positive_conditioning")
    context_negative_conditioning = context.get("negative_conditioning")

    wd14_model = context.get("wd14_model")
    wd14_processor = context.get("wd14_processor")

    mask_b64 = settings.get("b64_canvas") or settings.get("mask_canvas") or settings.get("mask")
    if not mask_b64:
        raise ValueError("Missing brush mask for inpaint filter.")

    canvas = base64_to_tensor(mask_b64, True)
    if canvas.ndim != 4:
        raise ValueError("Unexpected brush payload for inpaint filter.")

    if canvas.shape[1] != image.shape[1] or canvas.shape[2] != image.shape[2]:
        canvas = F.interpolate(
            canvas.permute(0, 3, 1, 2),
            size=(image.shape[1], image.shape[2]),
            mode="nearest",
        ).permute(0, 2, 3, 1)

    alpha = canvas[..., 3] if canvas.shape[-1] >= 4 else canvas.mean(dim=-1)
    mask = (alpha > 0.01).float()
    if float(mask.max().item()) <= 0.0:
        raise ValueError("Inpaint mask strokes are empty.")
    mask = mask.clamp(0.0, 1.0)

    device = getattr(getattr(vae, "first_stage_model", None), "device", None)
    if isinstance(device, str):
        device = torch.device(device)
    if device is None:
        raw_device = getattr(vae, "device", None)
        if isinstance(raw_device, str):
            device = torch.device(raw_device)
        else:
            device = raw_device
    if device is None:
        device = image.device

    base_image = image.to(device=device, dtype=torch.float32)
    mask_tensor = mask.to(device=device, dtype=torch.float32)
    if mask_tensor.ndim == 4:
        mask_tensor = mask_tensor[..., 0]

    image_height = base_image.shape[1]
    image_width = base_image.shape[2]

    if mask_tensor.shape[-2] != image_height or mask_tensor.shape[-1] != image_width:
        mask_tensor = F.interpolate(
            mask_tensor.unsqueeze(1),
            size=(image_height, image_width),
            mode="nearest",
        ).squeeze(1)

    mask_tensor = mask_tensor.clamp(0.0, 1.0)
    mask_tensor = (mask_tensor > 0.5).float()

    mask_preview_tensor = mask_tensor.detach().cpu().unsqueeze(-1).repeat(1, 1, 1, 3)
    mask_image = tensor_to_pil(mask_preview_tensor)

    mask_save_type = str(settings.get("resource_type") or settings.get("output_type") or "temp")
    mask_base_output = get_comfy_dir(mask_save_type)

    mask_subfolder_raw = settings.get("subfolder")
    if isinstance(mask_subfolder_raw, str) and mask_subfolder_raw.strip():
        mask_normalized_subfolder = os.path.normpath(mask_subfolder_raw.strip()).strip("\\/")
        if mask_normalized_subfolder.startswith(".."):
            raise ValueError("Invalid subfolder path.")
    else:
        mask_normalized_subfolder = ""

    mask_prefix = os.path.join(mask_normalized_subfolder, "inpaint_mask") if mask_normalized_subfolder else "inpaint_mask"
    mask_output_file, mask_subfolder, mask_filename = resolve_filepath(
        filename_prefix=mask_prefix,
        base_output_path=mask_base_output,
        image=mask_preview_tensor,
    )
    mask_image.save(mask_output_file, format="PNG")
    mask_url = get_resource_url((mask_subfolder or "").replace("\\", "/"), mask_filename, mask_save_type)

    steps = _normalize_steps(settings.get("steps"))
    denoise_value = convert_to_float(settings.get("denoise", settings.get("denoise_percentage", 100.0)))
    if denoise_value > 1.0:
        denoise_value = denoise_value / 100.0
    denoise_value = max(0.0, min(1.0, denoise_value))

    cfg_candidate = convert_to_float(settings.get("cfg"))
    if cfg_candidate is None:
        cfg_candidate = convert_to_float(cfg_default)
    if cfg_candidate is None:
        cfg_candidate = 7.0
    cfg = cfg_candidate

    sampler_candidate = settings.get("sampler") or sampler_default or "dpmpp_2m"
    sampler_name = str(sampler_candidate)
    if sampler_name not in SAMPLERS:
        sampler_name = "dpmpp_2m"

    scheduler_candidate = settings.get("scheduler") or scheduler_default or "karras"
    scheduler_name = str(scheduler_candidate)
    if scheduler_name not in SCHEDULERS:
        scheduler_name = "normal"

    seed_candidate = _normalize_seed(settings.get("seed"))
    if seed_candidate is None or seed_candidate < 0:
        seed_candidate = _normalize_seed(seed_default)
    if seed_candidate is None or seed_candidate < 0:
        seed_candidate = random.randint(0, 2**32 - 1)
    seed = int(seed_candidate) & 0xFFFFFFFFFFFFFFFF

    positive_prompt = str(settings.get("positive_prompt") or context_positive_prompt)
    negative_prompt = str(settings.get("negative_prompt") or context_negative_prompt)

    conditioning_mix = _normalize_conditioning_mix(settings.get("conditioning_mix"))
    apply_unsharp_mask = convert_to_boolean(settings.get("apply_unsharp_mask", True))
    if apply_unsharp_mask is None:
        apply_unsharp_mask = True

    # Reuse the tensor-based inpaint path so outpainting / safe-border logic
    # stays consistent between the editor filter and the node.
    tensor_settings = dict(settings)
    tensor_settings.update(
        {
            "steps": steps,
            "denoise": denoise_value,
            "cfg": cfg,
            "sampler": sampler_name,
            "scheduler": scheduler_name,
            "seed": seed,
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "conditioning_mix": conditioning_mix,
            "positive_conditioning": context_positive_conditioning,
            "negative_conditioning": context_negative_conditioning,
            "apply_unsharp_mask": apply_unsharp_mask,
            "wd14_model": wd14_model,
            "wd14_processor": wd14_processor,
        }
    )

    processed, info = apply_inpaint_filter_tensor(
        image=base_image,
        mask=mask_tensor,
        model=model,
        clip=clip,
        vae=vae,
        settings=tensor_settings,
    )

    # Attach mask URL for UI/debug parity with the original filter path.
    info_with_mask = {"mask": mask_url}
    info_with_mask.update(info)
    if not apply_unsharp_mask:
        info_with_mask["unsharp_mask"] = "disabled"

    print(
        "[LF Inpaint] sampling "
        f"steps={steps}, denoise={denoise_value:.3f}, cfg={cfg:.2f}, seed={seed}, "
        f"conditioning_mix={conditioning_mix:.2f}"
    )

    return processed, info_with_mask
# endregion

# region Apply Inpaint Filter (Tensor Mask)
def apply_inpaint_filter_tensor(
    image: torch.Tensor,
    mask: torch.Tensor,
    *,
    model,
    clip,
    vae,
    settings: dict,
) -> FilterResult:
    """
    Applies an inpainting filter to the given image tensor using the provided mask and model components.

    Args:
        image (torch.Tensor): The input image tensor to be inpainted.
        mask (torch.Tensor): The mask tensor indicating regions to inpaint.
        model: The inpainting model to use for generating the inpainted region.
        clip: The CLIP model used for conditioning.
        vae: The VAE model used for encoding/decoding image data.
        settings (dict): A dictionary of settings and parameters for inpainting, such as prompts, sampler, scheduler, steps, denoise, cfg, seed, and conditioning options.

    Returns:
        FilterResult: A tuple containing the processed image tensor and additional information about the inpainting operation.

    Raises:
        ValueError: If the mask tensor has an unsupported shape.
    """
    device = getattr(getattr(vae, "first_stage_model", None), "device", None) or image.device

    positive_prompt = str(settings.get("positive_prompt") or "")
    negative_prompt = str(settings.get("negative_prompt") or "")

    base_image = image.to(device=device, dtype=torch.float32)
    m = mask
    if isinstance(m, (list, tuple)):
        m = m[0]
    if m.dim() == 4:
        if m.shape[-1] > 1:
            m = m.mean(dim=-1)
        else:
            m = m[..., 0]
    elif m.dim() == 3:
        pass
    elif m.dim() == 2:
        m = m.unsqueeze(0)
    else:
        raise ValueError("Unsupported MASK tensor shape.")

    # Original image size before any padding (used for final crop)
    orig_h, orig_w = int(base_image.shape[1]), int(base_image.shape[2])

    h, w = orig_h, orig_w
    m = m.to(device=base_image.device, dtype=torch.float32)
    if m.shape[-2] != h or m.shape[-1] != w:
        m = F.interpolate(m.unsqueeze(1), size=(h, w), mode="nearest").squeeze(1)
    m = m.clamp(0.0, 1.0)
    # Use a binary version for ROI/conditioning; a processed soft mask is captured later for final compositing.
    m = (m > 0.5).float()

    # If the brush comes close to image edges, pad the image/mask outward so any
    # model boundary artifacts fall outside the original frame (cheap outpainting).
    # Use a small band instead of a single pixel so near-edge strokes also trigger.
    edge_band = 4
    touches_top = bool((m[:, :edge_band, :] > 0.5).any())
    touches_bottom = bool((m[:, -edge_band:, :] > 0.5).any())
    touches_left = bool((m[:, :, :edge_band] > 0.5).any())
    touches_right = bool((m[:, :, -edge_band:] > 0.5).any())

    pad_margin = 32  # outpainting margin in pixels
    pad_top = pad_margin if touches_top else 0
    pad_bottom = pad_margin if touches_bottom else 0
    pad_left = pad_margin if touches_left else 0
    pad_right = pad_margin if touches_right else 0

    if pad_top or pad_bottom or pad_left or pad_right:
        # Pad image by replicating edge pixels outward.
        # base_image: (B, H, W, C) -> pad H and W, keep channels unchanged.
        base_image = F.pad(
            base_image,
            (0, 0, pad_left, pad_right, pad_top, pad_bottom),
            mode="replicate",
        )
        # Pad mask with ones so the inpaint region extends into the outpaint margin.
        # This lets the model hallucinate beyond the original frame; the final
        # crop and safe-border logic will decide what remains visible.
        m = F.pad(
            m.unsqueeze(1),
            (pad_left, pad_right, pad_top, pad_bottom),
            mode="constant",
            value=1.0,
        ).squeeze(1)

    # Updated working size after optional padding.
    h, w = int(base_image.shape[1]), int(base_image.shape[2])

    conditioning_mix = _normalize_conditioning_mix(settings.get("conditioning_mix"))

    positive_conditioning = settings.get("positive_conditioning")
    negative_conditioning = settings.get("negative_conditioning")
    has_context = positive_conditioning is not None or negative_conditioning is not None

    eps = 1e-3
    if not has_context:
        conditioning_mode = "prompts_only"
    else:
        if conditioning_mix <= -1.0 + eps:
            conditioning_mode = "context_only"
        elif conditioning_mix >= 1.0 - eps:
            conditioning_mode = "prompts_only"
        elif abs(conditioning_mix) < eps:
            conditioning_mode = "concat"
        else:
            conditioning_mode = "blend"
    apply_unsharp_mask = convert_to_boolean(settings.get("apply_unsharp_mask", True))
    if apply_unsharp_mask is None:
        apply_unsharp_mask = True

    work_image, work_mask_soft, paste_roi, region_meta = _prepare_inpaint_region(
        base_image=base_image,
        mask_tensor=m,
        vae=vae,
        settings=settings,
    )
    region_meta["apply_unsharp_mask"] = apply_unsharp_mask

    wd14_tagging = convert_to_boolean(settings.get("wd14_tagging"))
    if wd14_tagging:
        wd14_model = settings.get("wd14_model")
        wd14_processor = settings.get("wd14_processor")

        _save_tensor_preview(work_image, "wd14", "temp")

        positive_prompt = apply_wd14_tagging_to_prompt(
            positive_prompt,
            work_image,
            wd14_model,
            wd14_processor,
            threshold=0.70,
            top_k=10,
        )

    processed_region = perform_inpaint(
        model=model,
        clip=clip,
        vae=vae,
        image=work_image,
        mask=work_mask_soft,
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        sampler_name=str(settings.get("sampler") or "dpmpp_2m"),
        scheduler_name=str(settings.get("scheduler") or "karras"),
        steps=_normalize_steps(settings.get("steps")),
        denoise=_normalize_denoise(settings.get("denoise")),
        cfg=_normalize_cfg(settings.get("cfg")),
        seed=_normalize_seed(settings.get("seed")),
        disable_preview=True,
        positive_conditioning=positive_conditioning,
        negative_conditioning=negative_conditioning,
        conditioning_mix=conditioning_mix,
        conditioning_mode=conditioning_mode,
    )

    _ = _save_tensor_preview(processed_region, "inpaint_region", str(settings.get("resource_type") or settings.get("output_type") or "temp"))

    processed, info = _finalize_inpaint_output(
        processed_region=processed_region,
        base_image=base_image,
        paste_roi=paste_roi,
        meta=region_meta,
    )

    # If we padded for outpainting, crop back to the original frame.
    if pad_top or pad_bottom or pad_left or pad_right:
        crop_y0 = pad_top
        crop_y1 = pad_top + orig_h
        crop_x0 = pad_left
        crop_x1 = pad_left + orig_w
        processed = processed[:, crop_y0:crop_y1, crop_x0:crop_x1, :]
    else:
        processed = processed[:, :orig_h, :orig_w, :]
    if not apply_unsharp_mask:
        info["unsharp_mask"] = "disabled"

    return processed, info
# endregion
