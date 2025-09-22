import torch

from ..comfy import get_tokenizer_from_clip

# region get_clip_tokens
def get_clip_tokens(clip, text: str) -> tuple[int, list[str]]:
    """
    Counts the number of CLIP tokens in a given text string and decodes the token list.
    Parameters:
        clip: Either a CLIP model instance with a tokenizer attribute or a tokenizer instance.
        text (str): The text string to be tokenized.
    Returns:
        tuple: A tuple containing the number of tokens and the decoded token list.                
    """
    tokenizer = get_tokenizer_from_clip(clip)

    # HuggingFace style
    if callable(tokenizer):
        encoded = tokenizer(text, return_tensors="pt")
        token_ids = encoded.input_ids[0]
        tokens = tokenizer.convert_ids_to_tokens(token_ids)            
    # Fallbacks for other styles
    elif hasattr(tokenizer, "encode"):
        token_ids = torch.tensor(tokenizer.encode(text), dtype=torch.long)
        tokens = tokenizer.convert_ids_to_tokens(token_ids)
    elif hasattr(tokenizer, "tokenize_to_ids"):
        token_ids = torch.tensor(tokenizer.tokenize_to_ids(text), dtype=torch.long)
        tokens = tokenizer.convert_ids_to_tokens(token_ids)
    elif hasattr(tokenizer, "text_to_ids"):
        token_ids = torch.tensor(tokenizer.text_to_ids(text), dtype=torch.long)
        tokens = tokenizer.convert_ids_to_tokens(token_ids)
    else:
        raise AttributeError("Tokenizer does not support any known tokenization method.")

    return (len(tokens), [token.replace("</w>", " ") for token in tokens])
# endregion