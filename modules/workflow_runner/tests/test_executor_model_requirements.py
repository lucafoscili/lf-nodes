"""Server-side admission for explicit local model prerequisites."""

import asyncio
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import executor
from modules.workflow_runner.workflows.orchestration import (
    character_turnaround_orchestra,
    identity_cleanup_restage,
)


def test_sequence_preparation_owns_no_comfy_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        executor,
        "get_workflow",
        lambda _workflow_id: identity_cleanup_restage,
    )

    definition, prompt = executor._prepare_workflow_execution(
        {"workflowId": identity_cleanup_restage.id, "inputs": {}}
    )

    assert definition is identity_cleanup_restage
    assert prompt == {}


def test_direct_executor_rejects_sequence_without_supervised_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        executor,
        "get_settings",
        lambda: SimpleNamespace(COMFY_BACKEND_URL="http://127.0.0.1:8188"),
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        asyncio.run(
            executor.prepare_workflow_submission(
                {"workflowId": identity_cleanup_restage.id, "inputs": {}},
                (identity_cleanup_restage, {}),
            )
        )

    assert error.value.status == 400
    assert error.value.response_body["payload"]["error"]["message"] == (
        "sequence_requires_supervised_runner"
    )


def test_setup_required_model_asset_fails_before_workflow_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = SimpleNamespace(
        load_prompt=lambda: pytest.fail("blocked setup must not load the graph"),
        configure_prompt=lambda *_args: pytest.fail(
            "blocked setup must not configure or queue the graph"
        ),
    )
    monkeypatch.setattr(executor, "get_workflow", lambda _workflow_id: definition)
    monkeypatch.setattr(
        executor,
        "evaluate_declared_model_assets",
        lambda _definition: {
            "status": "setup_required",
            "issues": [
                {
                    "code": "model_asset_missing",
                    "message": "Required local model asset is incomplete: example.",
                }
            ],
        },
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor._prepare_workflow_execution(
            {"workflowId": "example", "inputs": {}}
        )

    assert error.value.status == 409
    assert error.value.response_body["payload"]["error"]["message"] == (
        "workflow_setup_required"
    )
    assert error.value.response_body["payload"]["detail"] == (
        "Required local model asset is incomplete: example."
    )


def test_unavailable_selected_option_fails_before_graph_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requirement = SimpleNamespace(input_id="execution_profile")
    definition = SimpleNamespace(
        load_prompt=lambda: pytest.fail("blocked option must not load the graph"),
        configure_prompt=lambda *_args: pytest.fail(
            "blocked option must not configure or queue the graph"
        ),
    )
    monkeypatch.setattr(executor, "get_workflow", lambda _workflow_id: definition)
    monkeypatch.setattr(
        executor,
        "evaluate_declared_model_assets",
        lambda _definition: {"status": "ready", "issues": []},
    )
    monkeypatch.setattr(
        executor,
        "selected_input_option_requirements",
        lambda _definition, _inputs: (requirement,),
    )
    monkeypatch.setattr(
        executor,
        "evaluate_input_option_requirement",
        lambda _requirement: {
            "status": "setup_required",
            "issues": [
                {
                    "code": "option_node_missing",
                    "message": "Required Turbo node is not installed.",
                }
            ],
        },
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor._prepare_workflow_execution(
            {
                "workflowId": "example",
                "inputs": {"execution_profile": "turbo"},
            }
        )

    assert error.value.status == 409
    assert error.value.response_body["payload"]["error"] == {
        "message": "workflow_setup_required",
        "input": "execution_profile",
    }
    assert error.value.response_body["payload"]["detail"] == (
        "Required Turbo node is not installed."
    )


def test_sequence_stage_preflight_rejects_late_invalid_geometry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from modules.workflow_runner.services.sequence_runtime import (
        normalize_sequence_definition,
        sequence_stage_declared_inputs,
    )
    from modules.workflow_runner.services.registry import get_workflow

    plan = normalize_sequence_definition(
        character_turnaround_orchestra,
        {
            "source_image": "portable-input.png",
            "canvas_size": 1024,
            "content_height": 1000,
            "bottom_padding": 48,
        },
    )
    final_index = len(plan["stages"]) - 1
    block = get_workflow(plan["stages"][final_index]["workflow_id"])
    assert block is not None
    monkeypatch.setattr(executor, "validate_workflow_requirements", lambda *_args: None)
    monkeypatch.setattr(
        executor,
        "evaluate_workflow_readiness",
        lambda *_args, **_kwargs: pytest.fail(
            "invalid geometry must fail before the readiness scan"
        ),
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor.validate_sequence_stage_preflight(
            block,
            sequence_stage_declared_inputs(plan, final_index),
        )

    assert error.value.status == 400
    assert error.value.response_body["payload"]["error"]["message"] == "invalid_input"
    assert "content_height plus bottom_padding" in error.value.response_body[
        "payload"
    ]["detail"]


def test_sequence_stage_preflight_requires_a_portable_configurator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = SimpleNamespace(id="legacy-stage", configure_download=None)
    monkeypatch.setattr(executor, "validate_workflow_requirements", lambda *_args: None)
    monkeypatch.setattr(
        executor,
        "evaluate_workflow_readiness",
        lambda *_args, **_kwargs: pytest.fail(
            "a stage without portable configuration must fail first"
        ),
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor.validate_sequence_stage_preflight(definition, {})

    assert error.value.status == 500
    assert error.value.response_body["payload"]["error"]["message"] == (
        "sequence_stage_preflight_unavailable"
    )


@pytest.mark.parametrize("code", ["node_missing", "model_missing"])
def test_sequence_stage_preflight_rejects_unready_configured_graph(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
) -> None:
    definition = SimpleNamespace(
        id="final-stage",
        load_prompt=lambda: {"node": {"class_type": "Example", "inputs": {}}},
        configure_download=lambda _prompt, _inputs: None,
    )
    monkeypatch.setattr(executor, "validate_workflow_requirements", lambda *_args: None)
    monkeypatch.setattr(
        executor,
        "evaluate_workflow_readiness",
        lambda *_args, **_kwargs: {
            "status": "setup_required",
            "issues": [{"code": code, "message": "Final stage dependency is missing."}],
        },
    )

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor.validate_sequence_stage_preflight(definition, {})

    assert error.value.status == 409
    assert error.value.response_body["payload"]["error"]["message"] == (
        "workflow_setup_required"
    )
    assert error.value.response_body["payload"]["detail"] == (
        "Final stage dependency is missing."
    )


def test_sequence_stage_preflight_rejects_a_missing_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    definition = SimpleNamespace(
        id="final-stage",
        load_prompt=lambda: (_ for _ in ()).throw(FileNotFoundError("missing graph")),
        configure_download=lambda _prompt, _inputs: None,
    )
    monkeypatch.setattr(executor, "validate_workflow_requirements", lambda *_args: None)

    with pytest.raises(executor.WorkflowPreparationError) as error:
        executor.validate_sequence_stage_preflight(definition, {})

    assert error.value.status == 400
    assert error.value.response_body["payload"]["error"]["message"] == "missing_source"
