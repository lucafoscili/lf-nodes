import importlib.util
import pathlib
import pytest

# load shared test utilities
spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

MockRequest = test_utils.MockRequest
load_helpers_module = test_utils.load_helpers_module

def compute_expected_owner(subject: str) -> str:
    import hashlib

    return hashlib.sha256(subject.encode("utf-8")).hexdigest()

@pytest.mark.asyncio
async def test_get_owner_from_request_various():
    helpers = load_helpers_module()

    # cache case
    email = "User@Example.com"
    req = MockRequest(cache={"google_oauth_email": email})
    out = await helpers.get_owner_from_request(req)
    assert out == compute_expected_owner(email)

    # attribute case
    req = MockRequest(cache=None, attr={"google_oauth_email": "a@b"})
    out = await helpers.get_owner_from_request(req)
    assert out == compute_expected_owner("a@b")

    # non-str subj
    class SubjObj:
        def __str__(self):
            return "t@t"

    req = MockRequest(cache={"google_oauth_email": SubjObj()})
    out = await helpers.get_owner_from_request(req)
    assert out == compute_expected_owner("t@t")

    # missing subject -> None
    req = MockRequest(cache={})
    out = await helpers.get_owner_from_request(req)
    assert out is None
