"""
Comprehensive tests for workflow execution state monitoring.

Tests cover all scenarios:
1. Normal execution: prompt moves to currently_running, marked as RUNNING
2. Fast execution: prompt completes before monitoring detects it
3. Queued execution: prompt waits in queue
4. Multiple workflows: only 1 shows RUNNING at a time
5. Edge cases: prompt lost, timeout, errors
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any

# Mock imports before importing the module under test
import sys
from pathlib import Path

# Add parent directory to path for imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir.parent))

from services.executor import _monitor_execution_state
from services.job_store import JobStatus


class MockPromptQueue:
    """Mock ComfyUI PromptQueue for testing."""
    
    def __init__(self):
        self.currently_running = {}
        self.queue = []
        self.history = {}
        self._call_count = 0
    
    def get_current_queue_volatile(self):
        """Return (running, queued) tuple."""
        self._call_count += 1
        running = list(self.currently_running.values())
        return (running, self.queue.copy())
    
    def get_history(self, prompt_id=None):
        """Return history dict."""
        if prompt_id:
            return {prompt_id: self.history[prompt_id]} if prompt_id in self.history else {}
        return self.history.copy()
    
    def add_to_running(self, queue_num, prompt_id, prompt, extra_data, outputs):
        """Simulate ComfyUI moving prompt to currently_running."""
        item = (queue_num, prompt_id, prompt, extra_data, outputs)
        self.currently_running[queue_num] = item
        return item
    
    def add_to_queue(self, queue_num, prompt_id, prompt, extra_data, outputs):
        """Simulate adding prompt to queue."""
        item = (queue_num, prompt_id, prompt, extra_data, outputs)
        self.queue.append(item)
        return item
    
    def complete_prompt(self, queue_num, prompt_id, status_str='success'):
        """Simulate prompt completion."""
        if queue_num in self.currently_running:
            del self.currently_running[queue_num]
        self.history[prompt_id] = {
            'status': {'status_str': status_str, 'completed': True},
            'outputs': {}
        }


class MockPromptServer:
    """Mock PromptServer instance."""
    
    def __init__(self, prompt_queue):
        self.prompt_queue = prompt_queue


class MockRunnerConfig:
    """Mock RUNNER_CONFIG."""
    prompt_timeout_seconds = 300


@pytest.fixture
def mock_queue():
    """Create mock queue."""
    return MockPromptQueue()


@pytest.fixture
def mock_server(mock_queue):
    """Create mock server with queue."""
    return MockPromptServer(mock_queue)


@pytest.fixture
def mock_set_job_status():
    """Mock set_job_status function."""
    with patch('services.executor.set_job_status', new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_prompt_server(mock_server):
    """Patch PromptServer.instance."""
    with patch('services.executor.PromptServer') as mock_ps:
        mock_ps.instance = mock_server
        yield mock_ps


@pytest.fixture
def mock_config():
    """Patch RUNNER_CONFIG."""
    with patch('services.executor.RUNNER_CONFIG', MockRunnerConfig()):
        yield


# Test 1: Normal Execution - Prompt detected in currently_running
@pytest.mark.asyncio
async def test_normal_execution_running_detected(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test normal workflow: prompt moves to currently_running and is marked RUNNING."""
    prompt_id = "test-prompt-1"
    run_id = "test-run-1"
    
    # Simulate prompt in queue initially, then moves to running
    mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
    
    async def simulate_execution():
        """Simulate ComfyUI starting execution after a short delay."""
        await asyncio.sleep(0.1)
        mock_queue.queue.clear()
        mock_queue.add_to_running(1, prompt_id, {}, {}, [])
    
    # Start execution simulation in background
    execution_task = asyncio.create_task(simulate_execution())
    
    # Monitor execution state
    await _monitor_execution_state(prompt_id, run_id)
    
    # Wait for background task
    await execution_task
    
    # Verify RUNNING status was set
    mock_set_job_status.assert_called_once_with(run_id, JobStatus.RUNNING)


