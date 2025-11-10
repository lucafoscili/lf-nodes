"""
Comprehensive test suite for owner_id propagation through the workflow runner.

This test file traces owner_id from authentication through to persistence,
helping identify where the value gets lost or incorrectly passed.
"""
import pytest
import sys

from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add package root to path so imports resolve
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

# Mock server.PromptServer before any imports that might load it
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

from modules.workflow_runner.services.auth_service import derive_owner_id
from modules.workflow_runner.services import job_store

# Configure pytest-anyio to use asyncio backend for all async tests
pytestmark = pytest.mark.anyio


class TestDeriveOwnerId:
    """Test that derive_owner_id produces non-empty hashes from emails."""
    
    def test_derive_owner_id_with_valid_email(self):
        """derive_owner_id should return a non-empty hex string for valid email"""
        email = "test@example.com"
        owner_id = derive_owner_id(email)
        
        assert owner_id is not None, "owner_id should not be None"
        assert isinstance(owner_id, str), "owner_id should be a string"
        assert len(owner_id) > 0, "owner_id should not be empty"
        assert owner_id != email, "owner_id should be hashed, not plaintext"
        # HMAC-SHA256 produces 64-char hex string
        assert len(owner_id) == 64, f"Expected 64-char hex, got {len(owner_id)}"
    
    def test_derive_owner_id_empty_string(self):
        """derive_owner_id should return empty string for empty input"""
        owner_id = derive_owner_id("")
        assert owner_id == "", "Empty input should return empty string"
    
    def test_derive_owner_id_deterministic(self):
        """derive_owner_id should return same hash for same email"""
        email = "consistent@example.com"
        owner_id1 = derive_owner_id(email)
        owner_id2 = derive_owner_id(email)
        assert owner_id1 == owner_id2, "Same email should produce same owner_id"


class TestJobStoreCreateJob:
    """Test job_store.create_job correctly persists owner_id."""
    
    async def test_create_job_in_memory_with_owner_id(self):
        """In-memory job creation should preserve owner_id"""
        job_id = "test-run-123"
        workflow_id = "test-workflow"
        owner_id = "a" * 64  # Mock hex owner_id
        
        # Ensure we're using in-memory store (not persistence)
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            job = await job_store.create_job(job_id, workflow_id, owner_id)
            
            assert job is not None, "create_job should return a Job"
            assert job.id == job_id, f"Expected job.id={job_id}, got {job.id}"
            assert job.workflow_id == workflow_id, f"Expected workflow_id={workflow_id}, got {job.workflow_id}"
            assert job.owner_id == owner_id, f"Expected owner_id={owner_id}, got {job.owner_id}"
            
            # Verify job was stored
            retrieved = await job_store.get_job(job_id)
            assert retrieved is not None, "Job should be retrievable after creation"
            assert retrieved.owner_id == owner_id, f"Retrieved job owner_id={retrieved.owner_id}, expected {owner_id}"
    
    async def test_create_job_in_memory_without_owner_id(self):
        """In-memory job creation with None owner_id should preserve None"""
        job_id = "test-run-no-owner"
        workflow_id = "test-workflow"
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            job = await job_store.create_job(job_id, workflow_id, owner_id=None)
            
            assert job is not None
            assert job.owner_id is None, f"Expected owner_id=None, got {job.owner_id}"


