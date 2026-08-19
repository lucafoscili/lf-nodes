"""Queue-free workflow graph and LF coverage preflight tests."""

from __future__ import annotations

from modules.workflow_runner.scripts.workflow_preflight import (
    discover_lf_node_types,
    preflight_workflow_data,
)


def _workflow() -> dict:
    return {
        "nodes": [
            {
                "id": 1,
                "type": "LF_Source",
                "inputs": [],
                "outputs": [{"name": "value", "links": [7]}],
            },
            {
                "id": 2,
                "type": "LF_Target",
                "inputs": [{"name": "value", "link": 7}],
                "outputs": [],
            },
        ],
        "links": [[7, 1, 0, 2, 0, "STRING"]],
    }


def _converter(workflow: dict) -> dict:
    return {
        str(node["id"]): {"class_type": node["type"], "inputs": {}}
        for node in workflow["nodes"]
    }


def test_source_mapping_inventory_includes_current_nodes() -> None:
    mappings = discover_lf_node_types()

    assert "LF_GetValueFromJSON" in mappings
    assert "LF_YouTubeReference" in mappings


def test_valid_graph_reports_coverage_without_queueing() -> None:
    report = preflight_workflow_data(
        _workflow(),
        lf_node_types={"LF_Source", "LF_Target", "LF_Unused"},
        converter=_converter,
    )

    assert report["status"] == "complete"
    assert report["counts"] == {
        "links": 1,
        "nodes": 2,
        "prompt_nodes": 2,
        "unique_lf_types": 2,
        "unique_types": 2,
    }
    assert report["uncovered_lf_types"] == ["LF_Unused"]


def test_require_all_nodes_turns_coverage_gap_into_blocker() -> None:
    report = preflight_workflow_data(
        _workflow(),
        lf_node_types={"LF_Source", "LF_Target", "LF_Unused"},
        require_all_lf_nodes=True,
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert any("LF_Unused" in error for error in report["errors"])


def test_unknown_lf_type_blocks_preflight() -> None:
    report = preflight_workflow_data(
        _workflow(),
        lf_node_types={"LF_Source"},
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert report["missing_lf_types"] == ["LF_Target"]


def test_broken_link_endpoint_blocks_preflight() -> None:
    workflow = _workflow()
    workflow["links"][0][3] = 999
    report = preflight_workflow_data(
        workflow,
        lf_node_types={"LF_Source", "LF_Target"},
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert any("missing target node 999" in error for error in report["errors"])
    assert any("does not target node 2" in error for error in report["errors"])


def test_duplicate_node_and_link_ids_block_preflight() -> None:
    workflow = _workflow()
    workflow["nodes"].append(dict(workflow["nodes"][0]))
    workflow["links"].append(list(workflow["links"][0]))
    report = preflight_workflow_data(
        workflow,
        lf_node_types={"LF_Source", "LF_Target"},
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert "Duplicate node id: 1" in report["errors"]
    assert "Duplicate link id: 7" in report["errors"]


def test_malformed_socket_metadata_blocks_without_crashing() -> None:
    workflow = _workflow()
    workflow["nodes"][0]["outputs"][0]["links"] = 7
    workflow["nodes"][1]["inputs"] = {"link": 7}

    report = preflight_workflow_data(
        workflow,
        lf_node_types={"LF_Source", "LF_Target"},
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert "Node 1 output 0 links must be a list" in report["errors"]
    assert "Node 2 inputs must be a list" in report["errors"]


def test_orphan_link_blocks_preflight() -> None:
    workflow = _workflow()
    workflow["nodes"][0]["outputs"][0]["links"] = []
    workflow["nodes"][1]["inputs"][0]["link"] = None

    report = preflight_workflow_data(
        workflow,
        lf_node_types={"LF_Source", "LF_Target"},
        converter=_converter,
    )

    assert report["status"] == "blocked"
    assert "Link 7 is not attached to target input metadata" in report["errors"]
    assert "Link 7 is not attached to source output metadata" in report["errors"]
