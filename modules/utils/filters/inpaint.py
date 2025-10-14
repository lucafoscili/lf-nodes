from typing import Dict, Tuple

import os
import random
import torch
import torch.nn.functional as F

import comfy.sample
import nodes

from ..constants import SAMPLERS, SCHEDULERS
from ..helpers.api import get_resource_url
from ..helpers.comfy import get_comfy_dir, resolve_filepath
from ..helpers.conversion import base64_to_tensor, convert_to_boolean, convert_to_float, convert_to_int, tensor_to_pil
from ..helpers.editing import get_editing_context
from .unsharp_mask import unsharp_mask_effect

# region Debug Preview Save
# Toggle debug preview saves. Hardwired to False for normal runs; set True when debugging.
DEBUG_PREVIEW_SAVES = True

def _save_tensor_preview(tensor: torch.Tensor, filename_prefix: str, save_type: str = "temp") -> str | None:
    """Save a tensor preview (first image in batch) to the comfy dir and return a resource URL.

    - tensor: expected shape (B,H,W,C) or (H,W,C) or (B,C,H,W); function will normalize.
    - filename_prefix: passed to resolve_filepath (may include subfolder path).
    - save_type: passed to get_comfy_dir (e.g., 'temp' or other resource types).

    Returns the resource URL string on success or None on failure.
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

FilterResult = Tuple[torch.Tensor, Dict[str, str]]

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
    use_conditioning: bool = False,
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
        use_conditioning (bool, optional): If True, combines additional conditioning with prompts. Defaults to False.

    Returns:
        torch.Tensor: The inpainted image tensor, blended with the original image according to the mask.
    """
    with torch.inference_mode():
        clip_encoder = nodes.CLIPTextEncode()
        positive = clip_encoder.encode(clip, positive_prompt)[0]
        negative = clip_encoder.encode(clip, negative_prompt)[0]

        if use_conditioning:
            combine_node = nodes.ConditioningCombine()
            if positive_conditioning is not None:
                positive = combine_node.combine(positive_conditioning, positive)[0]
            if negative_conditioning is not None:
                negative = combine_node.combine(negative_conditioning, negative)[0]

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

