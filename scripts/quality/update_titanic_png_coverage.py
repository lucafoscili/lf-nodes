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
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import titanic_append as titanic  # noqa: E402

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
    specimen = titanic.Specimen("PNG", START_NODE, START_LINK, ORDER)
    node = specimen.node

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
    specimen.connect(workflow, 667, 0, 668, "image")
    return specimen.append(workflow, {"id": GROUP_ID, "title": "Stored-value PNG load and save · CPU coverage",
        "bounding": [x0 - 50, y0 - 200, 850, 600], "color": "#3f789e", "flags": {}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    workflow = add_specimen(titanic.read_workflow())
    workflow_bytes = titanic.canonical_bytes(workflow)
    manifest = titanic.MANIFEST_PATH.read_text(encoding="utf-8")
    manifest = titanic.upsert_cases(titanic.set_counts(manifest, workflow, workflow_bytes), [CASE])
    titanic.check_or_write({titanic.WORKFLOW_PATH: workflow_bytes, titanic.MANIFEST_PATH: manifest.encode()},
                           options.check, "PNG")
    print(f"PNG fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links")


if __name__ == "__main__":
    main()