class TestRunServicePropagation:
    """Test run_service.run_workflow passes owner_id to create_job."""
    
    async def test_run_workflow_passes_owner_id_to_create_job(self):
        """run_workflow should pass owner_id to create_job"""
        from modules.workflow_runner.services.run_service import run_workflow
        
        payload = {
            "workflowId": "test-workflow",
            "workflow": {},
            "prompt": {}
        }
        owner_id = "b" * 64
        
        # Mock create_job to capture arguments
        create_job_calls = []
        
        async def mock_create_job(job_id, workflow_id, owner_id=None):
            create_job_calls.append({
                "job_id": job_id,
                "workflow_id": workflow_id,
                "owner_id": owner_id
            })
            # Return a mock job
            mock_job = Mock()
            mock_job.id = job_id
            mock_job.workflow_id = workflow_id
            mock_job.owner_id = owner_id
            return mock_job
        
        # Mock the entire execution flow to avoid side effects
        with patch('modules.workflow_runner.services.run_service.create_job', side_effect=mock_create_job), \
             patch('modules.workflow_runner.services.run_service._prepare_workflow_execution') as mock_prep, \
             patch('modules.workflow_runner.services.run_service.submit_workflow') as mock_submit, \
             patch('modules.workflow_runner.services.run_service._emit_run_progress'), \
             patch('modules.workflow_runner.services.run_service.PromptServer') as mock_server:
            
            # Mock _prepare_workflow_execution to return (definition, prompt) tuple
            mock_definition = Mock()
            mock_prompt = {"mock": "prompt"}
            mock_prep.return_value = (mock_definition, mock_prompt)
            
            # Mock submit_workflow to return (prompt_id, client_id, comfy_url, prompt, validation, workflow_id)
            mock_prompt_id = "mock-prompt-123"
            mock_client_id = "mock-client-456"
            mock_comfy_url = "http://mock:8188"
            mock_validation = (True, "", [], [])  # Valid
            mock_workflow_id = "test-workflow"
            mock_submit.return_value = (mock_prompt_id, mock_client_id, mock_comfy_url, mock_prompt, mock_validation, mock_workflow_id)
            
            mock_loop = Mock()
            mock_loop.create_task = Mock()
            mock_server.instance.loop = mock_loop
            
            result = await run_workflow(payload, owner_id=owner_id)
            
            assert "run_id" in result, "run_workflow should return run_id"
            assert len(create_job_calls) == 1, f"create_job should be called once, got {len(create_job_calls)} calls"
            
            call = create_job_calls[0]
            assert call["workflow_id"] == "test-workflow", f"Expected workflow_id='test-workflow', got {call['workflow_id']}"
            assert call["owner_id"] == owner_id, f"Expected owner_id={owner_id}, got {call['owner_id']}"
    
    async def test_run_workflow_without_owner_id(self):
        """run_workflow should pass None owner_id when not provided"""
        from modules.workflow_runner.services.run_service import run_workflow
        
        payload = {
            "workflowId": "test-workflow",
            "workflow": {},
            "prompt": {}
        }
        
        create_job_calls = []
        
        async def mock_create_job(job_id, workflow_id, owner_id=None):
            create_job_calls.append({
                "job_id": job_id,
                "workflow_id": workflow_id,
                "owner_id": owner_id
            })
            mock_job = Mock()
            mock_job.id = job_id
            mock_job.workflow_id = workflow_id
            mock_job.owner_id = owner_id
            return mock_job
        
        with patch('modules.workflow_runner.services.run_service.create_job', side_effect=mock_create_job), \
             patch('modules.workflow_runner.services.run_service._prepare_workflow_execution') as mock_prep, \
             patch('modules.workflow_runner.services.run_service.submit_workflow') as mock_submit, \
             patch('modules.workflow_runner.services.run_service._emit_run_progress'), \
             patch('modules.workflow_runner.services.run_service.PromptServer') as mock_server:
            
            # Mock _prepare_workflow_execution to return (definition, prompt) tuple
            mock_definition = Mock()
            mock_prompt = {"mock": "prompt"}
            mock_prep.return_value = (mock_definition, mock_prompt)
            
            # Mock submit_workflow to return (prompt_id, client_id, comfy_url, prompt, validation, workflow_id)
            mock_prompt_id = "mock-prompt-123"
            mock_client_id = "mock-client-456"
            mock_comfy_url = "http://mock:8188"
            mock_validation = (True, "", [], [])  # Valid
            mock_workflow_id = "test-workflow"
            mock_submit.return_value = (mock_prompt_id, mock_client_id, mock_comfy_url, mock_prompt, mock_validation, mock_workflow_id)
            
            mock_loop = Mock()
            mock_loop.create_task = Mock()
            mock_server.instance.loop = mock_loop
            
            result = await run_workflow(payload, owner_id=None)
            
            assert len(create_job_calls) == 1
            call = create_job_calls[0]
            assert call["owner_id"] is None, f"Expected owner_id=None, got {call['owner_id']}"


