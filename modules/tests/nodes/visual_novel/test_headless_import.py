from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_visual_novel_compile_executes_without_host_or_provider_imports() -> None:
    repository_root = Path(__file__).resolve().parents[4]
    command = (
        "import sys; "
        "blocked = {'folder_paths', 'onnxruntime', 'cv2', 'torch'}; "
        "assert blocked.isdisjoint(sys.modules); "
        "import modules.nodes.visual_novel.compile as module; "
        "assert module.LF_VNCompile.RETURN_NAMES[0] == 'bundle'; "
        "state = {'schema': 'lf.vn.state.v1', 'fixtureId': 'fixture.test', "
        "'values': {}, 'appliedEffectIds': []}; "
        "caught = False; "
        "\ntry:\n "
        " module.LF_VNCompile().on_exec(graph={}, state=state, workflow_id='', "
        "entry_scene_id='')\n"
        "except module.VNContractError:\n caught = True\n"
        "assert caught; "
        "assert blocked.isdisjoint(sys.modules)"
    )

    completed = subprocess.run(
        [sys.executable, "-B", "-c", command],
        cwd=repository_root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
