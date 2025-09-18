"""IPAdapter runtime scaffolding.

This MVP focuses on:
- Providing a patch builder used with ComfyUI's transformer_options["patches"].
- Pooling CLIP-Vision features.
- Preparing simple additive K/V modulation data per attached adapter.

Future expansions:
- Proper weight parsing for different IPAdapter variants.
- Multi-image aggregation, negative adapters.
- Advanced scheduling & different fusion modes (concat, replace-heads, attention re-weight).
"""
from typing import Any, Callable, Dict, List, Tuple
import torch

from .weights.parser import parse_ipadapter_weights
    
# region Public API
def pool_vision_features(feats: torch.Tensor, mode: str = "mean") -> torch.Tensor:
    """
    Pools vision features from a tensor by reducing the sequence dimension.

    Args:
        feats (torch.Tensor): Input tensor of shape [B, N, C] or [B, C], where
            B is batch size, N is sequence length (e.g., tokens), and C is feature dimension.
        mode (str, optional): Pooling mode. If "mean", averages features across the sequence dimension.
            If "cls", selects the first token (commonly used for CLS token in transformers).
            Defaults to "mean".

    Returns:
        torch.Tensor: Pooled features of shape [B, C].

    Raises:
        ValueError: If feats is None or has an unexpected number of dimensions.
    """
    if feats is None:
        raise ValueError("vision feats cannot be None")
    if feats.dim() == 2:
        return feats  # already pooled [B, C]
    if feats.dim() != 3:
        raise ValueError(f"Unexpected feats shape {tuple(feats.shape)}; expected 3D or 2D")
    if mode == "cls":
        return feats[:, 0]
    # default mean
    return feats.mean(dim=1)