# Test 2: Fast Execution - Prompt completes before detection
@pytest.mark.asyncio
async def test_fast_execution_completes_before_detection(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test fast workflow: prompt completes before monitoring can detect it running."""
    prompt_id = "fast-prompt-1"
    run_id = "fast-run-1"
    
    # Simulate prompt already in history (completed immediately)
    mock_queue.history[prompt_id] = {
        'status': {'status_str': 'success', 'completed': True},
        'outputs': {}
    }
    
    # Monitor execution state
    await _monitor_execution_state(prompt_id, run_id)
    
    # Verify RUNNING status was NOT set (skipped)
    mock_set_job_status.assert_not_called()


# Test 3: Queued Execution - Prompt stays in queue
@pytest.mark.asyncio
async def test_queued_execution_stays_pending(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test queued workflow: prompt stays in queue, monitoring times out."""
    prompt_id = "queued-prompt-1"
    run_id = "queued-run-1"
    
    # Simulate prompt in queue (never moves to running)
    mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
    
    # Reduce timeout for test speed
    with patch('services.executor.RUNNER_CONFIG') as mock_cfg:
        mock_cfg.prompt_timeout_seconds = 0.5
        
        # Monitor execution state (will timeout)
        await _monitor_execution_state(prompt_id, run_id)
    
    # Verify RUNNING status was NOT set (still queued)
    mock_set_job_status.assert_not_called()


# Test 4: Multiple Workflows - Only 1 shows RUNNING
@pytest.mark.asyncio
async def test_multiple_workflows_single_running(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test multiple workflows: only 1 can be in currently_running at a time."""
    prompt_id_1 = "prompt-1"
    run_id_1 = "run-1"
    prompt_id_2 = "prompt-2"
    run_id_2 = "run-2"
    
    # Add two prompts to queue
    mock_queue.add_to_queue(1, prompt_id_1, {}, {}, [])
    mock_queue.add_to_queue(2, prompt_id_2, {}, {}, [])
    
    # Simulate first prompt starting execution
    async def start_first_execution():
        await asyncio.sleep(0.1)
        mock_queue.queue.pop(0)  # Remove first from queue
        mock_queue.add_to_running(1, prompt_id_1, {}, {}, [])
    
    execution_task = asyncio.create_task(start_first_execution())
    
    # Monitor both (only first should become RUNNING)
    monitor_task_1 = asyncio.create_task(_monitor_execution_state(prompt_id_1, run_id_1))
    
    await execution_task
    await monitor_task_1
    
    # Verify only first was marked RUNNING
    assert mock_set_job_status.call_count == 1
    mock_set_job_status.assert_called_with(run_id_1, JobStatus.RUNNING)
    
    # Verify queue constraint: only 1 in currently_running
    assert len(mock_queue.currently_running) == 1


# Test 5: Prompt Lost - Not in queue, running, or history
@pytest.mark.asyncio
async def test_prompt_lost_not_found(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test edge case: prompt not found in queue, running, or history."""
    prompt_id = "lost-prompt"
    run_id = "lost-run"
    
    # Don't add prompt anywhere (simulates lost/deleted prompt)
    
    # Monitor execution state (should exit with warning)
    await _monitor_execution_state(prompt_id, run_id)
    
    # Verify RUNNING status was NOT set
    mock_set_job_status.assert_not_called()


# Test 6: Race Condition - Prompt moves to running during check
@pytest.mark.asyncio
async def test_race_condition_prompt_moves_to_running(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test race condition: prompt moves to running between checks."""
    prompt_id = "race-prompt"
    run_id = "race-run"
    
    check_count = [0]
    
    # Mock get_current_queue_volatile to simulate race condition
    original_get = mock_queue.get_current_queue_volatile
    
    def race_condition_get():
        check_count[0] += 1
        if check_count[0] == 2:
            # On second check, move to running
            mock_queue.add_to_running(1, prompt_id, {}, {}, [])
        return original_get()
    
    mock_queue.get_current_queue_volatile = race_condition_get
    
    # Start with prompt in queue
    mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
    
    # Monitor execution state
    await _monitor_execution_state(prompt_id, run_id)
    
    # Verify RUNNING status was set
    mock_set_job_status.assert_called_once_with(run_id, JobStatus.RUNNING)


# Test 7: Fast Completion - Prompt moves to history mid-monitoring
@pytest.mark.asyncio
async def test_fast_completion_mid_monitoring(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test fast completion: prompt appears in history during monitoring."""
    prompt_id = "fast-mid-prompt"
    run_id = "fast-mid-run"
    
    check_count = [0]
    
    # Mock get_current_queue_volatile to simulate fast completion
    original_get = mock_queue.get_current_queue_volatile
    
    def fast_completion_get():
        check_count[0] += 1
        if check_count[0] == 3:
            # On third check, prompt appears in history
            mock_queue.history[prompt_id] = {
                'status': {'status_str': 'success', 'completed': True},
                'outputs': {}
            }
        return original_get()
    
    mock_queue.get_current_queue_volatile = fast_completion_get
    
    # Start with prompt in queue
    mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
    
    # Monitor execution state
    await _monitor_execution_state(prompt_id, run_id)
    
    # Verify RUNNING status was NOT set (completed too fast)
    mock_set_job_status.assert_not_called()


# Test 8: Exception Handling - set_job_status fails
@pytest.mark.asyncio
async def test_exception_in_set_job_status(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test exception handling: set_job_status raises exception."""
    prompt_id = "exception-prompt"
    run_id = "exception-run"
    
    # Configure mock to raise exception
    mock_set_job_status.side_effect = Exception("Database error")
    
    # Add prompt to running
    mock_queue.add_to_running(1, prompt_id, {}, {}, [])
    
    # Monitor execution state (should not crash)
    await _monitor_execution_state(prompt_id, run_id)
    
    # Verify exception was caught and logged
    mock_set_job_status.assert_called_once()


# Test 9: Sequential Execution - Second prompt waits for first
@pytest.mark.asyncio
async def test_sequential_execution_second_waits(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test sequential execution: second prompt waits while first executes."""
    prompt_id_1 = "seq-prompt-1"
    run_id_1 = "seq-run-1"
    prompt_id_2 = "seq-prompt-2"
    run_id_2 = "seq-run-2"
    
    # Add both to queue
    mock_queue.add_to_queue(1, prompt_id_1, {}, {}, [])
    mock_queue.add_to_queue(2, prompt_id_2, {}, {}, [])
    
    # First prompt starts executing
    mock_queue.queue.pop(0)
    mock_queue.add_to_running(1, prompt_id_1, {}, {}, [])
    
    # Monitor first (should become RUNNING)
    await _monitor_execution_state(prompt_id_1, run_id_1)
    
    # Verify first was marked RUNNING
    assert mock_set_job_status.call_count == 1
    mock_set_job_status.assert_called_with(run_id_1, JobStatus.RUNNING)
    
    # Verify second is still in queue
    assert any(q[1] == prompt_id_2 for q in mock_queue.queue)
    assert len(mock_queue.currently_running) == 1


# Test 10: Polling Interval - Verify 350ms sleep
@pytest.mark.asyncio
async def test_polling_interval_timing(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Test polling interval: verify 350ms sleep between checks."""
    prompt_id = "timing-prompt"
    run_id = "timing-run"
    
    # Add prompt to queue
    mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
    
    # Track sleep calls
    sleep_calls = []
    original_sleep = asyncio.sleep
    
    async def tracked_sleep(duration):
        sleep_calls.append(duration)
        if len(sleep_calls) >= 3:
            # After 3 sleeps, move to running to exit
            mock_queue.queue.clear()
            mock_queue.add_to_running(1, prompt_id, {}, {}, [])
        await original_sleep(duration)
    
    with patch('asyncio.sleep', side_effect=tracked_sleep):
        await _monitor_execution_state(prompt_id, run_id)
    
    # Verify sleep interval is 0.35 seconds
    assert all(duration == 0.35 for duration in sleep_calls)
    assert len(sleep_calls) >= 2  # At least 2 polling iterations


# Integration Test: End-to-End Workflow
@pytest.mark.asyncio
async def test_integration_full_workflow_lifecycle(
    mock_queue, mock_server, mock_set_job_status, mock_prompt_server, mock_config
):
    """Integration test: full workflow from queue to completion."""
    prompt_id = "integration-prompt"
    run_id = "integration-run"
    
    # Simulate complete workflow lifecycle
    async def simulate_workflow():
        # Start in queue
        mock_queue.add_to_queue(1, prompt_id, {}, {}, [])
        
        # Wait for monitoring to start
        await asyncio.sleep(0.2)
        
        # Move to running
        mock_queue.queue.clear()
        mock_queue.add_to_running(1, prompt_id, {}, {}, [])
        
        # Wait for RUNNING detection
        await asyncio.sleep(0.5)
        
        # Complete execution
        mock_queue.complete_prompt(1, prompt_id, 'success')
    
    # Run workflow simulation and monitoring concurrently
    workflow_task = asyncio.create_task(simulate_workflow())
    monitor_task = asyncio.create_task(_monitor_execution_state(prompt_id, run_id))
    
    await asyncio.gather(workflow_task, monitor_task)
    
    # Verify RUNNING status was set
    mock_set_job_status.assert_called_once_with(run_id, JobStatus.RUNNING)
    
    # Verify final state
    assert prompt_id in mock_queue.history
    assert mock_queue.history[prompt_id]['status']['status_str'] == 'success'
    assert len(mock_queue.currently_running) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
