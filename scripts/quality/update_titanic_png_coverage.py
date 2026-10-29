#!/usr/bin/env python3
"""Append the stored-value PNG nodes' CPU specimen to the canonical Titanic workflow.

Run from any directory: python -I scripts/quality/update_titanic_png_coverage.py
Use --check to inspect reproducibility without writing. The maintainer's user
workflow is never read or written. Existing canonical nodes/links keep their IDs.

The specimen loads Core's stock example image (the pinned
``titanic-sam3/comfy-example.png``, bound by absolute path at run time) with
Load PNG and writes it back at 16 bits with Save PNG. No model is loaded.
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
START_NODE = 667
START_LINK = 1307
GROUP_ID = 22
ORDER = 427
SOURCE = "scripts/quality/fixtures/titanic-sam3/comfy-example.png"
SIZE = 768

CASE = {
    "id": "cpu.png-stored-values",
    "title": "Load PNG and Save PNG keep the stock example's stored values, written back at 16 bits",
    "resourceClass": "cpu",
    "targets": [668],
    "timeoutSeconds": 120,
    "bindings": {"fixturePngSourceNodeIds": [667]},
    "execution": {"requiredNodeIds": [667, 668], "forbiddenCachedNodeIds": [667, 668]},
    "expect": {
        "667": {"minimumPreviewCount": 1, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.load-png.v1", "color_type": "rgb", "bit_depth": 8,
                                        "width": SIZE, "height": SIZE, "alpha": False}},
        "668": {"minimumPreviewCount": 1, "minimumLivePreviewCount": 1, "previewStorageType": "input",
                "requiredNamedValues": {"schema": "lf.save-png.v1", "rounding": "nearest", "metadata": "none",
                                        "channels": "rgb", "bit_depth": 16}},
    },
}


def add_specimen(workflow):
    nodes, links = [], []

    def node(identifier, kind, x, y, inputs=(), outputs=(), widgets=None, title=None):
        widgets = widgets or {}
        value = {"id": identifier, "type": kind, "pos": [x, y], "size": [360, 320],
                 "flags": {}, "order": ORDER + identifier - START_NODE, "mode": 0,
                 "inputs": [{"name": name, "type": typ, "link": None,
                     **({"widget": {"name": name}} if name in widgets else {})}
                     for name, typ in inputs],
                 "outputs": [{"name": name, "type": typ, "links": None, "slot_index": i,
                     **({"shape": 6} if is_list else {})}
                     for i, (name, typ, is_list) in enumerate(outputs)],
                 "properties": {"cnr_id": "lf-nodes", "Node name for S&R": kind},
                 "widgets_values": list(widgets.values()), "widgets_values_named": widgets}
        if title:
            value["title"] = title
        nodes.append(value)

    x0, y0 = 15400, -2600
    node(667, "LF_LoadPNG", x0, y0, [("image", "COMBO"), ("ui_widget", "LF_MASONRY")],
         (("image", "IMAGE", False), ("alpha", "MASK", False), ("bit_depth", "INT", False),
          ("receipt", "JSON", False), ("image_list", "IMAGE", True)),
         {"image": SOURCE, "upload": "image", "ui_widget": {}}, "Stock example, stored values")
    node(668, "LF_SavePNG", x0 + 400, y0,
         [("image", "IMAGE"), ("filename_prefix", "STRING"), ("bit_depth", "INT"), ("compress_level", "INT"),
          ("ui_widget", "LF_MASONRY")],
         (("file_names", "STRING", True), ("receipt", "JSON", False)),
         {"filename_prefix": "LF_Nodes/Titanic/stored_png", "bit_depth": 16, "compress_level": 4, "ui_widget": {}},
         "Written back at 16 bits, rounded, no metadata")
    identifier = START_LINK
    links.append([identifier, 667, 0, 668, 0, "IMAGE"])
    nodes[0]["outputs"][0]["links"] = [identifier]
    nodes[1]["inputs"][0]["link"] = identifier

    by_id = {n["id"]: n for n in workflow["nodes"]}
    if any(n["id"] in by_id for n in nodes):
        if any(by_id.get(n["id"]) != n for n in nodes):
            raise ValueError("PNG specimen nodes drifted; review the canonical graph before updating.")
        if any(link not in workflow["links"] for link in links):
            raise ValueError("PNG specimen links drifted.")
        return workflow
    if workflow["last_node_id"] != START_NODE - 1 or workflow["last_link_id"] != START_LINK - 1:
        raise ValueError("Unexpected Titanic append boundary; preserve and review existing IDs.")
    workflow["nodes"].extend(nodes)
    workflow["links"].extend(links)
    workflow["last_node_id"] = max(n["id"] for n in nodes)
    workflow["last_link_id"] = links[-1][0]
    workflow["groups"].append({"id": GROUP_ID, "title": "Stored-value PNG load and save · CPU coverage",
        "bounding": [x0 - 50, y0 - 200, 850, 600], "color": "#3f789e", "flags": {}})
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
            raise SystemExit("PNG fixture drift: " + ", ".join(drift))
    else:
        for path, data in outputs.items():
            path.write_bytes(data)
    print(f"PNG fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links")


if __name__ == "__main__":
    main()