def _shape_curve(x: float, kind: str) -> float:
    """
    Shapes the input value `x` according to the specified curve type.

    Parameters:
        x (float): Input value, expected to be in the range [0, 1].
        kind (str): Type of curve to apply. Supported values are:
            - "cosine": Smooth ease in/out using a cosine function.
            - "ease_in_out": Cubic ease in/out.
            - Any other value: Linear (default).

    Returns:
        float: Transformed value according to the selected curve type.
               Returns 0.0 if x <= 0, 1.0 if x >= 1.
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if kind == "cosine":  # smooth ease in/out
        import math
        return 0.5 - 0.5 * math.cos(math.pi * x)
    if kind == "ease_in_out":  # cubic ease
        return 3 * x * x - 2 * x * x * x
    return x  # linear / default


def build_ipadapter_attn_patch(adapters: List[Dict[str, Any]]) -> Callable:
    """Return an attn1 patch: f(q, k, v, extra_options[, mask]) -> (q, k', v').

    For each attached adapter with a pooled vision embedding, compute per-head residuals Δk, Δv and
    add them to the current K/V. Includes schedule window gating, optional shaping curve, and
    optional per-sample norm clamp (kv_bias_residual only). If no active adapters, returns a no-op.
    """
    active_adapters = [a for a in adapters if a.get("vision_pooled") is not None]
    if not active_adapters:
        def _noop(q, k, v, extra_options, mask=None):
            # No-op: return original q, k, v. If legacy callers pass mask and expect 4 returns,
            # propagate it back for ABI compatibility.
            return (q, k, v) if mask is None else (q, k, v, mask)
        return _noop

    def _patch(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, extra_options: Dict[str, Any], mask=None):
        # Supports two layouts used by Comfy at this hook:
        # - 3D: [B, N, C]
        # - 4D: [B, H, N, Dh]
        dims = k.dim()
        device = k.device
        dtype = k.dtype

        # Diffusion progress (best-effort; different samplers may expose different keys)
        step_percent = None
        if isinstance(extra_options, dict):
            for key in ("percent_through", "timestep_percent", "sigma_progress"):
                sp = extra_options.get(key)
                if sp is not None:
                    try:
                        step_percent = float(sp)
                        break
                    except Exception:
                        pass

        # Accumulators
        delta_k_heads = None  # [B, H, Dh] for 4D path
        delta_v_heads = None  # [B, H, Dh] for 4D path
        delta_k_3d = None     # [B, C] for 3D path
        delta_v_3d = None     # [B, C] for 3D path

        for ad in active_adapters:
            pooled = ad["vision_pooled"]  # [C] or [B, C]
            strength = float(ad.get("strength", 0.0))
            if strength <= 0:
                continue

            # Schedule gating + shaping
            if step_percent is not None:
                sp = float(ad.get("start_percent", 0.0))
                ep = float(ad.get("end_percent", 1.0))
                if not (sp <= step_percent <= ep):
                    continue
                prog_range = max(ep - sp, 1e-6)
                local_prog = (step_percent - sp) / prog_range
                curve_kind = ad.get("schedule_curve", "linear")
                shaped = _shape_curve(local_prog, curve_kind)
            else:
                shaped = 1.0

            # Device/dtype alignment for pooled and projectors, cache device key
            last_dev_key = "_cached_device_attn1"
            if ad.get(last_dev_key) != str(device):
                if torch.is_tensor(pooled) and pooled.device != device:
                    pooled = pooled.to(device)
                    ad["vision_pooled"] = pooled
                parsed = ad.get("parsed", {})
                for mk, mod in list(parsed.items()):
                    if hasattr(mod, "to"):
                        try:
                            parsed[mk] = mod.to(device=device, dtype=dtype)
                        except Exception:
                            pass
                ad[last_dev_key] = str(device)

            # Batch align pooled embedding to [B, Cv]
            B_eff = k.shape[0]
            if pooled.dim() == 1:
                pooled_b = pooled.unsqueeze(0).expand(B_eff, -1)
            else:
                pooled_b = pooled if pooled.shape[0] == B_eff else pooled[0:1].expand(B_eff, -1)
            if pooled_b.device != device or pooled_b.dtype != dtype:
                pooled_b = pooled_b.to(device=device, dtype=dtype)

            strategy = ad.get("strategy") or ad.get("mode") or "concat_token"
            if strategy == "concat_token":
                # In attn1, concat of context tokens doesn't apply. Treat as no-op to be explicit.
                continue

            parsed = ad.setdefault("parsed", {})

            if dims == 4:
                B4, H, N4, Dh = k.shape

                def project_to_heads(which: str):
                    out_total = H * Dh
                    x = pooled_b
                    candidates = []
                    pj = parsed.get(f"proj_{which}")
                    if pj is not None:
                        candidates.append(pj)
                    unified = parsed.get("unified_proj")
                    if unified is not None:
                        candidates.append(unified)
                    for mod in candidates:
                        out_features = getattr(mod, "out_features", None)
                        try:
                            y = mod(x)
                        except Exception:
                            continue
                        if out_features == Dh:
                            y = y.unsqueeze(1).expand(B4, H, Dh)
                        elif out_features == out_total:
                            y = y.view(B4, H, Dh)
                        else:
                            continue
                        if y.dtype != dtype:
                            y = y.to(dtype)
                        return y
                    if x.shape[-1] == Dh:
                        return x.unsqueeze(1).expand(B4, H, Dh)
                    return None

                dk = project_to_heads("k")
                dv = project_to_heads("v")
            else:  # dims == 3 -> k: [B, N, C]
                B3, N3, C = k.shape

                def project_to_channels(which: str):
                    x = pooled_b
                    candidates = []
                    pj = parsed.get(f"proj_{which}")
                    if pj is not None:
                        candidates.append(pj)
                    unified = parsed.get("unified_proj")
                    if unified is not None:
                        candidates.append(unified)
                    for mod in candidates:
                        out_features = getattr(mod, "out_features", None)
                        try:
                            y = mod(x)
                        except Exception:
                            continue
                        if out_features == C:
                            if y.dtype != dtype:
                                y = y.to(dtype)
                            return y
                    if x.shape[-1] == C:
                        return x
                    return None

                dk = project_to_channels("k")
                dv = project_to_channels("v")

            if dk is None and dv is None:
                continue
            if dk is None:
                dk = torch.zeros_like(dv)
            if dv is None:
                dv = torch.zeros_like(dk)

            if strategy == "kv_bias_residual":
                norm_clip = float(ad.get("kv_norm_clip", 0.0))
                if norm_clip > 0:
                    with torch.no_grad():
                        for t in (dk, dv):
                            nrm = t.norm(dim=-1, keepdim=True) + 1e-6
                            scale = torch.clamp(norm_clip / nrm, max=1.0)
                            t.mul_(scale)

            scale = strength * shaped
            dk = dk * scale
            dv = dv * scale

            if dims == 4:
                delta_k_heads = dk if delta_k_heads is None else (delta_k_heads + dk)
                delta_v_heads = dv if delta_v_heads is None else (delta_v_heads + dv)
            else:
                delta_k_3d = dk if delta_k_3d is None else (delta_k_3d + dk)
                delta_v_3d = dv if delta_v_3d is None else (delta_v_3d + dv)

        if (dims == 4 and delta_k_heads is None and delta_v_heads is None) or (dims == 3 and delta_k_3d is None and delta_v_3d is None):
            # Nothing to do; return original q, k, v (or q, k, v, mask for legacy callers)
            return (q, k, v) if mask is None else (q, k, v, mask)

        # Broadcast and add to K/V based on layout
        if dims == 4:
            B4, H, N4, Dh = k.shape
            if delta_k_heads is None:
                delta_k_heads = torch.zeros((B4, H, Dh), device=device, dtype=dtype)
            if delta_v_heads is None:
                delta_v_heads = torch.zeros((B4, H, Dh), device=device, dtype=dtype)
            dk_seq = delta_k_heads.unsqueeze(2)  # [B,H,1,Dh]
            dv_seq = delta_v_heads.unsqueeze(2)
            k = k + dk_seq
            v = v + dv_seq
        else:  # dims == 3
            B3, N3, C = k.shape
            if delta_k_3d is None:
                delta_k_3d = torch.zeros((B3, C), device=device, dtype=dtype)
            if delta_v_3d is None:
                delta_v_3d = torch.zeros((B3, C), device=device, dtype=dtype)
            dk_seq = delta_k_3d.unsqueeze(1)  # [B,1,C]
            dv_seq = delta_v_3d.unsqueeze(1)
            k = k + dk_seq
            v = v + dv_seq
        # Return updated q, k, v; if legacy mask-enabled API is in use, return 4 values.
        return (q, k, v) if mask is None else (q, k, v, mask)

    return _patch


def build_patches_dict(adapters: List[Dict[str, Any]]):
    """
    Builds a dictionary containing attention patch information for IPAdapter modules.

    Args:
        adapters (List[Dict[str, Any]]): A list of adapter configurations, where each adapter is represented as a dictionary.

    Returns:
        dict: A dictionary with a single key "attn1_patch" mapping to a list containing the result of build_ipadapter_attn_patch called with the adapters.
    """
    return {"attn1_patch": [build_ipadapter_attn_patch(adapters)]}
# endregion

# region Weight parsing (to be expanded)
def parse_adapter_weights(adapter: Dict[str, Any]):
    """
    Parses and processes the weights of an IP-Adapter from the provided adapter dictionary.

    This function checks if the adapter is loaded and if the weight parser is available.
    It then attempts to parse the adapter's state dictionary using the `parse_ipadapter_weights` function.
    If parsing is successful, it updates the adapter's "parsed" dictionary with the parsed results,
    sets certain keys to not require gradients, and adds a lightweight summary to "parsed_meta" for logging.
    If parsing fails, it marks the variant as "unrecognized".

    Args:
        adapter (Dict[str, Any]): A dictionary containing adapter information, including its state dict,
                                  filename, and loaded status.

    Returns:
        None
    """
    if not adapter.get("loaded"):
        return
    if parse_ipadapter_weights is None:
        return  # parser not available
    sd = adapter.get("state_dict") or {}
    if not isinstance(sd, dict) or not sd:
        return
    # Skip if already parsed with a recognized variant.
    parsed = adapter.setdefault("parsed", {})
    if parsed.get("variant"):
        return
    result = parse_ipadapter_weights(sd, {"filename": adapter.get("filename", "")})
    if result:
        parsed.update(result)
        # Provide backward compat keys expected by current patch builder.
        if "proj_k" in parsed and parsed["proj_k"] is not None:
            parsed["proj_k"].requires_grad_(False)
        if "proj_v" in parsed and parsed["proj_v"] is not None:
            parsed["proj_v"].requires_grad_(False)
        # Expose a lightweight summary separate from modules for logging ease
        adapter["parsed_meta"] = {
            "variant": parsed.get("variant"),
            "vision_dim": parsed.get("vision_dim"),
            "target_dim": parsed.get("target_dim"),
            "num_lora_blocks": parsed.get("num_lora_blocks"),
            "has_k_ip": parsed.get("has_k_ip"),
            "has_v_ip": parsed.get("has_v_ip"),
            "perceiver_layers": parsed.get("perceiver_layers"),
        }
    else:
        # Leave parsed empty; patch builder will adapt dimensions on-the-fly.
        parsed.setdefault("variant", "unrecognized")
# endregion
