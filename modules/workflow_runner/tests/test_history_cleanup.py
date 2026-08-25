from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


# This suite exercises Runner cleanup/controller seams, not ComfyUI execution.
# Install the narrow runtime ABIs before importing the controller so collection
# remains deterministic on machines without Comfy's optional GPU extensions.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
sys.modules.setdefault("modules.utils.constants", constants_module)

if "execution" not in sys.modules:
    execution_module = types.ModuleType("execution")

    async def _validate_prompt(*args, **kwargs):
        return True, "", (), ()

    execution_module.validate_prompt = _validate_prompt  # type: ignore[attr-defined]
    sys.modules["execution"] = execution_module

if "server" not in sys.modules:
    server_module = types.ModuleType("server")
    server_module.PromptServer = SimpleNamespace(  # type: ignore[attr-defined]
        instance=SimpleNamespace(loop=None)
    )
    sys.modules["server"] = server_module

if "modules.utils.helpers" not in sys.modules:
    helpers_module = types.ModuleType("modules.utils.helpers")
    helpers_module.__path__ = []  # type: ignore[attr-defined]
    sys.modules["modules.utils.helpers"] = helpers_module

if "modules.utils.helpers.conversion" not in sys.modules:
    conversion_module = types.ModuleType("modules.utils.helpers.conversion")
    conversion_module.json_safe = lambda value: value  # type: ignore[attr-defined]
    sys.modules["modules.utils.helpers.conversion"] = conversion_module

if "modules.utils.helpers.comfy" not in sys.modules:
    comfy_helpers_module = types.ModuleType("modules.utils.helpers.comfy")
    comfy_helpers_module.safe_send_sync = lambda *args, **kwargs: None  # type: ignore[attr-defined]
    sys.modules["modules.utils.helpers.comfy"] = comfy_helpers_module

import modules.workflow_runner.controllers.api_controllers as api_controllers
from modules.workflow_runner.services import history_cleanup, job_store, job_store_sqlite


@pytest.fixture(autouse=True)
def verified_empty_comfy_queue(monkeypatch) -> None:
    """Destructive cleanup tests opt into a proven-empty Comfy queue."""

    monkeypatch.setattr(
        history_cleanup,
        "fetch_active_prompt_ids",
        AsyncMock(return_value=set()),
    )


def _result(*outputs: dict) -> dict:
    return {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        str(index): output for index, output in enumerate(outputs)
                    }
                }
            }
        }
    }


def _descriptor(filename: str, *, storage_type: str = "output", subfolder: str = "") -> dict:
    return {
        "images": [
            {
                "filename": filename,
                "subfolder": subfolder,
                "type": storage_type,
            }
        ]
    }


def _roots(tmp_path: Path) -> dict[str, Path]:
    roots = {kind: tmp_path / kind for kind in ("input", "output", "temp")}
    for root in roots.values():
        root.mkdir()
    return roots


def _job(
    run_id: str,
    status: job_store.JobStatus,
    *,
    owner_id: str | None = None,
    result=None,
    seq: int = 3,
) -> job_store.Job:
    return job_store.Job(
        id=run_id,
        workflow_id="generic",
        status=status,
        owner_id=owner_id,
        result=result,
        seq=seq,
        updated_at=1234.5,
    )


def test_succeeded_result_requires_every_recorded_artifact_to_be_missing(tmp_path: Path) -> None:
    roots = _roots(tmp_path)
    (roots["output"] / "kept.png").write_bytes(b"png")

    mixed = _result(_descriptor("gone.png"), _descriptor("kept.png"))
    missing = _result(
        _descriptor("gone.png"),
        _descriptor("also-gone.png", storage_type="temp"),
    )

    assert history_cleanup.classify_succeeded_result("mixed", mixed, roots=roots) == "resolvable"
    assert history_cleanup.classify_succeeded_result("missing", missing, roots=roots) == "missing"


def test_legacy_lf_file_names_are_resolved_under_output_root(tmp_path: Path) -> None:
    roots = _roots(tmp_path)
    nested = roots["output"] / "receipts"
    nested.mkdir()
    (nested / "kept.dds").write_bytes(b"dds")
    result = _result(
        {
            "lf_output": [
                {"file_names": ["receipts/kept.dds", "receipts/gone.dds"]}
            ]
        }
    )

    assert history_cleanup.classify_succeeded_result("legacy", result, roots=roots) == "resolvable"


@pytest.mark.parametrize(
    "result",
    [
        None,
        {},
        _result({"json": {"message": "valid fileless output"}}),
        _result(_descriptor("../escape.png")),
        _result(
            _descriptor("valid.png"),
            {"images": [{"filename": "bad.png", "subfolder": "../escape", "type": "output"}]},
        ),
        _result({"lf_output": [{"file_names": "not-a-list.png"}]}),
    ],
)
def test_ambiguous_malformed_and_fileless_successes_are_unknown(tmp_path: Path, result) -> None:
    assert history_cleanup.classify_succeeded_result(
        "unknown",
        result,
        roots=_roots(tmp_path),
    ) == "unknown"


