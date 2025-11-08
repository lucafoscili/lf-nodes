"""
Test suite for cold-load (page refresh) with real authenticated requests.
Tests the complete flow: browser refresh → GET /runs?owner=me → list_runs_controller
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiohttp import web
import json
import sys
from pathlib import Path

import sys
from pathlib import Path

# Add package root to path BEFORE any imports
pkg_root = Path(__file__).resolve().parents[2]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

try:
    from modules.workflow_runner.services.job_store import JobStatus
except ImportError:
    # Fallback: try adding the path again
    pkg_root = Path(__file__).resolve().parents[2]
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    from modules.workflow_runner.services.job_store import JobStatus

# Mock server module before imports
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

pytestmark = pytest.mark.anyio


class TestColdLoadWithAuth:
    """Test cold-load behavior with authentication."""
    
    async def test_list_runs_endpoint_exists(self):
        """Verify the list_runs endpoint is registered."""
        # This is a sanity check
        from modules.workflow_runner.controllers import routes
        
        # Check that routes module loaded
        assert routes is not None
        print("✓ Routes module loaded")
    
    async def test_list_runs_with_authenticated_request(self):
        """Simulate what happens when browser calls GET /runs?owner=me with cookie."""
        from modules.workflow_runner.services import job_store
        from modules.workflow_runner.services.auth_service import derive_owner_id
        
        # Create test data
        test_email = "luca.foscili@smeup.com"
        expected_owner_id = derive_owner_id(test_email)
        
        print(f"\n  Test email: {test_email}")
        print(f"  Expected owner_id: {expected_owner_id}")
        
        # Create a job with this owner_id
        test_job_id = "test-cold-load-123"
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job(test_job_id, "test_workflow", owner_id=expected_owner_id)
            
            # Verify job was created
            all_jobs = await job_store.list_jobs()
            assert test_job_id in all_jobs
            print(f"  ✓ Created test job: {test_job_id}")
            
            # Test filtering by owner_id
            filtered_jobs = await job_store.list_jobs(owner_id=expected_owner_id)
            assert test_job_id in filtered_jobs
            assert len(filtered_jobs) == 1
            print(f"  ✓ Filtering by owner_id returns the job")
            
            # Test filtering by different owner (should be empty)
            other_owner = "x" * 64
            other_jobs = await job_store.list_jobs(owner_id=other_owner)
            assert test_job_id not in other_jobs
            print(f"  ✓ Filtering by different owner_id returns empty")
    
    async def test_list_runs_controller_with_owner_me(self):
        """Test the actual controller with owner=me parameter."""
        from modules.workflow_runner.services import job_store
        from modules.workflow_runner.services.auth_service import derive_owner_id
        
        test_email = "luca.foscili@smeup.com"
        expected_owner_id = derive_owner_id(test_email)
        
        # Create mock request with authenticated email
        mock_request = Mock(spec=web.Request)
        mock_request.query = {'owner': 'me', 'status': 'succeeded', 'limit': '100'}
        mock_request._cache = {'google_oauth_email': test_email}
        mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
        
        # Create test job
        test_job_id = "test-controller-456"
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job(test_job_id, "test_workflow", owner_id=expected_owner_id)
            await job_store.set_job_status(test_job_id, JobStatus.SUCCEEDED)
            
            # Mock auth to succeed
            with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
                 patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None):
                
                # Import after patching
                from modules.workflow_runner.controllers.api_controllers import list_runs_controller
                
                # Call controller
                response = await list_runs_controller(mock_request)
                
                # Parse response
                assert response.status == 200
                data = json.loads(response.text)
                
                print(f"\n  Response status: {response.status}")
                print(f"  Response has 'runs': {'runs' in data}")
                print(f"  Number of runs: {len(data.get('runs', []))}")
                
                # Check if our job is in the response
                runs = data.get('runs', [])
                run_ids = [r['run_id'] for r in runs]
                
                print(f"  Run IDs in response: {run_ids}")
                print(f"  Looking for: {test_job_id}")
                
                # THIS IS THE KEY TEST
                assert test_job_id in run_ids, f"Expected job {test_job_id} not in response!"
                print(f"  ✓ Cold-load returned the authenticated user's job!")
    
    async def test_ui_cold_load_simulation(self):
        """Simulate the exact sequence the UI does on page refresh."""
        from modules.workflow_runner.services import job_store
        from modules.workflow_runner.services.auth_service import derive_owner_id
        
        test_email = "luca.foscili@smeup.com"
        expected_owner_id = derive_owner_id(test_email)
        
        print(f"\n  Simulating UI refresh for: {test_email}")
        
        # Step 1: Create some jobs (like previous session)
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            job1 = await job_store.create_job("ui-test-1", "workflow_a", owner_id=expected_owner_id)
            job2 = await job_store.create_job("ui-test-2", "workflow_b", owner_id=expected_owner_id)
            other_job = await job_store.create_job("ui-test-other", "workflow_c", owner_id="different" + "x"*56)
            
            print(f"  Created 3 jobs (2 for user, 1 for other)")
            
            # Step 2: Simulate browser refresh - UI calls coldLoadRuns()
            # which does: fetch('/workflow-runner/runs?status=...&owner=me&limit=200')
            
            mock_request = Mock(spec=web.Request)
            mock_request.query = {
                'status': 'pending,running,succeeded,failed,cancelled,timeout',
                'owner': 'me',
                'limit': '200'
            }
            mock_request._cache = {'google_oauth_email': test_email}
            mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
            
            with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
                 patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None):
                
                from modules.workflow_runner.controllers.api_controllers import list_runs_controller
                
                response = await list_runs_controller(mock_request)
                data = json.loads(response.text)
                runs = data.get('runs', [])
                
                print(f"\n  UI cold-load response:")
                print(f"    Total runs returned: {len(runs)}")
                
                run_ids = [r['run_id'] for r in runs]
                print(f"    Run IDs: {run_ids}")
                
                # Verify user's jobs are present
                assert "ui-test-1" in run_ids, "User's first job missing!"
                assert "ui-test-2" in run_ids, "User's second job missing!"
                
                # Verify other user's job is NOT present
                assert "ui-test-other" not in run_ids, "Other user's job leaked!"
                
                print(f"  ✓ UI cold-load correctly filters by owner_id!")
                print(f"  ✓ User sees only their 2 jobs, not other user's job")


class TestColdLoadFailureModes:
    """Test what happens when cold-load fails."""
    
    async def test_missing_email_in_request(self):
        """What happens if request doesn't have google_oauth_email?"""
        from modules.workflow_runner.services import job_store
        
        # Create mock request WITHOUT email
        mock_request = Mock(spec=web.Request)
        mock_request.query = {'owner': 'me'}
        mock_request._cache = {}  # No email!
        mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("test-no-email", "workflow", owner_id="abc123")
            
            with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
                 patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None):
                
                from modules.workflow_runner.controllers.api_controllers import list_runs_controller
                
                response = await list_runs_controller(mock_request)
                data = json.loads(response.text)
                
                print(f"\n  Request without email:")
                print(f"    Response status: {response.status}")
                print(f"    Runs returned: {len(data.get('runs', []))}")
                
                # With no email, derive_owner_id("") returns empty string
                # So it filters by owner_id="" which shouldn't match anything
                # (unless we created a job with owner_id="")
                
                # This should return EMPTY or ALL depending on implementation
                runs = data.get('runs', [])
                print(f"    Run IDs: {[r['run_id'] for r in runs]}")
    
    async def test_owner_me_with_oauth_disabled(self):
        """What happens if OAuth disabled but UI uses owner=me?"""
        from modules.workflow_runner.services import job_store
        
        mock_request = Mock(spec=web.Request)
        mock_request.query = {'owner': 'me'}
        mock_request._cache = {'google_oauth_email': 'test@example.com'}
        mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Ensure clean in-memory store for test isolation
            job_store._jobs.clear()
            await job_store.create_job("test-oauth-off", "workflow", owner_id="abc123")
            
            # OAuth DISABLED
            with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', False):
                
                from modules.workflow_runner.controllers.api_controllers import list_runs_controller
                
                response = await list_runs_controller(mock_request)
                data = json.loads(response.text)
                
                print(f"\n  OAuth disabled but owner=me:")
                print(f"    Response status: {response.status}")
                print(f"    Runs returned: {len(data.get('runs', []))}")
                
                # With OAuth disabled, owner=me is ignored
                # Should return ALL jobs
                runs = data.get('runs', [])
                assert len(runs) >= 1
                print(f"    ✓ Returns all jobs (owner=me ignored)")


if __name__ == "__main__":
    import asyncio
    import sys
    
    print("=" * 60)
    print("Running Cold-Load Tests")
    print("=" * 60)
    
    # Run with pytest
    sys.exit(pytest.main([__file__, "-v", "-s"]))
