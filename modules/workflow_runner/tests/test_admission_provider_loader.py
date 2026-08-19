"""Contract tests for the workflow-admission provider entry-point loader."""

from __future__ import annotations

import pytest

from modules.workflow_runner.services import admission


class _Provider:
    provider_id = "velora_guarded_v1"

    async def acquire(self, request):  # pragma: no cover - loader shape only
        raise AssertionError("loader tests must not acquire GPU admission")


class _EntryPoint:
    group = "lf_nodes.workflow_admission_providers"

    def __init__(self, name, factory):
        self.name = name
        self._factory = factory

    def load(self):
        return self._factory


class _EntryPoints(tuple):
    def select(self, **criteria):
        return _EntryPoints(
            entry_point
            for entry_point in self
            if all(getattr(entry_point, key) == value for key, value in criteria.items())
        )


def _install_entry_points(monkeypatch, *entry_points):
    monkeypatch.setattr(
        admission.importlib.metadata,
        "entry_points",
        lambda: _EntryPoints(entry_points),
    )


@pytest.fixture(autouse=True)
def _restore_provider_state(monkeypatch):
    previous = admission.get_workflow_admission_provider()
    previous_initialized = admission._environment_provider_initialized
    monkeypatch.delenv("WORKFLOW_RUNNER_SUBMISSION_PROVIDER", raising=False)
    yield
    admission.set_workflow_admission_provider(previous)
    admission._environment_provider_initialized = previous_initialized


def test_loader_binds_provider_to_the_exact_active_context_type(monkeypatch):
    calls = []

    def create_provider(*, prompt_context_type, submission_rejected_type):
        calls.append((prompt_context_type, submission_rejected_type))
        return _Provider()

    _install_entry_points(
        monkeypatch,
        _EntryPoint("velora_guarded_v1", create_provider),
    )

    provider = admission.configure_workflow_admission_from_environment(
        "velora_guarded_v1"
    )

    assert provider.provider_id == "velora_guarded_v1"
    assert calls == [
        (
            admission.WorkflowPromptContext,
            admission.WorkflowSubmissionRejectedBeforeQueue,
        )
    ]
    assert admission.get_workflow_admission_provider() is provider


def test_loader_rejects_unknown_selector(monkeypatch):
    _install_entry_points(monkeypatch)

    with pytest.raises(RuntimeError, match="no installed.*arbitrary.module"):
        admission.configure_workflow_admission_from_environment("arbitrary.module")


def test_loader_rejects_duplicate_selector(monkeypatch):
    _install_entry_points(
        monkeypatch,
        _EntryPoint("velora_guarded_v1", lambda **kwargs: _Provider()),
        _EntryPoint("velora_guarded_v1", lambda **kwargs: _Provider()),
    )

    with pytest.raises(RuntimeError, match="multiple.*velora_guarded_v1"):
        admission.configure_workflow_admission_from_environment(
            "velora_guarded_v1"
        )


def test_loader_rejects_provider_id_mismatch(monkeypatch):
    class WrongProvider(_Provider):
        provider_id = "wrong"

    _install_entry_points(
        monkeypatch,
        _EntryPoint("velora_guarded_v1", lambda **kwargs: WrongProvider()),
    )

    with pytest.raises(RuntimeError, match="returned wrong id"):
        admission.configure_workflow_admission_from_environment(
            "velora_guarded_v1"
        )


def test_absent_selector_preserves_programmatic_provider(monkeypatch):
    provider = _Provider()
    admission.set_workflow_admission_provider(provider)
    admission._environment_provider_initialized = False
    monkeypatch.setattr(
        admission.importlib.metadata,
        "entry_points",
        lambda: (_ for _ in ()).throw(AssertionError("must not discover")),
    )

    configured = admission.configure_workflow_admission_from_environment("")

    assert configured is provider
