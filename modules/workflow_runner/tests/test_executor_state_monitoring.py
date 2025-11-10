"""Tests for _monitor_until_running function."""
import asyncio
import pytest
import sys

from pathlib import Path
from unittest.mock import AsyncMock, patch

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

# Add package root to path (same as other working tests)
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

class MockResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json_data = json_data
    async def json(self):
        return self._json_data
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

class MockSession:
    def __init__(self, responses):
        self.responses = responses
        self.call_count = 0
    def get(self, url):
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response

async def test_normal_execution_running_detected():
    # Import modules with correct path
    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.executor import _monitor_until_running
    from modules.workflow_runner.services.job_store import JobStatus
    
    with patch.object(executor, "set_job_status", new_callable=AsyncMock) as mock_set_job_status:
        prompt_id = "test-prompt-1"
        stop_event = asyncio.Event()
        responses = [
            MockResponse(200, {"queue_running": [], "queue_pending": [[1, prompt_id, {}, {}]]}),
            MockResponse(200, {"queue_running": [[1, prompt_id, {}, {}]], "queue_pending": []})
        ]
        session = MockSession(responses)
        await _monitor_until_running(prompt_id, stop_event, comfy_url="http://test", session=session)
        mock_set_job_status.assert_called_once_with(prompt_id, JobStatus.RUNNING)

async def test_fast_execution_not_in_queue():
    # Import modules with correct path
    from modules.workflow_runner.services import executor
    from modules.workflow_runner.services.executor import _monitor_until_running
    from modules.workflow_runner.services.job_store import JobStatus
    
    with patch.object(executor, "set_job_status", new_callable=AsyncMock) as mock_set_job_status:
        prompt_id = "fast-prompt"
        stop_event = asyncio.Event()
        responses = [MockResponse(200, {"queue_running": [], "queue_pending": []})]
        session = MockSession(responses)
        await _monitor_until_running(prompt_id, stop_event, comfy_url="http://test", session=session)
        mock_set_job_status.assert_not_called()
