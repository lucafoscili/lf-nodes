import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

helpers = test_utils.load_helpers_module()


class MockJob:
    def __init__(self, id, workflow_id, status, result=None, seq=0):
        self.id = id
        self.run_id = id
        self.workflow_id = workflow_id
        self.status = status
        self.result = result
        self.seq = seq


def run_checks():
    j1 = MockJob("r1", "w1", "running", result={"a": 1}, seq=1)
    out1 = helpers.serialize_job(j1)
    assert out1["result"] is None

    j2 = MockJob("r2", "w2", "succeeded", result={"ok": True}, seq=2)
    out2 = helpers.serialize_job(j2)
    assert out2["result"] == {"ok": True}

    j3 = MockJob("r3", "w3", "running", result={"x": 1}, seq=3)
    out3 = helpers.serialize_job(j3, include_result_for_terminal=True)
    assert out3["result"] == {"x": 1}


if __name__ == "__main__":
    run_checks()
    print("OK: serialize_job checks passed")
