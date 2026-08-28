from __future__ import annotations

from modules.nodes.image import view_svgs
from modules.utils.constants import Input


def test_view_svgs_preserves_first_raw_input_and_extracts_every_svg(
    monkeypatch,
) -> None:
    events: list[tuple[str, dict, object]] = []
    monkeypatch.setattr(
        view_svgs,
        "safe_send_sync",
        lambda event, payload, node_id: events.append((event, payload, node_id)),
    )
    first_raw = b"prefix<svg id='first'>one</svg>suffix"
    second_raw = "before<svg id='second'>two</svg>after"

    response = view_svgs.LF_ViewSVGs().on_exec(
        svg=[first_raw, second_raw],
        node_id=["svg-node"],
    )
    result = response["result"]

    assert view_svgs.LF_ViewSVGs.RETURN_TYPES == (Input.STRING, Input.STRING)
    assert view_svgs.LF_ViewSVGs.RETURN_NAMES == ("svg", "svg_list")
    assert view_svgs.LF_ViewSVGs.OUTPUT_IS_LIST == (False, True)
    assert result == (
        first_raw.decode("utf-8"),
        ["<svg id='first'>one</svg>", "<svg id='second'>two</svg>"],
    )
    assert isinstance(result[0], str)
    assert isinstance(result[1], list)
    assert response["ui"]["lf_output"][0] is events[0][1]
    assert events == [
        (
            "viewsvgs",
            {
                "dataset": {
                    "nodes": [
                        {
                            "cells": {
                                "lfSlot": {"shape": "slot", "value": "slot-0"}
                            },
                            "id": "0",
                            "value": "0",
                        },
                        {
                            "cells": {
                                "lfSlot": {"shape": "slot", "value": "slot-1"}
                            },
                            "id": "1",
                            "value": "1",
                        },
                    ]
                },
                "slot_map": {
                    "slot-0": "<svg id='first'>one</svg>",
                    "slot-1": "<svg id='second'>two</svg>",
                },
            },
            ["svg-node"],
        )
    ]
