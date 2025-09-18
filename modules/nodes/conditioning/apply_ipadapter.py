import traceback
from typing import Any, Dict

from types import SimpleNamespace

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers import normalize_list_to_value
from ...utils.ipadapter.runtime import pool_vision_features, parse_adapter_weights
from ...utils.ipadapter.common import (
    resolve_encode_fn,
    extract_vision_features,
    l2_normalize,
    maybe_unsqueeze_batch,
)
from ...utils.ipadapter.helpers import attach_adapter, ensure_attn1_patch, format_parsed_meta_lines, send_node_log

def _send_log(event: str, node_id: str, title: str, lines: list[str]):
    send_node_log(event, node_id, title, lines)

# region LF_ApplyIPAdapter
class LF_ApplyIPAdapter:
    """Associate a loaded IPAdapter object with a diffusion model.

    NOTE: This skeleton does NOT yet perform attention injection. It stores the metadata on the
    model object (`model.lf_ipadapters` list) to allow future sampler / patch code to use it.
    """

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("MODEL", "IPADAPTER")
    RETURN_NAMES = ("model", "ipadapter")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (Input.MODEL, {}),
                "ipadapter": (Input.IPADAPTER, {}),
                "strength": (Input.FLOAT, {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                    "tooltip": "Intended guidance strength placeholder (not yet active)."
                }),
            },
            "optional": {
                "image": (Input.IMAGE, {
                    "tooltip": "Reference image for feature extraction (face/style)."
                }),
                "clip_vision": (Input.CLIP_VISION, {
                    "tooltip": "CLIP Vision model output or handle."
                }),
                "pool_mode": (Input.STRING, {
                    "default": "mean", 
                    "tooltip": "Pooling strategy for vision features: mean | cls."
                }),
                "mode": (Input.STRING, {
                    "default": "concat_token", 
                    "tooltip": "Fusion mode (MVP fixed to concat_token)."
                }),
                "start_percent": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 0.99,
                    "step": 0.01,
                    "tooltip": "Start % of diffusion steps (reserved)."
                }),
                "end_percent": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "End % of diffusion steps (reserved)."
                }),
                "device": (Input.STRING, {
                    "default": "auto",
                    "tooltip": "Target device for future injection (currently unused)."
                }),
                "normalize_embed": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If true, L2-normalize pooled vision embedding (useful for identity embeddings)."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    def on_exec(self, **kwargs: Dict[str, Any]):
        node_id = kwargs.get("node_id")
        model = normalize_list_to_value(kwargs.get("model"))
        ipadapter_obj = normalize_list_to_value(kwargs.get("ipadapter"))
        image = kwargs.get("image")  # Expect tensor [B,H,W,C] float 0..1
        clip_vision = normalize_list_to_value(kwargs.get("clip_vision"))
        pool_mode = normalize_list_to_value(kwargs.get("pool_mode", "mean"))
        strength = float(kwargs.get("strength", 0.8))
        start_percent = float(kwargs.get("start_percent", 0.0))
        end_percent = float(kwargs.get("end_percent", 1.0))
        normalize_embed = bool(kwargs.get("normalize_embed", False))

        lines = []
        # Stage 1: plan
        lines.append("- 🚦 Starting IPAdapter apply")
        lines.append(f"- 💪 Requested strength: {strength}")
        lines.append(f"- ⏱️ Window: {start_percent:.2f} → {end_percent:.2f}")
        _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)
        try:
            # Early exit: no-op if strength or end_percent are zero
            if strength <= 0.0 or end_percent <= 0.0:
                reason = "strength<=0" if strength <= 0.0 else "end_percent<=0"
                lines.append(f"- ⏹️ Skipping attach: {reason}; model left untouched")
                _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)
                return (model, ipadapter_obj)
            if model is None:
                raise ValueError("Model input is required.")
            if not isinstance(ipadapter_obj, dict) or ipadapter_obj.get("type") != "ipadapter_weights":
                raise TypeError("'ipadapter' input must be the object returned by LF_LoadIPAdapterModel.")

            # Attach metadata onto model for future use by custom samplers / patches.
            attached_list = getattr(model, "lf_ipadapters", [])
            record = {
                "path": ipadapter_obj.get("path"),
                "filename": ipadapter_obj.get("filename"),
                "strength": strength,
                "start_percent": start_percent,
                "end_percent": end_percent,
                "loaded": ipadapter_obj.get("loaded"),
            }
            record["state_dict"] = ipadapter_obj.get("state_dict")
            parsed_cache = ipadapter_obj.get("parsed")
            if parsed_cache:
                record["parsed"] = dict(parsed_cache)
            parsed_meta_cache = ipadapter_obj.get("parsed_meta")
            if parsed_meta_cache:
                record["parsed_meta"] = dict(parsed_meta_cache)

            # Vision feature extraction MVP (robust version)
            vision_pooled = None
            encoded = None
            if clip_vision is not None:
                encode_fn = None
                try:
                    encode_fn = resolve_encode_fn(clip_vision)
                except Exception:
                    encode_fn = None
                if encode_fn is not None:
                    if image is None:
                        raise ValueError("Image input is required when providing a CLIP-Vision model handle.")
                    if not torch.is_tensor(image):
                        raise TypeError("image must be a torch tensor in ComfyUI format.")
                    encoded = encode_fn(image)
                else:
                    encoded = clip_vision
            if encoded is None:
                if image is not None and clip_vision is None:
                    lines.append("- ℹ️ Provide a CLIP-Vision model or precomputed features to extract vision tokens")
                else:
                    lines.append("- ℹ️ No vision features supplied")
            else:
                try:
                    if isinstance(encoded, dict):
                        encoded = SimpleNamespace(**encoded)
                    pooled, token_feats = extract_vision_features(encoded)
                    if pooled is None and token_feats is not None:
                        pooled = pool_vision_features(token_feats, mode=pool_mode)
                    if pooled is None:
                        raise RuntimeError("No pooled or token features obtained from vision encoder.")
                    pooled = maybe_unsqueeze_batch(pooled)
                    if normalize_embed:
                        pooled = l2_normalize(pooled)
                        lines.append("- 🔄 L2-normalized vision embedding")
                    vision_pooled = pooled
                    record["vision_pooled"] = pooled
                    record["vision_pooled_dim"] = pooled.shape[-1]
                    if token_feats is not None:
                        record["vision_tokens_shape"] = tuple(token_feats.shape)
                    lines.append(f"- 👁️ Vision pooled features shape: {tuple(pooled.shape)} mode={pool_mode}")
                    if pool_mode == "mean":
                        lines.append("> mean pooling averages all vision tokens → smoother, more generalized style/content embedding.")
                        lines.append("> switch to 'cls' to use only the first (CLS) token if your vision model provides a strong global summary token.")
                    elif pool_mode == "cls":
                        lines.append("> cls pooling uses the first token only → can preserve sharper identity cues but may drop fine style nuances.")
                except Exception as ve:  # pragma: no cover
                    lines.append(f"- ⚠️ Vision feature extraction failed: {ve}")
            # Stage 2: after feature extraction attempt
            _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)

            # Parse weights (placeholder identity) if loaded
            try:
                parse_adapter_weights(record)
            except Exception as pe:  # pragma: no cover
                lines.append(f"- ⚠️ Weight parse skipped: {pe}")

            attached_list, _ = attach_adapter(model, record)

            lines.append(f"- 🔗 Attached IPAdapter `{record['filename']}` to model")
            # Parsed meta logging (after potential parse)
            pmeta = record.get("parsed_meta") or record.get("parsed") or {}
            lines.extend(format_parsed_meta_lines(pmeta))
            lines.append(f"- 💪 Strength: {strength}")
            lines.append(
                "> strength scales the influence of adapter tokens linearly right now; higher values push generation closer to the reference embedding."
            )
            lines.append(f"- 🕒 Schedule: {start_percent:.2f} → {end_percent:.2f}")
            lines.append(
                "> schedule controls which diffusion step range the adapter is active: earlier (near 0) shapes global layout; later (near 1) refines fine details."
            )
            lines.append(
                "> narrow ranges (e.g., 0.0→0.4) focus on coarse composition; late ranges (e.g., 0.6→1.0) bias detail/texture without restructuring."
            )
            # Sequence length / token accounting (MVP: one token per active adapter)
            try:
                active_with_feats = [a for a in getattr(model, "lf_ipadapters", []) if a.get("vision_pooled") is not None]
                if active_with_feats:
                    lines.append(f"- 🧮 Active adapters with tokens: {len(active_with_feats)} (adds {len(active_with_feats)} token(s) to context)")
                    if len(active_with_feats) > 1:
                        lines.append(
                            "> multiple adapters stack additively: more tokens = longer context = slightly higher VRAM + stronger combined steering."
                        )
                        lines.append(
                            "> consider future scheduling or lower individual strengths when stacking to avoid over-conditioning."
                        )
            except Exception:  # pragma: no cover
                pass
            if not ipadapter_obj.get("loaded"):
                lines.append("- ⚠️ Weights not loaded (metadata-only mode)")
            else:
                lines.append("- ✅ Weights present in memory (injection pending implementation)")
            if vision_pooled is not None:
                lines.append("- ✅ Vision features cached")
                lines.append(
                    "> cached features let repeated renders avoid recomputing CLIP-Vision; change the reference image to refresh."
                )

            # (Auto) Build / refresh attn1 patch immediately after updating adapter list.
            try:
                ok, info = ensure_attn1_patch(model)
                if ok:
                    lines.append("- 🧩 attn1_patch injected (concat token strategy)")
                else:
                    lines.append(f"- ℹ️ {info}")
            except Exception as inj_e:  # pragma: no cover
                lines.append(f"- ⚠️ Injection failed: {inj_e}")
            # Stage 3: after injection attempt
            _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)
        except Exception as e:  # pragma: no cover
            lines.append(f"- ❌ Error applying IPAdapter: {e}")
            lines.append("```)\n" + traceback.format_exc() + "```")
            _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)
            raise

        _send_log("applyipadapter", node_id, "Apply IPAdapter", lines)
        
        return (model, ipadapter_obj)
# endregion


# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ApplyIPAdapter": LF_ApplyIPAdapter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ApplyIPAdapter": "Apply IPAdapter",
}
# endregion
