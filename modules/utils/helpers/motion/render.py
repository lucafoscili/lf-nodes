"""Headless SMPL-X preview: CPU skinning, smooth shaded z-buffer, PyAV MP4.

No graphics context, external application, or model download is needed. The
camera is a fixed orthographic framing of the entire motion in camera space.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import numpy as np

from .format import POSE_WIDTHS, read_motion


DEFAULT_BETAS = "0.5,-1.5"


def parse_betas(value: str) -> np.ndarray:
    try:
        values = np.asarray([float(item.strip()) for item in value.split(",")], dtype=np.float32)
    except (AttributeError, TypeError, ValueError) as error:
        raise ValueError("Betas must be 1 to 10 comma-separated finite numbers.") from error
    if not 1 <= len(values) <= 10 or not np.isfinite(values).all():
        raise ValueError("Betas must be 1 to 10 comma-separated finite numbers.")
    return np.pad(values, (0, 10 - len(values)))


def resolve_body_model(body: str) -> Path:
    import folder_paths

    if body not in ("female", "neutral", "male"):
        raise ValueError(f"Unknown SMPL-X body: {body}")
    folder_paths.add_model_folder_path("smplx", str(Path(folder_paths.models_dir) / "smplx"))
    filename = f"SMPLX_{body.upper()}.npz"
    path = folder_paths.get_full_path("smplx", filename)
    if not path or not Path(path).is_file():
        raise FileNotFoundError(f"Missing SMPL-X model: models/smplx/{filename}")
    return Path(path)


def pose_meshes(motion: dict, model_path: Path, body: str, betas: np.ndarray):
    import torch

    try:
        import smplx
    except ImportError as error:
        raise RuntimeError("Motion renderer requires smplx>=0.1.28 to evaluate the body model.") from error
    try:
        model = smplx.SMPLX(
            str(model_path), gender=body, use_pca=False, flat_hand_mean=True,
        ).eval()
        parameters = {
            key: torch.as_tensor(motion["camera"][key], dtype=torch.float32)
            for key in POSE_WIDTHS
        }
        shape = torch.as_tensor(betas, dtype=torch.float32).reshape(1, 10)
        meshes = []
        # Bound skinning intermediates independently of clip duration.
        with torch.inference_mode():
            for start in range(0, len(parameters["body_pose"]), 16):
                batch = {key: values[start:start + 16] for key, values in parameters.items()}
                count = len(batch["body_pose"])
                zeros = torch.zeros(count, 3)
                result = model(
                    **batch, betas=shape.expand(count, -1),
                    jaw_pose=zeros, leye_pose=zeros, reye_pose=zeros,
                    expression=torch.zeros(count, 10),
                )
                meshes.append(result.vertices.cpu().numpy())
        return np.concatenate(meshes), np.asarray(model.faces, dtype=np.int32)
    except Exception as error:
        raise RuntimeError(f"SMPL-X body evaluation failed for {model_path.name}: {error}") from error


def _rasterize(vertices, faces, centre, scale, width, height):
    """Rasterize smooth normals with a true depth buffer, in bounded face chunks."""
    points = vertices.copy()
    points[:, :2] = (points[:, :2] - centre[:2]) * scale + (width / 2, height / 2)
    triangles = vertices[faces]
    normals = np.zeros_like(vertices)
    face_normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    for corner in range(3):
        np.add.at(normals, faces[:, corner], face_normals)
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    light = np.array([-0.4, -0.7, -1.0], dtype=np.float32)
    light /= np.linalg.norm(light)
    rim = np.array([0.8, -0.3, 0.6], dtype=np.float32)
    rim /= np.linalg.norm(rim)
    intensity = 0.38 + 0.66 * np.maximum(normals @ light, 0) + 0.22 * np.maximum(normals @ rim, 0)
    colors = np.clip(intensity[:, None] * np.array([0.78, 0.74, 0.70]), 0, 1) ** (1 / 2.2)
    pixels = np.full((height * width, 3), [238, 239, 242], dtype=np.uint8)
    depth = np.full(height * width, np.inf, dtype=np.float32)

    for start in range(0, len(faces), 512):
        face = faces[start:start + 512]
        tri = points[face]
        low = np.maximum(np.floor(tri[:, :, :2].min(axis=1)).astype(np.int32), 0)
        high = np.minimum(np.ceil(tri[:, :, :2].max(axis=1)).astype(np.int32), [width - 1, height - 1])
        span = np.maximum(high - low + 1, 0)
        counts = span[:, 0] * span[:, 1]
        indices = np.repeat(np.arange(len(face)), counts)
        if not len(indices):
            continue
        offsets = np.arange(len(indices)) - np.repeat(np.cumsum(counts) - counts, counts)
        x = low[indices, 0] + offsets % span[indices, 0]
        y = low[indices, 1] + offsets // span[indices, 0]
        a, b, c = tri[indices, 0], tri[indices, 1], tri[indices, 2]
        denominator = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
        valid = np.abs(denominator) > 1e-8
        divisor = np.where(valid, denominator, 1)
        u = ((b[:, 1] - c[:, 1]) * (x + 0.5 - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y + 0.5 - c[:, 1])) / divisor
        v = ((c[:, 1] - a[:, 1]) * (x + 0.5 - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y + 0.5 - c[:, 1])) / divisor
        w = 1 - u - v
        valid &= (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6)
        ids = y[valid] * width + x[valid]
        weights = np.stack([u[valid], v[valid], w[valid]], axis=1)
        distance = (tri[indices[valid], :, 2] * weights).sum(axis=1).astype(np.float32)
        np.minimum.at(depth, ids, distance)
        visible = distance == depth[ids]
        shaded = (colors[face[indices[valid][visible]]] * weights[visible, :, None]).sum(axis=1)
        pixels[ids[visible]] = np.clip(shaded * 255, 0, 255).astype(np.uint8)
    return pixels.reshape(height, width, 3)


def _source_frames(path: str, fps: float, count: int):
    """Sample decoded presentation times, preserving source-to-motion timing."""
    import av

    try:
        with av.open(path) as container:
            stream = container.streams.video[0]
            decoded = iter(container.decode(stream))
            current = next(decoded)
            origin = float(current.time or 0)
            following = next(decoded, None)
            for index in range(count):
                target = index / fps
                while following is not None and float(following.time or 0) - origin <= target:
                    current = following
                    following = next(decoded, None)
                duration = float(current.duration * current.time_base) if current.duration else 1 / float(stream.average_rate or fps)
                if following is None and target >= float(current.time or 0) - origin + duration + 1 / fps:
                    raise ValueError(f"Source video ends before motion frame {index}: {path}")
                yield current.to_image().convert("RGB")
    except Exception as error:
        raise RuntimeError(f"Source video decoding failed: {path}: {error}") from error


def render_motion(motion_file, model_path, body, betas, width, height, output_path, source_video=""):
    """Return one uint8 RGB array [frames,H,W,3] and write its H.264 MP4."""
    import av
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    if type(width) is not int or type(height) is not int or not 64 <= width <= 2048 or not 64 <= height <= 2048 or width % 2 or height % 2:
        raise ValueError("Preview width and height must be even integers from 64 to 2048.")
    shape = parse_betas(betas)
    motion = read_motion(motion_file)
    if source_video and not Path(source_video).is_file():
        raise FileNotFoundError(f"Source video is missing: {source_video}")
    meshes, faces = pose_meshes(motion, Path(model_path), body, shape)
    # Preserve translation over time; turn around the clip's shared centre.
    origin = (meshes.min(axis=(0, 1)) + meshes.max(axis=(0, 1))) / 2
    angle = np.deg2rad(45)
    turn = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0], [-np.sin(angle), 0, np.cos(angle)]], dtype=np.float32)
    views = (meshes, (meshes - origin) @ turn.T + origin)
    bounds = [(view.min(axis=(0, 1)), view.max(axis=(0, 1))) for view in views]
    # One scale for both views, one fixed frame across time. Leave room for labels.
    scale = min(min(width / (high[0] - low[0]), (height - 24) / (high[1] - low[1])) for low, high in bounds) / 1.12
    centres = [(low + high) / 2 for low, high in bounds]
    count = len(meshes)
    sources = _source_frames(source_video, float(motion["fps"]), count) if source_video else None
    frames = np.empty((count, height, width * (3 if sources else 2), 3), dtype=np.uint8)
    font = ImageFont.load_default(size=13)
    try:
        with av.open(str(output_path), mode="w") as container:
            stream = container.add_stream("libx264", rate=Fraction(str(motion["fps"])).limit_denominator(100000))
            stream.width, stream.height = frames.shape[2], height
            stream.pix_fmt = "yuv420p"
            stream.options = {"crf": "20", "preset": "fast"}
            for index in range(count):
                canvas = Image.new("RGB", (frames.shape[2], height), (238, 239, 242))
                offset = 0
                if sources is not None:
                    source = ImageOps.pad(next(sources), (width, height), color=(238, 239, 242))
                    canvas.paste(source, (0, 0))
                    offset = width
                for view, centre in zip(views, centres):
                    # Supersample edges without a graphics context.
                    rendered = _rasterize(view[index], faces, centre, scale * 2, width * 2, height * 2)
                    panel = Image.fromarray(rendered).resize((width, height), Image.Resampling.LANCZOS)
                    canvas.paste(panel, (offset, 0))
                    offset += width
                labels = (["Source"] if sources is not None else []) + ["Camera", "Turned 45 degrees"]
                draw = ImageDraw.Draw(canvas)
                for panel, label in enumerate(labels):
                    draw.rectangle((panel * width, 0, (panel + 1) * width, 22), fill=(238, 239, 242))
                    draw.text((panel * width + 7, 4), label, fill=(45, 46, 50), font=font)
                frames[index] = np.asarray(canvas)
                for packet in stream.encode(av.VideoFrame.from_ndarray(frames[index], format="rgb24")):
                    container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)
    except Exception as error:
        raise RuntimeError(f"Motion video render/encode failed: {output_path}: {error}") from error
    finally:
        if sources is not None:
            sources.close()
    return frames
