"""Face selection policies.

A detection is expected to be a dict with keys:
  - box: (x1,y1,x2,y2)
  - score: float
  - quality: float | None
  - area: int
  - idx: int (original order)
"""
from __future__ import annotations
from typing import List, Dict, Optional


def select_face(detections: List[Dict], strategy: str = "largest") -> Optional[Dict]:
    if not detections:
        return None
    strategy = (strategy or "largest").lower()
    if strategy == "largest":
        return max(detections, key=lambda d: d.get("area", 0))
    if strategy == "best_quality":
        return max(detections, key=lambda d: (d.get("quality") or d.get("score") or 0.0))
    if strategy.startswith("index:"):
        try:
            i = int(strategy.split(":", 1)[1])
            return detections[i] if 0 <= i < len(detections) else None
        except Exception:
            return None
    # default fallback
    return detections[0]

__all__ = ["select_face"]
