from __future__ import annotations

from types import SimpleNamespace
import json
import sys
import tracemalloc

import numpy as np
import pytest
import torch

from modules.nodes.motion import motion_to_video
from modules.nodes.motion.motion_to_video import LF_MotionToVideo
from modules.utils.constants import Input
from modules.utils.helpers.motion import render
from modules.utils.helpers.motion.format import JOINT_NAMES, POSE_WIDTHS, write_motion


@pytest.fixture
def synthetic_motion(monkeypatch, tmp_path):
    """Exercise real skinning batches/raster/encoding without licensed weights."""
    def create(count=3, fps=30, vertex_count=4):
        camera = {key: np.zeros((count, width), dtype=np.float32).tolist() for key, width in POSE_WIDTHS.items()}
        camera["transl"] = [[index / count * 0.2, 0, 0] for index in range(count)]
        motion = {"schema": "lf.motion.v1", "fps": fps, "joint_names": JOINT_NAMES, "camera": camera, "world": camera}
        path = tmp_path / f"motion-{count}.json"
        write_motion(path, motion)
        calls = []

        class Body:
            faces = np.array([[0, 1, 2], [0, 3, 1], [1, 3, 2], [2, 3, 0]], dtype=np.int32)
            def __init__(self, *args, **kwargs):
                pass
            def eval(self):
                return self
            def __call__(self, **kwargs):
                count = len(kwargs["body_pose"])
                calls.append(count)
                vertices = torch.zeros(count, vertex_count, 3)
                vertices[:, :4] = torch.tensor([[-0.5, -1, 2], [0.5, -1, 2], [0, 1, 2], [0, 0, 3]])
                vertices += kwargs["transl"][:, None, :]
                return SimpleNamespace(vertices=vertices)

        monkeypatch.setitem(sys.modules, "smplx", SimpleNamespace(SMPLX=Body))
        return path, motion, Body, calls
    return create


def legacy_preview(motion, body_type, width, height):
    """Frozen all-at-once framing/composition from the published renderer."""
    from PIL import Image, ImageDraw, ImageFont

    parameters = {key: torch.tensor(motion["camera"][key]) for key in POSE_WIDTHS}
    meshes = body_type()(**parameters).vertices.numpy()
    origin = (meshes.min(axis=(0, 1)) + meshes.max(axis=(0, 1))) / 2
    angle = np.deg2rad(45)
    turn = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0], [-np.sin(angle), 0, np.cos(angle)]], dtype=np.float32)
    views = (meshes, (meshes - origin) @ turn.T + origin)
    bounds = [(view.min(axis=(0, 1)), view.max(axis=(0, 1))) for view in views]
    scale = min(min(width / (high[0] - low[0]), (height - 24) / (high[1] - low[1])) for low, high in bounds) / 1.12
    centres = [(low + high) / 2 for low, high in bounds]
    frames = []
    for index in range(len(meshes)):
        canvas = Image.new("RGB", (width * 2, height), (238, 239, 242))
        for panel, (view, centre) in enumerate(zip(views, centres)):
            pixels = render._rasterize(view[index], body_type.faces, centre, scale * 2, width * 2, height * 2)
            canvas.paste(Image.fromarray(pixels).resize((width, height), Image.Resampling.LANCZOS), (panel * width, 0))
        draw = ImageDraw.Draw(canvas)
        for panel, label in enumerate(["Camera", "Turned 45 degrees"]):
            draw.rectangle((panel * width, 0, (panel + 1) * width, 22), fill=(238, 239, 242))
            draw.text((panel * width + 7, 4), label, fill=(45, 46, 50), font=ImageFont.load_default(size=13))
        frames.append(np.asarray(canvas))
    return np.stack(frames)