# region Helpers for Inpaint Node
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

    raw_upsample = settings.get("upsample")
    if raw_upsample is None or raw_upsample == "":
        raw_upsample = settings.get("upsample_target")
    upsample_target = convert_to_int(raw_upsample) if raw_upsample is not None else None

    upsample_applied = False
    upsample_info = None
    if upsample_target is not None and upsample_target > 0:
        orig_h, orig_w = int(work_image.shape[1]), int(work_image.shape[2])
        longest = max(orig_h, orig_w)
        if longest < upsample_target:
            scale = float(upsample_target) / float(longest)
            # Compute target sizes using the same scale, then align the longest side
            # and compute the other side proportionally to preserve aspect ratio.
            target_h = max(1, int(round(orig_h * scale)))
            target_w = max(1, int(round(orig_w * scale)))

            def align_up(value: int, alignment: int) -> int:
                return ((value + alignment - 1) // alignment) * alignment

            def align_nearest(value: int, alignment: int) -> int:
                # snap to nearest multiple of alignment (with minimum of alignment)
                if alignment <= 1:
                    return max(1, value)
                half = alignment // 2
                return max(alignment, ((value + half) // alignment) * alignment)

            # Align the longest side up to meet alignment requirements
            if orig_h >= orig_w:
                new_h = align_up(target_h, align_multiple)
                # compute width proportionally and snap to nearest alignment multiple
                new_w = max(1, int(round(new_h * (orig_w / float(orig_h)))))
                new_w = align_nearest(new_w, align_multiple)
            else:
                new_w = align_up(target_w, align_multiple)
                new_h = max(1, int(round(new_w * (orig_h / float(orig_w)))))
                new_h = align_nearest(new_h, align_multiple)

            wi = work_image.permute(0, 3, 1, 2)
            wi = F.interpolate(wi, size=(new_h, new_w), mode="bicubic", align_corners=False)
            work_image = wi.permute(0, 2, 3, 1).contiguous()

            wm = work_mask_soft.unsqueeze(1)
            wm = F.interpolate(wm, size=(new_h, new_w), mode="nearest")
            work_mask_soft = wm.squeeze(1).contiguous()

            upsample_applied = True
            upsample_info = (orig_h, orig_w, new_h, new_w)

    meta = {
        "dilate_px": dilate_px,
        "feather_px": feather_px,
        "upsample_applied": upsample_applied,
        "upsample_info": upsample_info,
        "image_shape": (h, w),
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
    upsample_applied = bool(meta.get("upsample_applied"))
    upsample_info = meta.get("upsample_info")
    dilate_px = int(meta.get("dilate_px", 4))
    feather_px = int(meta.get("feather_px", 2))

    # Debug helpers: save intermediate previews to temp so user can compare
    debug_files: dict = {}

    if upsample_applied and upsample_info is not None:
        orig_h, orig_w, _, _ = upsample_info
        # Save region before downscale (this is what the preview image was taken from)
        url = _save_tensor_preview(processed_region, "inpaint_region_before_downscale", "temp")
        if url:
            debug_files["region_before_downscale"] = url

        pr = processed_region.permute(0, 3, 1, 2)
        # Use bicubic with antialias to preserve high-frequency detail when downscaling.
        # antialias=True produces results that match Pillow for downsampling and generally
        # reduces destructive low-pass effects. Clamp afterwards to avoid bicubic overshoot.
        pr = F.interpolate(pr, size=(orig_h, orig_w), mode="bicubic", align_corners=False, antialias=True)
        processed_region = pr.permute(0, 2, 3, 1).contiguous()
        processed_region = processed_region.clamp(0.0, 1.0)

        # Optionally apply a conservative unsharp mask to restore perceived sharpness
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

    info: Dict[str, str] = {}
    # merge any debug file URLs collected earlier
    if debug_files:
        info.update(debug_files)
    if paste_roi != (0, 0, h, w):
        y0, x0, y1, x1 = paste_roi
        info["roi"] = f"y0={y0},x0={x0},y1={y1},x1={x1}"
    if upsample_applied and upsample_info is not None:
        oh, ow, nh, nw = upsample_info
        info["upsample"] = f"{ow}x{oh} -> {nw}x{nh}"
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

    use_conditioning_raw = settings.get("use_conditioning", "false")
    use_conditioning = convert_to_boolean(use_conditioning_raw)
    if use_conditioning is None:
        use_conditioning = False

    work_image, work_mask_soft, paste_roi, region_meta = _prepare_inpaint_region(
        base_image=base_image,
        mask_tensor=mask_tensor,
        vae=vae,
        settings=settings,
    )

    processed_region = perform_inpaint(
        model=model,
        clip=clip,
        vae=vae,
        image=work_image,
        mask=work_mask_soft,
        positive_prompt=positive_prompt,
        negative_prompt=negative_prompt,
        sampler_name=sampler_name,
        scheduler_name=scheduler_name,
        steps=steps,
        denoise=denoise_value,
        cfg=cfg,
        seed=seed,
        disable_preview=True,
        positive_conditioning=context_positive_conditioning if use_conditioning else None,
        negative_conditioning=context_negative_conditioning if use_conditioning else None,
        use_conditioning=use_conditioning,
    )
    # Save the raw processed region (before final downscale/stitch) to temp so user
    # can preview the area as generated. This mirrors how the mask preview is saved.
    region_url = _save_tensor_preview(processed_region, "inpaint_region", str(settings.get("resource_type") or settings.get("output_type") or "temp"))

    processed, info = _finalize_inpaint_output(
        processed_region=processed_region,
        base_image=base_image,
        paste_roi=paste_roi,
        meta=region_meta,
    )

    info_with_mask = {"mask": mask_url}
    info_with_mask.update(info)
    if region_url:
        info_with_mask["region"] = region_url

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

    h, w = int(base_image.shape[1]), int(base_image.shape[2])
    m = m.to(device=base_image.device, dtype=torch.float32)
    if m.shape[-2] != h or m.shape[-1] != w:
        m = F.interpolate(m.unsqueeze(1), size=(h, w), mode="nearest").squeeze(1)
    m = m.clamp(0.0, 1.0)
    m = (m > 0.5).float()

    work_image, work_mask_soft, paste_roi, region_meta = _prepare_inpaint_region(
        base_image=base_image,
        mask_tensor=m,
        vae=vae,
        settings=settings,
    )

    processed_region = perform_inpaint(
        model=model,
        clip=clip,
        vae=vae,
        image=work_image,
        mask=work_mask_soft,
        positive_prompt=str(settings.get("positive_prompt") or ""),
        negative_prompt=str(settings.get("negative_prompt") or ""),
        sampler_name=str(settings.get("sampler") or "dpmpp_2m"),
        scheduler_name=str(settings.get("scheduler") or "karras"),
        steps=_normalize_steps(settings.get("steps")),
        denoise=_normalize_denoise(settings.get("denoise")),
        cfg=_normalize_cfg(settings.get("cfg")),
        seed=_normalize_seed(settings.get("seed")),
        disable_preview=True,
        positive_conditioning=settings.get("positive_conditioning") if convert_to_boolean(settings.get("use_conditioning", False)) else None,
        negative_conditioning=settings.get("negative_conditioning") if convert_to_boolean(settings.get("use_conditioning", False)) else None,
        use_conditioning=convert_to_boolean(settings.get("use_conditioning", False)) or False,
    )

    _ = _save_tensor_preview(processed_region, "inpaint_region", str(settings.get("resource_type") or settings.get("output_type") or "temp"))

    processed, info = _finalize_inpaint_output(
        processed_region=processed_region,
        base_image=base_image,
        paste_roi=paste_roi,
        meta=region_meta,
    )

    return processed, info
# endregion
