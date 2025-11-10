import asyncio
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

helpers = test_utils.load_helpers_module()

class MockStreamResp:
    def __init__(self, fail_write=False, fail_drain=False):
        self.writes = []
        self.fail_write = fail_write
        self.fail_drain = fail_drain

    async def write(self, payload: bytes):
        if self.fail_write:
            raise ConnectionResetError()
        self.writes.append(payload)

    async def drain(self):
        if self.fail_drain:
            raise asyncio.CancelledError()
        return None

async def run_checks():
    resp = MockStreamResp()
    ev = {"run_id": "r1", "seq": 1, "status": "running"}
    ok = await helpers.write_sse_event(resp, ev)
    assert ok is True

    resp = MockStreamResp(fail_write=True)
    ev = {"run_id": "r2", "seq": 2}
    ok = await helpers.write_sse_event(resp, ev)
    assert ok is False

    resp = MockStreamResp(fail_drain=True)
    ev = {"run_id": "r3", "seq": 3}
    ok = await helpers.write_sse_event(resp, ev)
    assert ok is False

if __name__ == "__main__":
    asyncio.run(run_checks())
    print("OK: write_sse_event checks passed")