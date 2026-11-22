"""Shared steps of the scripts that append a specimen to the canonical Titanic workflow.

Each ``update_titanic_*_coverage.py`` script describes its nodes, links, group and manifest cases; this module
builds them after the canonical graph's last IDs, checks an appended specimen for drift, writes the workflow in the
sanitizer's byte format and updates ``titanic_cases.json`` line by line, so unrelated lines keep their layout.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "scripts/quality"
WORKFLOW_PATH = QUALITY / "fixtures/E2E.json"
MANIFEST_PATH = QUALITY / "titanic_cases.json"


def read_workflow() -> dict:
    return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))


# The frontend draws a node's title above its position, and a group's header inside its bounding.
NODE_TITLE_HEIGHT = 30
GROUP_HEADER_HEIGHT = 50


class Specimen:
    """New nodes and links numbered from ``start_node`` and ``start_link``, appended once and checked after."""

    def __init__(self, label: str, start_node: int, start_link: int, order: int, size=(360, 320)):
        self.label, self.start_node, self.start_link, self.order = label, start_node, start_link, order
        self.size = list(size)
        self.nodes: list[dict] = []
        self.links: list[list] = []

    def node(self, identifier, kind, x, y, inputs=(), outputs=(), widgets=None, title=None, mode=0) -> dict:
        """A node as the frontend serializes it: ``inputs`` (name, type), ``outputs`` (name, type, is_list)."""
        widgets = widgets or {}
        value = {"id": identifier, "type": kind, "pos": [x, y], "size": list(self.size),
                 "flags": {}, "order": self.order + identifier - self.start_node, "mode": mode,
                 "inputs": [{"name": name, "type": typ, "link": None,
                             **({"widget": {"name": name}} if name in widgets else {})}
                            for name, typ in inputs],
                 "outputs": [{"name": name, "type": typ, "links": None, "slot_index": index,
                              **({"shape": 6} if is_list else {})}
                             for index, (name, typ, is_list) in enumerate(outputs)],
                 "properties": {"cnr_id": "lf-nodes" if kind.startswith("LF_") else "comfy-core",
                                "Node name for S&R": kind},
                 "widgets_values": list(widgets.values()), "widgets_values_named": widgets}
        if title:
            value["title"] = title
        self.nodes.append(value)
        return value

    def connect(self, workflow, origin, output, target, input_name) -> int:
        """Link ``origin``'s output slot to the new node ``target``'s named input; ``origin`` may be canonical."""
        everything = {n["id"]: n for n in workflow["nodes"] + self.nodes}
        source, destination = everything[origin], everything[target]
        slot = next(i for i, item in enumerate(destination["inputs"]) if item["name"] == input_name)
        identifier = self.start_link + len(self.links)
        self.links.append([identifier, origin, output, target, slot, source["outputs"][output]["type"]])
        destination["inputs"][slot]["link"] = identifier
        return identifier

    def arrange(self, x0, top, rows, sizes=None, gap=60) -> int:
        """Size the named nodes (``sizes`` by ID) and lay them out row by row from ``(x0, top)``, each row below the
        tallest node of the one before; return the bottom of the last row."""
        by_id = {n["id"]: n for n in self.nodes}
        y = top
        for row in rows:
            x, tallest = x0, 0
            for identifier in row:
                node = by_id[identifier]
                node["size"] = list((sizes or {}).get(identifier, node["size"]))
                node["pos"] = [x, y]
                x += node["size"][0] + gap
                tallest = max(tallest, node["size"][1])
            y += tallest + gap + NODE_TITLE_HEIGHT
        return y - gap - NODE_TITLE_HEIGHT

    def group(self, identifier, title, ids, color, margin=30) -> dict:
        """A group around the named nodes, their titles and its own header included."""
        nodes = [n for n in self.nodes if n["id"] in set(ids)]
        left = min(n["pos"][0] for n in nodes) - margin
        top = min(n["pos"][1] for n in nodes) - NODE_TITLE_HEIGHT - GROUP_HEADER_HEIGHT - margin
        right = max(n["pos"][0] + n["size"][0] for n in nodes) + margin
        bottom = max(n["pos"][1] + n["size"][1] for n in nodes) + margin
        return {"id": identifier, "title": title, "bounding": [left, top, right - left, bottom - top], "color": color,
                "flags": {}}

    def append(self, workflow, *groups: dict) -> dict:
        """Append the specimen and its groups at the graph's end, or check the appended one has not drifted."""
        self.nodes.sort(key=lambda item: item["id"])
        mine = {n["id"]: n for n in self.nodes}
        for identifier, origin, output, *_ in self.links:
            if origin in mine:
                socket = mine[origin]["outputs"][output]
                socket["links"] = (socket["links"] or []) + [identifier]
        by_id = {n["id"]: n for n in workflow["nodes"]}
        if any(identifier in by_id for identifier in mine):
            own = {link[0] for link in self.links}
            if any(_own_links_only(by_id.get(identifier), own) != node for identifier, node in mine.items()):
                raise ValueError(f"{self.label} specimen nodes drifted; review the canonical graph before updating.")
            if any(link not in workflow["links"] for link in self.links):
                raise ValueError(f"{self.label} specimen links drifted.")
            if any(group not in workflow["groups"] for group in groups):
                raise ValueError(f"{self.label} specimen groups drifted.")
            return workflow
        if workflow["last_node_id"] != self.start_node - 1 or (
                self.links and workflow["last_link_id"] != self.start_link - 1):
            raise ValueError("Unexpected Titanic append boundary; preserve and review existing IDs.")
        for identifier, origin, output, *_ in self.links:
            if origin not in mine:
                socket = by_id[origin]["outputs"][output]
                socket["links"] = (socket["links"] or []) + [identifier]
        workflow["nodes"].extend(self.nodes)
        workflow["links"].extend(self.links)
        workflow["last_node_id"] = max(mine)
        if self.links:
            workflow["last_link_id"] = self.links[-1][0]
        workflow["groups"].extend(groups)
        return workflow


