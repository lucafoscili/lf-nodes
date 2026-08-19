from dataclasses import FrozenInstanceError
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

from modules.workflow_runner.services import registry as registry_module
from modules.workflow_runner.services.registry import (
    WorkflowNode,
    WorkflowRegistry,
    WorkflowSubmissionPolicy,
    get_workflow_submission_policy,
)


def _workflow(
    policy: WorkflowSubmissionPolicy | None = None,
) -> WorkflowNode:
    return WorkflowNode(
        id="guarded_workflow",
        value="Guarded workflow",
        description="Exercises trusted submission metadata.",
        inputs=[],
        outputs=[],
        configure_prompt=lambda _prompt, _inputs: None,
        workflow_path=Path("unused.json"),
        category="Tests",
        submission_policy=policy,
    )


def test_submission_policy_is_validated_and_immutable() -> None:
    policy = WorkflowSubmissionPolicy(
        provider_id="example_guarded_v1",
        expected_vram_mb=18_400,
        max_duration_seconds=90,
        required=True,
    )

    assert policy.max_duration_seconds == 90.0
    assert policy.fail_closed is True
    with pytest.raises(FrozenInstanceError):
        policy.expected_vram_mb = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("provider_id", "", ValueError),
        ("provider_id", "provider with spaces", ValueError),
        ("provider_id", "x" * 129, ValueError),
        ("expected_vram_mb", 0, ValueError),
        ("expected_vram_mb", True, ValueError),
        ("expected_vram_mb", 1.5, ValueError),
        ("max_duration_seconds", 0, ValueError),
        ("max_duration_seconds", 1.5, ValueError),
        ("max_duration_seconds", True, ValueError),
        ("required", 1, TypeError),
    ],
    ids=[
        "empty-provider",
        "spaced-provider",
        "long-provider",
        "zero-vram",
        "bool-vram",
        "fractional-vram",
        "zero-duration",
        "fractional-duration",
        "bool-duration",
        "non-bool-required",
    ],
)
def test_submission_policy_rejects_invalid_metadata(
    field: str,
    value: object,
    error_type: type[Exception],
) -> None:
    kwargs = {
        "provider_id": "example_guarded_v1",
        "expected_vram_mb": 18_400,
        "max_duration_seconds": 90,
        "required": True,
    }
    kwargs[field] = value

    with pytest.raises(error_type):
        WorkflowSubmissionPolicy(**kwargs)  # type: ignore[arg-type]


def test_registry_keeps_submission_policy_server_side() -> None:
    policy = WorkflowSubmissionPolicy(
        provider_id="example_guarded_v1",
        expected_vram_mb=18_400,
        max_duration_seconds=90,
    )
    registry = WorkflowRegistry()
    registry.register(_workflow(policy))

    assert registry.get_submission_policy("guarded_workflow") is policy
    listed = registry.list()["nodes"][0]
    assert set(listed) == {
        "id",
        "value",
        "description",
        "category",
        "children",
    }
    assert "submissionPolicy" not in listed
    assert "submission_policy" not in listed


def test_legacy_workflow_has_no_submission_policy() -> None:
    registry = WorkflowRegistry()
    registry.register(_workflow())

    assert registry.get_submission_policy("guarded_workflow") is None
    assert registry.get_submission_policy("missing") is None


def test_global_accessor_reads_only_registered_metadata(monkeypatch) -> None:
    policy = WorkflowSubmissionPolicy("guard_v1", 8_192, 30)
    registry = WorkflowRegistry()
    registry.register(_workflow(policy))
    monkeypatch.setattr(registry_module, "REGISTRY", registry)
    monkeypatch.setattr(registry_module, "_registered", True)

    assert get_workflow_submission_policy("guarded_workflow") is policy
    assert get_workflow_submission_policy("missing") is None


def test_workflow_rejects_untyped_submission_policy() -> None:
    with pytest.raises(TypeError, match="WorkflowSubmissionPolicy"):
        _workflow({"provider_id": "untrusted"})  # type: ignore[arg-type]
