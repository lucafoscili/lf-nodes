"""
Test to understand the actual cold-load behavior.
Simulates what happens when UI calls GET /runs?owner=me

This module is a developer utility (prints to stdout) and is not intended
to be executed as a pytest test. Skip it during automated test collection.
"""
import pytest

pytest.skip("Utility cold-load script; skip during automated pytest runs", allow_module_level=True)
import asyncio
import sys
from pathlib import Path

# Add package root to path
pkg_root = Path(__file__).resolve().parents[1]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

async def test_cold_load():
    """Test what happens when cold-loading runs."""
    from modules.workflow_runner.config import get_settings
    from modules.workflow_runner.services import job_store
    
    settings = get_settings()
    
    print("=" * 60)
    print("Cold Load Test")
    print("=" * 60)
    print()
    
    # Check settings
    print("Settings:")
    print(f"  ENABLE_GOOGLE_OAUTH: {settings.ENABLE_GOOGLE_OAUTH}")
    print(f"  WORKFLOW_RUNNER_USE_PERSISTENCE: {settings.WORKFLOW_RUNNER_USE_PERSISTENCE}")
    print(f"  WORKFLOW_RUNNER_DEBUG: {settings.WORKFLOW_RUNNER_DEBUG}")
    print()
    
    # Check what's in the job store
    print("Job Store Contents:")
    all_jobs = await job_store.list_jobs()
    print(f"  Total jobs: {len(all_jobs)}")
    print()
    
    if all_jobs:
        print("  Sample jobs:")
        for i, (job_id, job) in enumerate(list(all_jobs.items())[:3]):
            print(f"    {i+1}. {job_id[:16]}...")
            print(f"       status: {job.status}")
            print(f"       owner_id: {job.owner_id[:16] if job.owner_id else 'None'}...")
            print(f"       created_at: {job.created_at}")
            print(f"       updated_at: {job.updated_at}")
            print()
    
    # Simulate cold-load with owner filtering
    print("Simulating cold-load with owner_id filtering:")
    print("-" * 60)
    
    # Get unique owner_ids
    owner_ids = set()
    for job in all_jobs.values():
        if job.owner_id:
            owner_ids.add(job.owner_id)
    
    print(f"  Found {len(owner_ids)} unique owner_ids")
    print()
    
    if owner_ids:
        # Try filtering by first owner
        test_owner = list(owner_ids)[0]
        print(f"  Testing filter with owner_id: {test_owner[:16]}...")
        filtered_jobs = await job_store.list_jobs(owner_id=test_owner)
        print(f"  Filtered result: {len(filtered_jobs)} jobs")
        print()
        
        # Try filtering by non-existent owner
        fake_owner = "x" * 64
        empty_jobs = await job_store.list_jobs(owner_id=fake_owner)
        print(f"  Filter with fake owner_id: {len(empty_jobs)} jobs")
        print()
    
    # Check what happens with owner=None (should return all)
    print("  Filter with owner_id=None (should return all):")
    none_jobs = await job_store.list_jobs(owner_id=None)
    print(f"  Result: {len(none_jobs)} jobs")
    print()
    
    # Check what happens with empty string
    print("  Filter with owner_id='' (empty string):")
    empty_str_jobs = await job_store.list_jobs(owner_id="")
    print(f"  Result: {len(empty_str_jobs)} jobs")
    print()
    
    print("=" * 60)
    print("Key Findings:")
    print("=" * 60)
    
    if not settings.ENABLE_GOOGLE_OAUTH:
        print("⚠️  OAuth is DISABLED")
        print("   This means the endpoint doesn't require authentication")
        print("   BUT owner=me won't work because there's no email to derive owner_id from")
        print()
        print("   When UI calls GET /runs?owner=me:")
        print("   - Auth check is skipped")
        print("   - owner_q == 'me' but _ENABLE_GOOGLE_OAUTH is False")
        print("   - So owner_id stays None")
        print("   - list_jobs(owner_id=None) returns ALL jobs")
        print()
        print("   SOLUTION: Either enable OAuth OR UI shouldn't use owner=me")
    else:
        print("✓ OAuth is ENABLED")
        print("  The endpoint requires authentication")
        print("  If you're getting 403, it means the cookie is missing or invalid")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_cold_load())
