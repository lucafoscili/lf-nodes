from __future__ import annotations

from modules.nodes.json import string_to_json


def test_list_mode_event_and_history_publish_one_string(monkeypatch) -> None:
    sent = []
    monkeypatch.setattr(
        string_to_json,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = string_to_json.LF_StringToJSON().on_exec(
        string=['{"answer": 42}'],
        node_id=["node-7"],
    )

    assert response["result"] == ({"answer": 42},)
    payload = response["ui"]["lf_output"][0]
    assert payload == {"value": '{"answer": 42}'}
    assert sent == [("stringtojson", payload, ["node-7"])]