def test_truncated_traversal_and_unavailable_root_are_unknown(tmp_path: Path) -> None:
    nested: dict = {"filename": "gone.png", "type": "output"}
    for _ in range(40):
        nested = {"child": nested}
    assert history_cleanup.classify_succeeded_result(
        "deep",
        _result(nested),
        roots=_roots(tmp_path),
    ) == "unknown"

    assert history_cleanup.classify_succeeded_result(
        "permission",
        _result(_descriptor("gone.png")),
        roots={"input": tmp_path, "output": None, "temp": tmp_path},
    ) == "unknown"


def test_arbitrary_json_filename_is_not_treated_as_a_comfy_artifact(tmp_path: Path) -> None:
    roots = _roots(tmp_path)
    result = _result(
        {
            "json": {
                "filename": "story-metadata.txt",
                "description": "A domain payload, not a Comfy file descriptor.",
            }
        }
    )

    assert history_cleanup.classify_succeeded_result(
        "metadata",
        result,
        roots=roots,
    ) == "unknown"


@pytest.mark.asyncio
async def test_dry_run_scans_all_owner_rows_without_mutating(tmp_path: Path, monkeypatch) -> None:
    roots = _roots(tmp_path)
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: roots)
    job_store._jobs.update(
        {
            "missing": _job(
                "missing",
                job_store.JobStatus.SUCCEEDED,
                owner_id="owner-a",
                result=_result(_descriptor("gone.png")),
            ),
            "failed": _job("failed", job_store.JobStatus.FAILED, owner_id="owner-a"),
            "cancelled": _job("cancelled", job_store.JobStatus.CANCELLED, owner_id="owner-a"),
            "timeout": _job("timeout", job_store.JobStatus.TIMEOUT, owner_id="owner-a"),
            "unknown": _job(
                "unknown",
                job_store.JobStatus.SUCCEEDED,
                owner_id="owner-a",
                result=_result({"json": {"ok": True}}),
            ),
            "running": _job("running", job_store.JobStatus.RUNNING, owner_id="owner-a"),
            "other-owner": _job("other-owner", job_store.JobStatus.FAILED, owner_id="owner-b"),
        }
    )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a", dry_run=True, candidate_run_ids=None
    )

    assert response == {
        "dry_run": True,
        "candidate_count": 4,
        "candidate_run_ids": ["cancelled", "failed", "missing", "timeout"],
        "removed_count": 0,
        "removed_run_ids": [],
        "skipped_unknown": 1,
        "skipped_changed": 0,
    }
    assert set(job_store._jobs) == {
        "missing",
        "failed",
        "cancelled",
        "timeout",
        "unknown",
        "running",
        "other-owner",
    }


@pytest.mark.asyncio
async def test_cleanup_scan_is_not_limited_to_history_card_page_size(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: _roots(tmp_path))
    for index in range(205):
        run_id = f"failed-{index:03d}"
        job_store._jobs[run_id] = _job(
            run_id,
            job_store.JobStatus.FAILED,
            owner_id="owner-a",
        )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=True,
        candidate_run_ids=None,
    )

    assert response["candidate_count"] == 205
    assert len(job_store._jobs) == 205


@pytest.mark.asyncio
async def test_execute_hard_deletes_candidates_and_preserves_unknown_active_and_other_owner(
    tmp_path: Path, monkeypatch
) -> None:
    roots = _roots(tmp_path)
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: roots)
    job_store._jobs.update(
        {
            "missing": _job(
                "missing",
                job_store.JobStatus.SUCCEEDED,
                owner_id="owner-a",
                result=_result(_descriptor("gone.png")),
            ),
            "failed": _job("failed", job_store.JobStatus.FAILED, owner_id="owner-a"),
            "unknown": _job(
                "unknown",
                job_store.JobStatus.SUCCEEDED,
                owner_id="owner-a",
                result=_result({"json": {"ok": True}}),
            ),
            "pending": _job("pending", job_store.JobStatus.PENDING, owner_id="owner-a"),
            "other-owner": _job("other-owner", job_store.JobStatus.FAILED, owner_id="owner-b"),
        }
    )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=False,
        candidate_run_ids=["failed", "missing"],
    )

    assert response["candidate_count"] == 2
    assert response["removed_count"] == 2
    assert response["removed_run_ids"] == ["failed", "missing"]
    assert response["skipped_unknown"] == 1
    assert set(job_store._jobs) == {"unknown", "pending", "other-owner"}


