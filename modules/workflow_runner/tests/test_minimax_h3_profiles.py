"""Contracts for project-agnostic MiniMax H3 execution profiles."""

from __future__ import annotations

import pytest

from modules.workflow_runner.workflows.minimax_h3_profiles import (
    FL2VA_PROFILE_IDS,
    KITCHEN_TURBO_8STEP_LORA,
    NATIVE_MAX_EDGE,
    NATIVE_MAX_PIXELS,
    REF2VA_PROFILE_IDS,
    h3_profile_descriptions,
    resolve_h3_execution_profile,
)


def test_every_declared_profile_resolves_for_its_family() -> None:
    assert all(
        resolve_h3_execution_profile(profile_id, family="fl2va").id == profile_id
        for profile_id in FL2VA_PROFILE_IDS
    )
    assert all(
        resolve_h3_execution_profile(profile_id, family="ref2va").id == profile_id
        for profile_id in REF2VA_PROFILE_IDS
    )


def test_native_and_kitchen_quality_share_the_same_quality_envelope() -> None:
    native = resolve_h3_execution_profile("native_quality", family="fl2va")
    kitchen = resolve_h3_execution_profile("kitchen_quality", family="fl2va")

    assert (native.steps, native.max_edge, native.max_pixels) == (
        20,
        NATIVE_MAX_EDGE,
        NATIVE_MAX_PIXELS,
    )
    assert (kitchen.steps, kitchen.max_edge, kitchen.max_pixels) == (
        20,
        NATIVE_MAX_EDGE,
        NATIVE_MAX_PIXELS,
    )


def test_kitchen_turbo_is_exact_and_not_admitted_for_reference_video() -> None:
    profile = resolve_h3_execution_profile("kitchen_turbo_8step", family="fl2va")

    assert profile.accelerator == "kitchen_turbo"
    assert profile.steps == 8
    assert KITCHEN_TURBO_8STEP_LORA == (
        "MiniMax-H3\\minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
    )
    with pytest.raises(ValueError):
        resolve_h3_execution_profile("kitchen_turbo_8step", family="ref2va")


def test_unknown_family_and_profile_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown MiniMax H3 family"):
        resolve_h3_execution_profile("native_quality", family="unknown")
    with pytest.raises(ValueError, match="Unknown MiniMax H3 fl2va"):
        resolve_h3_execution_profile("missing", family="fl2va")


def test_descriptions_cover_requested_profiles_without_project_vocabulary() -> None:
    text = h3_profile_descriptions(("native_quality", "kitchen_quality"))

    assert "native_quality:" in text
    assert "kitchen_quality:" in text
    assert "velora" not in text.lower()
