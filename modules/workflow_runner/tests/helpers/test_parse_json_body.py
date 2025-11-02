import asyncio
import importlib.util
import pathlib
import sys

import pytest
from aiohttp import web

# import shared test utils from this helpers package
spec = importlib.util.spec_from_file_location(
    "test_utils",
    str(pathlib.Path(__file__).resolve().parent / "test_utils.py"),
)
test_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_utils)

MockRequest = test_utils.MockRequest
load_helpers_module = test_utils.load_helpers_module


@pytest.mark.asyncio
async def test_valid_json_dict():
    helpers = load_helpers_module()
    req = MockRequest(payload={"a": 1})
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert err is None
    assert body == {"a": 1}


@pytest.mark.asyncio
async def test_invalid_json_raises():
    helpers = load_helpers_module()
    req = MockRequest(exc=Exception("bad json"))
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert body is None
    assert isinstance(err, web.Response)
    assert err.status == 400
    assert "invalid_json" in err.text


@pytest.mark.asyncio
async def test_wrong_type_list_instead_of_dict():
    helpers = load_helpers_module()
    req = MockRequest(payload=[1, 2, 3])
    body, err = await helpers.parse_json_body(req, expected_type=dict)
    assert body is None
    assert isinstance(err, web.Response)
    assert err.status == 400
    assert "invalid_payload" in err.text


@pytest.mark.asyncio
async def test_allow_empty_allows_none():
    helpers = load_helpers_module()
    req = MockRequest(payload=None)
    body, err = await helpers.parse_json_body(req, expected_type=dict, allow_empty=True)
    assert err is None
    assert body is None


@pytest.mark.asyncio
async def test_valid_list_when_expected_list():
    helpers = load_helpers_module()
    req = MockRequest(payload=[1])
    body, err = await helpers.parse_json_body(req, expected_type=list)
    assert err is None
    assert body == [1]
