"""Deterministic public retarget inputs and honest Titanic inventory coverage."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from modules.utils.glb_texture import read_glb
from modules.utils.helpers.motion.format import validate_motion

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "scripts/quality/fixtures/titanic-motion"


def generator():
    spec = importlib.util.spec_from_file_location("motion_fixture_generator", ROOT / "scripts/quality/update_titanic_motion_coverage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_inputs_reproduce_existing_manifest_pins_and_are_self_contained():
    manifest = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
    pins = {Path(item["path"]).name: item["expectedSha256"] for item in manifest["fixtures"]}
    for name, blob in generator().synthetic_assets().items():
        assert blob == (ASSETS / name).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == pins[name]
    motion = validate_motion(json.loads((ASSETS / "motion.json").read_text(encoding="utf-8")))
    assert len(motion["world"]["body_pose"]) == 3
    assert motion["world"]["transl"][0] != motion["world"]["transl"][-1]
    rig, binary = read_glb((ASSETS / "rig.glb").read_bytes())
    assert len(rig["skins"][0]["joints"]) == 22
    assert rig["buffers"][0]["byteLength"] <= len(binary)
    assert all("uri" not in item for item in rig["buffers"])
    bone_map = json.loads((ASSETS / "bone-map.json").read_text(encoding="utf-8"))
    assert bone_map["schema"] == "lf.bone-map.v1" and bone_map["source"] == "smplx"
    assert set(bone_map["bones"].values()) == {node["name"] for node in rig["nodes"][:-1]}


def test_canonical_specimen_is_idempotent_disabled_inventory_and_preserves_existing_graph():
    workflow = json.loads((ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
    assert generator().add_specimen(copy.deepcopy(workflow)) == workflow
    node = next(node for node in workflow["nodes"] if node["id"] == 677)
    assert node["type"] == "LF_RetargetMotion" and node["mode"] == 2
    assert [(item["name"], item["type"]) for item in node["outputs"]] == [("glb_file", "STRING"), ("report", "JSON")]
    manifest = json.loads((ROOT / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
    policy = next(item for item in manifest["disabledNodes"] if item["id"] == 677)
    assert policy["type"] == node["type"]
    assert "licensed SMPL-X" in policy["reason"] and "inventory only" in policy["reason"]
    assert hashlib.sha256((ROOT / "scripts/quality/fixtures/E2E.json").read_bytes()).hexdigest() == manifest["workflow"]["expectedSha256"]
    assert len(workflow["nodes"]) == manifest["workflow"]["expectedNodeCount"]
