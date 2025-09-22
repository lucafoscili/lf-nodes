import torch

import comfy.sample
import nodes

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
) -> torch.Tensor:
    """Run an inpaint diffusion pass and blend the result with the original image."""
    with torch.inference_mode():
        clip_encoder = nodes.CLIPTextEncode()
        positive = clip_encoder.encode(clip, positive_prompt)[0]
        negative = clip_encoder.encode(clip, negative_prompt)[0]

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