def _own_links_only(node, own: set[int]):
    """``node`` with each output's links narrowed to the specimen's own: later specimens may consume its outputs."""
    if node is None:
        return None
    narrowed = copy.deepcopy(node)
    for socket in narrowed["outputs"]:
        if socket.get("links"):
            socket["links"] = [identifier for identifier in socket["links"] if identifier in own] or None
    return narrowed


def canonical_bytes(workflow) -> bytes:
    """The workflow in the sanitizer's ``JSON.stringify`` byte format, float spelling included."""
    return subprocess.run(
        ["node", "-e", 'process.stdout.write(JSON.stringify(JSON.parse(require("fs").readFileSync(0,"utf8")))+"\\n")'],
        input=json.dumps(workflow, ensure_ascii=False).encode("utf-8"), capture_output=True, check=True,
    ).stdout


def set_counts(source: str, workflow: dict, workflow_bytes: bytes) -> str:
    """The manifest's workflow hash and node and link counts, rewritten in place."""
    for key, value in {"expectedSha256": hashlib.sha256(workflow_bytes).hexdigest(),
                       "expectedNodeCount": len(workflow["nodes"]),
                       "expectedLinkCount": len(workflow["links"])}.items():
        source = re.sub(r'("' + key + r'": )("[^"]*"|[0-9]+)', lambda match: match[1] + json.dumps(value),
                        source, count=1)
    return source


def upsert_cases(source: str, cases: list[dict]) -> str:
    """Insert the missing coverage cases at the top, in order; a reviewed case that changed refuses."""
    manifest = json.loads(source)
    block = ""
    for case in cases:
        existing = next((item for item in manifest["coverageCases"] if item["id"] == case["id"]), None)
        if existing is None:
            block += "    " + json.dumps(case, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ",\n"
        elif existing != case:
            raise ValueError(f"Reviewed manifest case drifted: {case['id']}")
    return source.replace('  "coverageCases": [\n', '  "coverageCases": [\n' + block, 1)


def upsert_disabled(source: str, rows: list[dict]) -> str:
    """Insert the missing disabled-node policies at the top, one line each; a changed policy refuses."""
    manifest = json.loads(source)
    block = ""
    for row in rows:
        existing = next((item for item in manifest["disabledNodes"] if item["id"] == row["id"]), None)
        if existing is None:
            block += "    " + json.dumps(row, ensure_ascii=False) + ",\n"
        elif existing != row:
            raise ValueError(f"Disabled node policy drifted: {row['id']}")
    return source.replace('  "disabledNodes": [\n', '  "disabledNodes": [\n' + block, 1)


def replace_fixtures(source: str, fixtures: list[dict]) -> str:
    """The manifest's pinned fixture list, written whole (before ``smokeCases`` if it had none)."""
    block = '  "fixtures": ' + json.dumps(fixtures, indent=2).replace("\n", "\n  ") + ",\n"
    if '"fixtures":' in source:
        return re.sub(r'  "fixtures": \[[\s\S]*?\n  \],\n', lambda _: block, source, count=1)
    return source.replace('  "smokeCases": [', block + '  "smokeCases": [', 1)


def check_or_write(outputs: dict[Path, bytes], check: bool, label: str) -> None:
    """With ``check``, refuse when any output differs from its file; otherwise write them all."""
    if check:
        drift = [str(path.relative_to(ROOT)) for path, data in outputs.items()
                 if not path.is_file() or path.read_bytes() != data]
        if drift:
            raise SystemExit(f"{label} fixture drift: " + ", ".join(drift))
        return
    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
