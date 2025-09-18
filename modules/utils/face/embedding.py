import hashlib
import math
import torch
import numpy as np

from typing import Any, Dict, Optional, List, Tuple

_EMBED_VERSION = 2  # bump when cache/meta logic changes

_ENGINE: Dict[str, Any] = {}
_CACHE: Dict[str, Dict[str, Any]] = {}

try:
    import insightface
    from insightface.app import FaceAnalysis
    _HAS_INSIGHTFACE = True
except Exception:
    _HAS_INSIGHTFACE = False
    FaceAnalysis = None


def _tensor_image_hash(image: torch.Tensor) -> str:
    with torch.no_grad():
        # Downsample to fixed small size for deterministic hashing to avoid huge mem copy.
        if image.dim() == 4:  # [B,H,W,C] we hash only first sample for cache key
            sample = image[0]
        else:
            sample = image
        # Convert to bytes (quantize to uint8 0-255 for stability)
        arr = (sample.clamp(0, 1) * 255).to(torch.uint8).cpu().numpy()
        h = hashlib.sha256(arr.tobytes()).hexdigest()
        return h


def _load_engine(name: str = "buffalo_l", det_size: Tuple[int, int] = (640, 640)) -> Any:
    if not _HAS_INSIGHTFACE:
        return None
    # Provider auto-selection via insightface (ONNX runtime picks best available)
    key = f"{name}|{det_size}"
    if key in _ENGINE:
        return _ENGINE[key]
    app = FaceAnalysis(name=name)
    # prepare sets ctx_id automatically when GPU available (ctx_id=0) else CPU
    app.prepare(ctx_id=0 if torch.cuda.is_available() else -1, det_size=det_size)
    _ENGINE[key] = app
    return app


def _select_face(faces: List[Any], selection: str) -> Optional[Any]:
    if not faces:
        return None
    if selection.startswith("index:"):
        try:
            idx = int(selection.split(":", 1)[1])
        except ValueError:
            idx = 0
        return faces[idx] if 0 <= idx < len(faces) else faces[0]
    if selection == "largest":
        return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    if selection == "best_quality":
        # heuristic: area * det_score (when available)
        return max(faces, key=lambda f: ((f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])) * getattr(f, 'det_score', 1.0))
    return faces[0]


def _face_to_embedding(face: Any) -> torch.Tensor:
    # insightface Face object has .normed_embedding (already L2)
    emb = getattr(face, "normed_embedding", None)
    if emb is None:
        raw = getattr(face, "embedding", None)
        if raw is None:
            raise RuntimeError("Face object missing embedding")
        emb = raw / (raw.norm() + 1e-6)
    if isinstance(emb, torch.Tensor):
        t = emb.float()
    else:
        import numpy as np  # local import
        t = torch.from_numpy(emb).float()
    if t.ndim == 1:
        t = t.unsqueeze(0)
    # ArcFace embeddings typically 512-d already
    if t.shape[-1] != 512:
        if t.shape[-1] > 512:
            t = t[..., :512]
        else:
            t = torch.nn.functional.pad(t, (0, 512 - t.shape[-1]))
    # Ensure L2
    t = t / (t.norm(dim=-1, keepdim=True) + 1e-6)
    return t


def _placeholder_embedding(image: torch.Tensor) -> torch.Tensor:
    pseudo = image.mean(dim=[1, 2])  # [B,C]
    emb = pseudo / (pseudo.norm(dim=-1, keepdim=True) + 1e-6)
    emb = emb[:, :512] if emb.shape[-1] >= 512 else torch.nn.functional.pad(emb, (0, 512 - emb.shape[-1]))
    return emb


