import hashlib
import json
import os
import shutil
import threading
import time
import uuid

from contextlib import contextmanager
from pathlib import Path

import folder_paths

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.env import bool_env
from ...utils.helpers.comfy import safe_send_sync
from ...utils.youtube_url import parse_youtube_video_url


_PROFILE = {
    "audio_flac": "reference.flac",
    "audio_m4a": "reference.m4a",
    "video_mp4": "reference.mp4",
}
_PROGRESSIVE_MP4_FORMAT = "18"
_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _normalized_resolved_path(path):
    """Return one stable comparison form for a resolved filesystem path.

    Windows may add the extended-length ``\\\\?\\`` prefix when a path becomes
    visible between two concurrent ``resolve`` calls.  The prefix changes only
    the spelling, not the target, so strip it before the containment comparison.
    """

    resolved = os.fspath(Path(path).resolve())
    if os.name == "nt":
        if resolved.startswith("\\\\?\\UNC\\"):
            resolved = "\\\\" + resolved[8:]
        elif resolved.startswith("\\\\?\\"):
            resolved = resolved[4:]
        resolved = os.path.normcase(resolved)
    return os.path.normpath(resolved)


def _contained(root, path):
    try:
        resolved_root = _normalized_resolved_path(root)
        resolved_path = _normalized_resolved_path(path)
        contained = os.path.commonpath((resolved_root, resolved_path)) == resolved_root
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError("YouTube cache path escapes ComfyUI input") from error
    if not contained:
        raise ValueError("YouTube cache path escapes ComfyUI input")


def _cache_root():
    root = Path(folder_paths.get_input_directory()).resolve()
    cache = root / "lf-workflow-runner" / "youtube"
    _contained(root, cache)
    return root, cache


def _lock_for(key):
    with _LOCKS_GUARD:
        return _LOCKS.setdefault(key, threading.Lock())


def _relative_input_path(video_id, media_kind, media_name):
    return (Path("lf-workflow-runner") / "youtube" / video_id / media_kind / media_name).as_posix()


def _try_lock(handle):
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(handle):
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def _cross_process_lock(root, video_dir, media_kind, timeout_seconds=600.0):
    """Bound cache publication to one process without stale-lock deletion."""

    lock_path = video_dir / f".{media_kind}.lock"
    _contained(root, lock_path)
    if lock_path.is_symlink():
        raise ValueError("YouTube cache lock is unsafe")

    deadline = time.monotonic() + timeout_seconds
    with lock_path.open("a+b") as handle:
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(b"\0")
            handle.flush()
        while True:
            try:
                _try_lock(handle)
                break
            except OSError as error:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Timed out waiting for the YouTube cache lock") from error
                time.sleep(0.05)
        try:
            _contained(root, video_dir)
            _contained(root, lock_path)
            if lock_path.is_symlink():
                raise ValueError("YouTube cache lock is unsafe")
            yield
        finally:
            _unlock(handle)


def _receipt(video_id, canonical_url, media_kind, relative_path, media_path):
    if media_path.stat().st_size <= 0:
        raise ValueError("YouTube media file is empty")
    payload = {
        "bytes": media_path.stat().st_size,
        "media_kind": media_kind,
        "relative_input_path": relative_path,
        "schema": "lf.youtube-reference.v1",
        "sha256": _sha256(media_path),
        "source_url": canonical_url,
        "video_id": video_id,
    }
    payload["receipt_sha256"] = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return payload


def _widget_summary(receipt, cache_status):
    return "\n".join((
        "## YouTube reference ready",
        f"**Status:** {cache_status}",
        f"**Video:** {receipt['video_id']}",
        f"**Profile:** {receipt['media_kind']}",
        f"**Input path:** `{receipt['relative_input_path']}`",
        f"**Bytes:** {receipt['bytes']}",
        f"**SHA-256:** `{receipt['sha256']}`",
        f"**Receipt:** `{receipt['receipt_sha256']}`",
    ))


def _return_reference(relative_path, video_id, receipt, node_id, cache_status):
    safe_send_sync(
        "youtubereference",
        {"value": _widget_summary(receipt, cache_status)},
        node_id,
    )
    return (relative_path, video_id, receipt)


def _load_cached(root, profile_dir, media_name, video_id, canonical_url, media_kind):
    media_path = profile_dir / media_name
    receipt_path = profile_dir / "receipt.json"
    if not media_path.exists() and not receipt_path.exists() and not profile_dir.exists():
        return None
    if not media_path.is_file() or not receipt_path.is_file() or media_path.is_symlink() or receipt_path.is_symlink():
        raise ValueError("YouTube cache entry is incomplete or unsafe")
    _contained(root, media_path)
    _contained(root, receipt_path)
    try:
        raw_receipt = receipt_path.read_text(encoding="utf-8")
        receipt = json.loads(raw_receipt)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("YouTube cache receipt is corrupt") from error
    sealed = dict(receipt)
    receipt_sha256 = sealed.pop("receipt_sha256", None)
    expected = _receipt(
        video_id,
        canonical_url,
        media_kind,
        _relative_input_path(video_id, media_kind, media_name),
        media_path,
    )
    if (
        raw_receipt != _canonical_json(receipt)
        or receipt != expected
        or receipt_sha256 != hashlib.sha256(_canonical_json(sealed).encode("utf-8")).hexdigest()
    ):
        raise ValueError("YouTube cache entry failed integrity verification")
    return receipt


