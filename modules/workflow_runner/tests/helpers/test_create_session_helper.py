import importlib.util
import pathlib
import pytest


spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

helpers = test_utils.load_helpers_module()
MockRequest = test_utils.MockRequest


class MockResponse:
    def __init__(self):
        self.cookies_set = {}
        self.cookies_deleted = []

    def set_cookie(self, name, value, **kwargs):
        self.cookies_set[name] = (value, kwargs)

    def del_cookie(self, name, **kwargs):
        self.cookies_deleted.append((name, kwargs))


def test_create_and_set_session_cookie_success():
    called = {}

    def stub_create(email):
        called['email'] = email
        return "sess-123", 999999

    resp = MockResponse()
    req = MockRequest(attr={"scheme": "https"})
    sid, exp = helpers.create_and_set_session_cookie(resp, req, "u@e", create_session_fn=stub_create)
    assert sid == "sess-123"
    assert exp == 999999
    assert resp.cookies_set.get("LF_SESSION") is not None


def test_create_and_set_session_cookie_failure():
    def bad_create(email):
        raise RuntimeError("boom")

    resp = MockResponse()
    req = MockRequest()
    sid, exp = helpers.create_and_set_session_cookie(resp, req, "u@e", create_session_fn=bad_create)
    assert sid is None and exp is None
    assert not resp.cookies_set