def extract_face_embedding(
    image: torch.Tensor,
    selection: str = "largest",
    mode: str = "insightface",
    cache: bool = True,
    debug: bool = False,
    det_size: Optional[Tuple[int, int]] = (640, 640),
    det_thresh: float = 0.45,
    robust: bool = True,
) -> Dict[str, Any]:
    """Return a dict containing identity embedding + metadata.

    If insightface available uses RetinaFace+ArcFace pipeline, else placeholder.
    Cache keyed on image hash + model parameters for speed.
    """
    if not torch.is_tensor(image):
        raise TypeError("image must be a torch tensor")
    if image.dim() != 4:
        raise ValueError("image must be [B,H,W,C]")

    key = None
    if cache:
        key = _tensor_image_hash(image) + f"|v{_EMBED_VERSION}|{mode}|{selection}|{int(debug)}|{('auto' if det_size is None else det_size[0])}|{det_thresh:.2f}|{int(robust)}"
        if key in _CACHE:
            return _CACHE[key]

    # Placeholder-only modes (future: clip_vision etc.)
    if mode == "clip_vision":
        # TODO: implement CLIP-based identity embedding; for now placeholder
        emb = _placeholder_embedding(image)
        result = {"embedding": emb, "meta": {"backend": "clip_vision_placeholder", "faces_detected": 0, "selection": selection, "embedding_dim": emb.shape[-1], "cached": False}}
        if key: _CACHE[key] = result
        return result

    if mode == "auto":
        mode = "insightface" if _HAS_INSIGHTFACE else "placeholder"

    if mode == "insightface" and not _HAS_INSIGHTFACE:
        mode = "placeholder"

    if mode == "placeholder":
        emb = _placeholder_embedding(image)
        result = {
            "embedding": emb,
            "meta": {
                "source_hash": _tensor_image_hash(image),
                "faces_detected": 1,
                "selection": selection,
                "backend": "placeholder",
                "embedding_dim": emb.shape[-1],
                "cached": False,
                "detection_status": "library_missing" if not _HAS_INSIGHTFACE else "placeholder_mode",
            },
        }
        if key:
            _CACHE[key] = result
        return result

    # At this point mode should be insightface
    model_name = "buffalo_l"
    # clamp provided det_size into reasonable range
    auto_sizes: List[int] = []
    if det_size is None:  # auto mode: prefer mid-range first
        auto_sizes = [512, 640, 800, 320]
    else:
        ds0 = max(160, min(1536, int(det_size[0])))
        det_size = (ds0, ds0)
        auto_sizes = [det_size[0]]

    engine: Optional[Any] = None
    current_size = None
    engine_cache: Dict[int, Any] = {}

    # Convert image tensor [B,H,W,C] in 0..1 to uint8 BGR for engine (expects numpy)
    # We only use first frame for identity (consistent with most pipelines)
    sample = image[0]
    if sample.shape[-1] == 4:  # drop alpha if present
        sample = sample[..., :3]
    np_img = (sample.clamp(0,1)*255).byte().cpu().numpy()
    # Engine expects BGR (input tensor assumed RGB)
    np_img = np_img[..., ::-1]
    np_img = np.ascontiguousarray(np_img)

    attempts: List[Dict[str, Any]] = []
    faces: List[Any] = []
    faced_get_error: Optional[str] = None

    # Define attempt configurations
    primary_cfg = {"det_thresh": det_thresh, "bgr": True, "scale": 1.0, "note": "primary"}
    fallback_cfgs: List[Dict[str, Any]] = []
    if robust:
        # Lower threshold
        fallback_cfgs.append({"det_thresh": max(0.05, det_thresh - 0.15), "bgr": True, "scale": 1.0, "note": "lower_thresh"})
        # Upscale (only if original smaller than target upscale)
        fallback_cfgs.append({"det_thresh": det_thresh, "bgr": True, "scale": 1.25, "note": "upscale_1.25"})
        fallback_cfgs.append({"det_thresh": det_thresh, "bgr": True, "scale": 1.5, "note": "upscale_1.5"})
        # Try without BGR swap (in case upstream already BGR) at lowered threshold
        fallback_cfgs.append({"det_thresh": max(0.05, det_thresh - 0.20), "bgr": False, "scale": 1.0, "note": "no_bgr_swap"})
    all_cfgs = [primary_cfg] + fallback_cfgs

    selected = None
    used_cfg: Optional[Dict[str, Any]] = None
    for cfg in all_cfgs:
        try:
            work = np_img
            if cfg["scale"] != 1.0:
                # simple nearest upscale to preserve speed
                new_h = int(work.shape[0]*cfg["scale"]) ; new_w = int(work.shape[1]*cfg["scale"])
                work = np.array(torch.nn.functional.interpolate(torch.from_numpy(work).permute(2,0,1).unsqueeze(0).float(), size=(new_h,new_w), mode='bilinear', align_corners=False).byte()[0].permute(1,2,0).numpy())
            work_input = work if cfg["bgr"] else work[..., ::-1]
            # Iterate through size candidates until face found (outer selection)
            faces = []
            for size_candidate in auto_sizes:
                current_size = size_candidate
                if size_candidate not in engine_cache:
                    engine_cache[size_candidate] = _load_engine(model_name, det_size=(size_candidate, size_candidate))
                engine = engine_cache[size_candidate]
                if engine is None:
                    continue
                if 'detection' in engine.models:
                    try:
                        engine.models['detection'].threshold = cfg['det_thresh']
                    except Exception:
                        pass
                try:
                    faces = engine.get(work_input)
                except Exception as ie:  # pragma: no cover
                    faced_get_error = str(ie)
                    faces = []
                faces_sorted = sorted(faces, key=lambda f: getattr(f, 'det_score', 0.0), reverse=True)
                selected = _select_face(faces_sorted, selection) if faces_sorted else None
                attempts.append({
                    "note": cfg["note"],
                    "faces": len(faces_sorted),
                    "top_score": float(getattr(faces_sorted[0], 'det_score', 0.0)) if faces_sorted else 0.0,
                    "used_thresh": cfg['det_thresh'],
                    "scale": cfg['scale'],
                    "bgr": cfg['bgr'],
                    "det_size": size_candidate,
                })
                if selected is not None:
                    used_cfg = {**cfg, "det_size": size_candidate}
                    break
            if selected is not None:
                break
        except Exception as ge:  # pragma: no cover
            faced_get_error = str(ge)
            attempts.append({"note": cfg["note"], "error": faced_get_error})

    if selected is None:
        emb = _placeholder_embedding(image)
        # Build compact attempt summary: list of unique size -> best score
        attempt_summary: Dict[int, float] = {}
        for a in attempts:
            if 'det_size' in a:
                prev = attempt_summary.get(a['det_size'], 0.0)
                attempt_summary[a['det_size']] = max(prev, float(a.get('top_score', 0.0)))
        compacts = [f"{sz}:{attempt_summary[sz]:.2f}" for sz in sorted(attempt_summary.keys())]
        meta_fail: Dict[str, Any] = {
            "backend": "placeholder",
            "faces_detected": 0,
            "detection_status": "no_face",
            "attempt_summary": compacts,
            "auto_sizes": auto_sizes,
        }
        if debug:
            meta_fail.update({
                "debug_engine_models": list(getattr(engine, 'models', {}).keys()) if engine else [],
                "debug_engine_available": engine is not None,
                "debug_attempts": attempts,
                "debug_get_error": faced_get_error,
                "image_mean": float(sample.mean().item()),
                "image_std": float(sample.std().item()),
                "image_min": float(sample.min().item()),
                "image_max": float(sample.max().item()),
                "color_space": "BGR",
            })
        result = {"embedding": emb, "meta": meta_fail}
        if key:
            _CACHE[key] = result
        return result

    emb = _face_to_embedding(selected)
    meta = {
        "source_hash": _tensor_image_hash(image),
        "faces_detected": len(faces),
        "selection": selection,
        "backend": "insightface",
        "embedding_dim": emb.shape[-1],
        "model_name": model_name,
        "det_size": used_cfg.get('det_size') if used_cfg else (det_size[0] if det_size else None),
        "cached": False,
        "det_score": float(getattr(selected, 'det_score', 0.0)),
        "detection_status": "ok",
    }
    if debug:
        meta.update({
            "debug_engine_models": list(getattr(engine, 'models', {}).keys()),
            "debug_engine_available": engine is not None,
            "debug_face_scores": [float(getattr(f, 'det_score', 0.0)) for f in faces],
            "debug_attempts": attempts,
            "debug_used_attempt": used_cfg.get('note') if used_cfg else None,
            "image_mean": float(sample.mean().item()),
            "image_std": float(sample.std().item()),
            "image_min": float(sample.min().item()),
            "image_max": float(sample.max().item()),
            "color_space": "BGR",
        })
    result = {"embedding": emb, "meta": meta}
    if key:
        meta["cached"] = True
        _CACHE[key] = result
    return result

__all__ = ["extract_face_embedding"]
