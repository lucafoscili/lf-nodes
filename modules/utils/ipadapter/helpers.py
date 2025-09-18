from server import PromptServer
from typing import Any, Dict, List, Tuple

from ...utils.constants import EVENT_PREFIX
from .runtime import build_ipadapter_attn_patch
from .common import markdown_block

# region get_strategy_and_curve
def get_strategy_and_curve(record: Dict[str, Any], user_strategy: str) -> Tuple[str, str | None]:
    """
    Determines the strategy to use based on the provided record and user-specified strategy.

    Args:
        record (Dict[str, Any]): A dictionary containing model configuration and parsed parameters.
        user_strategy (str): The strategy specified by the user. Can be "auto", "kv_bias_residual", or other supported strategies.

    Returns:
        Tuple[str, str | None]: A tuple containing the chosen strategy and an optional reason or flag.
            - If the strategy is determined automatically, returns ("kv_bias_residual", None) or ("add_kv", None).
            - If the user strategy is "kv_bias_residual" but required projectors are missing, returns ("add_kv", "no_projector").
            - Otherwise, returns (user_strategy, None).
    """
    if user_strategy == "auto":
        if "kv_bias_residual" in record.get("supported_strategies", []):
            return "kv_bias_residual", None
        return "add_kv", None
    if user_strategy == "kv_bias_residual" and not record.get("projectors", {}).get("kv", False):
        return "add_kv", "no_projector"
    return user_strategy, None
# endregion

# region send_node_log
def send_node_log(event: str, node_id: str, title: str, lines: List[str]) -> None:
    """
    Sends a log event for a specific node to the PromptServer.

    Args:
        event (str): The type of event to log.
        node_id (str): The identifier of the node.
        title (str): The title of the log message.
        lines (List[str]): The content lines of the log message.

    Returns:
        None
    """
    PromptServer.instance.send_sync(f"{EVENT_PREFIX}{event}", {"node": node_id, "value": markdown_block(title, lines)})
# endregion

# region attach_adapter
def attach_adapter(model: Any, record: Dict[str, Any], *, dedupe: bool = True, key: str = "path") -> Tuple[List[Dict[str, Any]], bool]:
    """
    Attaches an adapter record to the given model's 'lf_ipadapters' attribute.

    Note: dedupe is ignored; records are always appended to preserve explicit chaining.
    The function returns the updated list of attached adapters and a boolean indicating whether a replacement occurred
    (always False in this simplified behavior).

    Args:
        model (Any): The model object to which the adapter will be attached.
        record (Dict[str, Any]): The adapter record to attach.
    dedupe (bool, optional): Deprecated and ignored. Kept for backward compatibility.
    key (str, optional): Deprecated and ignored.

    Returns:
        Tuple[List[Dict[str, Any]], bool]: 
            - The updated list of attached adapter records.
            - A boolean indicating if a replacement occurred (True) or if the record was appended (False).
    """

    attached_list = getattr(model, "lf_ipadapters", [])
    replaced = False
    # Always append to allow explicit chaining of multiple embeddings/adapters.
    attached_list.append(record)
    setattr(model, "lf_ipadapters", attached_list)
    return attached_list, replaced
# endregion

# region ensure_attn1_patch
def ensure_attn1_patch(model: Any) -> Tuple[bool, str]:
    """
    Ensures that the attention patch (`attn1_patch`) is injected into the given model or its patcher.

    The function checks if the model or one of its attributes (`model_patcher` or `patcher`) has the method
    `set_model_attn1_patch`. If found, it builds an attention patch using the model's `lf_ipadapters` attribute
    and injects it via the `set_model_attn1_patch` method.

    Args:
        model (Any): The model object to patch.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success, and a message describing the result.
    """
    patch_target = None
    if hasattr(model, "set_model_attn1_patch"):
        patch_target = model
    else:
        for attr in ("model_patcher", "patcher"):
            if hasattr(model, attr):
                cand = getattr(model, attr)
                if hasattr(cand, "set_model_attn1_patch"):
                    patch_target = cand
                    break
    if patch_target is None:
        return False, "No patch target found"
    adapters = getattr(model, "lf_ipadapters", [])
    patch_callable = build_ipadapter_attn_patch(adapters)
    patch_target.set_model_attn1_patch(patch_callable)
    return True, "attn1_patch injected"
# endregion

# region format_parsed_meta_lines
def format_parsed_meta_lines(pmeta: Dict[str, Any]) -> List[str]:
    """
    Formats parsed metadata from a dictionary into a list of human-readable strings.

    Args:
        pmeta (Dict[str, Any]): A dictionary containing parsed metadata with expected keys such as
            'variant', 'vision_dim', 'target_dim', 'num_lora_blocks', 'has_k_ip', 'has_v_ip', and optionally 'perceiver_layers'.

    Returns:
        List[str]: A list of formatted strings representing the metadata. If the input dictionary is empty,
            returns an empty list. Includes a header and formatted key-value pairs, with special handling for
            the 'perceiver_layers' key to preview up to 6 layers.
    """
    lines: List[str] = []
    if not pmeta:
        return lines
    lines.append("- 🔎 Parsed variant metadata:")
    def _fmt(k: str, v: Any):
        return f"   • {k}: {v}" if v is not None else f"   • {k}: -"
    for key in ("variant", "vision_dim", "target_dim", "num_lora_blocks", "has_k_ip", "has_v_ip"):
        lines.append(_fmt(key, pmeta.get(key)))
    if pmeta.get("perceiver_layers"):
        layers = pmeta.get("perceiver_layers")
        try:
            preview = layers[:6]
            suffix = "..." if len(layers) > 6 else ""
            lines.append(f"   • perceiver_layers: {preview}{suffix}")
        except Exception:
            lines.append(f"   • perceiver_layers: {pmeta.get('perceiver_layers')}")
    return lines
# endregion

# region choose_strategy
def choose_strategy(record: Dict[str, Any], user_strategy: str) -> Tuple[str, str | None]:
    """
    Determines the strategy to use based on the provided record and user-specified strategy.

    Args:
        record (Dict[str, Any]): A dictionary containing model configuration and parsed parameters.
        user_strategy (str): The strategy specified by the user. Can be "auto", "kv_bias_residual", or other supported strategies.

    Returns:
        Tuple[str, str | None]: A tuple containing the chosen strategy and an optional reason or flag.
            - If the strategy is determined automatically, returns ("kv_bias_residual", None) or ("add_kv", None).
            - If the user strategy is "kv_bias_residual" but required projectors are missing, returns ("add_kv", "no_projector").
            - Otherwise, returns (user_strategy, None).
    """
    parsed = record.get("parsed", {})
    if user_strategy == "auto":
        vision_dim = parsed.get("vision_dim") or record.get("vision_pooled_dim")
        target_dim = parsed.get("target_dim")
        has_proj = parsed.get("proj_k") is not None or parsed.get("proj_v") is not None
        if has_proj or (vision_dim is not None and target_dim is not None and vision_dim == target_dim):
            return "kv_bias_residual", None
        return "add_kv", None
    if user_strategy == "kv_bias_residual":
        if not (parsed.get("proj_k") or parsed.get("proj_v") or record.get("vision_pooled_dim")):
            return "add_kv", "no_projector"
    return user_strategy, None
# endregion