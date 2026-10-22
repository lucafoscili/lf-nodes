"""Offline contracts for every curated hero declared by a shipped workflow."""

from __future__ import annotations

from importlib import import_module
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


def _declared_heroes(shipped_workflows) -> dict[str, str]:
    return {
        workflow.id: workflow.card.hero.asset
        for workflow in shipped_workflows.values()
        if workflow.card is not None and workflow.card.hero is not None
    }


def test_every_hero_file_is_declared_by_a_shipped_workflow(shipped_workflows) -> None:
    declared = set(_declared_heroes(shipped_workflows).values())
    on_disk = {
        path.relative_to(_HERO_ROOT).as_posix()
        for path in _HERO_ROOT.rglob("*")
        if path.is_file()
    }

    assert declared, "The curated catalogue must contain at least one hero."
    assert on_disk == declared


def test_every_shipped_workflow_has_a_concise_catalogue_summary(shipped_workflows) -> None:
    missing = [
        workflow.id
        for workflow in shipped_workflows.values()
        if workflow.card is None or not workflow.card.summary
    ]

    assert missing == []
    assert all(len(workflow.card.summary) <= 180 for workflow in shipped_workflows.values())


def test_shipped_heroes_are_small_decodable_and_metadata_free(shipped_workflows) -> None:
    for workflow_id, asset in _declared_heroes(shipped_workflows).items():
        asset_path = (_HERO_ROOT / asset).resolve()

        assert asset_path.is_relative_to(_HERO_ROOT.resolve()), workflow_id
        assert asset_path.is_file(), workflow_id
        assert 0 < asset_path.stat().st_size <= 128 * 1024, workflow_id
        with Image.open(asset_path) as raster:
            assert raster.format == "WEBP", workflow_id
            assert raster.size == (960, 540), workflow_id
            assert raster.n_frames == 1, workflow_id
            raster.load()
            metadata_keys = {key.lower() for key in raster.info}
            assert metadata_keys.isdisjoint({"prompt", "workflow", "exif", "xmp"}), workflow_id
            assert not raster.getexif(), workflow_id
