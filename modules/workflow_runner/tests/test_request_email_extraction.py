"""
Simple integration test to verify owner_id extraction from request works correctly.
This test doesn't require torch/CUDA since it mocks the downstream dependencies.
"""
import pytest

from aiohttp import web
from unittest.mock import Mock, AsyncMock, patch

pytestmark = pytest.mark.anyio

async def test_controller_extracts_email_from_request_dict_access():
    """Test that controller correctly extracts email using request['google_oauth_email']"""
    from modules.workflow_runner.controllers.api_controllers import start_workflow_controller
    
    # Create a real-ish aiohttp Request mock that supports dict-style access
    mock_request = Mock(spec=web.Request)
    mock_request._cache = {'google_oauth_email': 'test@example.com'}
    mock_request.get = lambda key, default=None: mock_request._cache.get(key, default)
    mock_request.json = AsyncMock(return_value={
        "workflowId": "test-workflow",
        "workflow": {},
        "prompt": {}
    })
    
    # Track what owner_id was passed to run_workflow
    captured_owner_id = []
    
    async def mock_run_workflow(payload, owner_id=None):
        captured_owner_id.append(owner_id)
        return {"run_id": "test-123", "status": "pending"}
    
    with patch('modules.workflow_runner.controllers.api_controllers._ENABLE_GOOGLE_OAUTH', True), \
         patch('modules.workflow_runner.controllers.api_controllers._require_auth', return_value=None), \
         patch('modules.workflow_runner.controllers.api_controllers.run_workflow', side_effect=mock_run_workflow):
        
        response = await start_workflow_controller(mock_request)
        
        # Verify owner_id was extracted and passed
        assert len(captured_owner_id) == 1, "run_workflow should have been called once"
        owner_id = captured_owner_id[0]
        
        assert owner_id is not None, "owner_id should not be None"
        assert isinstance(owner_id, str), f"owner_id should be a string, got {type(owner_id)}"
        assert len(owner_id) == 64, f"owner_id should be 64-char hex, got length {len(owner_id)}"
        assert owner_id != "", "owner_id should not be empty string"
        
        # Verify it's a valid hex string (HMAC-SHA256 output)
        try:
            int(owner_id, 16)
        except ValueError:
            pytest.fail(f"owner_id should be valid hex, got: {owner_id}")
        
        print(f"✓ Successfully extracted and derived owner_id: {owner_id[:16]}...")
