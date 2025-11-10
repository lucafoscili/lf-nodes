import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

helpers = test_utils.load_helpers_module()

def run_checks():
    assert helpers.parse_last_event_id("run-1:5") == ("run-1", 5)
    assert helpers.parse_last_event_id("run-x") == ("run-x", 0)
    assert helpers.parse_last_event_id("") is None
    assert helpers.parse_last_event_id(None) is None
    assert helpers.parse_last_event_id("bad:seq") is None

if __name__ == "__main__":
    run_checks()
    print("OK: parse_last_event_id checks passed")