@pytest.mark.asyncio
async def test_execute_is_bounded_to_the_preceding_preview_candidate_ids(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: _roots(tmp_path))
    job_store._jobs["previewed"] = _job(
        "previewed", job_store.JobStatus.FAILED, owner_id="owner-a"
    )

    preview = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a", dry_run=True, candidate_run_ids=None
    )
    assert preview["candidate_run_ids"] == ["previewed"]

    # This row becomes eligible after the user has seen the confirmation
    # count. It must not be swept into that already-confirmed operation.
    job_store._jobs["newly-eligible"] = _job(
        "newly-eligible", job_store.JobStatus.FAILED, owner_id="owner-a"
    )
    result = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=False,
        candidate_run_ids=preview["candidate_run_ids"],
    )

    assert result["candidate_run_ids"] == ["previewed"]
    assert result["removed_run_ids"] == ["previewed"]
    assert set(job_store._jobs) == {"newly-eligible"}


@pytest.mark.asyncio
async def test_execute_cannot_delete_a_submitted_candidate_owned_by_someone_else(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: _roots(tmp_path))
    job_store._jobs["foreign"] = _job(
        "foreign", job_store.JobStatus.FAILED, owner_id="owner-b"
    )

    result = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a", dry_run=False, candidate_run_ids=["foreign"]
    )

    assert result["candidate_run_ids"] == []
    assert result["removed_run_ids"] == []
    assert "foreign" in job_store._jobs


@pytest.mark.asyncio
async def test_execute_preserves_candidate_changed_after_scan(tmp_path: Path, monkeypatch) -> None:
    roots = _roots(tmp_path)
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: roots)
    job_store._jobs["failed"] = _job(
        "failed", job_store.JobStatus.FAILED, owner_id="owner-a"
    )
    original = job_store.hard_delete_job_if_unchanged

    async def race(run_id: str, **snapshot) -> bool:
        job_store._jobs[run_id].seq += 1
        return await original(run_id, **snapshot)

    monkeypatch.setattr(job_store, "hard_delete_job_if_unchanged", race)
    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a", dry_run=False, candidate_run_ids=["failed"]
    )

    assert response["candidate_count"] == 1
    assert response["removed_count"] == 0
    assert response["skipped_changed"] == 1
    assert "failed" in job_store._jobs


@pytest.mark.asyncio
async def test_execute_preserves_prompt_that_becomes_comfy_active_after_scan(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: _roots(tmp_path))
    job_store._jobs["queued-during-scan"] = _job(
        "queued-during-scan",
        job_store.JobStatus.FAILED,
        owner_id="owner-a",
    )
    original_list_jobs = job_store.list_jobs
    scan_complete = False

    async def list_jobs(*, owner_id=None, status=None):
        nonlocal scan_complete
        jobs = await original_list_jobs(owner_id=owner_id, status=status)
        scan_complete = True
        return jobs

    async def active_after_scan():
        assert scan_complete
        return {"queued-during-scan"}

    monkeypatch.setattr(job_store, "list_jobs", list_jobs)
    monkeypatch.setattr(
        history_cleanup,
        "fetch_active_prompt_ids",
        active_after_scan,
    )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=False,
        candidate_run_ids=["queued-during-scan"],
    )

    assert response["candidate_count"] == 1
    assert response["removed_count"] == 0
    assert response["skipped_changed"] == 1
    assert "queued-during-scan" in job_store._jobs


@pytest.mark.asyncio
async def test_execute_fails_safe_when_comfy_queue_cannot_be_verified(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: _roots(tmp_path))
    job_store._jobs["unverified"] = _job(
        "unverified",
        job_store.JobStatus.FAILED,
        owner_id="owner-a",
    )
    monkeypatch.setattr(
        history_cleanup,
        "fetch_active_prompt_ids",
        AsyncMock(return_value=None),
    )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=False,
        candidate_run_ids=["unverified"],
    )

    assert response["candidate_count"] == 1
    assert response["removed_count"] == 0
    assert response["skipped_changed"] == 1
    assert "unverified" in job_store._jobs


@pytest.mark.asyncio
async def test_execute_preserves_success_when_artifact_reappears_after_scan(
    tmp_path: Path, monkeypatch
) -> None:
    roots = _roots(tmp_path)
    monkeypatch.setattr(history_cleanup, "_artifact_roots", lambda: roots)
    job_store._jobs["restored"] = _job(
        "restored",
        job_store.JobStatus.SUCCEEDED,
        owner_id="owner-a",
        result=_result(_descriptor("restored.png")),
    )
    original = history_cleanup.classify_succeeded_result
    calls = 0

    def restore_after_scan(run_id: str, result, *, roots=None):
        nonlocal calls
        calls += 1
        if calls == 2:
            (roots["output"] / "restored.png").write_bytes(b"png")
        return original(run_id, result, roots=roots)

    monkeypatch.setattr(
        history_cleanup,
        "classify_succeeded_result",
        restore_after_scan,
    )

    response = await history_cleanup.prune_missing_artifacts(
        owner_id="owner-a",
        dry_run=False,
        candidate_run_ids=["restored"],
    )

    assert response["candidate_count"] == 1
    assert response["removed_count"] == 0
    assert response["skipped_changed"] == 1
    assert "restored" in job_store._jobs


