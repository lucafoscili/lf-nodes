"""Simple quality heuristics for face crops.

Advanced systems may integrate MagFace or SER-FIQ. For now we implement:
  - focus_score: variance of Laplacian (sharpness proxy) if OpenCV available.
  - composite_score: weighted blend of detector confidence and focus.

All functions are safe to call even if optional deps missing (return None / fallbacks).
"""
from __future__ import annotations
from typing import Optional
import math

try:  # optional cv2
    import cv2  # type: ignore
    _HAS_CV2 = True
except Exception:  # pragma: no cover
    _HAS_CV2 = False


def focus_score(image_bgr) -> Optional[float]:  # image as np.ndarray BGR uint8
    if not _HAS_CV2:
        return None
    try:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        val = cv2.Laplacian(gray, cv2.CV_64F).var()
        return float(val)
    except Exception:  # pragma: no cover
        return None


def composite_quality(det_conf: float, focus: Optional[float]) -> float:
    # Normalize focus via log scaling if present; else rely on det_conf only.
    if focus is None or focus <= 0:
        return float(det_conf)
    scaled = math.log1p(focus) / 10.0  # crude normalization
    return float(0.7 * det_conf + 0.3 * scaled)

__all__ = ["focus_score", "composite_quality"]
