"""Headless motion preview: CPU skinning, smooth shaded z-buffer, PyAV MP4.

No graphics context, external application, or model download is needed. The
camera keeps fixed orthographic framing unless travel requires root following.
"""

from __future__ import annotations

from fractions import Fraction
import logging
from pathlib import Path

import numpy as np

from .format import POSE_WIDTHS, read_motion


DEFAULT_BETAS = "0.5,-1.5"
DEFAULT_IMAGE_FRAME_LIMIT = 32
# Both selected uint8 frames and the node's float32 IMAGE conversion coexist.
IMAGE_OUTPUT_BUDGET_BYTES = 256 * 1024 * 1024
# Normal captures stay below 3 m/s; monocular depth failures can exceed 700 m/s.
DEPTH_SPEED_LIMIT = 10.0


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


def load_body_model(model_path: Path, body: str):
    """Shared lazy CPU model construction for rendering and the SMPL-X adapter."""
    try:
        import smplx
    except ImportError as error:
        raise RuntimeError("Motion renderer requires smplx>=0.1.28 to evaluate the body model.") from error
    try:
        return smplx.SMPLX(
            str(model_path), gender=body, use_pca=False, flat_hand_mean=True,
        ).eval()
    except Exception as error:
        raise RuntimeError(f"SMPL-X body evaluation failed for {model_path.name}: {error}") from error


def pose_meshes(motion: dict, model_path: Path, body: str, betas: np.ndarray):
    import torch

    try:
        model = load_body_model(model_path, body)
        parameters = {
            key: torch.as_tensor(motion["camera"][key], dtype=torch.float32)
            for key in POSE_WIDTHS
        }
        shape = torch.as_tensor(betas, dtype=torch.float32).reshape(1, 10)
        roots = np.empty((len(parameters["body_pose"]), 3), dtype=np.float32)
        def mesh_batches():
            # Re-evaluate bounded batches for framing and rendering. Retaining
            # all vertices (and their turned copy) scales with clip duration.
            try:
                for start in range(0, len(parameters["body_pose"]), 16):
                    with torch.inference_mode():
                        batch = {key: values[start:start + 16] for key, values in parameters.items()}
                        count = len(batch["body_pose"])
                        zeros = torch.zeros(count, 3)
                        result = model(
                            **batch, betas=shape.expand(count, -1),
                            jaw_pose=zeros, leye_pose=zeros, reye_pose=zeros,
                            expression=torch.zeros(count, 10),
                        )
                        vertices = result.vertices.cpu().numpy()
                        roots[start:start + count] = result.joints[:, 0].cpu().numpy()
                    yield vertices
            except Exception as error:
                raise RuntimeError(f"SMPL-X body evaluation failed for {model_path.name}: {error}") from error
        mesh_batches.root_positions = roots
        return mesh_batches, np.asarray(model.faces, dtype=np.int32)
    except Exception as error:
        raise RuntimeError(f"SMPL-X body evaluation failed for {model_path.name}: {error}") from error


def _rasterize(vertices, faces, centre, scale, width, height, normals=None):
    """Rasterize smooth normals with a true depth buffer, in bounded face chunks.

    ``normals`` (unit, one per vertex, in the vertices' frame) are drawn as
    given; without them each vertex takes its faces' area-weighted normal,
    which splits shading wherever the mesh splits its vertices.
    """
    points = vertices.copy()
    points[:, :2] = (points[:, :2] - centre[:2]) * scale + (width / 2, height / 2)
    if normals is not None:
        if normals.shape != vertices.shape:
            raise ValueError("Render normals must be one VEC3 per vertex.")
    else:
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


def select_image_frames(count, width, height, image_frame_limit):
    """Select ordered playback indices within the combined IMAGE storage budget."""
    if type(image_frame_limit) is not int or image_frame_limit < 0:
        raise ValueError("image_frame_limit must be a non-negative integer; 0 requests all frames.")
    selected = count if image_frame_limit == 0 else min(count, image_frame_limit)
    size = selected * height * width * 3 * (1 + 4)
    if size > IMAGE_OUTPUT_BUDGET_BYTES:
        raise ValueError(
            f"IMAGE selection of {selected} frames requires {size / 1024**2:.1f} MiB "
            f"for uint8 and float32 storage; the budget is {IMAGE_OUTPUT_BUDGET_BYTES / 1024**2:.0f} MiB. "
            "Reduce image_frame_limit or preview dimensions. The MP4 always includes every frame."
        )
    return np.linspace(0, count - 1, selected, dtype=np.int64)


def _depth_warning(motion_file, roots, fps):
    """One diagnostic for the clip; depth is the posed pelvis, in camera metres."""
    speeds = np.abs(np.diff(roots[:, 2])) * fps
    if not len(speeds) or speeds.max() <= DEPTH_SPEED_LIMIT:
        return None
    frame = int(np.argmax(speeds)) + 1
    message = (
        f"Motion {Path(motion_file).name}: camera root depth speed {speeds[frame - 1]:.2f} m/s "
        f"at frame {frame}; near {roots[:, 2].min():.2f} m, far {roots[:, 2].max():.2f} m "
        f"(limit {DEPTH_SPEED_LIMIT:g} m/s)."
    )
    logging.getLogger(__name__).warning(message)
    return message


