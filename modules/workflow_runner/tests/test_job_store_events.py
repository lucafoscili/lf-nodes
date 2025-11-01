import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# ensure package root on path
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from modules.workflow_runner.services import job_store

pytestmark = pytest.mark.anyio


async def test_create_job_publishes_event_with_workflow_and_updated_at():
    # use in-memory store
    with patch.object(job_store, '_USE_PERSISTENCE', False):
        q = job_store.subscribe_events()
        job = await job_store.create_job('test-run-evt', 'remove_bg', owner_id='owner1')
        # get published event
        ev = await q.get()
        assert ev.get('run_id') == 'test-run-evt'
        assert ev.get('workflow_id') == 'remove_bg'
        # updated_at should be present (created_at used initially)
        assert 'created_at' in ev
        assert 'seq' in ev
        job_store.unsubscribe_events(q)


async def test_set_job_status_publishes_event_preserving_workflow_id():
    with patch.object(job_store, '_USE_PERSISTENCE', False):
        # create job first
        _ = await job_store.create_job('test-run-2', 'resize', owner_id=None)
        q = job_store.subscribe_events()
        # set status to succeeded with result
        updated = await job_store.set_job_status('test-run-2', job_store.JobStatus.SUCCEEDED, result={'ok': True})
        ev = await q.get()
        assert ev.get('run_id') == 'test-run-2'
        # workflow_id should still be present
        assert ev.get('workflow_id') == 'resize'
        assert ev.get('status') == job_store.JobStatus.SUCCEEDED.value
        job_store.unsubscribe_events(q)
