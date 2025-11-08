"""Finalize workflow success path using comfy_api_mock to avoid real network."""

import sys
from pathlib import Path
import pytest
from types import SimpleNamespace

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))


@pytest.mark.asyncio
async def test_finalize_workflow_fast_success(monkeypatch, comfy_api_mock):
    import types
    mock_install_util = types.ModuleType('utils.install_util')
    mock_install_util.get_missing_requirements_message = lambda: ""
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