def _smooth_roots(roots, fps):
    """Symmetric 0.1-second smoothing; the framing pass bounds its visible lag."""
    radius = min(len(roots) - 1, max(1, round(fps * 0.1)))
    weights = radius + 1 - np.abs(np.arange(-radius, radius + 1))
    weights = weights / weights.sum()
    padded = np.pad(roots, ((radius, radius), (0, 0)), mode="edge")
    return np.stack([np.convolve(padded[:, axis], weights, mode="valid") for axis in range(3)], axis=1)


def _following_centre(view, proposed, scale, width, height):
    # A depth discontinuity must not leave the body outside its smoothed frame.
    # Bound lag by the actual free margins, including the panel's label strip.
    low, high = view.min(axis=0), view.max(axis=0)
    lower = high[:2] - np.array([width / 2 - 2, height / 2 - 2]) / scale
    upper = low[:2] + np.array([width / 2 - 2, height / 2 - 24]) / scale
    centre = proposed.copy()
    centre[:2] = np.clip(centre[:2], lower, upper)
    return centre


def pose_glb_meshes(motion, model_path, body, body_glb):
    """Place the target in the clip's camera frame, retaining its own pelvis."""
    from .retarget_glb import glb_meshes
    from .retarget_smplx import camera_from_world

    try:
        world_batches, faces, metadata = glb_meshes(body_glb)
        count = len(motion["camera"]["transl"])
        if metadata["frame_count"] != count or not np.isclose(metadata["fps"], motion["fps"]):
            raise ValueError("Retargeted animation frame count and fps must match the motion.")
        scale = float(metadata["scale"])
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError("Retargeted animation scale must be positive and finite.")
        rotation, translation, camera_root = camera_from_world(motion, load_body_model(model_path, body))
        def mesh_batches(normals=False):
            start = 0
            for batch in world_batches(normals=normals):
                meshes, turned = batch if normals else (batch, None)
                stop = start + len(meshes)
                placed = (np.einsum("fij,fvj->fvi", rotation[start:stop], meshes / scale)
                          + translation[start:stop, None]).astype(np.float32)
                yield ((placed, np.einsum("fij,fvj->fvi", rotation[start:stop], turned).astype(np.float32))
                       if normals else placed)
                start = stop
        mesh_batches.normals = world_batches.normals
        mesh_batches.root_positions = (np.einsum("fij,fj->fi", rotation, world_batches.root_positions / scale)
                                       + translation).astype(np.float32)
        mesh_batches.depth_positions = camera_root
        return mesh_batches, faces
    except (OSError, ValueError, KeyError) as error:
        raise ValueError(f"Body GLB {body_glb}: {error}") from error


