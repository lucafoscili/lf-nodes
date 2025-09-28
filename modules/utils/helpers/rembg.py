"""Compatibility shim re-exporting rembg session helpers."""

from __future__ import annotations

from .detection.rembg import get_rembg_session

__all__ = ["get_rembg_session"]
