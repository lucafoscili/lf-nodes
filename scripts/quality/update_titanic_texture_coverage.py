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
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import titanic_append as titanic  # noqa: E402

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
    specimen = titanic.Specimen("Texture", START_NODE, START_LINK, 415)
    node = specimen.node

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
        specimen.connect(workflow, source, output, target, name)
    return specimen.append(workflow, {"id": GROUP_ID, "title": "Texture tools on the stock example · CPU coverage",
        "bounding": [x0 - 50, y0 - 200, 2450, 2150], "color": "#3f789e", "flags": {}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    workflow = add_specimen(titanic.read_workflow())
    workflow_bytes = titanic.canonical_bytes(workflow)
    manifest = titanic.MANIFEST_PATH.read_text(encoding="utf-8")
    manifest = titanic.upsert_cases(titanic.set_counts(manifest, workflow, workflow_bytes), [CASE])
    titanic.check_or_write({titanic.WORKFLOW_PATH: workflow_bytes, titanic.MANIFEST_PATH: manifest.encode()},
                           options.check, "Texture")
    print(f"Texture fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links")


if __name__ == "__main__":
    main()
