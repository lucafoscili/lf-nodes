#!/usr/bin/env python3
"""Append the Texture nodes' CPU specimen to the canonical Titanic workflow.

Run from any directory: python -I scripts/quality/update_titanic_texture_coverage.py
Use --check to inspect reproducibility without writing. The maintainer's user
workflow is never read or written. Existing canonical nodes/links keep their IDs.

The specimen grades a central square of Core's stock example image (the
pinned ``titanic-sam3/comfy-example.png`` loaded by node 654) to the colour of
its top band, restores the detail the grade narrowed, pads the rest of the
image from the square, and repacks a flat, unnormalised normal map from
OpenGL to DirectX green. Stock mask nodes make the masks; no model is loaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "scripts/quality"
START_NODE = 655
START_LINK = 1289
GROUP_ID = 21
SOURCE_NODE = 654
SIZE = 768
SQUARE = 384
BAND = 192
NORMAL_SIZE = 64

CASE = {
    "id": "cpu.texture-tools",
    "title": "Masked Lab grade, detail transfer, edge padding and normal repack on the stock example",
    "resourceClass": "cpu",
    "targets": [663, 666],
    "timeoutSeconds": 120,
    "bindings": {"fixtureImageSourceNodeIds": [SOURCE_NODE]},
    "execution": {"requiredNodeIds": [660, 661, 662, 665], "forbiddenCachedNodeIds": [660, 661, 662, 665]},
    "expect": {
        "660": {"minimumPreviewCount": 3, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.masked-lab-grade.v1", "apply_to": "mask",
                                        "changed_pixels": SQUARE * SQUARE}},
        "661": {"minimumPreviewCount": 3, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.detail-transfer.v1", "mode": "match_reference",
                                        "radius": 4, "changed_pixels": SQUARE * SQUARE}},
        "662": {"minimumPreviewCount": 3, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.edge-padding.v1", "covered_pixels": SQUARE * SQUARE,
                                        "padded_pixels": SIZE * SIZE - SQUARE * SQUARE}},
        "665": {"minimumPreviewCount": 2, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.normal-map-repack.v1", "green_flipped": True,
                                        "checked_pixels": NORMAL_SIZE * NORMAL_SIZE, "invalid_share": 0,
                                        "renormalized_share": 1}},
    },
}


def add_specimen(workflow):
    nodes, links = [], []

    def node(identifier, kind, x, y, inputs=(), outputs=(), widgets=None, title=None):
        widgets = widgets or {}
        value = {"id": identifier, "type": kind, "pos": [x, y], "size": [360, 320],
                 "flags": {}, "order": 415 + identifier - START_NODE, "mode": 0,
                 "inputs": [{"name": name, "type": typ, "link": None,
                     **({"widget": {"name": name}} if name in widgets else {})}
                     for name, typ in inputs],
                 "outputs": [{"name": name, "type": typ, "links": None, "slot_index": i,
                     **({"shape": 6} if is_list else {})}
                     for i, (name, typ, is_list) in enumerate(outputs)],
                 "properties": {"cnr_id": "lf-nodes" if kind.startswith("LF_") else "comfy-core",
                                "Node name for S&R": kind},
                 "widgets_values": list(widgets.values()), "widgets_values_named": widgets}
        if title:
            value["title"] = title
        nodes.append(value)

    def connect(origin, output, target, input_name):
        everything = {n["id"]: n for n in workflow["nodes"] + nodes}
        source, destination = everything[origin], everything[target]
        slot = next(i for i, item in enumerate(destination["inputs"]) if item["name"] == input_name)
        identifier = START_LINK + len(links)
        typ = source["outputs"][output]["type"]
        links.append([identifier, origin, output, target, slot, typ])
        destination["inputs"][slot]["link"] = identifier
        return identifier

    images = (("image", "IMAGE", False), ("image_list", "IMAGE", True))
    texture_outputs = (("image", "IMAGE", False), ("report", "JSON", False), ("image_list", "IMAGE", True))
    mask_controls = [("value", "FLOAT"), ("width", "INT"), ("height", "INT")]
    composite_inputs = [("destination", "MASK"), ("source", "MASK"), ("x", "INT"), ("y", "INT"),
                        ("operation", "COMBO")]
    x0, y0 = 15400, -4700
    node(655, "SolidMask", x0, y0, mask_controls, [("MASK", "MASK", False)],
         {"value": 0, "width": SIZE, "height": SIZE}, "Empty 768 × 768 base")
    node(656, "SolidMask", x0, y0 + 360, mask_controls, [("MASK", "MASK", False)],
         {"value": 1, "width": SQUARE, "height": SQUARE})
    node(657, "MaskComposite", x0 + 400, y0 + 180, composite_inputs, [("MASK", "MASK", False)],
         {"x": (SIZE - SQUARE) // 2, "y": (SIZE - SQUARE) // 2, "operation": "add"},
         "Central square: graded, detailed, kept")
    node(658, "SolidMask", x0, y0 + 720, mask_controls, [("MASK", "MASK", False)],
         {"value": 1, "width": SIZE, "height": BAND})
    node(659, "MaskComposite", x0 + 400, y0 + 720, composite_inputs, [("MASK", "MASK", False)],
         {"x": 0, "y": 0, "operation": "add"}, "Top band: the colour reference")
    node(664, "LF_EmptyImage", x0, y0 + 1500,
         [("width", "INT"), ("height", "INT"), ("color", "STRING"), ("ui_widget", "LF_MASONRY")],
         images, {"width": NORMAL_SIZE, "height": NORMAL_SIZE, "color": "A0A0E0", "ui_widget": {}},
         "Flat normal, unnormalised (length 0.83)")
    node(660, "LF_MaskedLabGrade", x0 + 800, y0,
         [("image", "IMAGE"), ("mask", "MASK"), ("reference_image", "IMAGE"), ("reference_mask", "MASK"),
          ("min_stretch", "FLOAT"), ("max_stretch", "FLOAT"), ("amount", "FLOAT"), ("apply_to", "COMBO"),
          ("ui_widget", "LF_COMPARE")], texture_outputs,
         {"min_stretch": 0.25, "max_stretch": 1, "amount": 1, "apply_to": "mask", "ui_widget": {}},
         "Grade the square to the top band · CPU")
    node(661, "LF_DetailTransfer", x0 + 1200, y0,
         [("image", "IMAGE"), ("detail_source", "IMAGE"), ("radius", "INT"), ("mode", "COMBO"),
          ("strength", "FLOAT"), ("mask", "MASK"), ("reference_image", "IMAGE"), ("reference_mask", "MASK"),
          ("ui_widget", "LF_COMPARE")], texture_outputs,
         {"radius": 4, "mode": "match_reference", "strength": 1, "ui_widget": {}},
         "Restore the square's original fine detail · CPU")
    node(662, "LF_EdgePadding", x0 + 1600, y0,
         [("image", "IMAGE"), ("mask", "MASK"), ("ui_widget", "LF_COMPARE")], texture_outputs[:1] + (
             ("receipt", "JSON", False), ("image_list", "IMAGE", True)),
         {"ui_widget": {}}, "Pad everything outside the square · CPU")
    node(663, "LF_ViewImages", x0 + 2000, y0, [("image", "IMAGE"), ("ui_widget", "LF_MASONRY")], images,
         {"ui_widget": {}}, "Graded, detailed and padded texture")
    node(665, "LF_NormalMapRepack", x0 + 800, y0 + 1500,
         [("image", "IMAGE"), ("layout", "COMBO"), ("green_in", "COMBO"), ("green_out", "COMBO"),
          ("z_mode", "COMBO"), ("max_invalid_share", "FLOAT"), ("mask", "MASK"), ("ui_widget", "LF_COMPARE")],
         texture_outputs, {"layout": "xyz_rgb", "green_in": "opengl", "green_out": "directx",
                           "z_mode": "rebuild_z", "max_invalid_share": 0.01, "ui_widget": {}},
         "OpenGL to DirectX green, Z rebuilt · CPU")
    node(666, "LF_ViewImages", x0 + 1200, y0 + 1500, [("image", "IMAGE"), ("ui_widget", "LF_MASONRY")], images,
         {"ui_widget": {}}, "Unit-length DirectX normal")
    nodes.sort(key=lambda item: item["id"])
    for source, output, target, name in (
        (655, 0, 657, "destination"), (656, 0, 657, "source"), (655, 0, 659, "destination"),
        (658, 0, 659, "source"),
        (SOURCE_NODE, 0, 660, "image"), (657, 0, 660, "mask"), (SOURCE_NODE, 0, 660, "reference_image"),
        (659, 0, 660, "reference_mask"),
        (660, 0, 661, "image"), (SOURCE_NODE, 0, 661, "detail_source"), (657, 0, 661, "mask"),
        (SOURCE_NODE, 0, 661, "reference_image"), (657, 0, 661, "reference_mask"),
        (661, 0, 662, "image"), (657, 0, 662, "mask"), (662, 0, 663, "image"),
        (664, 0, 665, "image"), (665, 0, 666, "image"),
    ):
        connect(source, output, target, name)
    mine = {n["id"]: n for n in nodes}
    for identifier, origin, output, _target, _slot, _typ in links:
        if origin in mine:
            socket = mine[origin]["outputs"][output]
            socket["links"] = (socket["links"] or []) + [identifier]
    by_id = {n["id"]: n for n in workflow["nodes"]}
    if any(n["id"] in by_id for n in nodes):
        if any(by_id.get(n["id"]) != n for n in nodes):
            raise ValueError("Texture specimen nodes drifted; review the canonical graph before updating.")
        if any(link not in workflow["links"] for link in links):
            raise ValueError("Texture specimen links drifted.")
        return workflow
    if workflow["last_node_id"] != START_NODE - 1 or workflow["last_link_id"] != START_LINK - 1:
        raise ValueError("Unexpected Titanic append boundary; preserve and review existing IDs.")
    # The stock source's outgoing link list gains the specimen's links.
    for identifier, origin, output, _target, _slot, _typ in links:
        if origin not in mine:
            socket = by_id[origin]["outputs"][output]
            socket["links"] = (socket["links"] or []) + [identifier]
    workflow["nodes"].extend(nodes)
    workflow["links"].extend(links)
    workflow["last_node_id"] = max(n["id"] for n in nodes)
    workflow["last_link_id"] = links[-1][0]
    workflow["groups"].append({"id": GROUP_ID, "title": "Texture tools on the stock example · CPU coverage",
        "bounding": [x0 - 50, y0 - 200, 2450, 2150], "color": "#3f789e", "flags": {}})
    return workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    workflow_path = QUALITY / "fixtures/E2E.json"
    workflow = add_specimen(json.loads(workflow_path.read_text(encoding="utf-8")))
    # Match the sanitizer's JSON.stringify byte format, including float spelling.
    workflow_bytes = subprocess.run(
        ["node", "-e", 'process.stdout.write(JSON.stringify(JSON.parse(require("fs").readFileSync(0,"utf8")))+"\\n")'],
        input=json.dumps(workflow, ensure_ascii=False).encode(), capture_output=True, check=True,
    ).stdout
    manifest_path = QUALITY / "titanic_cases.json"
    manifest_source = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_source)
    counts = {"expectedSha256": hashlib.sha256(workflow_bytes).hexdigest(),
              "expectedNodeCount": len(workflow["nodes"]), "expectedLinkCount": len(workflow["links"])}
    existing = next((c for c in manifest["coverageCases"] if c["id"] == CASE["id"]), None)
    if existing is not None and existing != CASE:
        raise ValueError(f"Reviewed manifest case drifted: {CASE['id']}")
    for key, value in counts.items():
        manifest_source = re.sub(r'("' + key + r'": )("[^"]*"|[0-9]+)',
            lambda match: match[1] + json.dumps(value), manifest_source, count=1)
    if existing is None:
        case_block = "    " + json.dumps(CASE, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ",\n"
        manifest_source = manifest_source.replace('  "coverageCases": [\n', '  "coverageCases": [\n' + case_block, 1)
    outputs = {workflow_path: workflow_bytes, manifest_path: manifest_source.encode()}
    if options.check:
        drift = [str(p.relative_to(ROOT)) for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
        if drift:
            raise SystemExit("Texture fixture drift: " + ", ".join(drift))
    else:
        for path, data in outputs.items():
            path.write_bytes(data)
    print(f"Texture fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links")


if __name__ == "__main__":
    main()
