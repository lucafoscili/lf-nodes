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


def test_titanic_face_icon_and_motion_inventory_has_explicit_execution_boundaries():
    workflow = json.loads((REPO_ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
    manifest = json.loads((REPO_ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in workflow["nodes"]}
    cases = {case["id"]: case for case in manifest["coverageCases"]}
    disabled = {item["id"]: item for item in manifest["disabledNodes"]}

    def upstream(identifier, name):
        slot = next(i for i, value in enumerate(nodes[identifier]["inputs"]) if value["name"] == name)
        return next(link[1:3] for link in workflow["links"] if link[3:5] == [identifier, slot])

    for identifier, kind in ((669, "LF_VideoToMotion"), (670, "LF_MotionToVideo")):
        assert nodes[identifier]["type"] == kind
        assert nodes[identifier]["mode"] == 2
        assert disabled[identifier]["type"] == kind
        assert "required" in disabled[identifier]["reason"]
    assert upstream(670, "motion_file") == [669, 0]
    assert nodes[669]["widgets_values_named"]["stage_timeout_seconds"] == 0
    assert nodes[670]["widgets_values_named"]["image_frame_limit"] == 32
    assert not ({669, 670} & {target for case in cases.values() for target in case["targets"]})

    assert nodes[671]["type"] == "LF_FaceAlign"
    assert nodes[672]["type"] == "LF_FaceIdentity"
    assert nodes[676]["type"] == "LF_LoadImages"
    assert nodes[676]["widgets_values_named"]["dir"] == "scripts/quality/fixtures/titanic-face"
    assert nodes[676]["widgets_values_named"]["load_cap"] == 2
    assert upstream(671, "image") == [676, 1]
    assert upstream(672, "image") == [671, 0]
    assert upstream(672, "metadata") == [671, 2]
    assert upstream(673, "json_input") == [672, 0]
    face_case = cases["model.face-align-identity"]
    assert face_case["resourceClass"] == "model-cpu"
    assert face_case["targets"] == [673]
    assert face_case["bindings"] == {"fixtureFaceSourceNodeIds": [676]}
    assert face_case["execution"]["requiredNodeIds"] == [671, 672]
    assert face_case["execution"]["forbiddenCachedNodeIds"] == [671, 672]
    assert face_case["expect"]["672"]["faceIdentity"]["minimumCrossCosine"] == 0.65
    for identifier in (671, 672, 673, 676):
        assert nodes[identifier]["mode"] == 0
        assert identifier not in disabled

    assert nodes[674]["type"] == "LF_IconFramer"
    assert upstream(674, "image") == [654, 0]
    assert upstream(674, "mask") == [657, 0]
    assert cases["cpu.icon-framer"]["resourceClass"] == "cpu"
    assert upstream(675, "image") == [674, 2]
    assert cases["cpu.icon-framer"]["targets"] == [675]
    assert cases["cpu.icon-framer"]["execution"]["requiredNodeIds"] == [674]
