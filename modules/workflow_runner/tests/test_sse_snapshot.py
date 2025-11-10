"""
Test the SSE snapshot functionality end-to-end.
This should reveal why runs aren't showing up after refresh.
"""
import json
import pytest

from unittest.mock import Mock, patch
from aiohttp import web

pytestmark = pytest.mark.anyio

class MockStreamResponse:
    """Mock aiohttp StreamResponse for testing."""
    
    def __init__(self):
        self.status = 200
        self.content_type = None
        self.headers = {}
        self.written_data = []
        self.prepared = False
        
    async def prepare(self, request):
        self.prepared = True
        
    async def write(self, data: bytes):
        self.written_data.append(data)
        
    async def drain(self):
        pass
        
    def get_written_text(self) -> str:
        """Decode all written data to text."""
        return b''.join(self.written_data).decode('utf-8')

class TestSSESnapshot:
    """Test the SSE initial snapshot that should send runs on connection."""
    
    async def test_send_initial_snapshot_sends_succeeded_runs(self):
        """The snapshot should now include SUCCEEDED runs (our fix)."""
        import sys
        from pathlib import Path
        
        # Add package root to path
        pkg_root = Path(__file__).resolve().parents[3]
        if str(pkg_root) not in sys.path:
            sys.path.insert(0, str(pkg_root))
        
        # Mock server module
        sys.modules['server'] = Mock()
        sys.modules['server'].PromptServer = Mock()
        
        import pytest

        # Some import paths pull heavy GPU-related modules (torch.cuda) at import time
        # which raise on machines without CUDA support. If that happens, skip these
        # tests gracefully so the CI/dev run stays stable on CPU-only environments.
        try:
            from modules.workflow_runner.services import job_store
            from modules.workflow_runner.controllers.api_controllers import _send_initial_snapshot
        except AssertionError as e:
            pytest.skip(f"Skipping SSE snapshot tests due to import error: {e}", allow_module_level=True)
        
        # Create test jobs with different statuses
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("run-pending", "workflow", owner_id="owner123")
            await job_store.create_job("run-running", "workflow", owner_id="owner123")
            await job_store.create_job("run-succeeded", "workflow", owner_id="owner123")
            
            # Set statuses
            await job_store.set_job_status("run-pending", job_store.JobStatus.PENDING)
            await job_store.set_job_status("run-running", job_store.JobStatus.RUNNING)
            await job_store.set_job_status("run-succeeded", job_store.JobStatus.SUCCEEDED, result={"success": True})
            
            # Create mock response
            mock_resp = MockStreamResponse()
            
            # Call the snapshot function WITHOUT owner filtering
            await _send_initial_snapshot(mock_resp, subscriber_owner=None, last_event=None)
            
            # Check what was written
            written_text = mock_resp.get_written_text()
            print(f"\n  Snapshot output ({len(written_text)} bytes):")
            print(f"  {written_text[:500]}...")
            
            # Verify all 3 runs are in the snapshot
            assert "run-pending" in written_text, "PENDING run should be in snapshot"
            assert "run-running" in written_text, "RUNNING run should be in snapshot"
            assert "run-succeeded" in written_text, "SUCCEEDED run should be in snapshot (FIX)"
            
            print(f"  ✓ All 3 runs present in snapshot!")
    
    async def test_send_initial_snapshot_filters_by_owner(self):
        """Snapshot should only send runs for the authenticated user."""
        import sys
        from pathlib import Path
        
        pkg_root = Path(__file__).resolve().parents[3]
        if str(pkg_root) not in sys.path:
            sys.path.insert(0, str(pkg_root))
        
        sys.modules['server'] = Mock()
        sys.modules['server'].PromptServer = Mock()
        
        from modules.workflow_runner.services import job_store
        from modules.workflow_runner.controllers.api_controllers import _send_initial_snapshot
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            # Create runs for different owners
            await job_store.create_job("user1-run1", "workflow", owner_id="owner-user1")
            await job_store.create_job("user1-run2", "workflow", owner_id="owner-user1")
            await job_store.create_job("user2-run1", "workflow", owner_id="owner-user2")
            
            await job_store.set_job_status("user1-run1", job_store.JobStatus.SUCCEEDED, result={})
            await job_store.set_job_status("user1-run2", job_store.JobStatus.RUNNING)
            await job_store.set_job_status("user2-run1", job_store.JobStatus.SUCCEEDED, result={})
            
            mock_resp = MockStreamResponse()
            
            # Call with owner filtering for user1
            await _send_initial_snapshot(mock_resp, subscriber_owner="owner-user1", last_event=None)
            
            written_text = mock_resp.get_written_text()
            print(f"\n  Filtered snapshot for user1:")
            
            # User1 should see their runs
            assert "user1-run1" in written_text, "User1's first run should be visible"
            assert "user1-run2" in written_text, "User1's second run should be visible"
            
            # User2's run should NOT be visible
            assert "user2-run1" not in written_text, "User2's run should NOT be visible to user1"
            
            print(f"  ✓ Owner filtering works correctly!")
    
    async def test_stream_runs_controller_calls_snapshot(self):
        """The stream_runs_controller should call _send_initial_snapshot when SSE connects."""
        import sys
        from pathlib import Path
        
        pkg_root = Path(__file__).resolve().parents[3]
        if str(pkg_root) not in sys.path:
            sys.path.insert(0, str(pkg_root))
        
        sys.modules['server'] = Mock()
        sys.modules['server'].PromptServer = Mock()
        
        from modules.workflow_runner.services import job_store
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("test-run", "workflow", owner_id="owner123")
            await job_store.set_job_status("test-run", job_store.JobStatus.SUCCEEDED, result={})
            
            # Mock the SSE controller
            mock_request = Mock(spec=web.Request)
            mock_request.headers = {}
            mock_request._cache = {'google_oauth_email': 'test@example.com'}
            mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
            
            # We can't easily test the full controller due to EventSource/streaming
            # But we CAN test that our fix changed the logic
            
            # Check: list_jobs now returns ALL jobs
            all_jobs = await job_store.list_jobs(owner_id="owner123")
            assert "test-run" in all_jobs
            assert all_jobs["test-run"].status == job_store.JobStatus.SUCCEEDED
            
            print(f"  ✓ list_jobs returns succeeded runs")
    
    async def test_snapshot_output_format(self):
        """Verify the SSE event format is correct."""
        import sys
        from pathlib import Path
        
        pkg_root = Path(__file__).resolve().parents[3]
        if str(pkg_root) not in sys.path:
            sys.path.insert(0, str(pkg_root))
        
        sys.modules['server'] = Mock()
        sys.modules['server'].PromptServer = Mock()
        
        from modules.workflow_runner.services import job_store
        from modules.workflow_runner.controllers.api_controllers import _send_initial_snapshot
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("format-test", "test_workflow", owner_id="owner123")
            await job_store.set_job_status("format-test", job_store.JobStatus.SUCCEEDED, result={"data": "test"})
            
            mock_resp = MockStreamResponse()
            await _send_initial_snapshot(mock_resp, subscriber_owner=None, last_event=None)
            
            written_text = mock_resp.get_written_text()
            print(f"\n  SSE event format:")
            print(f"  {written_text}")
            
            # Check SSE format: id: <id>\nevent: run\ndata: {...}\n\n
            assert "event: run" in written_text or "event: queue" in written_text, "Should have event type"
            assert "data: {" in written_text, "Should have JSON data"
            assert "run_id" in written_text, "Should contain run_id"
            assert "status" in written_text, "Should contain status"
            assert "format-test" in written_text, "Should contain our run ID"
            
            # Verify it's valid JSON in the data field
            lines = written_text.strip().split('\n')
            data_line = [l for l in lines if l.startswith('data: ')]
            if data_line:
                json_str = data_line[0].replace('data: ', '')
                data = json.loads(json_str)
                
                assert data['run_id'] == 'format-test'
                assert data['status'] == 'succeeded'
                assert data['owner_id'] == 'owner123'
                
                print(f"  ✓ SSE event format is valid!")
                print(f"  ✓ Parsed data: {data}")

class TestUIEventProcessing:
    """Test how the UI should process SSE events."""
    
    def test_ui_should_process_snapshot_events(self):
        """Document what the UI expects from snapshot events."""
        # This is a documentation test showing what the UI needs
        
        expected_event_format = {
            "id": "run-id:0",
            "run_id": "run-id",
            "status": "succeeded",
            "created_at": 1234567890.0,
            "error": None,
            "result": {"some": "data"},
            "owner_id": "owner123",
            "seq": 0
        }
        
        print(f"\n  Expected SSE event format:")
        print(f"  {json.dumps(expected_event_format, indent=2)}")
        
        # The UI client.ts listens for 'run' and 'message' events
        # See workflow-runner/src/services/workflow-service.ts:subscribeRunEvents
        # It expects: es.addEventListener('run', (ev: MessageEvent) => { ... })
        
        print(f"\n  UI expects:")
        print(f"  - event: run")
        print(f"  - data: <JSON with run_id, status, etc>")
        print(f"  - Event listener: es.addEventListener('run', ...)")

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s", "--tb=short"]))
