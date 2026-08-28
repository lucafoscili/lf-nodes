from __future__ import annotations

import pytest

from modules.nodes.json import set_value_in_json
from modules.utils.constants import Input


def test_json_list_socket_remains_a_legacy_scalar_json_collection(
    monkeypatch,
) -> None:
    monkeypatch.setattr(set_value_in_json, "safe_send_sync", lambda *_args: None)
    documents = [{"name": "first"}]

    result = set_value_in_json.LF_SetValueInJSON().on_exec(
        json_input=documents,
        key=["rank"],
        value=[1],
        node_id=["json-node"],
    )

    assert set_value_in_json.LF_SetValueInJSON.RETURN_TYPES == (
        Input.JSON,
        Input.JSON,
    )
    assert set_value_in_json.LF_SetValueInJSON.RETURN_NAMES == (
        "json",
        "json_list",
    )
    assert set_value_in_json.LF_SetValueInJSON.OUTPUT_IS_LIST == (False, False)
    assert result == (
        {"name": "first", "rank": 1},
        [{"name": "first", "rank": 1}],
    )
    assert isinstance(result[0], dict)
    assert isinstance(result[1], list)
    assert result[0] is result[1][0]


def test_set_value_rejects_partial_value_cardinality(monkeypatch) -> None:
    monkeypatch.setattr(set_value_in_json, "safe_send_sync", lambda *_args: None)

    with pytest.raises(ValueError, match="value.*exactly 3 values; got 2"):
        set_value_in_json.LF_SetValueInJSON().on_exec(
            json_input=[{"id": 1}, {"id": 2}, {"id": 3}],
            key=["rank"],
            value=[10, 20],
        )
