import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# make package imports work
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

# Mock heavy top-level modules that aren't available in the test environment
from unittest.mock import Mock
sys.modules['execution'] = Mock()
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

import pytest

# Some import paths pull heavy GPU-related modules (torch.cuda) at import time
# which raise on machines without CUDA support. If that happens, skip these
# tests gracefully so the CI/dev run stays stable on CPU-only environments.
try:
    from modules.workflow_runner.controllers import api_controllers
    from modules.workflow_runner.services import job_store
except AssertionError as e:
    pytest.skip(f"Skipping SSE snapshot payload tests due to import error: {e}", allow_module_level=True)

pytestmark = pytest.mark.anyio


class FakeResponse:
    def __init__(self):
        self.written = []

    async def write(self, data: bytes):
        # collect bytes for inspection
        self.written.append(data)

    async def drain(self):
        return None


async def test_send_initial_snapshot_includes_workflow_id_and_updated_at():
    # create a Job instance to be returned by job_store.list_jobs
    job = job_store.Job(id="r1", workflow_id="remove_bg")
    # populate updated_at so snapshot includes it
    job.updated_at = 1234567.89
    job.seq = 2

    async def fake_list_jobs(owner_id=None):
        return {job.id: job}

    resp = FakeResponse()

    with patch.object(job_store, 'list_jobs', side_effect=fake_list_jobs):
        # Call the internal snapshot sender
        await api_controllers._send_initial_snapshot(resp, subscriber_owner=None, last_event=None)

    # Combine written payloads and decode
    combined = b''.join(resp.written).decode('utf-8')
    # Expect workflow_id and updated_at present in the JSON payload
    assert '"workflow_id": "remove_bg"' in combined
    assert '"updated_at":' in combined
