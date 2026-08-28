from __future__ import annotations

from modules.nodes.primitives import something_2_string


def test_something_to_string_returns_all_declared_combinations_and_history(
    monkeypatch,
) -> None:
    sent = []
    monkeypatch.setattr(
        something_2_string,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    node = something_2_string.LF_Something2String
    response = node().on_exec(
        separator=" | ",
        json={"name": "LF"},
        boolean=True,
        float=1.5,
        integer=7,
        node_id=["string-node"],
    )

    result = response["result"]
    assert len(node.RETURN_TYPES) == 15
    assert len(node.RETURN_NAMES) == 15
    assert len(node.OUTPUT_IS_LIST) == 15
    assert len(node.OUTPUT_TOOLTIPS) == 15
    assert len(result) == 15
    assert all(isinstance(value, str) for value in result)
    by_name = dict(zip(node.RETURN_NAMES, result))
    assert by_name["json"] == '{"name": "LF"}'
    assert by_name["boolean_float_integer"] == "true | 1.5 | 7"
    assert by_name["json_boolean_float_integer"] == (
        '{"name": "LF"} | true | 1.5 | 7'
    )
    final_payload = response["ui"]["lf_output"][0]
    assert sent == [("something2string", final_payload, ["string-node"])]
