from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest


# The retention tests need only Workflow Runner's configured API prefix, not
# ComfyUI's GPU-heavy constants bootstrap.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
sys.modules.setdefault("modules.utils.constants", constants_module)

from modules.workflow_runner.services import background, job_store, job_store_sqlite


def test_runner_api_routes_await_background_lifecycle_startup() -> None:
    routes_path = Path(background.__file__).parents[1] / "controllers" / "api_routes.py"
    source = routes_path.read_text(encoding="utf-8")

    assert "async def _get_api_controllers" in source
    assert "await background.start_background_tasks(PromptServer.instance.app)" in source
    assert "api_controllers = _get_api_controllers()" not in source


@pytest.mark.asyncio
async def test_runner_api_loader_starts_background_tasks_before_controller_import(
    monkeypatch,
) -> None:
    routes_path = Path(background.__file__).parents[1] / "controllers" / "api_routes.py"
    module_name = "modules.workflow_runner.controllers._api_routes_lifecycle_test"

    class FakeRoutes:
        @staticmethod
        def get(_path):
            return lambda handler: handler

        @staticmethod
        def post(_path):
            return lambda handler: handler

    app = {}
    server_stub = types.ModuleType("server")
    server_stub.PromptServer = SimpleNamespace(
        instance=SimpleNamespace(app=app, routes=FakeRoutes())
    )
    config_stub = types.ModuleType("modules.workflow_runner.config")
    config_stub.API_ROUTE_PREFIX = "/api/lf-nodes"
    config_stub.get_settings = lambda: SimpleNamespace(WORKFLOW_RUNNER_ENABLED=True)
    starter = AsyncMock()
    controller_sentinel = object()

    monkeypatch.setattr(background, "start_background_tasks", starter)
    with monkeypatch.context() as context:
        context.setitem(sys.modules, "server", server_stub)
        context.setitem(sys.modules, "modules.workflow_runner.config", config_stub)
        spec = importlib.util.spec_from_file_location(module_name, routes_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        context.setitem(sys.modules, module_name, module)
        spec.loader.exec_module(module)
        import_controller = Mock(return_value=controller_sentinel)
        context.setattr(module.importlib, "import_module", import_controller)

        loaded = await module._get_api_controllers()

    assert loaded is controller_sentinel
    starter.assert_awaited_once_with(app)
    import_controller.assert_called_once_with(
        "lf_nodes.modules.workflow_runner.controllers.api_controllers"
    )


def _job(
    run_id: str,
    status: job_store.JobStatus,
    *,
    created_at: float,
    updated_at: float | None,
    comfy_url: str | None = "http://comfy:8188",
) -> job_store.Job:
    return job_store.Job(
        id=run_id,
        workflow_id="generic",
        status=status,
        created_at=created_at,
        updated_at=updated_at,
        seq=2,
        owner_id="owner-a",
        comfy_url=comfy_url,
    )


def test_queue_snapshot_requires_both_well_formed_active_queues() -> None:
    assert background._active_prompt_ids_from_queue(
        {
            "queue_pending": [[1, "pending-prompt", {}, {}]],
            "queue_running": [[0, "running-prompt", {}, {}]],
        }
    ) == {"pending-prompt", "running-prompt"}

    assert background._active_prompt_ids_from_queue({}) is None
    assert background._active_prompt_ids_from_queue(
        {"queue_pending": [], "queue_running": [[0]]}
    ) is None


@pytest.mark.asyncio
async def test_zero_ttl_disables_automatic_terminal_history_deletion() -> None:
    manager = types.SimpleNamespace(list_jobs=AsyncMock())

    removed = await background._prune_jobs_once(manager, now=10_000.0, ttl_seconds=0)

    assert removed == []
    manager.list_jobs.assert_not_awaited()


@pytest.mark.asyncio
async def test_pending_job_older_than_ten_minutes_is_never_made_terminal(
    monkeypatch,
) -> None:
    now = 10_000.0
    job_store._jobs["long-pending"] = _job(
        "long-pending",
        job_store.JobStatus.PENDING,
        created_at=now - 3_600.0,
        updated_at=now - 3_600.0,
    )
    queue_fetch = AsyncMock(return_value=set())
    monkeypatch.setattr(background, "fetch_active_prompt_ids", queue_fetch)

    removed = await background._prune_jobs_once(
        job_store,
        now=now,
        ttl_seconds=300.0,
    )

    assert removed == []
    assert job_store._jobs["long-pending"].status is job_store.JobStatus.PENDING
    queue_fetch.assert_not_awaited()


@pytest.mark.asyncio
async def test_reconciler_fails_old_active_job_only_after_verified_absence(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "orphaned-running"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    events = job_store.subscribe_events()
    session = comfy_api_mock(
        history_sequence=[{}, {}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == [(prompt_id, "failed")]
    updated = job_store._jobs[prompt_id]
    assert updated.status is job_store.JobStatus.FAILED
    assert updated.owner_id == "owner-a"
    assert updated.seq == 3
    assert updated.error == "execution_state_lost"
    assert updated.result["body"]["payload"]["error"]["message"] == "execution_state_lost"
    assert session._history_i == 2
    assert session._queue_i == 1
    event = events.get_nowait()
    assert event["run_id"] == prompt_id
    assert event["status"] == "failed"
    assert event["owner_id"] == "owner-a"
    assert event["seq"] == 3


@pytest.mark.asyncio
async def test_reconciler_preserves_active_prompt_in_verified_queue(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "still-running"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    session = comfy_api_mock(
        history_sequence=[{}],
        queue_sequence=[
            {"queue_pending": [], "queue_running": [[0, prompt_id, {}, {}]]}
        ],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.RUNNING
    assert session._history_i == 1


@pytest.mark.asyncio
async def test_reconciler_preserves_active_job_when_core_queue_is_unavailable(
    monkeypatch,
) -> None:
    now = 10_000.0
    prompt_id = "unverified-running"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    history_fetch = AsyncMock(return_value=(True, None))
    monkeypatch.setattr(
        background,
        "fetch_active_prompt_ids",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(background, "_fetch_prompt_history", history_fetch)

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=object(),
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.RUNNING
    assert history_fetch.await_count == 1


@pytest.mark.asyncio
async def test_reconciler_preserves_recent_active_job_even_with_empty_core(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "publication-grace"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.PENDING,
        created_at=now - 30.0,
        updated_at=now - 30.0,
    )
    session = comfy_api_mock(
        history_sequence=[{}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.PENDING
    assert session._queue_i == 0


@pytest.mark.asyncio
async def test_reconciler_preserves_legacy_active_job_without_backend_authority(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "legacy-unbound"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
        comfy_url=None,
    )
    session = comfy_api_mock(
        history_sequence=[{}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.RUNNING
    assert session._history_i == 0
    assert session._queue_i == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("history_status", "messages", "expected_status", "expected_error"),
    [
        ("success", [], job_store.JobStatus.SUCCEEDED, None),
        (
            "error",
            [["execution_error", {"exception_message": "model failed"}]],
            job_store.JobStatus.FAILED,
            "execution_failed",
        ),
        (
            "error",
            [["execution_interrupted", {"timestamp": 1}]],
            job_store.JobStatus.CANCELLED,
            None,
        ),
    ],
)
async def test_reconciler_publishes_actual_terminal_history_state(
    comfy_api_mock,
    history_status,
    messages,
    expected_status,
    expected_error,
) -> None:
    now = 10_000.0
    prompt_id = f"history-{expected_status.value}"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    history_entry = {
        "status": {
            "completed": True,
            "status_str": history_status,
            "messages": messages,
        },
        "outputs": {"save": {"images": [{"filename": "result.png"}]}},
    }
    session = comfy_api_mock(
        history_sequence=[{prompt_id: history_entry}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == [(prompt_id, expected_status.value)]
    updated = job_store._jobs[prompt_id]
    assert updated.status is expected_status
    assert updated.error == expected_error
    assert updated.result["body"]["payload"]["history"]["outputs"] == history_entry["outputs"]


@pytest.mark.asyncio
async def test_reconciler_rechecks_history_after_queue_before_declaring_state_lost(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "published-after-queue"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    history_entry = {
        "status": {"completed": True, "status_str": "success", "messages": []},
        "outputs": {"save": {"images": [{"filename": "late.png"}]}},
    }
    session = comfy_api_mock(
        history_sequence=[{}, {prompt_id: history_entry}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == [(prompt_id, "succeeded")]
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.SUCCEEDED
    assert job_store._jobs[prompt_id].error is None
    assert session._history_i == 2
    assert session._queue_i == 1


@pytest.mark.asyncio
async def test_reconciler_preserves_when_second_history_read_is_ambiguous(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "ambiguous-second-history"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    session = comfy_api_mock(
        history_sequence=[{}, {"different-prompt": {"outputs": {}}}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.RUNNING
    assert session._history_i == 2
    assert session._queue_i == 1


@pytest.mark.asyncio
async def test_reconciler_preserves_completed_history_with_unknown_status(
    comfy_api_mock,
) -> None:
    now = 10_000.0
    prompt_id = "future-history-status"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    session = comfy_api_mock(
        history_sequence=[
            {
                prompt_id: {
                    "status": {
                        "completed": True,
                        "status_str": "future-terminal",
                        "messages": [],
                    },
                    "outputs": {},
                }
            }
        ],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.RUNNING
    assert session._history_i == 1
    assert session._queue_i == 0


@pytest.mark.asyncio
async def test_reconciler_cas_does_not_overwrite_concurrent_cancellation(
    comfy_api_mock,
    monkeypatch,
) -> None:
    now = 10_000.0
    prompt_id = "cancel-race"
    job_store._jobs[prompt_id] = _job(
        prompt_id,
        job_store.JobStatus.RUNNING,
        created_at=now - 1_000.0,
        updated_at=now - 1_000.0,
    )
    original_cas = job_store.set_job_status_if_unchanged

    async def cancel_before_cas(*args, **kwargs):
        await job_store.set_job_status(prompt_id, job_store.JobStatus.CANCELLED)
        return await original_cas(*args, **kwargs)

    monkeypatch.setattr(
        job_store,
        "set_job_status_if_unchanged",
        cancel_before_cas,
    )
    session = comfy_api_mock(
        history_sequence=[{}],
        queue_sequence=[{"queue_pending": [], "queue_running": []}],
    )

    reconciled = await background._reconcile_active_jobs_once(
        job_store,
        now=now,
        grace_seconds=120.0,
        session=session,
    )

    assert reconciled == []
    assert job_store._jobs[prompt_id].status is job_store.JobStatus.CANCELLED


@pytest.mark.asyncio
async def test_retention_starts_at_terminal_updated_at(monkeypatch) -> None:
    now = 1_000.0
    job_store._jobs.update(
        {
            "recent-terminal": _job(
                "recent-terminal",
                job_store.JobStatus.SUCCEEDED,
                created_at=0.0,
                updated_at=900.0,
            ),
            "expired-terminal": _job(
                "expired-terminal",
                job_store.JobStatus.FAILED,
                created_at=0.0,
                updated_at=600.0,
            ),
            "unknown-terminal-time": _job(
                "unknown-terminal-time",
                job_store.JobStatus.CANCELLED,
                created_at=0.0,
                updated_at=None,
            ),
        }
    )
    monkeypatch.setattr(
        background,
        "fetch_active_prompt_ids",
        AsyncMock(return_value=set()),
    )

    removed = await background._prune_jobs_once(
        job_store,
        now=now,
        ttl_seconds=300.0,
    )

    assert removed == ["expired-terminal"]
    assert set(job_store._jobs) == {"recent-terminal", "unknown-terminal-time"}


@pytest.mark.asyncio
async def test_retention_preserves_comfy_pending_and_running_prompts(monkeypatch) -> None:
    job_store._jobs.update(
        {
            "comfy-pending": _job(
                "comfy-pending",
                job_store.JobStatus.FAILED,
                created_at=0.0,
                updated_at=100.0,
            ),
            "comfy-running": _job(
                "comfy-running",
                job_store.JobStatus.SUCCEEDED,
                created_at=0.0,
                updated_at=100.0,
            ),
            "inactive": _job(
                "inactive",
                job_store.JobStatus.CANCELLED,
                created_at=0.0,
                updated_at=100.0,
            ),
        }
    )
    monkeypatch.setattr(
        background,
        "fetch_active_prompt_ids",
        AsyncMock(return_value={"comfy-pending", "comfy-running"}),
    )

    removed = await background._prune_jobs_once(
        job_store,
        now=1_000.0,
        ttl_seconds=300.0,
    )

    assert removed == ["inactive"]
    assert set(job_store._jobs) == {"comfy-pending", "comfy-running"}


@pytest.mark.asyncio
async def test_retention_fails_safe_when_comfy_queue_is_unverified(monkeypatch) -> None:
    job_store._jobs["expired"] = _job(
        "expired",
        job_store.JobStatus.FAILED,
        created_at=0.0,
        updated_at=100.0,
    )
    monkeypatch.setattr(
        background,
        "fetch_active_prompt_ids",
        AsyncMock(return_value=None),
    )

    removed = await background._prune_jobs_once(
        job_store,
        now=1_000.0,
        ttl_seconds=300.0,
    )

    assert removed == []
    assert "expired" in job_store._jobs


@pytest.mark.asyncio
async def test_retention_hard_deletes_expired_sqlite_row(monkeypatch, tmp_path) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "retention.db"))
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", job_store_sqlite)
    monkeypatch.setattr(background, "fetch_active_prompt_ids", AsyncMock(return_value=set()))
    try:
        monkeypatch.setattr(job_store_sqlite.time, "time", lambda: 100.0)
        await job_store_sqlite.create_job("sqlite-expired", "generic", "owner-a")
        monkeypatch.setattr(job_store_sqlite.time, "time", lambda: 200.0)
        await job_store_sqlite.set_job_status("sqlite-expired", "succeeded")

        removed = await background._prune_jobs_once(
            job_store,
            now=501.0,
            ttl_seconds=300.0,
        )

        assert removed == ["sqlite-expired"]
        assert await job_store_sqlite.get_job("sqlite-expired") is None
    finally:
        await job_store_sqlite.close()
        job_store_sqlite.configure(None)


@pytest.mark.asyncio
async def test_reconciler_sqlite_cas_preserves_owner_and_publishes_event(
    comfy_api_mock,
    monkeypatch,
    tmp_path,
) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "reconcile.db"))
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", job_store_sqlite)
    events = job_store_sqlite.subscribe_events()
    try:
        monkeypatch.setattr(job_store_sqlite.time, "time", lambda: 100.0)
        await job_store.create_job(
            "sqlite-orphan",
            "generic",
            owner_id="owner-a",
            submission_id="sqlite-orphan-submission",
            request_fingerprint="a" * 64,
            comfy_url="http://comfy:8188",
        )
        events.get_nowait()
        session = comfy_api_mock(
            history_sequence=[{}],
            queue_sequence=[{"queue_pending": [], "queue_running": []}],
        )

        reconciled = await background._reconcile_active_jobs_once(
            job_store,
            now=1_000.0,
            grace_seconds=120.0,
            session=session,
        )

        assert reconciled == [("sqlite-orphan", "failed")]
        updated = await job_store_sqlite.get_job("sqlite-orphan")
        assert updated is not None
        assert updated.status == "failed"
        assert updated.owner_id == "owner-a"
        assert updated.seq == 1
        event = events.get_nowait()
        assert event["run_id"] == "sqlite-orphan"
        assert event["status"] == "failed"
        assert event["owner_id"] == "owner-a"
        assert event["seq"] == 1
    finally:
        job_store_sqlite.unsubscribe_events(events)
        await job_store_sqlite.close()
        job_store_sqlite.configure(None)
