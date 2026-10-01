#!/usr/bin/env python3
"""Append the six-node CPU specimen; regenerate only its synthetic assets.

Run from any directory: python -I scripts/quality/update_titanic_cpu_coverage.py
Use --check to inspect reproducibility without writing. The maintainer's user
workflow is never read or written. Existing canonical nodes/links keep their IDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "scripts/quality"
ASSETS = QUALITY / "fixtures/titanic-cpu"
START_NODE = 612
START_LINK = 1230


def encode_png(width, height, pixel):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    scanlines = b"".join(b"\0" + bytes(v for x in range(width) for v in pixel(x, y))
                         for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">2I5B", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(scanlines, 9)) + chunk(b"IEND", b""))


def synthetic_assets():
    lower = encode_png(16, 8, lambda x, y: (240, 140 + x * 4, 30, 0 if x < 2 or y < 1 else 160))
    upper = encode_png(8, 8, lambda x, y: (40, 180, 240, 220 if abs(x - y) <= 2 else 0))
    binary = bytearray()
    views = []
    accessors = []

    def append(data, target=None):
        binary.extend(b"\0" * (-len(binary) % 4))
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        binary.extend(data)
        return len(views) - 1

    def accessor(values, kind, component=5126, target=None, **bounds):
        count = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[kind]
        data = struct.pack("<" + ("f" if component == 5126 else "H") * len(values), *values)
        accessors.append({"bufferView": append(data, target), "componentType": component,
                          "count": len(values) // count, "type": kind, **bounds})
        return len(accessors) - 1

    positions = accessor([-.5, 0, 0, .5, 0, 0, .5, 1, 0, -.5, 1, 0], "VEC3", target=34962,
                         min=[-.5, 0, 0], max=[.5, 1, 0])
    uv = accessor([0, 1, 1, 1, 1, 0, 0, 0], "VEC2", target=34962)
    joints = accessor([0, 0, 0, 0] * 4, "VEC4", 5123, 34962)
    weights = accessor([1, 0, 0, 0] * 4, "VEC4", target=34962)
    indices = accessor([0, 1, 2, 0, 2, 3], "SCALAR", 5123, 34963)
    identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    tip_inverse = identity.copy()
    tip_inverse[13] = -1
    inverse_bind = accessor(identity + tip_inverse, "MAT4")
    times = accessor([0, 1], "SCALAR", min=[0], max=[1])
    translations = accessor([0, 0, 0, .25, 0, 0], "VEC3")
    image_view = append(lower)
    document = {
        "asset": {"version": "2.0", "generator": "LF synthetic CPU fixture"},
        "buffers": [{"byteLength": len(binary)}], "bufferViews": views, "accessors": accessors,
        "images": [{"bufferView": image_view, "mimeType": "image/png"}],
        "textures": [{"source": 0}],
        "materials": [{"doubleSided": True, "alphaMode": "BLEND", "pbrMetallicRoughness": {
            "baseColorTexture": {"index": 0}, "metallicFactor": 0, "roughnessFactor": 1}}],
        "meshes": [{"primitives": [{"attributes": {
            "POSITION": positions, "TEXCOORD_0": uv, "JOINTS_0": joints, "WEIGHTS_0": weights},
            "indices": indices, "material": 0}]}],
        "nodes": [{"name": "Scene", "children": [1, 3]},
                  {"name": "Root joint", "children": [2]},
                  {"name": "Tip joint", "translation": [0, 1, 0]},
                  {"name": "Textured quad", "mesh": 0, "skin": 0}],
        "skins": [{"joints": [1, 2], "skeleton": 1, "inverseBindMatrices": inverse_bind}],
        "animations": [{"name": "Sideways", "samplers": [{"input": times, "output": translations,
            "interpolation": "LINEAR"}], "channels": [{"sampler": 0,
            "target": {"node": 1, "path": "translation"}}]}],
        "scene": 0, "scenes": [{"nodes": [0]}],
    }
    encoded = json.dumps(document, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    binary.extend(b"\0" * (-len(binary) % 4))
    glb = (struct.pack("<4sII", b"glTF", 2, 28 + len(encoded) + len(binary))
           + struct.pack("<II", len(encoded), 0x4E4F534A) + encoded
           + struct.pack("<II", len(binary), 0x004E4942) + binary)
    return {"lower.png": lower, "upper.png": upper, "synthetic.glb": glb}


def add_specimen(workflow, assets):
    nodes, links = [], []

    def node(identifier, kind, x, y, inputs=(), outputs=(), widgets=None, title=None):
        widgets = widgets or {}
        value = {"id": identifier, "type": kind, "pos": [x, y], "size": [340, 280],
                 "flags": {}, "order": 372 + identifier - START_NODE, "mode": 0,
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
        source = next(n for n in nodes if n["id"] == origin)
        destination = next(n for n in nodes if n["id"] == target)
        slot = next(i for i, item in enumerate(destination["inputs"]) if item["name"] == input_name)
        identifier = START_LINK + len(links)
        typ = source["outputs"][output]["type"]
        links.append([identifier, origin, output, target, slot, typ])
        source["outputs"][output]["links"] = (source["outputs"][output]["links"] or []) + [identifier]
        destination["inputs"][slot]["link"] = identifier

    images = (("image", "IMAGE", False), ("image_list", "IMAGE", True))
    def write_json(identifier, x, y, value, title):
        node(identifier, "LF_WriteJSON", x, y, [("ui_widget", "LF_TEXTAREA")],
             [("json", "JSON", False)], {"ui_widget": json.dumps(value, separators=(",", ":"))}, title)
    def view(identifier, x, y, title):
        node(identifier, "LF_ViewImages", x, y, [("image", "IMAGE"), ("ui_widget", "LF_MASONRY")],
             images, {"ui_widget": {}}, title)
    def brightness(identifier, x, y, strength, title):
        node(identifier, "LF_Brightness", x, y,
             [("image", "IMAGE"), ("brightness_strength", "FLOAT"), ("gamma", "FLOAT"),
              ("midpoint", "FLOAT"), ("localized_brightness", "BOOLEAN"), ("ui_widget", "LF_COMPARE")],
             images, {"brightness_strength": strength, "gamma": 1, "midpoint": .5,
                      "localized_brightness": False, "ui_widget": {}}, title)

    node(612, "LF_ApplyTextureToGLB", 9700, -4700,
         [("source_glb", "STRING"), ("texture", "IMAGE"), ("material_index", "INT")],
         [("glb", "FILE_3D_GLB", False)], {"source_glb": "titanic-cpu/synthetic.glb", "material_index": 0})
    write_json(613, 9700, -4350, {"nodes": [{"nodeIndex": 1, "nodeName": "Root joint",
        "anchorLocal": [0, 0, 0]}], "minPercent": 65, "maxPercent": 115}, "Synthetic joint selection")
    node(614, "LF_ScaleGLBNodes", 10100, -4700,
         [("glb", "FILE_3D_GLB"), ("targets", "JSON"), ("percent", "FLOAT")],
         [("glb", "FILE_3D_GLB", False)], {"percent": 75})
    node(615, "Preview3DAdvanced", 10500, -4700,
         [("model_3d", "FILE_3D_GLB"), ("model_3d_info", "LOAD_3D_MODEL_INFO"),
          ("viewport_state", "LOAD_3D"), ("camera_info", "LOAD_3D_CAMERA"),
          ("width", "INT"), ("height", "INT")],
         [("model_3d", "FILE_3D", False), ("model_3d_info", "LOAD_3D_MODEL_INFO", False),
          ("camera_info", "LOAD_3D_CAMERA", False), ("width", "INT", False), ("height", "INT", False)],
         {"viewport_state": {}, "width": 256, "height": 256}, "Textured animated quad at 75% · temp preview")
    regions = {"regions": [{"id": "left", "label": "Left panel", "rect": [0, 0, 32, 24]},
                           {"id": "right", "label": "Right panel", "rect": [32, 24, 32, 24]}]}
    write_json(616, 9700, -3700, regions, "Two non-overlapping base regions")
    node(617, "LF_EmptyImage", 9300, -3700,
         [("width", "INT"), ("height", "INT"), ("color", "STRING"), ("ui_widget", "LF_MASONRY")],
         images, {"width": 64, "height": 48, "color": "243447", "ui_widget": {}}, "Shared 64 × 48 base")
    node(618, "LF_ExtractImageRegions", 10100, -3700,
         [("image", "IMAGE"), ("regions", "JSON"), ("canvas_size", "INT")],
         [("images", "IMAGE", False), ("image_list", "IMAGE", True),
          ("layout", "JSON", False), ("editor_config", "JSON", False)], {"canvas_size": 32})
    brightness(619, 10500, -3700, .2, "Brighten both region canvases")
    node(620, "LF_ComposeImageRegions", 10900, -3700,
         [("original", "IMAGE"), ("edited", "IMAGE"), ("original_regions", "IMAGE"), ("layout", "JSON")], images)
    view(621, 11300, -3700, "Two edited regions; untouched pixels preserved")
    layer_manifest = {"root": "scripts/quality/fixtures/titanic-cpu", "layers": [
        {"id": "lower", "label": "Orange strip", "file": "lower.png",
         "sha256": hashlib.sha256(assets["lower.png"]).hexdigest(), "rect": [8, 8, 32, 16]},
        {"id": "upper", "label": "Blue diagonal", "file": "upper.png",
         "sha256": hashlib.sha256(assets["upper.png"]).hexdigest(), "rect": [24, 8, 16, 16]}]}
    write_json(622, 9700, -2900, layer_manifest, "Pinned native RGBA layers · prompt binds root")
    node(623, "LF_LoadImageLayers", 10100, -2900,
         [("manifest", "JSON"), ("canvas_size", "INT"), ("include_masks", "BOOLEAN"),
          ("base", "IMAGE"), ("base_regions", "JSON")],
         [("images", "IMAGE", False), ("image_list", "IMAGE", True), ("layout", "JSON", False),
          ("editor_config", "JSON", False), ("source_layers", "IMAGE", True)],
         {"canvas_size": 32, "include_masks": True}, "Two base crops + two layers + two cut masks")
    brightness(624, 10500, -2900, -.25, "Darken RGB; gray cut masks reduce coverage")
    node(625, "LF_ComposeImageLayers", 10900, -2900,
         [("base", "IMAGE"), ("edited", "IMAGE"), ("original_layers", "IMAGE"),
          ("source_layers", "IMAGE"), ("layout", "JSON"), ("base_mask", "MASK")],
         [("atlas", "IMAGE", False), ("atlas_list", "IMAGE", True), ("layer_images", "IMAGE", True)])
    view(626, 11300, -2900, "Combined base, RGB layer, and cut-mask edits")
    view(627, 11300, -2450, "Native 16 × 8 and 8 × 8 RGBA layers · ordered list")
    view(628, 10500, -2450, "Six ordered baseline canvases; labels in editor_config")
    node(629, "SolidMask", 10900, -2450,
         [("value", "FLOAT"), ("width", "INT"), ("height", "INT")], [("MASK", "MASK", False)],
         {"value": 1, "width": 64, "height": 48}, "Allow base edits within named regions")
    for source, output, target, name in (
        (617, 0, 612, "texture"), (612, 0, 614, "glb"), (613, 0, 614, "targets"), (614, 0, 615, "model_3d"),
        (617, 0, 618, "image"), (616, 0, 618, "regions"), (618, 0, 619, "image"),
        (617, 0, 620, "original"), (619, 1, 620, "edited"), (618, 1, 620, "original_regions"),
        (618, 2, 620, "layout"), (620, 1, 621, "image"), (622, 0, 623, "manifest"),
        (617, 0, 623, "base"), (616, 0, 623, "base_regions"), (623, 0, 624, "image"),
        (617, 0, 625, "base"), (624, 1, 625, "edited"), (623, 1, 625, "original_layers"),
        (623, 4, 625, "source_layers"), (623, 2, 625, "layout"), (629, 0, 625, "base_mask"),
        (625, 1, 626, "image"), (625, 2, 627, "image"), (623, 1, 628, "image"),
    ):
        connect(source, output, target, name)
    existing = {n["id"]: n for n in workflow["nodes"]}
    if any(n["id"] in existing for n in nodes):
        if any(existing.get(n["id"]) != n for n in nodes):
            raise ValueError("CPU specimen nodes drifted; review the canonical graph before updating.")
        if any(link not in workflow["links"] for link in links):
            raise ValueError("CPU specimen links drifted.")
        return workflow
    if workflow["last_node_id"] != 611 or workflow["last_link_id"] != 1229:
        raise ValueError("Unexpected Titanic append boundary; preserve and review existing IDs.")
    workflow["nodes"].extend(nodes)
    workflow["links"].extend(links)
    workflow["last_node_id"] = 629
    workflow["last_link_id"] = links[-1][0]
    workflow["groups"].append({"id": 17, "title": "Synthetic GLB, regions and RGBA layers · CPU coverage",
        "bounding": [9250, -4900, 2550, 2900], "color": "#3f789e", "flags": {}})
    return workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    assets = synthetic_assets()
    workflow_path = QUALITY / "fixtures/E2E.json"
    workflow = add_specimen(json.loads(workflow_path.read_text(encoding="utf-8")), assets)
    # Match the sanitizer's JSON.stringify byte format, including float spelling.
    workflow_bytes = subprocess.run(
        ["node", "-e", 'process.stdout.write(JSON.stringify(JSON.parse(require("fs").readFileSync(0,"utf8")))+"\\n")'],
        input=json.dumps(workflow, ensure_ascii=False).encode(), capture_output=True, check=True,
    ).stdout
    manifest_path = QUALITY / "titanic_cases.json"
    manifest_source = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_source)
    manifest["workflow"].update(expectedSha256=hashlib.sha256(workflow_bytes).hexdigest(),
        expectedNodeCount=len(workflow["nodes"]), expectedLinkCount=len(workflow["links"]))
    manifest["fixtures"] = [{"path": f"scripts/quality/fixtures/titanic-cpu/{name}",
        "expectedSha256": hashlib.sha256(data).hexdigest()} for name, data in assets.items()]
    cases = [
        {"id": "cpu.glb-texture-scale", "title": "Pinned animated GLB texture replacement and joint scale",
         "resourceClass": "cpu", "targets": [613, 615], "timeoutSeconds": 120,
         "bindings": {"fixtureGlbSourceNodeIds": [612]},
         "execution": {"requiredNodeIds": [612, 614, 615], "forbiddenCachedNodeIds": [612, 614, 615]},
         "expect": {"615": {"minimumPreviewCount": 1, "previewStorageType": "temp", "previewKind": "model-3d"}}},
        {"id": "cpu.image-regions-layers", "title": "Named region edits and combined RGBA layers with cut masks",
         "resourceClass": "cpu", "targets": [616, 621, 622, 626, 627, 628], "timeoutSeconds": 120,
         "bindings": {"fixtureLayerManifestNodeIds": [622]},
         "execution": {"requiredNodeIds": [618, 620, 623, 625],
                       "forbiddenCachedNodeIds": [618, 620, 623, 625]},
         "expect": {str(identifier): {"minimumPreviewCount": count, "previewStorageType": "input"}
                    for identifier, count in ((621, 1), (626, 1), (627, 2), (628, 6))}},
    ]
    for case in cases:
        existing = next((c for c in manifest["coverageCases"] if c["id"] == case["id"]), None)
        if existing is None:
            manifest["coverageCases"].insert(0, case)
        elif existing != case:
            raise ValueError(f"Reviewed manifest case drifted: {case['id']}")
    outputs = {ASSETS / name: data for name, data in assets.items()}
    outputs[workflow_path] = workflow_bytes
    # Preserve the established compact case/ID arrays and every unrelated line.
    for key in ("expectedSha256", "expectedNodeCount", "expectedLinkCount"):
        manifest_source = re.sub(r'("' + key + r'": )("[^"]*"|[0-9]+)',
            lambda match: match[1] + json.dumps(manifest["workflow"][key]), manifest_source, count=1)
    fixture_block = "  \"fixtures\": " + json.dumps(manifest["fixtures"], indent=2).replace("\n", "\n  ") + ",\n"
    if '"fixtures":' in manifest_source:
        manifest_source = re.sub(r'  "fixtures": \[[\s\S]*?\n  \],\n',
            lambda _: fixture_block, manifest_source, count=1)
    else:
        manifest_source = manifest_source.replace('  "smokeCases": [', fixture_block + '  "smokeCases": [', 1)
    for case in cases:
        if f'"id": "{case["id"]}"' not in manifest_source:
            case_block = "    " + json.dumps(case, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ",\n"
            manifest_source = manifest_source.replace('  "coverageCases": [\n',
                '  "coverageCases": [\n' + case_block, 1)
    outputs[manifest_path] = manifest_source.encode()
    if options.check:
        drift = [str(p.relative_to(ROOT)) for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
        if drift:
            raise SystemExit("CPU fixture drift: " + ", ".join(drift))
    else:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"CPU fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links, {len(assets)} pinned synthetic assets")


if __name__ == "__main__":
    main()
