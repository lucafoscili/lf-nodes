import traceback
from typing import Any, Dict

import torch

from . import CATEGORY
from ...utils.ipadapter.constants import CURVE_CHOICES, STRATEGY_CHOICES, PRESET_CHOICES, IPADAPTER_PRESETS
from ...utils.constants import FUNCTION, Input
from ...utils.helpers import normalize_list_to_value
from ...utils.ipadapter.runtime import parse_adapter_weights
from ...utils.ipadapter.common import l2_normalize
from ...utils.ipadapter.helpers import (
    attach_adapter,
    ensure_attn1_patch,
    format_parsed_meta_lines,
    send_node_log,
    choose_strategy,
)

# region LF_ApplyFaceIDIPAdapter
class LF_ApplyFaceIDIPAdapter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (Input.MODEL, {
                    "tooltip": "Diffusion model to modify."
                }),
                "ipadapter": (Input.IPADAPTER, {
                    "tooltip": "IPAdapter to apply."
                }),
                "strength": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 3.0,
                    "step": 0.05,
                    "tooltip": "Identity influence strength."
                }),
                "face_embed": (Input.FACE_EMBED, {
                    "tooltip": "Precomputed face embedding. Accepts a list of embeddings for different angles."
                }),
            },
            "optional": {
                "preset": (PRESET_CHOICES, {
                    "default": "balanced",
                    "tooltip": "Quick profiles that adjust strategy, schedule and clamp. Choose 'custom' to use manual settings."
                }),
                "face_meta": (Input.FACE_META, {
                    "tooltip": "Metadata output from Extract Face Embedding node (for validation/logging)."
                }),
                "require_real": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Fail if embedding backend is placeholder."
                }),
                "allow_no_face": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If no face detected (detection_status=no_face) skip attaching instead of raising error."
                }),
                "start_percent": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 0.99,
                    "step": 0.01
                }),
                "end_percent": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.01,
                    "max": 1.0,
                    "step": 0.01
                }),
                "strategy": (STRATEGY_CHOICES, {
                    "default": "auto",
                    "tooltip": "Fusion strategy; auto selects best supported."
                }),
                "schedule_curve": (CURVE_CHOICES, {
                    "default": "linear",
                    "tooltip": "Strength shaping curve across schedule window."
                }),
                "kv_norm_clip": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.05,
                    "tooltip": "Clamp norm of projected residuals (kv_bias_residual). 0=disabled."
                }),
                "device": (Input.STRING, {
                    "default": "auto",
                    "tooltip": "(Reserved)."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("MODEL", "IPADAPTER")
    RETURN_NAMES = ("model", "ipadapter")

    def on_exec(self, **kwargs: Dict[str, Any]):
        node_id = kwargs.get("node_id")
        model = normalize_list_to_value(kwargs.get("model"))
        ipadapter_obj = normalize_list_to_value(kwargs.get("ipadapter"))
        face_embed_input = kwargs.get("face_embed")

        def _unwrap_face_embed(value):
            if isinstance(value, (list, tuple)):
                if len(value) == 1:
                    return _unwrap_face_embed(value[0])
                return list(value)
            return value

        face_embed = _unwrap_face_embed(face_embed_input)  # required tensor or list of tensors
        face_meta = normalize_list_to_value(kwargs.get("face_meta")) or {}
        require_real = normalize_list_to_value(bool(kwargs.get("require_real", True)))
        allow_no_face = normalize_list_to_value(bool(kwargs.get("allow_no_face", False)))
        strength = normalize_list_to_value(float(kwargs.get("strength", 1.0)))
        start_percent = normalize_list_to_value(float(kwargs.get("start_percent", 0.0)))
        end_percent = normalize_list_to_value(float(kwargs.get("end_percent", 1.0)))
        preset = normalize_list_to_value(kwargs.get("preset", "balanced")) or "balanced"
        user_strategy = normalize_list_to_value(kwargs.get("strategy", "auto")) or "auto"
        schedule_curve = normalize_list_to_value(kwargs.get("schedule_curve", "linear")) or "linear"
        kv_norm_clip = normalize_list_to_value(float(kwargs.get("kv_norm_clip", 0.0)))

        lines: list[str] = []
        # Stage 1: announce plan
        lines.append("## 🚦 Starting FaceID IPAdapter apply\n")
        lines.append(f"- 💪 Strength: {strength}")
        lines.append(f"- ⏱️ Window: {start_percent:.2f} → {end_percent:.2f}")
        lines.append(f"- 🧭 Preset: {preset} | strategy: {user_strategy} | curve: {schedule_curve} | clamp: {kv_norm_clip}")
        send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)
        try:
            # Early exit: no-op if strength or end_percent are zero
            if strength <= 0.0 or end_percent <= 0.0:
                reason = "strength<=0" if strength <= 0.0 else "end_percent<=0"
                lines.append(f"- ⏹️ Skipping attach: {reason}; model left untouched")
                send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)
                return (model, ipadapter_obj)
            # Apply preset defaults (non-destructive): when preset != custom, seed defaults first,
            # then honor explicit user overrides from inputs above.
            if preset != "custom":
                p = IPADAPTER_PRESETS.get(preset, {})
                # Seed values only when user left them at defaults
                # Strength: only update if user didn't change from default 1.0
                if float(kwargs.get("strength", 1.0)) == 1.0 and "strength" in p:
                    strength = float(p["strength"])  # noqa: F821 (strength defined earlier)
                # Window
                if float(kwargs.get("start_percent", 0.0)) == 0.0 and "start_percent" in p:
                    start_percent = float(p["start_percent"])  # noqa: F821
                if float(kwargs.get("end_percent", 1.0)) == 1.0 and "end_percent" in p:
                    end_percent = float(p["end_percent"])  # noqa: F821
                # Curve
                if normalize_list_to_value(kwargs.get("schedule_curve", "linear")) == "linear" and "schedule_curve" in p:
                    schedule_curve = p["schedule_curve"]
                # Clamp
                if float(kwargs.get("kv_norm_clip", 0.0)) == 0.0 and "kv_norm_clip" in p:
                    kv_norm_clip = float(p["kv_norm_clip"])  # noqa: F821
                # Strategy (only seed if user kept 'auto')
                if user_strategy == "auto" and "strategy" in p:
                    user_strategy = p["strategy"]

            if model is None:
                raise ValueError("Model input is required.")
            if not isinstance(ipadapter_obj, dict) or ipadapter_obj.get("type") != "ipadapter_weights":
                raise TypeError("'ipadapter' input must be the object returned by LF_LoadIPAdapterModel.")

            attached_list = getattr(model, "lf_ipadapters", [])
            base_record = {
                "path": ipadapter_obj.get("path"),
                "filename": ipadapter_obj.get("filename"),
                "strength": strength,
                "start_percent": start_percent,
                "end_percent": end_percent,
                "loaded": ipadapter_obj.get("loaded"),
                "variant_hint": "faceid",
                # strategy decided below (auto -> best capability)
                "strategy": "add_kv",  # provisional; may override
                "schedule_curve": schedule_curve,
                "kv_norm_clip": kv_norm_clip,
            }
            base_record["state_dict"] = ipadapter_obj.get("state_dict")
            parsed_cache = ipadapter_obj.get("parsed")
            if parsed_cache:
                base_record["parsed"] = dict(parsed_cache)
            parsed_meta_cache = ipadapter_obj.get("parsed_meta")
            if parsed_meta_cache:
                base_record["parsed_meta"] = dict(parsed_meta_cache)
            backend = face_meta.get("backend") if isinstance(face_meta, dict) else None
            detection_status = face_meta.get("detection_status") if isinstance(face_meta, dict) else None
            if backend:
                lines.append(f"- 🧬 Identity backend: {backend} status={detection_status}")
            if backend:
                # Graceful skip path: if no face detected and user allows skipping, exit early.
                if backend == "placeholder" and face_meta.get("detection_status") == "no_face" and allow_no_face:
                    lines.append("- 🚫 No face detected; skipping adapter attach (allow_no_face=True)")
                    send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)
                    return (model, ipadapter_obj)
                if require_real and backend != "insightface":
                    raise ValueError(f"Real embedding required but backend={backend}")

            if face_embed is None:
                raise ValueError("face_embed is required; use LF_ExtractFaceEmbedding upstream.")
            # Support chaining/list of embeddings: accept 1D [C], 2D [B,C], or list/tuple of 1D tensors
            embeds_list = []
            if torch.is_tensor(face_embed):
                if face_embed.dim() == 1:
                    embeds_list = [face_embed.unsqueeze(0)]
                elif face_embed.dim() == 2:
                    embeds_list = [face_embed]
                else:
                    raise TypeError("face_embed must be 1D or 2D tensor or list of 1D tensors")
            elif isinstance(face_embed, (list, tuple)):
                # filter tensors and stack as batch
                tensors = [t for t in face_embed if torch.is_tensor(t)]
                if not tensors:
                    raise TypeError("face_embed list must contain torch tensors")
                tensors = [t.unsqueeze(0) if t.dim() == 1 else t for t in tensors]
                # ensure all are 2D [1,C] or [B,C]; concatenate along batch
                embeds_list = [torch.cat(tensors, dim=0)]
            else:
                raise TypeError("Unsupported face_embed type")

            total_emb = sum(e.shape[0] for e in embeds_list)
            lines.append(f"- 👤 Face embeddings batch count={total_emb}")

            # For each embedding in batch, attach a separate adapter record to enable chaining
            for batch_embeds in embeds_list:
                vision_pooled = l2_normalize(batch_embeds)
                emb_norm = float((batch_embeds.norm(dim=-1) / max(batch_embeds.shape[-1], 1)).mean().item())
                lines.append(f"  • normalized batch: shape={tuple(vision_pooled.shape)} dim={vision_pooled.shape[-1]} avg(norm/len)≈{emb_norm:.4f}")
                for i in range(vision_pooled.shape[0]):
                    record = dict(base_record)
                    record["vision_pooled"] = vision_pooled[i]
                    record["vision_pooled_dim"] = vision_pooled.shape[-1]
                    # Parse weights (once is enough; harmless if repeated)
                    try:
                        parse_adapter_weights(record)
                    except Exception as pe:  # pragma: no cover
                        lines.append(f"- ⚠️ Weight parse skipped: {pe}")
                    attached_list, _ = attach_adapter(model, record)

            # Stage 2: after parse (if any)
            # Use last attached record (if any) for metadata preview
            last = attached_list[-1] if attached_list else base_record
            pmeta_stage = last.get("parsed_meta") or last.get("parsed") or {}
            if pmeta_stage:
                lines.append("- 🧩 Weights parsed; capabilities detected")
            send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)

            # Deduping
            # Strategy decision based on last record for capability awareness
            record_ref = attached_list[-1] if attached_list else base_record

            # Decide strategy if user requested auto
            chosen_strategy, fallback_reason = choose_strategy(record_ref, user_strategy)
            record_ref["strategy"] = chosen_strategy

            # Parsed meta logging (after potential parse)
            pmeta = record_ref.get("parsed_meta") or record_ref.get("parsed") or {}
            lines.extend(format_parsed_meta_lines(pmeta))

            lines.append(f"- 🧪 Strategy: {record_ref['strategy']} (requested={user_strategy})")
            if fallback_reason:
                lines.append(f"   • fallback: {fallback_reason}")
            if schedule_curve != 'linear':
                lines.append(f"- 📈 Schedule curve: {schedule_curve}")
            if record_ref['strategy'] == 'kv_bias_residual' and kv_norm_clip > 0:
                lines.append(f"- 🧷 Norm clamp: {kv_norm_clip}")
            # Stage 3: strategy decided
            send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)

            lines.append(f"- 🔗 Attached FaceID IPAdapter `{base_record['filename']}` x{len(attached_list)}")
            lines.append(f"- 💪 Strength: {strength}")
            lines.append(f"- 🕒 Schedule: {start_percent:.2f} → {end_percent:.2f}")
            if detection_status:
                lines.append(f"- 🧪 Detection status upstream: {detection_status}")
            if not ipadapter_obj.get("loaded"):
                lines.append("- ⚠️ Weights not loaded (metadata only)")
            else:
                lines.append("- ✅ Weights loaded")
            lines.append("- ✅ Identity embedding(s) prepared")

            # Patch injection (add_kv strategy preferred when projector or fallback linear present)
            try:
                ok, info = ensure_attn1_patch(model)
                lines.append(f"- 🧩 {info}" if ok else f"- ℹ️ {info}")
            except Exception as inj_e:  # pragma: no cover
                lines.append(f"- ⚠️ Injection failed: {inj_e}")
            # Stage 4: after injection attempt
            send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)
        except Exception as e:  # pragma: no cover
            lines.append(f"- ❌ Error applying FaceID IPAdapter: {e}")
            lines.append("```\n" + traceback.format_exc() + "```")
            send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)
            raise

        send_node_log("applyfaceidipadapter", node_id, "Apply FaceID IPAdapter", lines)

        return (model, ipadapter_obj)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ApplyFaceIDIPAdapter": LF_ApplyFaceIDIPAdapter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ApplyFaceIDIPAdapter": "Apply FaceID IPAdapter",
}
# endregion
