"""
Test suite for updated_at field propagation in workflow runner.
Investigates why updated_at remains NULL/empty in database.
"""
import pytest
import sys
import time

from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add package root to path
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

# Mock server module before imports
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

from modules.workflow_runner.services import job_store
from modules.workflow_runner.services.job_store import JobStatus

pytestmark = pytest.mark.anyio

class TestUpdatedAtInMemory:
    """Test that in-memory job store would handle updated_at if the field existed."""
    
    async def test_create_job_has_created_at(self):
        """Verify created_at is set on job creation"""
        job_id = "test-run-123"
        workflow_id = "test-workflow"
        owner_id = "a" * 64
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            before = time.time()
            job = await job_store.create_job(job_id, workflow_id, owner_id=owner_id)
            after = time.time()
            
            assert job.created_at is not None, "created_at should be set"
            assert before <= job.created_at <= after, "created_at should be within test timeframe"
            
            # In-memory Job dataclass now includes updated_at for parity with SQLite
            assert hasattr(job, 'updated_at'), "In-memory Job should have updated_at field"
            # On creation, updated_at may be None or equal to created_at depending on implementation
            assert job.updated_at is None or isinstance(job.updated_at, float)
    
    async def test_set_job_status_in_memory(self):
        """Verify set_job_status works for in-memory jobs"""
        job_id = "test-run-456"
        workflow_id = "test-workflow"
        
        with patch.object(job_store, '_USE_PERSISTENCE', False):
            # Create job
            job = await job_store.create_job(job_id, workflow_id)
            assert job.status == JobStatus.PENDING
            
            # Update status
            updated = await job_store.set_job_status(
                job_id, 
                JobStatus.SUCCEEDED, 
                result={"output": "test"}
            )
            
            assert updated is not None
            assert updated.status == JobStatus.SUCCEEDED
            assert updated.result == {"output": "test"}
            
            # In-memory Job dataclass now includes updated_at and it should be set on status update
            assert hasattr(updated, 'updated_at')
            assert isinstance(updated.updated_at, float)

class TestUpdatedAtSQLite:
    """Test SQLite adapter's handling of updated_at field."""
    
    async def test_create_job_sql_statement_parameters(self):
        """Test that create_job SQL statement has correct number of parameters"""
        from modules.workflow_runner.services.job_store_sqlite import create_job
        
        # Mock the connection
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchone = AsyncMock(return_value=(
            "test-123", "wf", "pending", 12345.0, 12345.0, None, None, 0, "owner"
        ))
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.commit = AsyncMock()
        
        with patch('modules.workflow_runner.services.job_store_sqlite._conn', mock_conn):
            await create_job("test-123", "test-workflow", owner_id="abc123")
            
            # Check the INSERT statement call
            calls = mock_conn.execute.call_args_list
            insert_call = calls[0]  # First call should be INSERT
            
            sql = insert_call[0][0]
            params = insert_call[0][1]
            
            # Count placeholders in SQL
            placeholder_count = sql.count('?')
            param_count = len(params)
            
            print(f"SQL: {sql}")
            print(f"Params: {params}")
            print(f"Placeholder count: {placeholder_count}, Param count: {param_count}")
            
            assert placeholder_count == param_count, \
                f"SQL has {placeholder_count} placeholders but {param_count} parameters provided"
    
    async def test_set_job_status_sql_statement_parameters(self):
        """Test that set_job_status SQL statement has correct number of parameters"""
        from modules.workflow_runner.services.job_store_sqlite import set_job_status, get_job
        
        # Mock the connection
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchone = AsyncMock(return_value=(
            "test-456", "wf", "succeeded", 12345.0, 12346.0, '{"output":"test"}', None, 1, "owner"
        ))
        mock_conn.execute = AsyncMock(return_value=mock_cursor)
        mock_conn.commit = AsyncMock()
        
        with patch('modules.workflow_runner.services.job_store_sqlite._conn', mock_conn), \
             patch('modules.workflow_runner.services.job_store_sqlite.get_job', return_value=Mock()):
            
            await set_job_status("test-456", "succeeded", result={"output": "test"})
            
            # Check the INSERT statement call (within transaction)
            calls = [c for c in mock_conn.execute.call_args_list if 'INSERT INTO runs' in str(c)]
            
            if calls:
                insert_call = calls[0]
                sql = insert_call[0][0]
                params = insert_call[0][1]
                
                # Count placeholders in SQL
                placeholder_count = sql.count('?')
                param_count = len(params)
                
                print(f"SQL: {sql}")
                print(f"Params: {params}")
                print(f"Placeholder count: {placeholder_count}, Param count: {param_count}")
                
                assert placeholder_count == param_count, \
                    f"SQL has {placeholder_count} placeholders but {param_count} parameters provided"
    
    async def test_updated_at_field_in_jobrecord(self):
        """Verify JobRecord has updated_at field"""
        from modules.workflow_runner.services.job_store_sqlite import JobRecord
        import dataclasses
        
        # Check JobRecord has updated_at field
        fields = {f.name for f in dataclasses.fields(JobRecord)}
        assert 'updated_at' in fields, "JobRecord should have updated_at field"
        assert 'created_at' in fields, "JobRecord should have created_at field"
        
        # Create instance and verify both timestamps
        rec = JobRecord(
            run_id="test",
            workflow_id="wf",
            status="pending",
            created_at=123.0,
            updated_at=456.0,
            seq=0
        )
        
        assert rec.created_at == 123.0
        assert rec.updated_at == 456.0