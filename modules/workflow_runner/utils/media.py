"""Shared media-type helpers for Workflow Runner artifacts."""

from __future__ import annotations

from typing import Optional


_MEDIA_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "dds": "image/vnd-ms.dds",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "flac": "audio/flac",
    "ogg": "audio/ogg",
    "opus": "audio/opus",
    "glb": "model/gltf-binary",
    "gltf": "model/gltf+json",
    "ply": "application/octet-stream",
    "splat": "application/octet-stream",
    "spz": "application/octet-stream",
    "ksplat": "application/octet-stream",
    "json": "application/json",
    "txt": "text/plain",
}


def media_type_for_filename(filename: str) -> Optional[str]:
    """Return the suite's stable media type for a known artifact filename."""

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return _MEDIA_TYPES.get(extension)


__all__ = ["media_type_for_filename"]
