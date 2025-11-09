"""Ensure adapter status coercion defaults to PENDING for unexpected objects."""

import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, Mock

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

pytestmark = pytest.mark.anyio

async def test_adapter_status_coercion_defaults_pending(monkeypatch):
    from modules.workflow_runner.services import job_store
    from modules.workflow_runner.services.job_store import JobStatus

    class DummyRec:
        def __init__(self):
            self.run_id = "abc123"
            self.workflow_id = "wf1"
            self.created_at = 123.0
            # status is a Mock to simulate fragile adapter return
            self.status = Mock()
            self.result = None
            self.error = None
            self.owner_id = None
            self.seq = 0
            self.updated_at = 123.0

    dummy = DummyRec()

    async def fake_create_job(job_id, workflow_id, owner_id=None):  # noqa: D401
        return dummy

    # Force persistence path to exercise adapter branch
    monkeypatch.setattr(job_store, "_USE_PERSISTENCE", True)
    monkeypatch.setattr(job_store, "_adapter", Mock(create_job=AsyncMock(side_effect=fake_create_job)))

    job = await job_store.create_job("abc123", "wf1")
    # Coercion should fall back to PENDING when status attr is unexpected
    assert job.status == JobStatus.PENDING