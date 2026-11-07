#!/usr/bin/env python3
"""Generate a tiny motion/rig/map specimen and append its disabled Titanic node.

Run with --check to verify reproducibility. Execution still needs a registered,
licensed SMPL-X body model and these fixtures copied to the selected input paths.
Only repository-owned canonical files are read or written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "scripts/quality"
ASSETS = QUALITY / "fixtures/titanic-motion"
NODE_ID = 677
REASON = "generated motion, rig and map available; registered licensed SMPL-X model and local input paths required; inventory only"


def synthetic_assets():
    # Load the owning codecs without importing the optional Comfy node package.
    def helper(relative, name):
        spec = importlib.util.spec_from_file_location(name, ROOT / relative)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    codec = helper("modules/utils/glb_texture.py", "titanic_motion_glb_codec")
    motion_format = helper("modules/utils/helpers/motion/format.py", "titanic_motion_format")
    names = motion_format.JOINT_NAMES["root"] + motion_format.JOINT_NAMES["body"]
    parents = [-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19]
    positions = [(0, 1, 0), (.1, .95, 0), (-.1, .95, 0), (0, 1.15, 0),
                 (.1, .55, .03), (-.1, .55, .03), (0, 1.3, 0), (.1, .1, 0), (-.1, .1, 0),
                 (0, 1.45, 0), (.1, 0, .15), (-.1, 0, .15), (0, 1.6, 0),
                 (.1, 1.48, 0), (-.1, 1.48, 0), (0, 1.75, 0), (.3, 1.5, 0), (-.3, 1.5, 0),
                 (.55, 1.3, 0), (-.55, 1.3, 0), (.75, 1.15, 0), (-.75, 1.15, 0)]
    binary, views, accessors = bytearray(), [], []

    def accessor(values, kind, width, component=5126, **bounds):
        binary.extend(b"\0" * (-len(binary) % 4))
        data = struct.pack("<" + ("f" if component == 5126 else "H") * len(values), *values)
        views.append({"buffer": 0, "byteOffset": len(binary), "byteLength": len(data)})
        binary.extend(data)
        accessors.append({"bufferView": len(views) - 1, "componentType": component,
                          "count": len(values) // width, "type": kind, **bounds})
        return len(accessors) - 1

    vertices = accessor([-.2, .8, 0, .2, .8, 0, 0, 1.4, 0], "VEC3", 3,
                        min=[-.2, .8, 0], max=[.2, 1.4, 0])
    joints = accessor([0, 0, 0, 0] * 3, "VEC4", 4, 5123)
    weights = accessor([1, 0, 0, 0] * 3, "VEC4", 4)
    indices = accessor([0, 1, 2], "SCALAR", 1, 5123)
    matrices = []
    for x, y, z in positions:
        matrices.extend([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -x, -y, -z, 1])
    inverse_bind = accessor(matrices, "MAT4", 16)
    nodes = []
    for index, (name, parent) in enumerate(zip(names, parents)):
        origin = positions[parent] if parent >= 0 else (0, 0, 0)
        node = {"name": name, "translation": [round(a - b, 6) for a, b in zip(positions[index], origin)]}
        children = [i for i, p in enumerate(parents) if p == index]
        if children:
            node["children"] = children
        nodes.append(node)
    nodes.append({"name": "Synthetic skin", "mesh": 0, "skin": 0})
    document = {"asset": {"version": "2.0", "generator": "LF synthetic motion fixture"},
                "buffers": [{"byteLength": len(binary)}], "bufferViews": views, "accessors": accessors,
                "nodes": nodes, "scene": 0, "scenes": [{"nodes": [0, len(names)]}],
                "skins": [{"joints": list(range(len(names))), "skeleton": 0, "inverseBindMatrices": inverse_bind}],
                "meshes": [{"primitives": [{"attributes": {"POSITION": vertices, "JOINTS_0": joints,
                    "WEIGHTS_0": weights}, "indices": indices}]}]}
    glb = codec.pack_glb(document, binary)
    parameters = {key: [[0.0] * width for _ in range(3)] for key, width in motion_format.POSE_WIDTHS.items()}
    parameters["transl"] = [[0, 0, 0], [.05, 0, 0], [.1, 0, 0]]
    parameters["body_pose"][1][17 * 3 + 2] = .15
    parameters["body_pose"][2][17 * 3 + 2] = -.15
    motion = {"schema": motion_format.SCHEMA, "fps": 30, "joint_names": motion_format.JOINT_NAMES,
              "camera": parameters, "world": parameters}
    motion_format.validate_motion(motion)
    bone_map = {"schema": "lf.bone-map.v1", "source": "smplx", "unmapped": "rest",
                "bones": {name: name for name in names}}
    as_json = lambda value: (json.dumps(value, separators=(",", ":")) + "\n").encode("utf-8")
    return {"rig.glb": glb, "motion.json": as_json(motion), "bone-map.json": as_json(bone_map)}


def add_specimen(workflow):
    widgets = {"motion_file": "scripts/quality/fixtures/titanic-motion/motion.json", "body": "female",
               "betas": "0.5,-1.5", "glb_path": "scripts/quality/fixtures/titanic-motion/rig.glb",
               "bone_map_path": "scripts/quality/fixtures/titanic-motion/bone-map.json",
               "keep_rest_facing": "[]", "flatten_slope": "[]", "ui_widget": ""}
    node = {"id": NODE_ID, "type": "LF_RetargetMotion", "pos": [16400, -1200], "size": [420, 520],
            "flags": {}, "order": len(workflow["nodes"]), "mode": 2,
            "inputs": [{"name": name, "type": "LF_CODE" if name == "ui_widget" else "COMBO" if name == "body" else "STRING",
                        "link": None, "widget": {"name": name}} for name in widgets],
            "outputs": [{"name": name, "type": typ, "links": None, "slot_index": index}
                        for index, (name, typ) in enumerate((("glb_file", "STRING"), ("report", "JSON")))],
            "properties": {"cnr_id": "lf-nodes", "Node name for S&R": "LF_RetargetMotion"},
            "widgets_values": list(widgets.values()), "widgets_values_named": widgets,
            "title": "Synthetic retarget motion - licensed body model required"}
    existing = next((item for item in workflow["nodes"] if item["id"] == NODE_ID), None)
    if existing:
        # The ordinal is historical once later specimens have been appended.
        node["order"] = existing["order"]
        if existing != node:
            raise ValueError("Motion specimen drifted; review the canonical graph.")
        return workflow
    if workflow["last_node_id"] != NODE_ID - 1:
        raise ValueError("Unexpected Titanic append boundary; preserve existing IDs.")
    workflow["nodes"].append(node)
    workflow["last_node_id"] = NODE_ID
    workflow["groups"].append({"id": 26, "title": "Synthetic retarget motion - prerequisites pending",
        "bounding": [16350, -1400, 550, 800], "color": "#3f789e", "flags": {}})
    return workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    workflow_path, manifest_path = QUALITY / "fixtures/E2E.json", QUALITY / "titanic_cases.json"
    workflow = add_specimen(json.loads(workflow_path.read_text(encoding="utf-8")))
    workflow_bytes = subprocess.run(
        ["node", "-e", 'process.stdout.write(JSON.stringify(JSON.parse(require("fs").readFileSync(0,"utf8")))+"\\n")'],
        input=json.dumps(workflow, ensure_ascii=False).encode("utf-8"), capture_output=True, check=True,
    ).stdout
    assets = synthetic_assets()
    source = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(source)
    for key, value in {"expectedSha256": hashlib.sha256(workflow_bytes).hexdigest(),
                       "expectedNodeCount": len(workflow["nodes"]), "expectedLinkCount": len(workflow["links"])}.items():
        source = re.sub(r'("' + key + r'": )("[^"]*"|[0-9]+)',
                        lambda match: match[1] + json.dumps(value), source, count=1)
    fixtures = [row for row in manifest["fixtures"] if not row["path"].startswith("scripts/quality/fixtures/titanic-motion/")]
    fixtures.extend({"path": f"scripts/quality/fixtures/titanic-motion/{name}",
                     "expectedSha256": hashlib.sha256(data).hexdigest()} for name, data in assets.items())
    source = re.sub(r'  "fixtures": \[[\s\S]*?\n  \],\n',
                    lambda _: '  "fixtures": ' + json.dumps(fixtures, indent=2).replace("\n", "\n  ") + ",\n",
                    source, count=1)
    disabled = {"id": NODE_ID, "type": "LF_RetargetMotion", "reason": REASON}
    existing = next((row for row in manifest["disabledNodes"] if row["id"] == NODE_ID), None)
    if existing and existing != disabled:
        raise ValueError("Motion specimen disabled policy drifted.")
    if not existing:
        source = source.replace('  "disabledNodes": [\n', '  "disabledNodes": [\n    ' + json.dumps(disabled) + ",\n", 1)
    outputs = {ASSETS / name: data for name, data in assets.items()}
    outputs.update({workflow_path: workflow_bytes, manifest_path: source.encode("utf-8")})
    if options.check:
        drift = [str(path.relative_to(ROOT)) for path, data in outputs.items()
                 if not path.is_file() or path.read_bytes() != data]
        if drift:
            raise SystemExit("Motion fixture drift: " + ", ".join(drift))
    else:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"Motion fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes; inventory only")


if __name__ == "__main__":
    main()
