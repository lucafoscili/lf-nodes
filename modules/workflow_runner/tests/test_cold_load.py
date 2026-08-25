"""
Test suite for cold-load (page refresh) functionality.
Investigates why UI shows empty run history after refresh.
"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add package root to path
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

# Mock server module before imports
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

from modules.workflow_runner.services import job_store, lifecycle
from modules.workflow_runner.services.job_store import JobStatus, Job

pytestmark = pytest.mark.anyio

class TestListJobsFiltering:
    """Test that list_jobs correctly filters by owner_id."""
    
    async def test_list_jobs_with_owner_id_filter(self):
        """list_jobs should only return jobs matching owner_id"""
        owner_a = "a" * 64
        owner_b = "b" * 64
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            # Create jobs for different owners
            await job_store.create_job("run-a-1", "workflow", owner_id=owner_a)
            await job_store.create_job("run-a-2", "workflow", owner_id=owner_a)
            await job_store.create_job("run-b-1", "workflow", owner_id=owner_b)
            await job_store.create_job("run-no-owner", "workflow", owner_id=None)
            
            # Filter by owner_a
            jobs_a = await job_store.list_jobs(owner_id=owner_a)
            
            assert len(jobs_a) == 2, f"Expected 2 jobs for owner_a, got {len(jobs_a)}"
            assert "run-a-1" in jobs_a
            assert "run-a-2" in jobs_a
            assert "run-b-1" not in jobs_a
            assert "run-no-owner" not in jobs_a
            
    async def test_list_jobs_without_owner_id_returns_all(self):
        """list_jobs without owner_id should return all jobs"""
        owner_a = "a" * 64
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("run-1", "workflow", owner_id=owner_a)
            await job_store.create_job("run-2", "workflow", owner_id=None)
            
            # No filter
            all_jobs = await job_store.list_jobs(owner_id=None)
            
            assert len(all_jobs) >= 2, f"Expected at least 2 jobs, got {len(all_jobs)}"

class TestListRunsAPIEndpoint:
    """Test the list_runs_controller endpoint with owner filtering."""
    
    async def test_list_runs_with_owner_me_extracts_email(self):
        """GET /runs?owner=me should derive owner_id from authenticated email"""
        # This test will fail until we fix the email extraction bug
        from aiohttp import web
        
        # Create mock request with authenticated email
        mock_request = Mock(spec=web.Request)
        mock_request._cache = {'google_oauth_email': 'test@example.com'}
        mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
        mock_request.query = {'owner': 'me'}
        
        # Mock job_store to capture the owner_id parameter
        captured_owner_ids = []
        
        async def mock_list_jobs(owner_id=None, status=None):
            captured_owner_ids.append(owner_id)
            return {}
        
        with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
             patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None), \
             patch.object(job_store, 'list_jobs', side_effect=mock_list_jobs):
            
            from modules.workflow_runner.controllers.api_controllers import list_runs_controller
            
            response = await list_runs_controller(mock_request)
            
            # Verify list_jobs was called
            assert len(captured_owner_ids) == 1, "list_jobs should be called once"
            
            owner_id = captured_owner_ids[0]
            
            # This will fail before the fix (owner_id will be empty string)
            # After fix, it should be the hash of 'test@example.com'
            assert owner_id is not None, "owner_id should not be None"
            assert owner_id != "", "owner_id should not be empty string"
            assert len(owner_id) == 64, f"owner_id should be 64-char hex, got length {len(owner_id)}"
            
            print(f"PASS: Successfully extracted owner_id: {owner_id[:16]}...")
    
    async def test_list_runs_returns_json_with_runs_array(self):
        """Endpoint should return {runs: [...]} structure"""
        from aiohttp import web
        
        mock_request = Mock(spec=web.Request)
        mock_request.query = {}
        
        # Mock job_store to return a test job
        test_job = Job(
            id="test-123",
            workflow_id="test-wf",
            status=JobStatus.SUCCEEDED,
            owner_id="owner123",
            seq=0,
            updated_at=12345.0
        )
        
        async def mock_list_jobs(owner_id=None, status=None):
            return {"test-123": test_job}
        
        with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', False), \
             patch.object(job_store, 'list_jobs', side_effect=mock_list_jobs):
            
            from modules.workflow_runner.controllers.api_controllers import list_runs_controller
            
            response = await list_runs_controller(mock_request)
            
            # Parse JSON response
            import json
            data = json.loads(response.text)
            
            assert "runs" in data, "Response should have 'runs' key"
            assert isinstance(data["runs"], list), "'runs' should be an array"
            assert len(data["runs"]) == 1, "Should return 1 run"
            
            run = data["runs"][0]
            assert run["run_id"] == "test-123"
            assert run["owner_id"] == "owner123"
            assert run["updated_at"] == 12345.0

    async def test_list_runs_restores_stable_submission_control_handle(self):
        """A browser refresh must retain exact Stop authority for active runs."""
        from aiohttp import web
        import json

        mock_request = Mock(spec=web.Request)
        mock_request.query = {"summary": "1"}
        test_job = Job(
            id="run-restored-control",
            workflow_id="test-wf",
            status=JobStatus.RUNNING,
            seq=2,
        )
        payload = {
            "workflowId": "test-wf",
            "submissionId": "lf-web:restored-control",
            "inputs": {},
        }
        await lifecycle.reserve_submission(payload, "test-wf")
        await lifecycle.bind_prompt(
            "lf-web:restored-control",
            "run-restored-control",
            "http://comfy:8188",
        )
        await lifecycle.record_cancel_requested("lf-web:restored-control")

        with patch(
            "modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH",
            False,
        ), patch.object(
            job_store,
            "list_jobs",
            return_value={"run-restored-control": test_job},
        ):
            from modules.workflow_runner.controllers.api_controllers import (
                list_runs_controller,
            )

            response = await list_runs_controller(mock_request)
            run = json.loads(response.text)["runs"][0]

        assert run["submission_id"] == "lf-web:restored-control"
        assert run["cancel_requested"] is True

    async def test_list_runs_orders_mixed_statuses_by_created_at_descending(self):
        """History pagination must not inherit status/store insertion order."""
        from aiohttp import web
        import json

        mock_request = Mock(spec=web.Request)
        mock_request.query = {
            "status": "failed,succeeded",
            "summary": "1",
            "limit": "2",
        }
        jobs = {
            "legacy": Job(
                id="legacy",
                workflow_id="wf",
                status=JobStatus.FAILED,
                # Legacy JavaScript milliseconds: numerically larger than
                # the newer second timestamps until the API canonicalizes it.
                created_at=1_763_168_015_000.0,
                updated_at=1_763_168_073_000.0,
            ),
            "newest": Job(
                id="newest",
                workflow_id="wf",
                status=JobStatus.SUCCEEDED,
                created_at=1_786_848_000.0,
                updated_at=1_786_848_001.0,
            ),
            "middle": Job(
                id="middle",
                workflow_id="wf",
                status=JobStatus.SUCCEEDED,
                created_at=1_786_840_000.0,
                updated_at=1_786_847_000.0,
            ),
        }

        async def mock_list_jobs(owner_id=None, status=None):
            return {key: job for key, job in jobs.items() if status is None or job.status.value == status}

        with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', False), \
             patch.object(job_store, 'list_jobs', side_effect=mock_list_jobs):
            from modules.workflow_runner.controllers.api_controllers import list_runs_controller

            response = await list_runs_controller(mock_request)
            data = json.loads(response.text)

        assert [run["run_id"] for run in data["runs"]] == ["newest", "middle"]

    async def test_list_runs_normalizes_invalid_and_millisecond_timestamps(self):
        from aiohttp import web
        import json

        mock_request = Mock(spec=web.Request)
        mock_request.query = {"summary": "1", "limit": "10"}
        jobs = {
            "legacy-ms": Job(
                id="legacy-ms",
                workflow_id="wf",
                status=JobStatus.FAILED,
                created_at=1_763_168_015_000.0,
                updated_at=float("inf"),
            ),
            "new-seconds": Job(
                id="new-seconds",
                workflow_id="wf",
                status=JobStatus.SUCCEEDED,
                created_at=1_786_848_000.0,
                updated_at=1_786_848_001.0,
            ),
            "invalid": Job(
                id="invalid",
                workflow_id="wf",
                status=JobStatus.FAILED,
                created_at=float("nan"),
                updated_at=float("nan"),
            ),
        }

        with patch(
            "modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH",
            False,
        ), patch.object(job_store, "list_jobs", return_value=jobs):
            from modules.workflow_runner.controllers.api_controllers import (
                list_runs_controller,
            )

            response = await list_runs_controller(mock_request)
            data = json.loads(response.text)

        assert [run["run_id"] for run in data["runs"]] == [
            "new-seconds",
            "legacy-ms",
            "invalid",
        ]
        by_id = {run["run_id"]: run for run in data["runs"]}
        assert by_id["legacy-ms"]["created_at"] == 1_763_168_015.0
        assert by_id["legacy-ms"]["updated_at"] == 1_763_168_015.0
        assert by_id["invalid"]["created_at"] == 0.0
        assert by_id["invalid"]["updated_at"] == 0.0

class TestOwnerIdDerivationConsistency:
    """Test that owner_id derivation is consistent across endpoints."""
    
    def test_same_email_produces_same_owner_id(self):
        """derive_owner_id should be deterministic"""
        from modules.workflow_runner.services.auth_service import derive_owner_id
        
        email = "user@example.com"
        
        owner_id_1 = derive_owner_id(email)
        owner_id_2 = derive_owner_id(email)
        
        assert owner_id_1 == owner_id_2, "Same email should produce same owner_id"
        assert len(owner_id_1) == 64, "Should be 64-char hex hash"
    
    def test_empty_email_produces_empty_owner_id(self):
        """derive_owner_id with empty string should return empty string"""
        from modules.workflow_runner.services.auth_service import derive_owner_id
        
        owner_id = derive_owner_id("")
        
        assert owner_id == "", "Empty email should produce empty owner_id"
