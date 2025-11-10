import asyncio
import hashlib
import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

load_helpers_module = test_utils.load_helpers_module
MockRequest = test_utils.MockRequest

async def main():
    helpers = load_helpers_module()
    req = MockRequest(cache=None, attr={"google_oauth_email": "a@b"})
    out = await helpers.get_owner_from_request(req)
    print("helper out:", out)
    print("expected:", hashlib.sha256(b"a@b").hexdigest())

if __name__ == "__main__":
    asyncio.run(main())
