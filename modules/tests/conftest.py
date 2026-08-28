"""Ensure 'modules' package is importable when running pytest from repo root.

We append the lf-nodes root so that 'modules' resolves to
custom_nodes/lf-nodes/modules during test collection.
"""

import os
import sys
import types
from pathlib import Path
from types import SimpleNamespace

THIS_DIR = Path(__file__).resolve().parent
LF_NODES_ROOT = THIS_DIR.parent.parent  # .../custom_nodes/lf-nodes

if str(LF_NODES_ROOT) not in sys.path:
    sys.path.insert(0, str(LF_NODES_ROOT))

# Node unit tests exercise LF contracts, not ComfyUI's optional native model
# stack.  Importing the real ``server`` during collection pulls in CUDA,
# xformers, flash-attn, and version-sensitive comfy_kitchen extensions before
# an individual test can install its narrow fixture.  Provide the same inert
# host boundary used by focused node tests; suites that need route behavior
# replace ``PromptServer.instance`` explicitly in their own fixtures.
if "server" not in sys.modules:
    server = types.ModuleType("server")
    server.PromptServer = SimpleNamespace(instance=None)
    sys.modules["server"] = server

for host_module_name in ("comfy.sample", "nodes"):
    sys.modules.setdefault(host_module_name, types.ModuleType(host_module_name))

if "comfy.samplers" not in sys.modules:
    comfy_samplers = types.ModuleType("comfy.samplers")
    comfy_samplers.KSampler = type(
        "KSampler",
        (),
        {"SAMPLERS": [], "SCHEDULERS": []},
    )
    sys.modules["comfy.samplers"] = comfy_samplers
