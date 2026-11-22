"""The Titanic append scripts reproduce the canonical workflow and manifest, each after the specimens appended later."""
import copy
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
QUALITY = ROOT / "scripts/quality"
SCRIPTS = sorted(QUALITY.glob("update_titanic_*_coverage.py"))


def _helper():
    spec = importlib.util.spec_from_file_location("titanic_append_under_test", QUALITY / "titanic_append.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("script", SCRIPTS, ids=[path.stem for path in SCRIPTS])
def test_each_append_script_checks_clean(script):
    assert shutil.which("node"), "the append scripts write the sanitizer's JSON.stringify bytes through Node"
    done = subprocess.run([sys.executable, "-I", str(script), "--check"], capture_output=True, text=True, cwd=ROOT)
    assert done.returncode == 0, done.stderr or done.stdout


def _graph():
    return {"nodes": [{"id": 1, "type": "LF_Source", "outputs": [{"name": "image", "type": "IMAGE", "links": None}]}],
            "links": [], "groups": [], "last_node_id": 1, "last_link_id": 10}


def _specimen(helper, start_node, start_link, origin):
    specimen = helper.Specimen("Test", start_node, start_link, 0)
    specimen.node(start_node, "LF_View", 0, 0, [("image", "IMAGE")], [("image", "IMAGE", False)])
    specimen.connect(_graph() if origin == 1 else {"nodes": []}, origin, 0, start_node, "image")
    return specimen


def test_a_later_specimen_consuming_an_earlier_one_leaves_it_checking_clean():
    helper = _helper()
    graph = _specimen(helper, 2, 11, 1).append(_graph())
    later = helper.Specimen("Later", 3, 12, 0)
    later.node(3, "LF_View", 0, 0, [("image", "IMAGE")], [("image", "IMAGE", False)])
    later.connect(graph, 2, 0, 3, "image")
    graph = later.append(graph)
    assert next(n for n in graph["nodes"] if n["id"] == 2)["outputs"][0]["links"] == [12]
    assert _specimen(helper, 2, 11, 1).append(copy.deepcopy(graph)) == graph


def test_a_changed_specimen_or_a_moved_boundary_refuses():
    helper = _helper()
    graph = _specimen(helper, 2, 11, 1).append(_graph())
    changed = _specimen(helper, 2, 11, 1)
    changed.nodes[0]["title"] = "renamed"
    with pytest.raises(ValueError, match="drifted"):
        changed.append(copy.deepcopy(graph))
    with pytest.raises(ValueError, match="boundary"):
        _specimen(helper, 5, 11, 1).append(graph)
