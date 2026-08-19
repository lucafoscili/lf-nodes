"""Strict, side-effect-free parsing for supported YouTube video URLs."""

from __future__ import annotations

import re

from urllib.parse import parse_qsl, urlsplit


_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_SI_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,256}$")
_WATCH_HOSTS = frozenset({"youtube.com", "www.youtube.com", "m.youtube.com"})


def parse_youtube_video_url(value: object) -> tuple[str, str]:
    """Return ``(video_id, canonical_url)`` for one deliberately narrow URL.

    The optional ``si`` parameter is a YouTube share-tracking token, not part
    of the media identity.  It is accepted only in its safe, standalone form
    and intentionally removed from the URL passed downstream.
    """

    if not isinstance(value, str) or not value.strip():
        raise ValueError("YouTube URL is required")

    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("Use an exact HTTPS YouTube video URL")
    try:
        if parsed.port is not None:
            raise ValueError("YouTube URLs may not specify a port")
    except ValueError as error:
        raise ValueError("Use an exact HTTPS YouTube video URL") from error

    host = (parsed.hostname or "").lower()
    if parsed.query:
        try:
            query = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
        except ValueError as error:
            raise ValueError("YouTube URL query is malformed") from error
    else:
        query = []

    if host in _WATCH_HOSTS:
        if parsed.path != "/watch":
            raise ValueError("Only https://www.youtube.com/watch?v=<video-id> is allowed")
        video_values = [item_value for item_name, item_value in query if item_name == "v"]
        si_values = [item_value for item_name, item_value in query if item_name == "si"]
        if (
            len(video_values) != 1
            or len(si_values) > 1
            or len(query) != len(video_values) + len(si_values)
        ):
            raise ValueError("Only a video id and optional YouTube share token are allowed")
        video_id = video_values[0]
    elif host == "youtu.be":
        if parsed.path.count("/") != 1:
            raise ValueError("Only https://youtu.be/<video-id> is allowed")
        si_values = [item_value for item_name, item_value in query if item_name == "si"]
        if len(si_values) > 1 or len(query) != len(si_values):
            raise ValueError("Only an optional YouTube share token is allowed")
        video_id = parsed.path[1:]
    else:
        raise ValueError("YouTube host is not allowed")

    if not _VIDEO_ID.fullmatch(video_id):
        raise ValueError("YouTube video id must be exactly 11 URL-safe characters")
    if si_values and not _SI_TOKEN.fullmatch(si_values[0]):
        raise ValueError("YouTube share token is invalid")
    return video_id, f"https://www.youtube.com/watch?v={video_id}"
