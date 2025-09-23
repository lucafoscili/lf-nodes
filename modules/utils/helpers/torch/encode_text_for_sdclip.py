import inspect
import torch

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
    toks = tokenizer(
        prompt,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=tokenizer.model_max_length,
    )
    id_list = toks.input_ids.tolist()

    sig = inspect.signature(text_encoder.forward)
    params = [p for p in sig.parameters if p != "self"]

    if params == ["tokens"]:
        args, kwargs = [id_list], {}
    else:
        args, kwargs = toks.input_ids.to(device), {}

    with torch.no_grad():
        out = text_encoder(*args, **kwargs)

    toks = { k: v.to(device) for k,v in toks.items() }
    sd_embeds = out[0]

    return sd_embeds, toks["input_ids"], toks["attention_mask"]
# endregion