from __future__ import annotations

from modules.nodes.seeds import sequential_seeds_generator


def test_sequential_seeds_returns_all_declared_outputs_and_history(
    monkeypatch,
) -> None:
    history = []
    sent = []
    monkeypatch.setattr(
        sequential_seeds_generator,
        "create_history_node",
        lambda seed, nodes: history.append((seed, nodes)),
    )
    monkeypatch.setattr(
        sequential_seeds_generator,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    node = sequential_seeds_generator.LF_SequentialSeedsGenerator
    response = node().on_exec(
        seed=[41],
        enable_history=[True],
        ui_widget={"nodes": []},
        node_id=[["seed-node"]],
    )

    assert len(node.RETURN_TYPES) == 20
    assert len(node.RETURN_NAMES) == 20
    assert len(node.OUTPUT_TOOLTIPS) == 20
    assert response["result"] == tuple(range(41, 61))
    assert history and history[0][0] == "41"
    final_payload = response["ui"]["lf_output"][0]
    assert sent == [
        ("sequentialseedsgenerator", final_payload, [["seed-node"]])
    ]
