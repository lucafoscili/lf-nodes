from __future__ import annotations

import math

import pytest
import torch

from modules.nodes.image import select_loop_segment as module


def _orbit_shot(frames: int, period: int, *, static_from: int | None = None) -> torch.Tensor:
    """A bright square orbiting on a dark field; exactly periodic, optionally frozen."""

    batch = torch.zeros((frames, 32, 32, 3))
    for index in range(frames):
        t = min(index, static_from) if static_from is not None else index
        angle = 2.0 * math.pi * float(t) / float(period)
        x = int(round(16 + 8 * math.cos(angle)))
        y = int(round(16 + 8 * math.sin(angle)))
        batch[index, y - 2 : y + 2, x - 2 : x + 2, :] = 1.0
    return batch


def test_finds_the_planted_period_and_samples_a_closed_cycle() -> None:
    shot = _orbit_shot(120, 20)
    sampled, receipt = module.select_loop_segment(
        shot,
        source_fps=24.0,
        target_count=10,
        min_period_frames=12,
        max_period_frames=96,
    )
    selected = receipt["selected"]
    assert selected["periodFrames"] == 20
    assert selected["seam"] == pytest.approx(0.0, abs=1e-6)
    assert selected["motion"] > 0.0
    assert selected["cycleSeconds"] == pytest.approx(20.0 / 24.0)
    assert receipt["intendedFps"] == pytest.approx(10.0 / (20.0 / 24.0))
    assert receipt["targetCount"] == 10
    assert sampled.shape == (10, 32, 32, 3)
    indices = receipt["sampledSourceIndices"]
    assert len(indices) == 10
    assert indices[0] == selected["start"]
    assert max(indices) < selected["start"] + 20, "the final endpoint must be excluded"
    assert receipt["schema"] == module.LOOP_SEGMENT_RECEIPT_SCHEMA
    assert receipt["topCandidates"][0]["periodFrames"] == 20


def test_prefers_the_shortest_cycle_on_exact_ties() -> None:
    _sampled, receipt = module.select_loop_segment(
        _orbit_shot(120, 20),
        source_fps=24.0,
        target_count=8,
        min_period_frames=12,
        max_period_frames=96,
    )
    assert receipt["selected"]["periodFrames"] == 20


def test_frozen_stretch_cannot_win_on_a_tiny_seam() -> None:
    shot = _orbit_shot(120, 20, static_from=60)
    _sampled, receipt = module.select_loop_segment(
        shot,
        source_fps=24.0,
        target_count=10,
        min_period_frames=12,
        max_period_frames=40,
    )
    start = receipt["selected"]["start"]
    assert start + receipt["selected"]["periodFrames"] <= 61, receipt["selected"]


def test_static_shot_is_refused_with_guidance() -> None:
    static = torch.zeros((40, 16, 16, 3))
    with pytest.raises(ValueError, match="No loop segment satisfies"):
        module.select_loop_segment(
            static,
            source_fps=24.0,
            target_count=8,
            min_period_frames=8,
            max_period_frames=30,
        )


def test_target_count_longer_than_any_period_is_refused() -> None:
    with pytest.raises(ValueError, match="No loop segment satisfies"):
        module.select_loop_segment(
            _orbit_shot(60, 20),
            source_fps=24.0,
            target_count=50,
            min_period_frames=12,
            max_period_frames=40,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source_fps": 0.0},
        {"target_count": 0},
        {"min_period_frames": 1},
        {"max_period_frames": 4},
        {"motion_floor": 9.0},
    ],
)
def test_invalid_controls_are_refused(kwargs: dict) -> None:
    arguments = {
        "source_fps": 24.0,
        "target_count": 8,
        "min_period_frames": 12,
        "max_period_frames": 40,
        **kwargs,
    }
    with pytest.raises(ValueError):
        module.select_loop_segment(_orbit_shot(60, 20), **arguments)


def test_node_declares_its_contract() -> None:
    types = module.LF_SelectLoopSegment.INPUT_TYPES()
    assert set(types["required"]) == {
        "image",
        "source_fps",
        "target_count",
        "min_period_frames",
        "max_period_frames",
        "motion_floor",
    }
    assert "analysis_max_edge" in types["optional"]
    assert module.LF_SelectLoopSegment.RETURN_NAMES == ("image", "receipt", "image_list")
    assert module.NODE_CLASS_MAPPINGS["LF_SelectLoopSegment"] is module.LF_SelectLoopSegment
