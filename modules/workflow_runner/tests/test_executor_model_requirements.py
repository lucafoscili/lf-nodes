"""Server-side admission for explicit local model prerequisites."""

from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import executor


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