class TestControllerOwnerIdExtraction:
    """Test controller correctly extracts owner_id from authenticated request."""
    
    async def test_controller_derives_owner_id_from_authenticated_request(self):
        """Controller should derive owner_id from google_oauth_email attribute"""
        from modules.workflow_runner.controllers.api_controllers import start_workflow_controller
        from aiohttp import web
        
        # Create mock request with authenticated email
        mock_request = Mock(spec=web.Request)
        mock_request.google_oauth_email = "user@example.com"
        mock_request.get = Mock(return_value=None)
        mock_request.json = AsyncMock(return_value={
            "workflowId": "test-workflow",
            "workflow": {},
            "prompt": {}
        })
        
        run_workflow_calls = []
        
        async def mock_run_workflow(payload, owner_id=None):
            run_workflow_calls.append({
                "payload": payload,
                "owner_id": owner_id
            })
            return {"run_id": "test-123"}
        
        with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
             patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None), \
             patch('modules.workflow_runner.controllers.api_controllers.run_workflow', side_effect=mock_run_workflow):
            
            response = await start_workflow_controller(mock_request)
            
            assert len(run_workflow_calls) == 1, "run_workflow should be called once"
            call = run_workflow_calls[0]
            
            # Verify owner_id was derived and passed
            assert call["owner_id"] is not None, "owner_id should not be None"
            assert isinstance(call["owner_id"], str), "owner_id should be a string"
            assert len(call["owner_id"]) == 64, f"Expected 64-char hex owner_id, got {len(call['owner_id'])}"
            
            # Verify it's the hash of the email
            expected_owner_id = derive_owner_id("user@example.com")
            assert call["owner_id"] == expected_owner_id, f"Expected owner_id={expected_owner_id}, got {call['owner_id']}"


class TestAdapterParameterOrder:
    """Test that adapter is called with correct parameter order."""
    
    async def test_adapter_called_with_correct_kwargs(self):
        """Adapter should receive workflow_id and owner_id in correct positions"""
        job_id = "test-123"
        workflow_id = "wf-456"
        owner_id = "c" * 64
        
        # Mock adapter
        mock_adapter = AsyncMock()
        mock_job = Mock()
        mock_job.id = job_id
        mock_job.workflow_id = workflow_id
        mock_job.owner_id = owner_id
        mock_adapter.create_job = AsyncMock(return_value=mock_job)
        
        async def mock_get_adapter():
            return mock_adapter
        
        with patch.object(job_store, '_USE_PERSISTENCE', True), \
             patch.object(job_store, '_get_adapter', side_effect=mock_get_adapter):
            
            result = await job_store.create_job(job_id, workflow_id, owner_id)
            
            # Verify adapter.create_job was called
            mock_adapter.create_job.assert_called_once()
            call_args = mock_adapter.create_job.call_args
            
            # Check positional args
            assert call_args[0][0] == job_id, f"First positional arg should be job_id={job_id}"
            
            # Check keyword args
            kwargs = call_args[1]
            assert "workflow_id" in kwargs, "workflow_id should be passed as kwarg"
            assert "owner_id" in kwargs, "owner_id should be passed as kwarg"
            assert kwargs["workflow_id"] == workflow_id, f"Expected workflow_id={workflow_id}, got {kwargs['workflow_id']}"
            assert kwargs["owner_id"] == owner_id, f"Expected owner_id={owner_id}, got {kwargs['owner_id']}"


if __name__ == "__main__":
    # Allow running tests directly with python
    pytest.main([__file__, "-v", "-s"])