@pytest.mark.asyncio
async def test_sqlite_hard_delete_is_owner_status_seq_and_timestamp_cas(tmp_path: Path) -> None:
    await job_store_sqlite.close()
    job_store_sqlite.configure(str(tmp_path / "history.db"))
    try:
        await job_store_sqlite.create_job("run-1", "generic", "owner-a")
        record = await job_store_sqlite.set_job_status("run-1", "failed", error="boom")
        assert record is not None

        assert not await job_store_sqlite.hard_delete_job_if_unchanged(
            "run-1",
            owner_id="owner-b",
            status=record.status,
            seq=record.seq,
            updated_at=record.updated_at,
        )
        assert not await job_store_sqlite.hard_delete_job_if_unchanged(
            "run-1",
            owner_id=record.owner_id,
            status=record.status,
            seq=record.seq + 1,
            updated_at=record.updated_at,
        )
        assert await job_store_sqlite.hard_delete_job_if_unchanged(
            "run-1",
            owner_id=record.owner_id,
            status=record.status,
            seq=record.seq,
            updated_at=record.updated_at,
        )
        assert await job_store_sqlite.get_job("run-1") is None
    finally:
        await job_store_sqlite.close()
        job_store_sqlite.configure(None)


class _Request:
    def __init__(self, payload) -> None:
        self.payload = payload

    async def json(self):
        return self.payload


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"dry_run": "true"},
        {"dry_run": True, "candidate_run_ids": ["unexpected"]},
        {"dry_run": False},
        {"dry_run": False, "candidate_run_ids": "run-a"},
        {"dry_run": False, "candidate_run_ids": [""]},
        {"dry_run": False, "candidate_run_ids": ["run-a", "run-a"]},
    ],
)
async def test_controller_rejects_unbound_or_malformed_cleanup_payload(payload) -> None:
    response = await api_controllers.prune_missing_artifacts_controller(
        _Request(payload)
    )
    assert response.status == 400
    assert json.loads(response.text) == {"detail": "invalid_payload"}


@pytest.mark.asyncio
async def test_controller_owner_scope_matches_authenticated_run_list() -> None:
    cleanup = AsyncMock(
        return_value={
            "dry_run": True,
            "candidate_count": 2,
            "candidate_run_ids": ["a", "b"],
            "removed_count": 0,
            "removed_run_ids": [],
            "skipped_unknown": 1,
            "skipped_changed": 0,
        }
    )
    with patch.object(api_controllers, "_ENABLE_GOOGLE_OAUTH", True), patch.object(
        api_controllers, "_require_auth", new=AsyncMock(return_value=None)
    ), patch.object(
        api_controllers,
        "get_owner_from_request",
        new=AsyncMock(return_value="owner-a"),
    ), patch.object(history_cleanup, "prune_missing_artifacts", new=cleanup):
        response = await api_controllers.prune_missing_artifacts_controller(
            _Request({"dry_run": True})
        )

    assert response.status == 200
    cleanup.assert_awaited_once_with(
        owner_id="owner-a", dry_run=True, candidate_run_ids=None
    )


@pytest.mark.asyncio
async def test_controller_passes_confirmed_candidate_ids_to_cleanup_service() -> None:
    cleanup = AsyncMock(
        return_value={
            "dry_run": False,
            "candidate_count": 1,
            "candidate_run_ids": ["run-a"],
            "removed_count": 1,
            "removed_run_ids": ["run-a"],
            "skipped_unknown": 0,
            "skipped_changed": 0,
        }
    )
    with patch.object(history_cleanup, "prune_missing_artifacts", new=cleanup):
        response = await api_controllers.prune_missing_artifacts_controller(
            _Request({"dry_run": False, "candidate_run_ids": ["run-a"]})
        )

    assert response.status == 200
    cleanup.assert_awaited_once_with(
        owner_id=None, dry_run=False, candidate_run_ids=["run-a"]
    )


def test_prune_route_is_registered_before_post_catch_all() -> None:
    source = (Path(api_controllers.__file__).with_name("api_routes.py")).read_text(
        encoding="utf-8"
    )
    route = "/workflow-runner/runs/prune-missing-artifacts"
    assert route in source
    assert source.index(route) < source.index("route_api_catch_all_post")