def test_motion_to_video_snapshots_public_schema_and_mapped_execution() -> None:
    schema = LF_MotionToVideo.INPUT_TYPES()
    assert {
        group: {
            key: (spec[0], spec[1].get("default"))
            for key, spec in values.items()
        }
        for group, values in schema.items() if group != "hidden"
    } == {
        "required": {
            "motion_file": (Input.STRING, ""),
            "body": (["female", "neutral", "male"], "female"),
            "betas": (Input.STRING, "0.5,-1.5"),
            "width": (Input.INTEGER, 320),
            "height": (Input.INTEGER, 560),
        },
        "optional": {"source_video": (Input.STRING, ""), "ui_widget": (Input.LF_CODE, ""), "image_frame_limit": (Input.INTEGER, 32)},
    }
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert LF_MotionToVideo.INPUT_IS_LIST is False
    assert LF_MotionToVideo.OUTPUT_NODE is True
    assert LF_MotionToVideo.FUNCTION == "on_exec"
    assert LF_MotionToVideo.RETURN_TYPES == (Input.STRING, Input.IMAGE, Input.IMAGE)
    assert LF_MotionToVideo.RETURN_NAMES == ("video_file", "frames", "frame_list")
    assert LF_MotionToVideo.OUTPUT_IS_LIST == (False, False, True)
    assert motion_to_video.NODE_CLASS_MAPPINGS == {"LF_MotionToVideo": LF_MotionToVideo}
    assert motion_to_video.NODE_DISPLAY_NAME_MAPPINGS == {"LF_MotionToVideo": "Motion to video"}


@pytest.mark.parametrize("node_id", [None, "render-node", ["render-node"]])
def test_motion_to_video_preserves_frame_order_and_final_event_history(monkeypatch, tmp_path, node_id, synthetic_motion) -> None:
    output = tmp_path / "motion" / "preview_00001.mp4"
    output.parent.mkdir()
    model = tmp_path / "SMPLX_FEMALE.npz"
    path, motion, body_type, _ = synthetic_motion()
    raw = legacy_preview(motion, body_type, 64, 64)
    sent = []
    monkeypatch.setattr(motion_to_video, "resolve_body_model", lambda body: model)
    monkeypatch.setattr(motion_to_video.folder_paths, "get_output_directory", lambda: str(tmp_path))

    def resolve(**kwargs):
        assert kwargs == {
            "filename_prefix": "LF_Nodes/Motion/preview", "base_output_path": str(tmp_path.resolve()),
            "extension": "mp4", "add_counter": True,
        }
        return str(output), None, None

    monkeypatch.setattr(motion_to_video, "resolve_filepath", resolve)
    monkeypatch.setattr(motion_to_video, "safe_send_sync", lambda *args: sent.append(args))

    response = LF_MotionToVideo().on_exec(
        str(path), body="female", betas="0.2,-0.4", width=64, height=64, node_id=node_id,
    )

    path, batch, frames = response["result"]
    assert path == str(output)
    assert batch.dtype == torch.float32
    assert batch.shape == (3, 64, 128, 3)
    assert isinstance(frames, list)
    assert [tuple(frame.shape) for frame in frames] == [(1, 64, 128, 3)] * 3
    torch.testing.assert_close(batch, torch.from_numpy(raw).float() / 255)
    for index, frame in enumerate(frames):
        torch.testing.assert_close(frame, batch[index:index + 1])
        assert frame.untyped_storage().data_ptr() == batch.untyped_storage().data_ptr()
    payload = response["ui"]["lf_output"][0]
    assert sent == [("motiontovideo", payload, node_id)]
    assert payload is sent[0][1]
    assert payload["file_names"] == ["motion/preview_00001.mp4"]
    assert payload["json"] == {
        "video_file": "motion/preview_00001.mp4", "frames": 3, "image_frames": 3,
        "frame_indices": [0, 1, 2], "fps": 30, "body": "female", "betas": "0.2,-0.4",
    }
    assert json.loads(payload["value"]) == payload["json"]


def test_motion_to_video_does_not_publish_failed_render(monkeypatch, tmp_path, synthetic_motion) -> None:
    path, _, _, _ = synthetic_motion()
    sent = []
    monkeypatch.setattr(motion_to_video, "resolve_body_model", lambda _: tmp_path / "model.npz")
    monkeypatch.setattr(motion_to_video.folder_paths, "get_output_directory", lambda: str(tmp_path))
    monkeypatch.setattr(motion_to_video, "resolve_filepath", lambda **_: (str(tmp_path / "preview.mp4"), None, None))
    monkeypatch.setattr(motion_to_video, "safe_send_sync", lambda *args: sent.append(args))

    def fail(*_args, **_kwargs):
        raise RuntimeError("Synthetic encode failure")

    monkeypatch.setitem(sys.modules, "av", SimpleNamespace(open=fail))
    with pytest.raises(RuntimeError, match="Synthetic encode failure"):
        LF_MotionToVideo().on_exec(str(path), width=64, height=64)
    assert not sent


