import torch

# region get_text_encoder_from_clip
def get_text_encoder_from_clip(clip) -> torch.nn.Module:
    """
    Retrieve the text encoder from a CLIP model.

    Args:
        clip: A CLIP model instance.

    Returns:
        torch.nn.Module: The text encoder module from the CLIP model.

    Raises:
        AttributeError: If the CLIP model does not have a text encoder.
    """
    # 1) SDXLClipModel in ComfyUI
    if hasattr(clip, "cond_stage_model"):
        cs = clip.cond_stage_model
        if hasattr(cs, "clip_l"):
            return cs.clip_l
        if hasattr(cs, "clip_g"):
            return cs.clip_g

    # 2) HuggingFace Transformers CLIPModel
    if hasattr(clip, "text_model"):
        return clip.text_model
    if hasattr(clip, "text_encoder"):
        return clip.text_encoder

    # 3) Diffusers pipelines
    if hasattr(clip, "pipeline") and hasattr(clip.pipeline, "text_encoder"):
        return clip.pipeline.text_encoder

    raise AttributeError(f"Could not find a CLIP text encoder in {clip!r}")
# endregion