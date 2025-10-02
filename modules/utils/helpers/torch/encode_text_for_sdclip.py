import inspect
import torch


def _resolve_context_length(tokenizer, text_encoder) -> int:
    """Determine a safe maximum sequence length shared by the tokenizer and encoder."""

    def _candidate(value):
        if isinstance(value, int) and value > 0:
            return value
        return None

    candidates = []

    for attr in ("model_max_length", "max_length", "max_len_single_sentence", "context_length"):
        value = getattr(tokenizer, attr, None)
        maybe = _candidate(value)
        if maybe is not None:
            candidates.append(maybe)

    encoder_cfg = getattr(text_encoder, "config", None)
    for source in (text_encoder, encoder_cfg):
        if source is None:
            continue
        for attr in ("max_length", "max_position_embeddings", "max_sequence_length", "n_positions", "context_length", "ctx_len", "n_ctx"):
            value = getattr(source, attr, None)
            maybe = _candidate(value)
            if maybe is not None:
                candidates.append(maybe)

    if not candidates:
        return 77

    context = min(candidates)
    # Guard against pathological tokenizer values (e.g., 8192 from some HF configs).
    return min(context, 512)

# region encode_text_for_sdclip
def encode_text_for_sdclip(text_encoder, tokenizer, prompt, device):
    """
    Encodes a text prompt using a given text encoder and tokenizer for use with SDClip models.
    This function tokenizes the input prompt and passes it through the provided text encoder,
    handling different encoder signatures (e.g., custom SDClipModel or HuggingFace CLIPTextModel).
    It returns the encoded text features suitable for downstream tasks.

    Args:
        text_encoder: The text encoder model to use for encoding the prompt.
        tokenizer: The tokenizer compatible with the text encoder.
        prompt (str): The text prompt to encode.
        device: The device (e.g., 'cpu' or 'cuda') to perform computation on.
        
    Returns:
        tuple: A tuple containing the encoded text features, input IDs, and attention mask.
    """
    max_length = _resolve_context_length(tokenizer, text_encoder)
    toks = tokenizer(
        prompt,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=max_length,
    )

    # Some tokenizers ignore max_length when padding; enforce manually.
    truncated = {}
    for key, value in toks.items():
        if hasattr(value, "dim") and callable(value.dim) and value.dim() >= 2:
            truncated[key] = value[:, :max_length]
        elif hasattr(value, "__getitem__"):
            truncated[key] = value[:max_length]
        else:
            truncated[key] = value
    toks = truncated
    id_list = toks["input_ids"].tolist()

    sig = inspect.signature(text_encoder.forward)
    params = [p for p in sig.parameters if p != "self"]

    if params == ["tokens"]:
        args, kwargs = [id_list], {}
    else:
        args, kwargs = toks["input_ids"].to(device), {}

    with torch.no_grad():
        out = text_encoder(*args, **kwargs)

    toks = {k: v.to(device) if hasattr(v, "to") else v for k, v in toks.items()}
    sd_embeds = out[0]

    return sd_embeds, toks["input_ids"], toks["attention_mask"]
# endregion