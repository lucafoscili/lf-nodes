from pathlib import Path
import sys
import types

import pytest

# Registry needs only ``json_safe``. Keep this pure contract test independent
# from ComfyUI, Torch, and LF's optional conversion dependencies.
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import WorkflowNode, WorkflowRegistry


def _workflow() -> WorkflowNode:
    return WorkflowNode(
        id="example_workflow",
        value="Example workflow",
        description="Exercises registry provenance.",
        inputs=[],
        outputs=[],
        configure_prompt=lambda _prompt, _inputs: None,
        workflow_path=Path("unused.json"),
        category="Tests",
    )


def test_registry_lists_only_catalogue_fields() -> None:
    registry = WorkflowRegistry()
    registry.register(
        _workflow(),
        origin="shipped",
        collection="LF Nodes",
    )

    listed = registry.list()["nodes"][0]
    assert set(listed) == {
        "id",
        "value",
        "description",
        "category",
        "kind",
        "origin",
        "collection",
        "readiness",
        "children",
    }
    assert listed["origin"] == "shipped"
    assert listed["kind"] == "block"
    assert listed["collection"] == "LF Nodes"
    assert listed["readiness"]["status"] == "setup_required"
    assert listed["readiness"]["issues"][0]["code"] == "workflow_file_missing"


def test_unmarked_duck_typed_registration_fails_closed_to_custom() -> None:
    definition = types.SimpleNamespace(
        id="unmarked_workflow",
        value="Unmarked workflow",
        description="No trusted packaged provenance.",
        category="Tests",
        cells_as_dict=lambda _direction: {},
    )
    registry = WorkflowRegistry()
    registry.register(definition)  # type: ignore[arg-type]

    listed = registry.list()["nodes"][0]
    assert listed["origin"] == "custom"
    assert listed["collection"] == "Custom"


def test_direct_workflow_node_registration_cannot_claim_shipped_defaults() -> None:
    registry = WorkflowRegistry()
    registry.register(_workflow())

    listed = registry.list()["nodes"][0]
    assert listed["origin"] == "custom"
    assert listed["collection"] == "Custom"
