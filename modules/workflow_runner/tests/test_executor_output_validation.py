"""Core's partial acceptance must not discard required Runner results."""

from __future__ import annotations

import asyncio
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


# Exercise Runner's queue boundary without importing Comfy's GPU runtime.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
sys.modules.setdefault("modules.utils.constants", constants_module)

if "execution" not in sys.modules:
    execution_module = types.ModuleType("execution")
    execution_module.validate_prompt = AsyncMock()
    sys.modules["execution"] = execution_module

from modules.workflow_runner.services import executor
from modules.workflow_runner.services.registry import WorkflowCell


@pytest.fixture
def validation_boundary(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    monkeypatch.setattr(
        executor,
        "get_settings",
        lambda: SimpleNamespace(COMFY_BACKEND_URL="http://127.0.0.1:8188"),
    )
    validate = AsyncMock()
    acquire = AsyncMock(side_effect=AssertionError("must reject before admission"))
    post = AsyncMock(side_effect=AssertionError("must reject before queueing"))
    monkeypatch.setattr(executor.execution, "validate_prompt", validate)
    monkeypatch.setattr(executor, "acquire_default_workflow_admission", acquire)
    monkeypatch.setattr(executor, "post_workflow_submission", post)
    return SimpleNamespace(validate=validate, acquire=acquire, post=post)


def _definition(*, optional: bool = False) -> SimpleNamespace:
    # Two result cells may use the same output node (as in Image to SVG).
    return SimpleNamespace(
        outputs=(
            WorkflowCell(id="svg_file", node_id="20"),
            WorkflowCell(id="svg_data", node_id="20"),
            WorkflowCell(id="png", node_id="61", required=not optional),
        ),
        submission_policy=None,
    )


def _source_error(*dependent_outputs: str) -> dict:
    return {
        "source": {
            "errors": [
                {
                    "type": "custom_validation_failed",
                    "message": "Custom validation failed for node",
                    "details": "Invalid image file: missing-source.png",
                }
            ],
            "dependent_outputs": list(dependent_outputs),
            "class_type": "LoadImage",
        }
    }


@pytest.mark.parametrize("validated", [("20", "61", "29"), ("20", "61")])
def test_all_required_outputs_allow_submission(validation_boundary, validated):
    validation = (True, None, list(validated), {})
    validation_boundary.validate.return_value = validation
    prompt = {node_id: {"class_type": "Output", "inputs": {}} for node_id in validated}

    request = asyncio.run(
        executor.prepare_workflow_submission(
            {"workflowId": "image_to_svg"}, (_definition(), prompt)
        )
    )

    assert request.prompt == prompt
    assert request.validation == (True, None, validated, {})
    validation_boundary.validate.assert_awaited_once()


def test_validated_output_root_covers_required_upstream_result(validation_boundary):
    definition = SimpleNamespace(
        outputs=(WorkflowCell(id="preview", node_id="20"),),
        submission_policy=None,
    )
    prompt = {
        "20": {"class_type": "PreviewValue", "inputs": {}},
        "61": {
            "class_type": "SaveImage",
            "inputs": {"images": ["20", 0]},
        },
    }
    validation_boundary.validate.return_value = (True, None, ["61"], {})

    request = asyncio.run(
        executor.prepare_workflow_submission(
            {"workflowId": "upstream-preview"},
            (definition, prompt),
        )
    )

    assert set(request.prompt) == {"20", "61"}
    assert request.validation[2] == ("61",)


def test_validated_output_root_does_not_cover_disconnected_result(validation_boundary):
    definition = SimpleNamespace(
        outputs=(WorkflowCell(id="preview", node_id="20"),),
        submission_policy=None,
    )
    prompt = {
        "20": {"class_type": "PreviewValue", "inputs": {}},
        "61": {"class_type": "SaveImage", "inputs": {}},
    }
    validation_boundary.validate.return_value = (True, None, ["61"], {})

    with pytest.raises(executor.WorkflowPreparationError) as error:
        asyncio.run(
            executor.prepare_workflow_submission(
                {"workflowId": "disconnected-preview"},
                (definition, prompt),
            )
        )

    assert error.value.response_body["payload"]["detail"] == (
        "Required workflow outputs failed validation: 20."
    )


@pytest.mark.parametrize(
    ("validated", "missing"),
    [(["29"], "20, 61"), (["20", "29"], "61"), ([], "20, 61")],
)
def test_partial_or_empty_acceptance_fails_before_queue(
    validation_boundary, validated, missing
):
    node_errors = _source_error("20", "61")
    validation_boundary.validate.return_value = (True, None, validated, node_errors)

    with pytest.raises(executor.WorkflowPreparationError) as error:
        asyncio.run(
            executor.submit_workflow(
                {"workflowId": "image_to_svg"}, (_definition(), {})
            )
        )

    assert error.value.status == 400
    payload = error.value.response_body["payload"]
    assert payload["error"]["message"] == "validation_failed"
    assert payload["detail"] == f"Required workflow outputs failed validation: {missing}."
    assert payload["history"] == {"outputs": {}, "node_errors": node_errors}
    validation_boundary.acquire.assert_not_awaited()
    validation_boundary.post.assert_not_awaited()


@pytest.mark.parametrize("optional", [False, True])
def test_unrelated_or_optional_output_errors_do_not_block(
    validation_boundary, optional
):
    validated = ["20"] if optional else ["20", "61"]
    node_errors = _source_error("61" if optional else "unused-preview")
    validation = (True, None, validated, node_errors)
    validation_boundary.validate.return_value = validation

    request = asyncio.run(
        executor.prepare_workflow_submission(
            {"workflowId": "example"}, (_definition(optional=optional), {})
        )
    )

    assert request.validation[:3] == (True, None, tuple(validated))
    retained_error = request.validation[3]["source"]
    assert retained_error["errors"][0] == node_errors["source"]["errors"][0]
    assert retained_error["dependent_outputs"] == tuple(
        node_errors["source"]["dependent_outputs"]
    )


def test_legacy_definition_without_outputs_keeps_existing_admission(validation_boundary):
    validation_boundary.validate.return_value = (True, None, [], {})

    request = asyncio.run(
        executor.prepare_workflow_submission(
            {"workflowId": "legacy"}, (SimpleNamespace(submission_policy=None), {})
        )
    )

    assert request.validation == (True, None, (), {})


def test_core_rejection_preserves_its_original_error(validation_boundary):
    node_errors = _source_error("20", "61")
    core_error = {"type": "prompt_outputs_failed_validation", "message": "No valid outputs"}
    validation_boundary.validate.return_value = (False, core_error, [], node_errors)

    with pytest.raises(executor.WorkflowPreparationError) as error:
        asyncio.run(
            executor.prepare_workflow_submission(
                {"workflowId": "example"}, (_definition(), {})
            )
        )

    payload = error.value.response_body["payload"]
    assert payload["detail"] == core_error
    assert payload["history"]["node_errors"] == node_errors


def test_validation_crash_cannot_bypass_required_output_coverage(validation_boundary):
    validation_boundary.validate.side_effect = RuntimeError("validator unavailable")

    with pytest.raises(executor.WorkflowPreparationError) as error:
        asyncio.run(
            executor.submit_workflow(
                {"workflowId": "example"}, (_definition(), {})
            )
        )

    assert error.value.response_body["payload"]["error"]["message"] == "validation_failed"
    validation_boundary.acquire.assert_not_awaited()
    validation_boundary.post.assert_not_awaited()