def render_motion(motion_file, model_path, body, betas, width, height, output_path, source_video="", image_frame_limit=DEFAULT_IMAGE_FRAME_LIMIT, body_glb=""):
    """Stream every RGB frame to H.264; return selected uint8 frames and timing."""
    import av
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    if type(width) is not int or type(height) is not int or not 64 <= width <= 2048 or not 64 <= height <= 2048 or width % 2 or height % 2:
        raise ValueError("Preview width and height must be even integers from 64 to 2048.")
    shape = parse_betas(betas)
    motion = read_motion(motion_file)
    if source_video and not Path(source_video).is_file():
        raise FileNotFoundError(f"Source video is missing: {source_video}")
    count = len(motion["camera"]["body_pose"])
    total_width = width * (3 if source_video else 2)
    indices = select_image_frames(count, total_width, height, image_frame_limit)
    mesh_batches, faces = (pose_glb_meshes(motion, Path(model_path), body, body_glb) if body_glb
                           else pose_meshes(motion, Path(model_path), body, shape))
    # Preserve translation over time; turn around the clip's shared centre.
    low, high = np.full(3, np.inf, dtype=np.float32), np.full(3, -np.inf, dtype=np.float32)
    relative_low, relative_high = low.copy(), high.copy()
    minimum_height = np.inf
    start = 0
    for meshes in mesh_batches():
        low = np.minimum(low, meshes.min(axis=(0, 1)))
        high = np.maximum(high, meshes.max(axis=(0, 1)))
        minimum_height = min(minimum_height, np.ptp(meshes[:, :, 1], axis=1).min())
        relative = meshes - mesh_batches.root_positions[start:start + len(meshes), None]
        relative_low = np.minimum(relative_low, relative.min(axis=(0, 1)))
        relative_high = np.maximum(relative_high, relative.max(axis=(0, 1)))
        start += len(meshes)
    roots = mesh_batches.root_positions
    warning = _depth_warning(motion_file, getattr(mesh_batches, "depth_positions", roots), float(motion["fps"]))
    origin = (low + high) / 2
    angle = np.deg2rad(45)
    turn = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0], [-np.sin(angle), 0, np.cos(angle)]], dtype=np.float32)
    turned_low, turned_high = np.full(3, np.inf, dtype=np.float32), np.full(3, -np.inf, dtype=np.float32)
    relative_turned_low, relative_turned_high = turned_low.copy(), turned_high.copy()
    start = 0
    for meshes in mesh_batches():
        turned = (meshes - origin) @ turn.T + origin
        turned_low = np.minimum(turned_low, turned.min(axis=(0, 1)))
        turned_high = np.maximum(turned_high, turned.max(axis=(0, 1)))
        relative = (meshes - roots[start:start + len(meshes), None]) @ turn.T
        relative_turned_low = np.minimum(relative_turned_low, relative.min(axis=(0, 1)))
        relative_turned_high = np.maximum(relative_turned_high, relative.max(axis=(0, 1)))
        start += len(meshes)
    bounds = [(low, high), (turned_low, turned_high)]
    # One scale for both views, one fixed frame across time. Leave room for labels.
    scale = min(min(width / (high[0] - low[0]), (height - 24) / (high[1] - low[1])) for low, high in bounds) / 1.12
    centres = [(low + high) / 2 for low, high in bounds]
    following = minimum_height * scale < height / 2
    if following:
        bounds = [(relative_low, relative_high), (relative_turned_low, relative_turned_high)]
        scale = min(min(width / (hi[0] - lo[0]), (height - 24) / (hi[1] - lo[1])) for lo, hi in bounds) / 1.12
        centres = [(lo + hi) / 2 for lo, hi in bounds]
        smoothed_roots = _smooth_roots(roots, float(motion["fps"]))
    sources = _source_frames(source_video, float(motion["fps"]), count) if source_video else None
    frames = np.empty((len(indices), height, total_width, 3), dtype=np.uint8)
    selected = iter(enumerate(indices))
    next_selection = next(selected, None)
    # Release framing batches before encoding begins.
    del meshes, turned, relative
    font = ImageFont.load_default(size=13)
    try:
        with av.open(str(output_path), mode="w") as container:
            stream = container.add_stream("libx264", rate=Fraction(str(motion["fps"])).limit_denominator(100000))
            stream.width, stream.height = total_width, height
            stream.pix_fmt = "yuv420p"
            stream.options = {"crf": "20", "preset": "fast"}
            def mesh_frames():
                # (positions, normals) per frame; normals None where the rasterizer smooths the faces.
                if getattr(mesh_batches, "normals", None) == "stored":
                    for meshes, normals in mesh_batches(normals=True):
                        yield from zip(meshes, normals)
                else:
                    for meshes in mesh_batches():
                        yield from ((mesh, None) for mesh in meshes)
            for index, (mesh, normals) in enumerate(mesh_frames()):
                canvas = Image.new("RGB", (total_width, height), (238, 239, 242))
                offset = 0
                if sources is not None:
                    source = ImageOps.pad(next(sources), (width, height), color=(238, 239, 242))
                    canvas.paste(source, (0, 0))
                    offset = width
                pivot = roots[index] if following else origin
                views = ((mesh, normals),
                         ((mesh - pivot) @ turn.T + pivot, None if normals is None else normals @ turn.T))
                for (view, view_normals), centre in zip(views, centres):
                    if following:
                        centre = _following_centre(view, smoothed_roots[index] + centre, scale, width, height)
                    # Supersample edges without a graphics context.
                    rendered = _rasterize(view, faces, centre, scale * 2, width * 2, height * 2, view_normals)
                    panel = Image.fromarray(rendered).resize((width, height), Image.Resampling.LANCZOS)
                    canvas.paste(panel, (offset, 0))
                    offset += width
                labels = (["Source"] if sources is not None else []) + ["Camera", "Turned 45 degrees"]
                if following:
                    labels = [label if label == "Source" else f"{label} (following)" for label in labels]
                draw = ImageDraw.Draw(canvas)
                for panel, label in enumerate(labels):
                    draw.rectangle((panel * width, 0, (panel + 1) * width, 22), fill=(238, 239, 242))
                    label_font = font
                    if following and label != "Source":
                        size = 13
                        while draw.textlength(label, font=label_font) > width - 14 and size > 1:
                            size -= 1
                            label_font = ImageFont.load_default(size=size)
                    draw.text((panel * width + 7, 4), label, fill=(45, 46, 50), font=label_font)
                pixels = np.asarray(canvas)
                if next_selection is not None and index == next_selection[1]:
                    frames[next_selection[0]] = pixels
                    next_selection = next(selected, None)
                for packet in stream.encode(av.VideoFrame.from_ndarray(pixels, format="rgb24")):
                    container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)
    except Exception as error:
        raise RuntimeError(f"Motion video render/encode failed: {output_path}: {error}") from error
    finally:
        if sources is not None:
            sources.close()
    timing = {"frames": count, "image_frames": len(indices), "frame_indices": indices.tolist(), "fps": float(motion["fps"])}
    if following:
        timing["framing"] = "following"
    if body_glb:
        # The body GLB's own normals, skinned, or (it carries none) its faces' smoothed normals.
        timing["normals"] = mesh_batches.normals
    if warning:
        timing["warnings"] = [warning]
    return frames, timing
