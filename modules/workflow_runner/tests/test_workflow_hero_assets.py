"""Offline contracts for every curated hero declared by a shipped workflow."""

from __future__ import annotations

import hashlib
from importlib import import_module
import json
from pathlib import Path
from runpy import run_path
import sys
import types
from typing import Any

from PIL import Image
import pytest

# Match the declaration-only Krea fixtures without starting Comfy's host stack.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
active_conversion = sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)
# Sort JSON imports this pure helper at declaration time. Load its real function
# directly, without importing the conversion package's image/model dependencies.
if not hasattr(active_conversion, "convert_to_json"):
    active_conversion.convert_to_json = run_path(str(
        Path(__file__).resolve().parents[2] / "utils/helpers/conversion/convert_to_json.py"
    ))["convert_to_json"]

from modules.workflow_runner.workflows import _WORKFLOW_MODULES


_HERO_ROOT = (
    Path(__file__).resolve().parents[3]
    / "web/deploy/assets/workflow-runner/heroes"
)


@pytest.fixture(scope="module")
def samples() -> dict[str, Any]:
    return json.loads((_HERO_ROOT / "samples.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def shipped_workflows() -> dict[str, Any]:
    """Inspect only packaged declarations, never custom roots or runtime registry."""
    workflows = {}
    for module_name in _WORKFLOW_MODULES:
        module = import_module(f"modules.workflow_runner.workflows.{module_name}")
        definitions = getattr(module, "WORKFLOWS", None)
        if definitions is None:
            definition = getattr(module, "WORKFLOW", None)
            definitions = () if definition is None else (definition,)
        elif not isinstance(definitions, (list, tuple, set)):
            definitions = (definitions,)
        for definition in definitions:
            assert definition.id not in workflows, f"Duplicate shipped workflow: {definition.id}"
            workflows[definition.id] = definition
    return workflows


def test_shipped_hero_declarations_match_the_manifest_entries(samples, shipped_workflows) -> None:
    heroes = samples["heroes"]
    manifest_assets = {hero["workflowId"]: hero["asset"] for hero in heroes}
    declared_assets = {
        workflow.id: workflow.card.hero.asset
        for workflow in shipped_workflows.values()
        if workflow.card is not None and workflow.card.hero is not None
    }

    assert heroes, "The curated catalogue must contain at least one hero."
    assert len(heroes) == len(manifest_assets), "Duplicate hero workflowId in samples.json."
    assert declared_assets == manifest_assets


def test_shipped_heroes_are_small_decodable_and_metadata_free(samples) -> None:
    for hero in samples["heroes"]:
        workflow_id = hero["workflowId"]
        asset_path = (_HERO_ROOT / hero["asset"]).resolve()

        assert asset_path.is_relative_to(_HERO_ROOT.resolve()), workflow_id
        assert asset_path.is_file(), workflow_id
        assert 0 < asset_path.stat().st_size == hero["bytes"] <= 128 * 1024, workflow_id
        assert hashlib.sha256(asset_path.read_bytes()).hexdigest() == hero["sha256"], workflow_id
        with Image.open(asset_path) as raster:
            assert raster.format == "WEBP", workflow_id
            assert raster.size == (960, 540), workflow_id
            assert raster.n_frames == 1, workflow_id
            raster.load()
            metadata_keys = {key.lower() for key in raster.info}
            assert metadata_keys.isdisjoint({"prompt", "workflow", "exif", "xmp"}), workflow_id
            assert not raster.getexif(), workflow_id


def test_hero_sources_reference_recorded_runs_without_requiring_original_files(
    samples, shipped_workflows,
) -> None:
    sources = samples["sources"]
    for hero in samples["heroes"]:
        assert hero["sources"], hero["workflowId"]
        for source_id in hero["sources"]:
            assert source_id in sources, (hero["workflowId"], source_id)
            source = sources[source_id]
            assert source["workflowId"] in shipped_workflows, source_id
            assert isinstance(source["runId"], str) and source["runId"], source_id
            # The source may be a raster, decoded DDS, text rendering, or a
            # recorded preview. Original run files need not ship with the hero.


def test_orchestra_manifest_stages_use_the_block_source_runs(samples, shipped_workflows) -> None:
    declaration = shipped_workflows["identity_cleanup_restage"]
    orchestra = samples["orchestra"]
    sources = samples["sources"]
    heroes = {hero["workflowId"]: hero for hero in samples["heroes"]}

    assert orchestra["workflowId"] == declaration.id
    assert orchestra["status"] == "succeeded"
    assert orchestra["runId"]
    assert orchestra["stages"] == [stage.id for stage in declaration.stages]
    assert len(orchestra["stages"]) == 2
    stage_run_ids = []
    for stage in declaration.stages:
        source = sources[stage.id]
        assert source["workflowId"] == stage.workflow_id
        assert source["runId"]
        assert heroes[stage.workflow_id]["sources"][-1] == stage.id
        stage_run_ids.append(source["runId"])
    assert len(set(stage_run_ids)) == 2

    # The block cards expose each step; the orchestra compares the same initial
    # reference with the final stage result. No original output files are read.
    identity_sources = heroes[declaration.stages[0].workflow_id]["sources"]
    restage_sources = heroes[declaration.stages[1].workflow_id]["sources"]
    assert identity_sources[-1] == restage_sources[0]
    assert heroes[declaration.id]["sources"] == [
        identity_sources[0], restage_sources[-1]
    ]