@pytest.mark.parametrize("body", ["female", "neutral", "male"])
def test_renderer_resolves_models_by_registered_name(monkeypatch, tmp_path, body) -> None:
    filename = f"SMPLX_{body.upper()}.npz"
    model = tmp_path / filename
    model.touch()
    registered, looked_up = [], []
    monkeypatch.setattr(motion_to_video.folder_paths, "models_dir", str(tmp_path))
    monkeypatch.setattr(motion_to_video.folder_paths, "add_model_folder_path", lambda *args: registered.append(args), raising=False)
    monkeypatch.setattr(motion_to_video.folder_paths, "get_full_path", lambda *args: looked_up.append(args) or str(model))
    assert render.resolve_body_model(body) == model
    assert looked_up == [("smplx", filename)]
    assert registered == [("smplx", str(tmp_path / "smplx"))]


def test_renderer_missing_model_and_unknown_body_fail_clearly(monkeypatch) -> None:
    monkeypatch.setattr(motion_to_video.folder_paths, "add_model_folder_path", lambda *_: None, raising=False)
    monkeypatch.setattr(motion_to_video.folder_paths, "get_full_path", lambda *_: None)
    with pytest.raises(FileNotFoundError, match="SMPLX_NEUTRAL.npz"):
        render.resolve_body_model("neutral")
    with pytest.raises(ValueError, match="Unknown SMPL-X body"):
        render.resolve_body_model("unsupported")


@pytest.mark.parametrize("value", ["", "a", "nan", "inf", "1,,2", ",".join(["1"] * 11), None])
def test_renderer_rejects_invalid_betas(value) -> None:
    with pytest.raises(ValueError, match="Betas"):
        render.parse_betas(value)


def test_renderer_zero_pads_explicit_shape_coefficients() -> None:
    np.testing.assert_array_equal(render.parse_betas(" 0.5, -1.5 "), [0.5, -1.5] + [0] * 8)


@pytest.mark.parametrize("width,height", [(63, 64), (64, 63), (65, 64), (64, 65), (2050, 64), (64, 2050), (64.0, 64), (64, 64.0), (True, 64), ("64", 64)])
def test_renderer_rejects_invalid_dimensions_before_model_work(monkeypatch, tmp_path, width, height) -> None:
    monkeypatch.setattr(render, "read_motion", lambda _: pytest.fail("Invalid dimensions reached motion loading"))
    with pytest.raises(ValueError, match="width and height"):
        render.render_motion("clip.json", "model.npz", "female", "0", width, height, tmp_path / "out.mp4")


