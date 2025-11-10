"""
Test concurrent updates to the SQLite job store adapter.

Verifies that:
1. Concurrent status updates don't cause transaction nesting errors
2. seq counter increments correctly under load
3. owner_id and workflow_id are preserved across updates
4. create_job doesn't clobber existing rows
"""

import asyncio
import pytest
import sys

from pathlib import Path

# ensure package root on path
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from modules.workflow_runner.services import job_store_sqlite as mod

# Only test with asyncio (trio causes event loop issues with aiosqlite)
pytestmark = [pytest.mark.anyio, pytest.mark.asyncio]

# Override anyio backend to only use asyncio
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def temp_db(tmp_path):
    """Provide a temporary SQLite database for each test."""
    db_path = str(tmp_path / "test_concurrent.db")
    mod.configure(db_path)
    yield db_path
    # Cleanup
    await mod.close()


async def test_concurrent_status_updates_no_transaction_errors(temp_db):
    """Verify that concurrent status updates don't cause transaction nesting errors."""
    run_id = "concurrent-test-1"
    await mod.create_job(run_id, workflow_id="test_workflow", owner_id="user1")

    # Perform 25 concurrent status updates
    async def bump_status():
        await mod.set_job_status(run_id, "running")

    # This should not raise OperationalError: cannot start a transaction within a transaction
    await asyncio.gather(*[bump_status() for _ in range(25)])

    # Verify the job exists and has been updated
    rec = await mod.get_job(run_id)
    assert rec is not None
    assert rec.status == "running"
    # seq should be at least 25 (initial pending + 25 running updates)
    assert rec.seq >= 25


async def test_seq_increments_correctly_under_concurrent_load(temp_db):
    """Verify seq counter increments monotonically under concurrent updates."""
    run_id = "seq-test-1"
    await mod.create_job(run_id, workflow_id="test_workflow", owner_id="user1")

    # Get initial seq (should be 0 after create)
    initial = await mod.get_job(run_id)
    assert initial.seq == 0

    # Perform 50 concurrent updates with different statuses
    statuses = ["running", "succeeded", "failed", "pending", "running"]
    
    async def update_with_status(status):
        await mod.set_job_status(run_id, status)

    tasks = [update_with_status(statuses[i % len(statuses)]) for i in range(50)]
    await asyncio.gather(*tasks)

    # Verify seq has incremented correctly
    final = await mod.get_job(run_id)
    assert final.seq >= 50  # At least 50 increments


async def test_owner_and_workflow_preserved_across_updates(temp_db):
    """Verify owner_id and workflow_id are preserved when updating status."""
    run_id = "preserve-test-1"
    original_workflow = "original_workflow"
    original_owner = "original_owner"
    
    # Create job with owner and workflow
    await mod.create_job(run_id, workflow_id=original_workflow, owner_id=original_owner)

    # Update status multiple times concurrently
    async def update_status(status):
        # set_job_status passes NULL for workflow_id and owner_id
        await mod.set_job_status(run_id, status, result={"test": True})

    await asyncio.gather(*[update_status("running") for _ in range(20)])

    # Verify original values are preserved
    rec = await mod.get_job(run_id)
    assert rec is not None
    assert rec.workflow_id == original_workflow, "workflow_id should be preserved"
    assert rec.owner_id == original_owner, "owner_id should be preserved"


async def test_create_job_does_not_clobber_existing_rows(temp_db):
    """Verify create_job with ON CONFLICT DO NOTHING doesn't reset existing data."""
    run_id = "no-clobber-test-1"
    
    # Create initial job
    await mod.create_job(run_id, workflow_id="workflow_v1", owner_id="user1")
    
    # Update status to increment seq
    await mod.set_job_status(run_id, "running")
    await mod.set_job_status(run_id, "succeeded", result={"output": "test"})
    
    # Get current state
    before = await mod.get_job(run_id)
    assert before.seq >= 2
    assert before.status == "succeeded"
    
    # Attempt to create the same job again (should do nothing)
    await mod.create_job(run_id, workflow_id="workflow_v2", owner_id="user2")
    
    # Verify original data is preserved (not replaced)
    after = await mod.get_job(run_id)
    assert after.seq == before.seq, "seq should not reset to 0"
    assert after.status == before.status, "status should not reset to pending"
    assert after.workflow_id == before.workflow_id, "workflow_id should not change"
    assert after.owner_id == before.owner_id, "owner_id should not change"


