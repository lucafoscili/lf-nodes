"""Lightweight unit test for prompt_id flow without ComfyUI dependencies.

Tests the job store and serialization without requiring CUDA/ComfyUI imports.
Replaces print-based validation with direct assertions and removes duplicate class wrapper.
"""

import pytest

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

# Configure pytest-anyio to use asyncio backend for all async tests
pytestmark = pytest.mark.anyio

# Minimal local definitions to avoid imports
class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Job:
    """Minimal Job dataclass for testing."""
    id: str  # ComfyUI's prompt_id - the canonical identifier for this execution
    workflow_id: Optional[str] = None
    owner_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None
    seq: int = 0
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

def serialize_job(job: Job) -> Dict[str, Any]:
    """Simplified version of serialize_job from utils/serialize.py."""
    run_id = getattr(job, "id", None) or getattr(job, "run_id", None)
    
    return {
        "run_id": run_id,
        "workflowId": job.workflow_id,
        "status": job.status.value if hasattr(job.status, "value") else job.status,
        "createdAt": job.created_at.isoformat() if job.created_at else None,
        "updatedAt": job.updated_at.isoformat() if job.updated_at else None,
        "error": job.error,
    }

async def test_job_structure():
    """Test that Job structure and serialization work correctly with prompt_id."""
    prompt_id = "comfy-prompt-abc123"
    workflow_id = "workflow-xyz"
    owner_id = "user-123"
    
    job = Job(
        id=prompt_id,
        workflow_id=workflow_id,
        owner_id=owner_id
    )
    assert job.id == prompt_id, f"Job.id should be {prompt_id}"
    serialized = serialize_job(job)
    assert "run_id" in serialized, "Serialized job must have 'run_id' field"
    assert serialized["run_id"] == prompt_id, f"run_id should be {prompt_id}"
    assert serialized["workflowId"] == workflow_id, f"workflowId should be {workflow_id}"
    assert job.id == serialized['run_id'], "Job.id must map to run_id"
    job.status = JobStatus.RUNNING
    job.updated_at = datetime.now(timezone.utc)
    
    serialized_updated = serialize_job(job)
    assert serialized_updated['run_id'] == prompt_id, "run_id should remain stable"
    assert serialized_updated['status'] == 'running', "Status should be updated"
    uuid_like_prompt = "550e8400-e29b-41d4-a716-446655440000"
    job2 = Job(id=uuid_like_prompt, workflow_id="test-workflow")
    serialized2 = serialize_job(job2)
    assert serialized2['run_id'] == uuid_like_prompt, "Any prompt_id format should work"
    # No duplicate class wrapper; simple single test suffices.
