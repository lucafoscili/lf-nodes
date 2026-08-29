#!/usr/bin/env python3
"""Run LF's deterministic CPU publication contracts.

This is the shared behavioral gate used by pull-request/node-count validation
and registry publication.  The selected tests import production helpers and
nodes through ``run_pytests.py``'s inert Comfy host boundary; they never require
a GPU, a running Comfy service, or the parent Comfy checkout.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
QUALITY_ROOT = ROOT / "scripts" / "quality"

BEHAVIOR_TESTS: tuple[str, ...] = (
    # Prove the isolated runner did not import the parent Comfy/GPU host.
    "scripts/quality/fixtures/host_boundary_probe.py",
    # Cross-cutting normalization, VAE/list, event, and durable-preview seams.
    "tests/test_normalization_contracts.py",
    "tests/test_vae_list_contracts.py",
    "tests/test_safe_send_sync_contract.py",
    "tests/test_progressive_preview_event_contract.py",
    "tests/test_durable_final_preview_history.py",
    "tests/test_blend_contracts.py",
    "tests/test_background_remover_contract.py",
    "modules/tests/helpers/test_generated_preview.py",
    "modules/tests/helpers/test_process_and_save_image_contract.py",
    "modules/tests/helpers/test_parallel_list_contract.py",
    "modules/tests/helpers/test_safe_send_sync_ownership.py",
    # Interactive editor ownership and fail-closed recovery.
    "modules/tests/api/test_edit_dataset_recovery.py",
    "modules/tests/api/test_image_editor_process_ownership.py",
    # Public metadata/widget declarations plus high-risk production behavior.
    "modules/tests/test_frontend_widget_registry.py",
    "modules/tests/nodes/test_output_metadata_contract.py",
    "modules/tests/nodes/configuration/test_civitai_metadata_setup_contract.py",
    "modules/tests/nodes/filters/test_bloom_contract.py",
    "modules/tests/nodes/filters/test_filter_bhwc_contract.py",
    "modules/tests/nodes/filters/test_inpaint_list_contract.py",
    "modules/tests/nodes/image/test_alpha_filter_contracts.py",
    "modules/tests/nodes/image/test_image_to_svg_list_contract.py",
    "modules/tests/nodes/image/test_multiple_image_resize_contract.py",
    "modules/tests/nodes/image/test_resize_list_contracts.py",
    "modules/tests/nodes/image/test_tiled_super_res_contract.py",
    "modules/tests/nodes/image/test_view_svgs_contract.py",
    "modules/tests/nodes/image/test_compare_images.py",
    "modules/tests/nodes/image/test_empty_image.py",
    "modules/tests/nodes/image/test_image_grid.py",
    "modules/tests/nodes/image/test_image_list.py",
    "modules/tests/nodes/image/test_normalize_sprite_batch.py",
    "modules/tests/nodes/image/test_periodic_image_batch_sampler.py",
    "modules/tests/nodes/image/test_side_by_side.py",
    "modules/tests/nodes/io/test_load_metadata_contract.py",
    "modules/tests/nodes/io/test_save_image_for_civitai_contract.py",
    "modules/tests/nodes/io/test_text_savers.py",
    "modules/tests/nodes/json/test_set_value_in_json_contract.py",
    "modules/tests/nodes/json/test_string_to_json_contract.py",
    "modules/tests/nodes/llm/test_gemini_node.py",
    "modules/tests/nodes/llm/test_multimodal_payload_contract.py",
    "modules/tests/nodes/llm/test_openai_node.py",
    "modules/tests/nodes/llm/test_stability_schema.py",
    "modules/tests/nodes/logic/test_extract_prompt_from_lora_tag_contract.py",
    "modules/tests/nodes/logic/test_switch_tensor_contract.py",
    "modules/tests/nodes/primitives/test_something_2_string_contract.py",
    "modules/tests/nodes/regions/test_region_mask.py",
    "modules/tests/nodes/seeds/test_sequential_seeds_generator_contract.py",
    "modules/tests/nodes/selector/test_combo_transport_contract.py",
    "modules/tests/nodes/visual_novel/test_headless_import.py",
    # Release metadata, note generation, and publication workflow contracts.
    "modules/tests/test_generate_release_notes.py",
    "modules/tests/test_release_metadata.py",
    "modules/tests/test_release_workflows.py",
)

# These established suites install broader legacy import doubles while pytest
# collects them.  Each is still a production behavior contract, but a separate
# inert-host process prevents one suite's doubles from leaking into another.
ISOLATED_BEHAVIOR_TESTS: tuple[tuple[str, ...], ...] = (
    ("modules/tests/nodes/io/test_save_dds.py",),
    ("modules/tests/nodes/io/test_save_json.py",),
    ("modules/tests/nodes/io/test_register_output_file.py",),
    ("modules/tests/nodes/visual_novel/test_visual_novel.py",),
)


def all_behavior_tests() -> tuple[str, ...]:
    """Return every behavior path in deterministic execution order."""

    return BEHAVIOR_TESTS + tuple(
        path
        for group in ISOLATED_BEHAVIOR_TESTS
        for path in group
    )


def build_commands(python: str = sys.executable) -> tuple[tuple[str, ...], ...]:
    """Return the exact, reusable CI command sequence."""

    commands = (
        (python, "-m", "compileall", "-q", "modules", "scripts", "tests"),
        (python, "-I", str(QUALITY_ROOT / "check_node_contracts.py")),
        (
            python,
            "-I",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts/quality/tests",
            "-p",
            "test_*.py",
        ),
        (
            python,
            "-I",
            str(QUALITY_ROOT / "run_pytests.py"),
            "-q",
            *BEHAVIOR_TESTS,
        ),
    )
    isolated_commands = tuple(
        (
            python,
            "-I",
            str(QUALITY_ROOT / "run_pytests.py"),
            "-q",
            *group,
        )
        for group in ISOLATED_BEHAVIOR_TESTS
    )
    return commands + isolated_commands


def _run(command: Sequence[str]) -> None:
    printable = subprocess.list2cmdline(list(command))
    print(f"+ {printable}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    missing = [path for path in all_behavior_tests() if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(
            "CPU contract manifest references missing tests:\n- "
            + "\n- ".join(missing)
        )

    for command in build_commands():
        _run(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
