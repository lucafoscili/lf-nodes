"""Prompt ID flow tests.

Validates that:
1. Jobs use ComfyUI's prompt_id as canonical Job.id
2. Serialization exposes this as run_id
3. Retrieval by prompt_id returns the same job
"""

import pytest
import sys

from pathlib import Path

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

pytestmark = pytest.mark.anyio

async def test_prompt_id_flow():
    from modules.workflow_runner.services.job_store import create_job, get_job
    from modules.workflow_runner.utils.serialize import serialize_job

    test_prompt_id = "test-prompt-12345"
    test_workflow_id = "test-workflow-abc"

    job = await create_job(job_id=test_prompt_id, workflow_id=test_workflow_id, owner_id="test-user")

    # Job created with canonical ID
    assert job.id == test_prompt_id
    assert job.workflow_id == test_workflow_id
    assert job.owner_id == "test-user"

    # Retrieval by prompt_id
    retrieved_job = await get_job(test_prompt_id)
    assert retrieved_job is not None
    assert retrieved_job.id == test_prompt_id

    # Serialization exposes run_id
    serialized = serialize_job(job)
    assert serialized["run_id"] == test_prompt_id
    assert serialized["workflow_id"] == test_workflow_id
    # Mapping invariant
    assert job.id == serialized["run_id"]
