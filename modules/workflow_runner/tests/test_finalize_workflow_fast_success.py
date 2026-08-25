"""Finalize workflow success path using comfy_api_mock to avoid real network."""

import sys
from pathlib import Path
import pytest

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

@pytest.mark.asyncio
async def test_finalize_workflow_fast_success(monkeypatch, comfy_api_mock):
    import types
    mock_install_util = types.ModuleType('utils.install_util')
    mock_install_util.get_missing_requirements_message = lambda: ""
    mock_install_util.get_required_packages_versions = lambda: {}
    mock_install_util.requirements_path = Path("/tmp/requirements.txt")
    monkeypatch.setitem(sys.modules, 'utils.install_util', mock_install_util)

    mock_json_util = types.ModuleType('utils.json_util')
    mock_json_util.merge_json_recursive = lambda *args: {}
    monkeypatch.setitem(sys.modules, 'utils.json_util', mock_json_util)

    from modules.workflow_runner.services.executor import finalize_workflow, submit_workflow, _wait_for_completion
    from modules.workflow_runner.services.executor import _make_run_payload
    from modules.workflow_runner.services.job_store import JobStatus

    # Prepare fake workflow definition so submit_workflow passes
    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services import registry

    class FakeDefinition:
        id = "wf-fast"
        value = "wf-fast"
        description = "fast wf"
        category = "test"
        workflow_path = Path(__file__)  # not read; load_prompt overridden
        inputs = []
        outputs = []
        def load_prompt(self):
            return {"1": {"class_type": "Test", "inputs": {}}}
        def configure_prompt(self, prompt, inputs):
            return
        def cells_as_dict(self, *_):
            return {}

    registry.REGISTRY.register(FakeDefinition())

    # Monkeypatch validate_prompt to succeed quickly
    async def fake_validate(prompt_id, prompt, _):
        return (True, "", ["1"], [])
    monkeypatch.setattr(executor.execution, "validate_prompt", fake_validate)

    # Configure mocked HTTP polling sequence: history shows immediate success
    prompt_id_placeholder = "prompt-fast-1"
    history_seq = [{prompt_id_placeholder: {"status": {"status_str": "success", "completed": True}, "outputs": {"1": {"images": []}}}}]
    queue_seq = [{"queue_running": [], "queue_pending": []}]
    # Patch aiohttp session factory used inside finalize_workflow/_wait_for_completion
    def session_factory():
        return comfy_api_mock(history_seq, queue_seq)
    monkeypatch.setattr("aiohttp.ClientSession", session_factory)

    # submit_workflow constructs body but we intercept network so supply prepared tuple directly
    definition = FakeDefinition()
    prepared = (definition, definition.load_prompt())
    payload = {"workflowId": definition.id, "inputs": {}}
    prompt_id, client_id, comfy_url, prompt, validation, wf_id = await submit_workflow(payload, prepared)

    # Overwrite returned prompt_id with our placeholder so history_seq matches
    prompt_id = prompt_id_placeholder
    status, response, http_status = await finalize_workflow(prompt_id, client_id, comfy_url, validation)

    assert status == JobStatus.SUCCEEDED
    assert http_status == 200
    assert response["payload"]["preferred_output"] == "1"


@pytest.mark.asyncio
async def test_finalize_workflow_preserves_bounded_comfy_execution_error(
    monkeypatch, comfy_api_mock
):
    """Expose Comfy's exception message without returning unbounded diagnostics."""
    import types

    mock_install_util = types.ModuleType("utils.install_util")
    mock_install_util.get_missing_requirements_message = lambda: ""
    mock_install_util.get_required_packages_versions = lambda: {}
    mock_install_util.requirements_path = Path("/tmp/requirements.txt")
    monkeypatch.setitem(sys.modules, "utils.install_util", mock_install_util)

    mock_json_util = types.ModuleType("utils.json_util")
    mock_json_util.merge_json_recursive = lambda *args: {}
    monkeypatch.setitem(sys.modules, "utils.json_util", mock_json_util)
    monkeypatch.setenv("LF_RUNNER_TEST_FAST", "1")

    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.job_store import JobStatus

    prompt_id = "prompt-error-1"
    exception_message = "Node failed: " + ("x" * 5000)
    history = {
        prompt_id: {
            "status": {
                "status_str": "error",
                "completed": True,
                "messages": [
                    [
                        "execution_error",
                        {
                            "exception_message": exception_message,
                            "traceback": ["private diagnostic details"],
                        },
                    ]
                ],
            },
            "outputs": {},
        }
    }
    monkeypatch.setattr(
        "aiohttp.ClientSession",
        lambda: comfy_api_mock([history], [{"queue_running": [], "queue_pending": []}]),
    )

    status, response, http_status = await executor.finalize_workflow(
        prompt_id, "client-error-1", "http://127.0.0.1:8188", (True, "", [], []),
    )

    detail = response["payload"]["detail"]
    assert status == JobStatus.FAILED
    assert http_status == 500
    assert detail.startswith("Node failed: ")
    assert len(detail.encode("utf-8")) <= 4096
    assert response["payload"]["error"]["message"] == "execution_failed"
    assert "private diagnostic details" not in detail


@pytest.mark.asyncio
async def test_finalize_workflow_prefers_durable_media_over_observational_output(
    monkeypatch, comfy_api_mock
):
    """A grid's temp LF dataset must not outrank its downstream saved sheet."""
    import types

    mock_install_util = types.ModuleType("utils.install_util")
    mock_install_util.get_missing_requirements_message = lambda: ""
    mock_install_util.get_required_packages_versions = lambda: {}
    mock_install_util.requirements_path = Path("/tmp/requirements.txt")
    monkeypatch.setitem(sys.modules, "utils.install_util", mock_install_util)

    mock_json_util = types.ModuleType("utils.json_util")
    mock_json_util.merge_json_recursive = lambda *args: {}
    monkeypatch.setitem(sys.modules, "utils.json_util", mock_json_util)

    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.job_store import JobStatus

    prompt_id = "prompt-sheet-1"
    history = {
        prompt_id: {
            "status": {"status_str": "success", "completed": True},
            "outputs": {
                "grid": {"lf_output": [{"dataset": {"nodes": []}}]},
                "save": {
                    "images": [
                        {
                            "filename": "sheet.png",
                            "subfolder": "LF_Nodes/ImageSheet",
                            "type": "output",
                        }
                    ]
                },
                "receipt": {"lf_output": [{"json": {"schema": "receipt"}}]},
            },
        }
    }
    monkeypatch.setattr(
        "aiohttp.ClientSession",
        lambda: comfy_api_mock([history], [{"queue_running": [], "queue_pending": []}]),
    )

    status, response, http_status = await executor.finalize_workflow(
        prompt_id,
        "client-sheet-1",
        "http://127.0.0.1:8188",
        (True, "", ["grid", "save", "receipt"], []),
    )

    assert status == JobStatus.SUCCEEDED
    assert http_status == 200
    assert response["payload"]["preferred_output"] == "save"
