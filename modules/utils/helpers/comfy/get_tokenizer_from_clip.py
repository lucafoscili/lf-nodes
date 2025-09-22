# region get_tokenizer_from_clip
def get_tokenizer_from_clip(clip):
    """
    Retrieve the tokenizer from a CLIP model.

    Args:
        clip: A CLIP model instance.

    Returns:
        tokenizer: The tokenizer associated with the CLIP model.

    Raises:
        AttributeError: If the CLIP model does not have a tokenizer.
    """
    # 1) SDXLClipModel in ComfyUI: clip.tokenizer has clip_l and clip_g
    if hasattr(clip, "tokenizer") and hasattr(clip.tokenizer, "clip_l") and hasattr(clip.tokenizer, "clip_g"):
        # prefer the 'clip_l' tokenizer for encoding
        tok = clip.tokenizer.clip_l
        if hasattr(tok, "tokenizer"):
            tok = tok.tokenizer
        return tok

    # 2) HuggingFace Transformers style
    if hasattr(clip, "tokenizer"):
        tok = clip.tokenizer
        # Some HF pipelines wrap the real tokenizer under .tokenizer
        if hasattr(tok, "tokenizer"):
            tok = tok.tokenizer
        return tok

    # 3) Diffusers pipelines
    if hasattr(clip, "pipeline") and hasattr(clip.pipeline, "tokenizer"):
        return clip.pipeline.tokenizer

    raise AttributeError(f"Could not find a CLIP tokenizer in {clip!r}")
# endregion