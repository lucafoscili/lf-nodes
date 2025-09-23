from typing import Dict, Tuple

import random
import torch
import torch.nn.functional as F

import comfy.sample
import nodes

from ..constants import SAMPLERS, SCHEDULERS
from ..helpers.api import get_resource_url
from ..helpers.comfy import resolve_filepath
from ..helpers.conversion import base64_to_tensor, convert_to_boolean, convert_to_float, convert_to_int, tensor_to_pil
from ..helpers.editing import get_editing_context

FilterResult = Tuple[torch.Tensor, Dict[str, str]]


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
    Run an inpaint diffusion pass and blend the result with the original image.

    When `use_conditioning` is True, any provided conditioning stacks are prepended to the freshly
    encoded prompts before sampling.

    Args:
        model: The diffusion model to use for inpainting.
        clip: The CLIP model for text encoding.
        vae: The VAE model for encoding/decoding images.
        image (torch.Tensor): The input image tensor to be inpainted.
        mask (torch.Tensor): The mask tensor indicating regions to inpaint (1=inpaint, 0=keep original).
        positive_prompt (str): The positive text prompt guiding the inpainting.
        negative_prompt (str): The negative text prompt for guidance.
        sampler_name (str): The name of the sampler to use.
        scheduler_name (str): The name of the scheduler to use.
        steps (int): Number of diffusion steps.
        denoise (float): Denoising strength (typically between 0 and 1).
        cfg (float): Classifier-free guidance scale.
        seed (int): Random seed for reproducibility.
        disable_preview (bool, optional): If True, disables preview sampling for efficiency. Defaults to True.

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

    Returns:
        FilterResult: A tuple containing:
            - processed (torch.Tensor): The inpainted image tensor.
            - info (dict): Dictionary with additional information, including the mask URL.
            
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
    seed_default = context.get("seed")
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
    mask_output_file, mask_subfolder, mask_filename = resolve_filepath(
        filename_prefix="inpaint_mask",
        image=mask_preview_tensor,
    )
    mask_image.save(mask_output_file, format="PNG")
    mask_url = get_resource_url(mask_subfolder, mask_filename, "temp")

    steps = max(1, int(round(convert_to_int(settings.get("steps", 20)))))
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

    seed_candidate = convert_to_int(settings.get("seed"))
    if seed_candidate is None or seed_candidate < 0:
        seed_candidate = convert_to_int(seed_default)
    if seed_candidate is None or seed_candidate < 0:
        seed_candidate = random.randint(0, 2**32 - 1)
    seed = seed_candidate & 0xFFFFFFFFFFFFFFFF

    positive_prompt = str(settings.get("positive_prompt") or context_positive_prompt)
    negative_prompt = str(settings.get("negative_prompt") or context_negative_prompt)

    use_conditioning_raw = settings.get("use_conditioning", "false")
    use_conditioning = convert_to_boolean(use_conditioning_raw)
    if use_conditioning is None:
        use_conditioning = False

    processed = perform_inpaint(
        model=model,
        clip=clip,
        vae=vae,
        image=base_image,
        mask=mask_tensor,
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

    processed = processed.detach().clamp(0.0, 1.0).to(torch.float32).cpu().contiguous()

    return processed, {"mask": mask_url}


__all__ = [
    "FilterResult",
    "apply_inpaint_filter",
    "perform_inpaint",
    "sample_without_preview",
]
