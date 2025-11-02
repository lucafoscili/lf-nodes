import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "serialize_shared",
    str(pathlib.Path(__file__).resolve().parent.parent.parent / "utils" / "serialize.py"),
)
serialize_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(serialize_mod)


class MockJob:
    def __init__(self, id, workflow_id, status, result=None, error=None, owner_id=None, seq=0, created_at=1.0, updated_at=None):
        self.id = id
        self.run_id = id
        self.workflow_id = workflow_id
        self.status = status
        self.result = result
        self.error = error
        self.owner_id = owner_id
        self.seq = seq
        self.created_at = created_at
        self.updated_at = updated_at


def test_shared_serialize_non_terminal_hides_result():
    job = MockJob("run-1", "wf-1", "running", result={"foo": "bar"}, seq=5)
    out = serialize_mod.serialize_job(job)
    assert out["run_id"] == "run-1"
    assert out["seq"] == 5
    assert out["result"] is None


def test_shared_serialize_terminal_includes_result():
    job = MockJob("run-2", "wf-2", "succeeded", result={"ok": True}, seq=2)
    out = serialize_mod.serialize_job(job)
    assert out["result"] == {"ok": True}


def test_shared_serialize_force_include_result():
    job = MockJob("run-3", "wf-3", "running", result={"x": 1}, seq=3)
    out = serialize_mod.serialize_job(job, include_result_for_terminal=True)
    assert out["result"] == {"x": 1}
