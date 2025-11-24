import torch

from typing import List, Tuple, Any

from ..conversion import tensor_to_pil

# region tag_image
def tag_image(
    processor: Any,
    model: Any,
    image_tensor: torch.Tensor,
    threshold: float = 0.25,
    top_k: int = 20,
    remove_underscore: bool = True,
    blacklist: List[str] = None,
) -> List[Tuple[str, float]]:
    """
    Tags an image using the provided WD14 processor and model.

    Args:
        processor: The image processor (e.g., transforms.Compose).
        model: The tagging model.
        image_tensor: The image tensor to tag.
        threshold: Minimum confidence to keep a tag.
        top_k: Maximum number of tags to output.
        remove_underscore: Whether to replace underscores with spaces.
        blacklist: List of tags to ignore.

    Returns:
        List of (tag, confidence) tuples.
    """
    from .build_id2label import build_id2label

    pil_img = tensor_to_pil(image_tensor)
    try:
        inputs = processor(images=pil_img, return_tensors="pt")  # HF-style API
    except TypeError:
        try:
            inputs = processor(pil_img, return_tensors="pt")  # positional + return_tensors
        except TypeError:
            raw = processor(pil_img)  # pure transform
            if isinstance(raw, torch.Tensor):
                inputs = {"pixel_values": raw.unsqueeze(0)}
            elif isinstance(raw, dict):
                inputs = raw
            else:
                raise RuntimeError(f"Unsupported processor output: {type(raw)}")

    with torch.no_grad():
        try:
            outputs = model(**inputs)
        except TypeError:
            if isinstance(inputs, dict) and "pixel_values" in inputs:
                x = inputs["pixel_values"]
            else:
                x = next(v for v in inputs.values() if torch.is_tensor(v))
            outputs = model(x)
        logits = outputs.logits if hasattr(outputs, "logits") else outputs

    probs = logits.sigmoid().cpu().numpy()[0]

    id2lab = build_id2label(model)

    candidates = []
    for i, p in enumerate(probs):
        if p < threshold:
            continue
        tag = id2lab[i]
        if remove_underscore:
            tag = tag.replace("_", " ")
        candidates.append((tag, float(p)))

    if blacklist:
        raw_blacklist = [b.strip().lower() for b in blacklist if b.strip()]
        candidates = [
            (tag, conf) for tag, conf in candidates
            if tag.lower() not in raw_blacklist
        ]

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:top_k]
# endregion

# region apply_wd14_tagging_to_prompt
def apply_wd14_tagging_to_prompt(
    positive_prompt: str,
    image_tensor: torch.Tensor,
    wd14_model,
    wd14_processor,
    threshold: float = 0.25,
    top_k: int = 20,
) -> str:
    """
    Applies WD14 tagging to the given positive prompt by tagging the provided image tensor.

    Args:
        positive_prompt: The original positive prompt string.
        image_tensor: The image tensor to tag.
        wd14_model: The WD14 tagging model.
        wd14_processor: The WD14 image processor.
        threshold: Minimum confidence threshold for tags.
        top_k: Maximum number of tags to include.

    Returns:
        The modified positive prompt with tags appended, or the original if tagging fails.
    """
    if not wd14_model or not wd14_processor:
        return positive_prompt

    tags = tag_image(
        processor=wd14_processor,
        model=wd14_model,
        image_tensor=image_tensor,
        threshold=threshold,
        top_k=top_k,
    )

    if tags:
        tag_strings = [tag for tag, _ in tags]
        tagged_prompt = positive_prompt + ", " + ", ".join(tag_strings)
        print(f"[WD14 Tagging] Added tags: {tag_strings}")
        return tagged_prompt

    return positive_prompt
# endregion