def test_renderer_rejects_absent_source_before_body_evaluation(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(render, "read_motion", lambda _: {"fps": 30})
    monkeypatch.setattr(render, "pose_meshes", lambda *_: pytest.fail("Missing source reached body evaluation"))
    with pytest.raises(FileNotFoundError, match="Source video is missing"):
        render.render_motion("clip.json", "model.npz", "female", "0", 64, 64, tmp_path / "out.mp4", str(tmp_path / "missing.mp4"))


def test_source_decoder_reports_source_ending_before_motion(monkeypatch) -> None:
    from PIL import Image

    frame = SimpleNamespace(time=0, duration=1, time_base=1 / 30, to_image=lambda: Image.new("RGB", (4, 4)))

    class Container:
        streams = SimpleNamespace(video=[SimpleNamespace(average_rate=30)])
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return False
        def decode(self, _):
            return iter([frame])

    monkeypatch.setitem(sys.modules, "av", SimpleNamespace(open=lambda _: Container()))
    with pytest.raises(RuntimeError, match="Source video ends before motion frame"):
        list(render._source_frames("synthetic.mp4", 30, 5))


@pytest.mark.parametrize("with_source,failure", [(False, None), (True, None), (True, "encode"), (True, "flush"), (True, "mux")])
def test_renderer_composes_source_and_body_views_and_wraps_encoder_failures(monkeypatch, tmp_path, with_source, failure, synthetic_motion) -> None:
    from PIL import Image

    inference_mode = torch.is_inference_mode_enabled()
    path, _, _, _ = synthetic_motion(count=2, fps=29.97)
    source = tmp_path / "source.mp4"
    source.touch()
    closed, encoded, packets = [], [], []

    class Sources:
        def __init__(self):
            self.frames = iter([Image.new("RGB", (32, 32), "red"), Image.new("RGB", (32, 32), "blue")])
        def __next__(self):
            return next(self.frames)
        def close(self):
            closed.append(True)

    monkeypatch.setattr(render, "_source_frames", lambda *_: Sources())

    class Stream:
        def encode(self, frame=None):
            if failure == "encode" and frame is not None:
                raise ValueError("Synthetic encoder failure")
            if failure == "flush" and frame is None:
                raise ValueError("Synthetic flush failure")
            if frame is not None:
                encoded.append(frame.copy())
            return ["packet"]

    stream = Stream()

    class Container:
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return False
        def add_stream(self, codec, rate):
            assert codec == "libx264"
            assert float(rate) == pytest.approx(29.97)
            return stream
        def mux(self, packet):
            if failure == "mux":
                raise ValueError("Synthetic mux failure")
            packets.append(packet)

    def from_ndarray(frame, format):
        assert format == "rgb24"
        return frame

    monkeypatch.setitem(sys.modules, "av", SimpleNamespace(
        open=lambda *args, **kwargs: Container(),
        VideoFrame=SimpleNamespace(from_ndarray=from_ndarray),
    ))
    output = tmp_path / "preview.mp4"
    source_path = str(source) if with_source else ""
    if failure:
        with pytest.raises(RuntimeError, match="Motion video render/encode failed") as caught:
            render.render_motion(path, "model.npz", "female", "0", 64, 64, output, source_path)
        assert isinstance(caught.value.__cause__, ValueError)
        assert f"Synthetic {failure}" in str(caught.value)
    else:
        frames, timing = render.render_motion(path, "model.npz", "female", "0", 64, 64, output, source_path)
        assert timing == {"frames": 2, "image_frames": 2, "frame_indices": [0, 1], "fps": 29.97}
        total_width = 192 if with_source else 128
        assert frames.shape == (2, 64, total_width, 3)
        assert frames.dtype == np.uint8
        if with_source:
            np.testing.assert_array_equal(frames[0, 40, 32], [255, 0, 0])
            np.testing.assert_array_equal(frames[1, 40, 32], [0, 0, 255])
        np.testing.assert_array_equal(np.stack(encoded), frames)
        assert len(packets) == 3  # Two frame packets, then encoder flush.
        assert stream.width == total_width and stream.height == 64
    assert closed == ([True] if with_source else [])
    assert torch.is_inference_mode_enabled() is inference_mode


def test_raster_depth_occlusion_survives_face_order_and_chunk_boundary() -> None:
    near = np.array([[-1, -1, 1], [1, -1, 1], [0, 1, 1]], dtype=np.float32)
    far = near.copy()
    far[:, 2] = 3
    vertices = np.concatenate([near, far])
    near_face = np.array([[0, 1, 2]], dtype=np.int32)
    far_face = np.array([[3, 5, 4]], dtype=np.int32)
    centre = np.array([0, 0, 0], dtype=np.float32)
    expected = render._rasterize(vertices, near_face, centre, 12, 32, 32)
    far_image = render._rasterize(vertices, far_face, centre, 12, 32, 32)
    assert not np.array_equal(expected[16, 16], far_image[16, 16])
    for faces in (
        np.concatenate([near_face, far_face]),
        np.concatenate([far_face, near_face]),
        np.concatenate([near_face, np.repeat(far_face, 512, axis=0)]),
    ):
        actual = render._rasterize(vertices, faces, centre, 12, 32, 32)
        np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("limit,expected", [(0, list(range(7))), (1, [0]), (3, [0, 3, 6]), (32, list(range(7)))])
def test_image_frame_selection_is_explicit_and_ordered(limit, expected) -> None:
    assert render.select_image_frames(7, 128, 64, limit).tolist() == expected


@pytest.mark.parametrize("limit", [-1, 1.5, True, "32", None])
def test_image_frame_selection_rejects_invalid_controls(limit) -> None:
    with pytest.raises(ValueError, match="image_frame_limit must be a non-negative integer"):
        render.select_image_frames(7, 128, 64, limit)


@pytest.mark.parametrize("limit,with_source", [(0, False), (1800, False), (0, True)])
def test_image_budget_fails_before_body_evaluation_or_output(monkeypatch, tmp_path, synthetic_motion, limit, with_source) -> None:
    path, _, _, calls = synthetic_motion(count=1800)
    output = tmp_path / "too-large.mp4"
    source = tmp_path / "source.mp4"
    source.touch()
    size = "13842.8" if with_source else "9228.5"
    with pytest.raises(ValueError, match=f"{size} MiB.*budget is 256 MiB"):
        render.render_motion(path, "model.npz", "female", "0", 320, 560, output, str(source) if with_source else "", image_frame_limit=limit)
    assert calls == []
    assert not output.exists()


@pytest.mark.parametrize("limit", [0, 5])
def test_real_pyav_preserves_legacy_pixels_and_all_frame_timing(tmp_path, synthetic_motion, limit) -> None:
    import av
    from fractions import Fraction

    path, motion, body_type, calls = synthetic_motion(count=35, fps=29.97)
    expected = legacy_preview(motion, body_type, 64, 64)
    calls.clear()
    output = tmp_path / "streamed.mp4"
    actual, timing = render.render_motion(path, "model.npz", "female", "0", 64, 64, output, image_frame_limit=limit)
    indices = timing["frame_indices"]
    np.testing.assert_array_equal(actual, expected[indices])
    assert calls == [16, 16, 3] * 3
    assert timing["frames"] == 35
    assert timing["image_frames"] == (35 if limit == 0 else 5)
    assert indices[0] == 0 and indices[-1] == 34

    # Re-encode the frozen legacy RGB frames using its exact published options.
    legacy = tmp_path / "legacy.mp4"
    with av.open(str(legacy), mode="w") as container:
        stream = container.add_stream("libx264", rate=Fraction("29.97"))
        stream.width, stream.height, stream.pix_fmt = 128, 64, "yuv420p"
        stream.options = {"crf": "20", "preset": "fast"}
        for pixels in expected:
            for packet in stream.encode(av.VideoFrame.from_ndarray(pixels, format="rgb24")):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    def decoded(video):
        with av.open(str(video)) as container:
            rate = container.streams.video[0].average_rate
            frames = [(frame.pts, frame.time_base, frame.to_ndarray(format="rgb24")) for frame in container.decode(video=0)]
        return rate, frames
    rate, streamed = decoded(output)
    legacy_rate, previous = decoded(legacy)
    assert rate == legacy_rate == Fraction("29.97")
    assert len(streamed) == len(previous) == 35
    for new, old in zip(streamed, previous):
        assert new[:2] == old[:2]
        np.testing.assert_array_equal(new[2], old[2])


def test_long_clip_bounds_mesh_and_image_memory_through_real_node(monkeypatch, tmp_path, synthetic_motion) -> None:
    monkeypatch.setattr(motion_to_video, "resolve_body_model", lambda _: tmp_path / "model.npz")
    monkeypatch.setattr(motion_to_video.folder_paths, "get_output_directory", lambda: str(tmp_path))
    peaks = []
    for count in (32, 600):
        path, _, _, calls = synthetic_motion(count=count, vertex_count=10475)
        output = tmp_path / f"memory-{count}.mp4"
        monkeypatch.setattr(motion_to_video, "resolve_filepath", lambda **_: (str(output), None, None))
        tracemalloc.start()
        try:
            response = LF_MotionToVideo().on_exec(str(path), width=64, height=64)
            peaks.append(tracemalloc.get_traced_memory()[1])
        finally:
            tracemalloc.stop()
        assert response["result"][1].shape == (32, 64, 128, 3)
        assert len(response["result"][2]) == 32
        assert response["ui"]["lf_output"][0]["json"]["frames"] == count
        assert max(calls) <= 16 and sum(calls) == count * 3
        del response
    # Includes JSON parsing, bounded mesh passes, rasterization and node output
    # conversion/list creation. tracemalloc excludes native torch storage.
    assert peaks[1] < 40 * 1024**2
    assert peaks[1] < peaks[0] + 20 * 1024**2
