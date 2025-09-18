import traceback
from typing import Any, Dict

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers import normalize_list_to_value
from ...utils.face.embedding import extract_face_embedding
from ...utils.helpers import resize_image
from ...utils.ipadapter.helpers import send_node_log

# region LF_ExtractFaceEmbedding
class LF_ExtractFaceEmbedding:
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("FACE_EMBED", "FACE_META")
    RETURN_NAMES = ("face_embed", "meta")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Reference image containing a face."
                }),
            },
            "optional": {
                "mode": (Input.STRING, {
                    "default": "auto",
                    "tooltip": "Embedding mode: auto | insightface | clip_vision | placeholder"
                }),
                "selection": (Input.STRING, {
                    "default": "largest",
                    "tooltip": "Face selection strategy",
                    "choices": ["largest", "best_quality", "index:0", "index:1", "index:2"]
                }),
                "cache": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Cache embedding per image & parameters."
                }),
                "auto_resize": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Resize longest side to 640 for stable detection speed."
                }),
                "debug": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Enable verbose detection diagnostics (slower)."
                }),
                "det_size": (Input.STRING, {
                    "default": "auto",
                    "choices": ["auto","320","512","640","800"],
                    "tooltip": "Auto tries multiple sizes until a face is found; manual size for speed."
                }),
                "det_thresh": (Input.FLOAT, {
                    "default": 0.45,
                    "min": 0.05,
                    "max": 0.95,
                    "step": 0.01,
                    "tooltip": "Face detection confidence threshold."
                }),
                "robust": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Try fallback strategies if initial detection fails (multi-threshold / upscale / alt color)."
                }),
                "force_refresh": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Bypass embedding cache for this run."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    def on_exec(self, **kwargs: Dict[str, Any]):
        node_id = kwargs.get("node_id")
        image = kwargs.get("image")
        selection = normalize_list_to_value(kwargs.get("selection", "largest")) or "largest"
        mode = normalize_list_to_value(kwargs.get("mode", "auto")) or "auto"
        cache = bool(kwargs.get("cache", True))
        auto_resize = bool(kwargs.get("auto_resize", True))
        debug = bool(kwargs.get("debug", False))
        force_refresh = bool(kwargs.get("force_refresh", False))
        det_size_opt = normalize_list_to_value(kwargs.get("det_size", "640")) or "640"
        if det_size_opt == "auto":
            det_side = None  # sentinel for auto mode
        else:
            try:
                det_side = int(det_size_opt)
            except ValueError:
                det_side = 640
        det_thresh = float(kwargs.get("det_thresh", 0.45))
        robust = bool(kwargs.get("robust", True))

        lines: list[str] = []
        # Stage 1: plan
        lines.append("- 🚦 Starting face embedding extraction")
        lines.append(f"- 🧪 Selection: {selection} | mode: {mode}")
        lines.append(f"- 🔧 det_size={det_side if det_size_opt!='auto' else 'auto'} thresh={det_thresh:.2f} robust={robust}")
        send_node_log("extractfaceembedding", node_id, "Extract Face Embedding", lines)

        try:
            if not torch.is_tensor(image):
                raise TypeError("image must be a tensor")
            if auto_resize and torch.is_tensor(image) and image.dim() == 4:
                _, h, w, _ = image.shape
                if max(h, w) != 640:
                    orig_h, orig_w = h, w
                    try:
                        image = resize_image(image, "bicubic", True, 640)
                        _, nh, nw, _ = image.shape
                        lines.append(f"- ✂️ Auto-resized input {orig_h}x{orig_w} -> {nh}x{nw}")
                    except Exception as re:
                        lines.append(f"- ⚠️ Auto-resize failed: {re}")
                # Stage 2: after potential auto-resize
                send_node_log("extractfaceembedding", node_id, "Extract Face Embedding", lines)

            data = extract_face_embedding(
                image,
                selection=selection,
                mode=mode,
                cache=False if force_refresh else cache,
                debug=debug,
                det_size=(det_side, det_side) if isinstance(det_side, int) else None,
                det_thresh=det_thresh,
                robust=robust,
            )
            emb = data["embedding"]  # [B,512]
            meta = data["meta"]
            lines.append(f"- 📐 Embedding shape: {tuple(emb.shape)} backend={meta.get('backend')}")
            lines.append(f"- 🧪 Selection: {selection} | faces_detected={meta.get('faces_detected')}")
            lines.append(f"- 🔧 det_size={det_side if det_side is not None else 'auto'} thresh={det_thresh:.2f} robust={robust}")
            if 'det_score' in meta and isinstance(meta.get('det_score'), (int, float)):
                lines.append(f"- 🎯 Det score: {meta['det_score']:.3f}")
            if meta.get('backend') == 'insightface':
                lines.append(f"- ⚙️ Engine: {meta.get('model_name','-')} det_size={meta.get('det_size','-')}")
            if meta.get('cached'):
                lines.append("- 🗄️ Returned cached embedding")
            if 'detection_status' in meta:
                lines.append(f"- 🧪 Detection status: {meta['detection_status']}")
                if meta.get('detection_status') == 'no_face':
                    if meta.get('attempt_summary'):
                        lines.append(f"- 🧪 Attempt summary (size:score): {', '.join(meta['attempt_summary'])}")
                    if not debug:
                        lines.append("- 💡 Enable debug=True for full attempt breakdown.")
                    lines.append("- 💡 Try det_thresh ↓ (e.g. 0.35) or manual det_size=512 if auto keeps failing.")
                elif meta.get('detection_status') == 'library_missing':
                    lines.append("- ❗ InsightFace not installed or failed to load.")
                if debug and meta.get('detection_status') != 'ok':
                    # Surface additional debug diagnostics
                    if 'debug_face_scores' in meta:
                        lines.append(f"- 🐛 Face scores: {meta.get('debug_face_scores')}")
                    if 'debug_get_error' in meta and meta.get('debug_get_error'):
                        lines.append(f"- 🐛 Engine error: {meta.get('debug_get_error')}")
                    im_mean = meta.get('image_mean', '-')
                    im_std = meta.get('image_std', '-')
                    im_min = meta.get('image_min', '-')
                    im_max = meta.get('image_max', '-')
                    def _fmt_num(x):
                        return f"{x:.4f}" if isinstance(x, (int, float)) else str(x)
                    lines.append(f"- 🐛 Image stats mean={_fmt_num(im_mean)} std={_fmt_num(im_std)} min={_fmt_num(im_min)} max={_fmt_num(im_max)}")
                    lines.append(f"- 🐛 Engine models: {meta.get('debug_engine_models')}")
            if meta.get('backend','').startswith('clip_vision'):
                lines.append("- ⚠️ CLIP vision identity embedding not yet implemented (placeholder).")
            elif meta.get('backend') == 'placeholder':
                lines.append("- ⚠️ Placeholder backend: install insightface (pip install insightface onnxruntime onnxruntime-gpu) for real identity embedding.")

            # Stage 3+: final summary
            send_node_log("extractfaceembedding", node_id, "Extract Face Embedding", lines)
            return (emb, meta)
        except Exception as e:  # pragma: no cover
            lines.append(f"- ❌ Error extracting face embedding: {e}")
            lines.append("```\n" + traceback.format_exc() + "```")
            send_node_log("extractfaceembedding", node_id, "Extract Face Embedding", lines)
            raise
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ExtractFaceEmbedding": LF_ExtractFaceEmbedding,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ExtractFaceEmbedding": "Extract Face Embedding",
}
# endregion