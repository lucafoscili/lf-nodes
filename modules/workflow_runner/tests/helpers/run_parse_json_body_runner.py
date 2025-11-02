import asyncio
import importlib.util
import pathlib
import sys

spec = importlib.util.spec_from_file_location(
    "test_utils", str(pathlib.Path(__file__).resolve().parent / "test_utils.py")
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

load_helpers_module = test_utils.load_helpers_module
MockRequest = test_utils.MockRequest


async def run_checks():
    helpers = load_helpers_module()

    # valid dict
    req = MockRequest(payload={"a": 1})
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert err is None and body == {"a": 1}

    # invalid json
    req = MockRequest(exc=Exception("bad json"))
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert body is None and hasattr(err, "status") and err.status == 400

    # wrong type
    req = MockRequest(payload=[1, 2, 3])
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert body is None and hasattr(err, "status") and err.status == 400

    # allow empty
    req = MockRequest(payload=None)
    body, err = await helpers.parse_json_body(req, expected_type=dict, allow_empty=True)
    assert err is None and body is None

    # list expected
    req = MockRequest(payload=[1])
    body, err = await helpers.parse_json_body(req, expected_type=list)
    assert err is None and body == [1]


if __name__ == "__main__":
    try:
        asyncio.run(run_checks())
        print("OK: parse_json_body checks passed")
    except AssertionError:
        print("FAILED: assertions in parse_json_body checks")
        raise
    except Exception:
        print("ERROR: exception while running parse_json_body checks")
        raise
