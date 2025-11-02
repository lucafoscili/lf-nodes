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


def test_parse_valid_with_seq():
    assert helpers.parse_last_event_id("run-1:10") == ("run-1", 10)


def test_parse_valid_no_seq():
    assert helpers.parse_last_event_id("run-abc") == ("run-abc", 0)


def test_parse_invalid_seq():
    assert helpers.parse_last_event_id("run-1:xyz") is None


def test_parse_empty_or_none():
    assert helpers.parse_last_event_id("") is None
    assert helpers.parse_last_event_id(None) is None