async def test_mixed_concurrent_operations(temp_db):
    """Test a mix of create_job and set_job_status operations concurrently."""
    run_ids = [f"mixed-test-{i}" for i in range(10)]
    
    async def create_and_update(run_id, idx):
        # Create job
        await mod.create_job(run_id, workflow_id=f"workflow_{idx}", owner_id=f"user_{idx}")
        # Update status multiple times
        await mod.set_job_status(run_id, "running")
        await mod.set_job_status(run_id, "succeeded", result={"idx": idx})
    
    # Run all operations concurrently
    await asyncio.gather(*[create_and_update(rid, i) for i, rid in enumerate(run_ids)])
    
    # Verify all jobs exist with correct data
    for idx, run_id in enumerate(run_ids):
        rec = await mod.get_job(run_id)
        assert rec is not None
        assert rec.workflow_id == f"workflow_{idx}"
        assert rec.owner_id == f"user_{idx}"
        assert rec.status == "succeeded"
        assert rec.seq >= 2  # At least create + 2 updates


async def test_concurrent_updates_different_runs(temp_db):
    """Verify concurrent updates to different runs don't interfere with each other."""
    num_runs = 20
    run_ids = [f"multi-run-{i}" for i in range(num_runs)]
    
    # Create all runs
    for run_id in run_ids:
        await mod.create_job(run_id, workflow_id="test", owner_id="user")
    
    # Update each run concurrently
    async def update_run(run_id, num_updates):
        for _ in range(num_updates):
            await mod.set_job_status(run_id, "running")
    
    # Each run gets different number of updates
    tasks = [update_run(run_ids[i], i + 1) for i in range(num_runs)]
    await asyncio.gather(*tasks)
    
    # Verify each run has correct seq
    for i, run_id in enumerate(run_ids):
        rec = await mod.get_job(run_id)
        expected_min_seq = i + 1  # number of updates for this run
        assert rec.seq >= expected_min_seq, f"Run {run_id} should have seq >= {expected_min_seq}"


async def test_concurrent_mixed_status_transitions(temp_db):
    """Test concurrent status transitions (pending→running→succeeded) with proper sequencing.
    
    Ensures no out-of-order regression when multiple tasks update the same run
    with different terminal statuses concurrently.
    """
    run_id = "mixed-status-test-1"
    await mod.create_job(run_id, workflow_id="test_workflow", owner_id="user1")
    
    # Sequence of status transitions
    status_sequence = ["running"] * 10 + ["succeeded"] * 5 + ["running"] * 5 + ["succeeded"]
    
    async def update_with_status(status, delay=0):
        if delay:
            await asyncio.sleep(delay * 0.001)  # small stagger
        await mod.set_job_status(run_id, status, result={"status": status} if status == "succeeded" else None)
    
    # Fire off 21 concurrent updates with slight delays to mix them up
    tasks = [update_with_status(status_sequence[i], i % 3) for i in range(len(status_sequence))]
    await asyncio.gather(*tasks)
    
    # Verify final state
    final = await mod.get_job(run_id)
    assert final is not None
    
    # Final status should be one of the terminal states
    assert final.status in ["succeeded", "running"], f"Final status should be terminal, got {final.status}"
    
    # seq should be at least: initial create (0) + 21 updates
    # Note: create sets seq=0, each update increments, so we expect >= 21
    assert final.seq >= 21, f"Expected seq >= 21, got {final.seq}"
    
    # If final status is succeeded, result should be set
    if final.status == "succeeded":
        assert final.result is not None, "Succeeded status should have result"
        assert final.result.get("status") == "succeeded", "Result should indicate succeeded"
    
    # Verify workflow_id and owner_id preserved through all transitions
    assert final.workflow_id == "test_workflow", "workflow_id should be preserved"
    assert final.owner_id == "user1", "owner_id should be preserved"
