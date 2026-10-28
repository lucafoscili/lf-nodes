import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_canonical_titanic_reaches_or_explicitly_exempts_every_published_lf_node_type():
    from modules.workflow_runner.scripts.workflow_preflight import validate_lf_node_coverage

    workflow = json.loads(
        (REPO_ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (REPO_ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8")
    )

    assert validate_lf_node_coverage(workflow, manifest) == []


def _coverage(workflow, *, exemptions=None, disabled=None):
    from modules.workflow_runner.scripts.workflow_preflight import validate_lf_node_coverage

    return validate_lf_node_coverage(
        workflow,
        {
            "coverageCases": [{"targets": [3]}],
            "coverageExemptions": exemptions or [],
            "disabledNodes": disabled or [],
        },
        lf_node_types={"LF_Source", "LF_Transform", "LF_Output"},
    )


def _coverage_workflow():
    return {
        "nodes": [
            {"id": 1, "type": "LF_Source"},
            {"id": 2, "type": "LF_Transform"},
            {"id": 3, "type": "LF_Output"},
        ],
        "links": [[1, 1, 0, 2, 0, "STRING"], [2, 2, 0, 3, 0, "STRING"]],
    }


def test_detached_type_presence_is_not_execution_coverage():
    workflow = _coverage_workflow()
    workflow["links"].pop(0)
    assert _coverage(workflow) == [
        "LF node type LF_Source is not reachable from coverage targets and has no exemption"
    ]


def test_ordinary_and_use_everywhere_ancestor_chains_count_as_coverage():
    workflow = _coverage_workflow()
    assert _coverage(workflow) == []
    workflow["links"].pop(0)
    workflow["extra"] = {"ue_links": [{"upstream": "1", "downstream": 2}]}
    assert _coverage(workflow) == []
    workflow["links"].append([3, 3, 0, 1, 0, "STRING"])
    assert _coverage(workflow) == []


def test_disabled_nodes_stop_coverage_and_reuse_policy_exemption_reasons():
    workflow = _coverage_workflow()
    workflow["nodes"][1]["mode"] = 2
    assert len(_coverage(workflow)) == 2
    assert _coverage(
        workflow,
        disabled=[{"id": 2, "type": "LF_Transform", "reason": "external intake disabled by policy"}],
        exemptions=[{"type": "LF_Source", "nodeIds": [1], "reason": "dormant upstream branch"}],
    ) == []
    # A disabled target is not execution coverage either.
    workflow["nodes"][2]["mode"] = 2
    assert any("LF_Output is not reachable" in error for error in _coverage(workflow))


def test_exemptions_require_reasons_and_exact_fixture_instances():
    workflow = _coverage_workflow()
    workflow["links"].pop(0)
    exemption = {"type": "LF_Source", "nodeIds": [1], "reason": "dormant source pending fixture work"}
    assert _coverage(workflow, exemptions=[exemption]) == []
    assert _coverage(workflow, exemptions=[{**exemption, "reason": " "}]) == [
        "Coverage exemption for LF_Source requires a reason"
    ]
    assert _coverage(workflow, exemptions=[{**exemption, "nodeIds": []}]) == [
        "Coverage exemption node IDs do not match LF_Source"
    ]
