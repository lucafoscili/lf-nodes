import random
from unittest.mock import patch

import pytest

from modules.nodes.json.get_key_from_json_by_index import LF_GetKeyFromJSONByIndex
from modules.utils.constants import Input


@pytest.mark.parametrize("target", [
    {"z": "", "a": 100, "m": None},
    '{"z":"","a":100,"m":null}',
    [{"z": "", "a": 100, "m": None}],
])
def test_insertion_order_and_headless_history(target):
    before = random.getstate()
    for index, key in enumerate(("z", "a", "m")):
        with patch("modules.nodes.json.get_key_from_json_by_index.safe_send_sync") as send:
            result = LF_GetKeyFromJSONByIndex().on_exec(json_input=target, index=index)
        assert result["result"] == (key,)
        payload = result["ui"]["lf_output"][0]
        assert key in payload["value"]
        send.assert_called_once_with("getkeyfromjsonbyindex", payload, None)
    assert random.getstate() == before


@pytest.mark.parametrize("target", [{}, [], [{"a": 1}, {"b": 2}], "invalid", None, {1: "bad"}])
def test_invalid_objects(target):
    with pytest.raises(ValueError):
        LF_GetKeyFromJSONByIndex().on_exec(json_input=target, index=0)


@pytest.mark.parametrize("index", [-1, 2, 100, 1.5, True, "1", None])
def test_invalid_indices_never_wrap(index):
    with pytest.raises(ValueError, match="[Ii]ndex"):
        LF_GetKeyFromJSONByIndex().on_exec(json_input={"a": "", "b": ""}, index=index)


def test_schema_and_scalar_wrapper():
    node = LF_GetKeyFromJSONByIndex()
    schema = node.INPUT_TYPES()
    assert list(schema["required"]) == ["json_input", "index"]
    assert schema["required"]["index"][1]["default"] == 0
    assert node.RETURN_TYPES == (Input.STRING,)
    assert node.RETURN_NAMES == ("string",)
    assert node.OUTPUT_IS_LIST == (False,)
    assert not getattr(node, "INPUT_IS_LIST", False)
    with patch("modules.nodes.json.get_key_from_json_by_index.safe_send_sync"):
        assert node.on_exec(json_input={"first": ""}, index=[0], node_id=["12"])["result"] == ("first",)