def _download_progressive_mp4(canonical_url, stage_dir):
    """Download only YouTube's fixed progressive MP4 format into staging.

    Format 18 is deliberately used for both profiles because it is a single
    credential-free MP4 containing video and AAC audio.  Audio-only formats
    can require a YouTube PO token, and this node does not accept credentials.
    """
    try:
        import yt_dlp
    except ImportError as error:
        raise RuntimeError("yt-dlp is required; install requirements-youtube-ingest.txt") from error

    options = {
        "format": _PROGRESSIVE_MP4_FORMAT,
        "noplaylist": True,
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreconfig": True,
        "js_runtimes": {"node": {}},
        "extractor_args": {"youtube": {"player_client": ["android"]}},
        "nopart": True,
        "outtmpl": str(stage_dir / "reference.%(ext)s"),
        "overwrites": False,
        "postprocessors": [],
    }
    with yt_dlp.YoutubeDL(options) as downloader:
        downloader.extract_info(canonical_url, download=True)
    media_path = stage_dir / "reference.mp4"
    if not media_path.is_file() or media_path.is_symlink():
        raise RuntimeError("yt-dlp did not produce progressive MP4 format 18")
    if {path.name for path in stage_dir.iterdir()} != {"reference.mp4"}:
        raise RuntimeError("yt-dlp produced files outside the requested single-file MP4 staging profile")
    return media_path


def _remux_aac_to_m4a(source_path, target_path):
    """Copy AAC packets from progressive MP4 to an audio-only M4A container.

    This deliberately performs no transcoding, shell invocation, or yt-dlp
    postprocessing.  A narrow source contract keeps the cache profile honest:
    exactly one AAC audio stream and at least one video stream must be present.
    """
    try:
        import av
    except ImportError as error:
        raise RuntimeError("PyAV is required; install requirements-youtube-ingest.txt") from error

    try:
        with av.open(str(source_path), mode="r") as source:
            audio_streams = [stream for stream in source.streams if stream.type == "audio"]
            video_streams = [stream for stream in source.streams if stream.type == "video"]
            if len(audio_streams) != 1 or not video_streams:
                raise ValueError("progressive MP4 must contain one audio stream and a video stream")
            source_audio = audio_streams[0]
            if source_audio.codec_context.name != "aac":
                raise ValueError("progressive MP4 audio stream must be AAC")

            with av.open(str(target_path), mode="w", format="ipod") as target:
                target_audio = target.add_stream_from_template(source_audio)
                for packet in source.demux(source_audio):
                    if packet.dts is None:
                        continue
                    packet.stream = target_audio
                    target.mux(packet)
    except (OSError, ValueError) as error:
        raise RuntimeError("could not losslessly remux progressive MP4 AAC audio to M4A") from error

    if not target_path.is_file() or target_path.is_symlink() or target_path.stat().st_size <= 0:
        raise RuntimeError("PyAV did not produce an M4A file")
    with target_path.open("rb") as handle:
        if handle.read(12)[4:12] != b"ftypM4A ":
            raise RuntimeError("PyAV did not produce an M4A container")
    try:
        with av.open(str(target_path), mode="r") as target:
            audio_streams = [stream for stream in target.streams if stream.type == "audio"]
            video_streams = [stream for stream in target.streams if stream.type == "video"]
            if len(audio_streams) != 1 or video_streams or audio_streams[0].codec_context.name != "aac":
                raise ValueError("M4A output must contain exactly one AAC audio stream and no video")
    except (OSError, ValueError) as error:
        raise RuntimeError("lossless M4A remux validation failed") from error


