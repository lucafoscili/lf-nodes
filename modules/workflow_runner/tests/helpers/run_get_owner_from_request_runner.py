import asyncio
import importlib.util
import pathlib

def load_helpers_module():
    p = pathlib.Path(__file__).resolve()
    base = next((x for x in p.parents if x.name == "workflow_runner"), None)
    if base is None:
        raise RuntimeError("could not locate workflow_runner ancestor")
    helper_path = base / "controllers" / "_helpers.py"
    spec = importlib.util.spec_from_file_location("wf_helpers", str(helper_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_auth_module():
    # kept for compatibility but not used in the runner; locate auth_service if needed
    p = pathlib.Path(__file__).resolve()
    base = next((x for x in p.parents if x.name == "workflow_runner"), None)
    if base is None:
        raise RuntimeError("could not locate workflow_runner ancestor")
    svc_path = base / "services" / "auth_service.py"
    spec = importlib.util.spec_from_file_location("wf_auth_service", str(svc_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class MockRequest:
    def __init__(self, cache=None, attr=None):
        self._cache = cache
        if attr is not None:
            for k, v in attr.items():
                try:
                    setattr(self, k, v)
                except Exception:
                    pass

    def get(self, key, default=None):
        if isinstance(self._cache, dict):
            return self._cache.get(key, default)
        return default

async def run_checks():
    helpers = load_helpers_module()

    def compute_expected_owner(subject: str) -> str:
        import hashlib

        return hashlib.sha256(subject.encode("utf-8")).hexdigest()

    req = MockRequest(cache={"google_oauth_email": "User@Example.com"})
    out = await helpers.get_owner_from_request(req)
    assert out == compute_expected_owner("User@Example.com")

    req = MockRequest(cache=None, attr={"google_oauth_email": "a@b"})
    out = await helpers.get_owner_from_request(req)
    expected = compute_expected_owner("a@b")
    if out != expected:
        print("DEBUG: actual:", out)
        print("DEBUG: expected:", expected)
    assert out == expected

    class SubjObj:
        def __str__(self):
            return "t@t"

    req = MockRequest(cache={"google_oauth_email": SubjObj()})
    out = await helpers.get_owner_from_request(req)
    assert out == compute_expected_owner("t@t")

    req = MockRequest(cache={})
    out = await helpers.get_owner_from_request(req)
    assert out is None

    print("OK: get_owner_from_request checks passed")

if __name__ == "__main__":
    try:
        asyncio.run(run_checks())
    except AssertionError:
        print("FAILED: assertions in get_owner_from_request checks")
        raise
    except Exception:
        print("ERROR: exception while running get_owner_from_request checks")
        raise
