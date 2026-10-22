"""Encode images with a core-loaded CLIP_VISION model, keeping patch tokens.

Core ``ClipVisionModel.encode_image`` calls ``out[1].to(...)`` unconditionally,
and DINOv3's forward returns ``(sequence, None, pooled, None)``, so core
CLIPVisionEncode raises with DINOv3. This mirrors encode_image (preprocess,
forward, Output fields) but only reads the hidden-state entry when it exists.
Comfy modules are imported lazily: the CPU test boundary stubs ``comfy``.
"""
import torch

CROPS = ('center', 'none')


def _check_inputs(clip_vision, image, crop):
    if clip_vision is None or getattr(clip_vision, 'model', None) is None \
            or getattr(clip_vision, 'patcher', None) is None:
        raise ValueError('clip_vision requires a CLIP_VISION model from core CLIPVisionLoader.')
    if getattr(clip_vision, 'model_type', None) == 'siglip2_vision_model':
        raise ValueError('clip_vision is a siglip2_vision_model, whose preprocessing differs; '
                         'use core CLIPVisionEncode for it.')
    if (not isinstance(image, torch.Tensor) or image.ndim != 4 or image.shape[0] < 1
            or image.shape[-1] not in (3, 4) or not image.is_floating_point()):
        raise ValueError('image must be an IMAGE tensor [B,H,W,C] with 3 or 4 channels.')
    if crop not in CROPS:
        raise ValueError("crop must be 'center' or 'none', as in core CLIPVisionEncode.")


def vision_output_from_pixel_values(model, pixel_values, device, intermediate_output=-2):
    """Run the loaded vision model on preprocessed pixels and build core's Output."""
    from comfy.clip_vision import Output

    out = model(pixel_values=pixel_values, intermediate_output=intermediate_output)
    if not isinstance(out, (tuple, list)) or len(out) < 3:
        raise ValueError('clip_vision model output must be a tuple (sequence, hidden, pooled, ...); '
                         f'got {type(out).__name__}.')
    sequence, hidden, pooled = out[0], out[1], out[2]
    if not isinstance(sequence, torch.Tensor) or sequence.ndim != 3:
        raise ValueError('clip_vision model output has no [B,T,D] sequence tensor at index 0.')
    if not isinstance(pooled, torch.Tensor):
        raise ValueError('clip_vision model output has no pooled tensor at index 2.')
    if sequence.shape[0] != pixel_values.shape[0]:
        raise ValueError('clip_vision model output batch does not match the image batch.')

    outputs = Output()
    outputs['last_hidden_state'] = sequence.to(device)
    outputs['image_embeds'] = pooled.to(device)
    outputs['image_sizes'] = [pixel_values.shape[1:]] * pixel_values.shape[0]
    if isinstance(hidden, torch.Tensor):
        if intermediate_output == 'all':
            hidden = hidden.to(device)
            outputs['penultimate_hidden_states'] = hidden[:, -2]
            outputs['all_hidden_states'] = hidden
        else:
            outputs['penultimate_hidden_states'] = hidden.to(device)
    outputs['mm_projected'] = out[3] if len(out) > 3 else None
    return outputs


def encode_vision_patches(clip_vision, image, crop):
    """CLIPVisionEncode's path for a core CLIP_VISION, tolerant of a None hidden state."""
    _check_inputs(clip_vision, image, crop)
    from comfy.clip_model import clip_preprocess
    from comfy.model_management import intermediate_device, load_model_gpu

    load_model_gpu(clip_vision.patcher)
    pixel_values = clip_preprocess(
        image.to(clip_vision.load_device), size=clip_vision.image_size,
        mean=clip_vision.image_mean, std=clip_vision.image_std, crop=crop == 'center').float()
    mode = 'all' if getattr(clip_vision, 'return_all_hidden_states', False) else -2
    return vision_output_from_pixel_values(clip_vision.model, pixel_values,
                                           intermediate_device(), mode)