def _transcode_aac_to_flac(source_path, target_path):
    """Decode progressive MP4 AAC into a broadly readable FLAC cache profile.

    M4A is the light, packet-preserving profile.  FLAC is the interoperability
    profile for consumers such as local audio-model APIs whose libsndfile path
    cannot decode AAC and whose optional FFmpeg fallback may be unavailable.
    """
    try:
        import av
    except ImportError as error:
        raise RuntimeError("PyAV is required; install requirements-youtube-ingest.txt") from error

    try:
        with av.open(str(source_path), mode="r") as source:
            audio_streams = [stream for stream in source.streams if stream.type == "audio"]
            video_streams = [stream for stream in source.streams if stream.type == "video"]
            if len(audio_streams) != 1 or not video_streams:
                raise ValueError("progressive MP4 must contain one audio stream and a video stream")
            source_audio = audio_streams[0]
            if source_audio.codec_context.name != "aac":
                raise ValueError("progressive MP4 audio stream must be AAC")

            sample_rate = source_audio.codec_context.sample_rate or 48000
            layout = source_audio.codec_context.layout.name or "stereo"
            resampler = av.AudioResampler(format="s16", layout=layout, rate=sample_rate)
            with av.open(str(target_path), mode="w", format="flac") as target:
                target_audio = target.add_stream("flac", rate=sample_rate)
                target_audio.layout = layout
                for frame in source.decode(source_audio):
                    for converted in resampler.resample(frame):
                        for packet in target_audio.encode(converted):
                            target.mux(packet)
                for converted in resampler.resample(None):
                    for packet in target_audio.encode(converted):
                        target.mux(packet)
                for packet in target_audio.encode(None):
                    target.mux(packet)
    except (OSError, ValueError) as error:
        raise RuntimeError("could not transcode progressive MP4 AAC audio to FLAC") from error

    if not target_path.is_file() or target_path.is_symlink() or target_path.stat().st_size <= 0:
        raise RuntimeError("PyAV did not produce a FLAC file")
    with target_path.open("rb") as handle:
        if handle.read(4) != b"fLaC":
            raise RuntimeError("PyAV did not produce a FLAC container")
    try:
        with av.open(str(target_path), mode="r") as target:
            audio_streams = [stream for stream in target.streams if stream.type == "audio"]
            video_streams = [stream for stream in target.streams if stream.type == "video"]
            if len(audio_streams) != 1 or video_streams or audio_streams[0].codec_context.name != "flac":
                raise ValueError("FLAC output must contain exactly one FLAC audio stream and no video")
    except (OSError, ValueError) as error:
        raise RuntimeError("FLAC transcode validation failed") from error


class LF_YouTubeReference:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "youtube_url": (Input.STRING, {"default": "", "multiline": False}),
                "media_kind": (["audio_m4a", "audio_flac", "video_mp4"], {"default": "audio_m4a"}),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": "## YouTube Reference\nEnable external intake, then run to populate the verified cache receipt."
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.JSON)
    RETURN_NAMES = ("input_reference", "video_id", "receipt")
    OUTPUT_TOOLTIPS = (
        "Portable path below ComfyUI input.",
        "The canonical eleven-character YouTube video id.",
        "Cache receipt containing the verified media SHA-256.",
    )

    def on_exec(self, youtube_url, media_kind, **kwargs):
        if not bool_env("LF_YOUTUBE_INGEST_ENABLED", False):
            raise RuntimeError("YouTube ingress is disabled; set LF_YOUTUBE_INGEST_ENABLED=1 to enable it")
        if media_kind not in _PROFILE:
            raise ValueError("Unsupported YouTube media profile")

        video_id, canonical_url = parse_youtube_video_url(youtube_url)
        media_name = _PROFILE[media_kind]
        root, cache = _cache_root()
        video_dir = cache / video_id
        profile_dir = video_dir / media_kind
        for path in (video_dir, profile_dir):
            _contained(root, path)
        relative_path = _relative_input_path(video_id, media_kind, media_name)

        with _lock_for((str(root), video_id, media_kind)):
            video_dir.mkdir(parents=True, exist_ok=True)
            _contained(root, video_dir)
            with _cross_process_lock(root, video_dir, media_kind):
                cached = _load_cached(root, profile_dir, media_name, video_id, canonical_url, media_kind)
                if cached is not None:
                    return _return_reference(
                        relative_path,
                        video_id,
                        cached,
                        kwargs.get("node_id"),
                        "verified cache hit",
                    )

                stage_dir = video_dir / f".{media_kind}.{uuid.uuid4().hex}.staging"
                _contained(root, stage_dir)
                stage_dir.mkdir()
                try:
                    source_path = _download_progressive_mp4(canonical_url, stage_dir)
                    if media_kind == "audio_m4a":
                        media_path = stage_dir / media_name
                        _remux_aac_to_m4a(source_path, media_path)
                        source_path.unlink()
                    elif media_kind == "audio_flac":
                        media_path = stage_dir / media_name
                        _transcode_aac_to_flac(source_path, media_path)
                        source_path.unlink()
                    else:
                        media_path = source_path
                    receipt = _receipt(video_id, canonical_url, media_kind, relative_path, media_path)
                    receipt_path = stage_dir / "receipt.json"
                    receipt_path.write_text(_canonical_json(receipt), encoding="utf-8")
                    _load_cached(root, stage_dir, media_name, video_id, canonical_url, media_kind)
                    os.replace(stage_dir, profile_dir)
                    return _return_reference(
                        relative_path,
                        video_id,
                        receipt,
                        kwargs.get("node_id"),
                        "downloaded and verified",
                    )
                except Exception:
                    shutil.rmtree(stage_dir, ignore_errors=True)
                    raise


NODE_CLASS_MAPPINGS = {
    "LF_YouTubeReference": LF_YouTubeReference,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_YouTubeReference": "YouTube Reference (opt-in)",
}
