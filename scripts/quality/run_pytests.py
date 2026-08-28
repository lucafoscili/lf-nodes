#!/usr/bin/env python3
"""Run LF's CPU contract tests without importing Comfy's optional GPU stack.

Pytest may import the repository package before a nested ``conftest.py`` can
install host doubles. On Windows that can eagerly load incompatible xformers or
flash-attn DLLs even when every selected test is CPU-only. This bootstrap owns
that pre-collection boundary and then forwards all arguments to pytest.
"""

from __future__ import annotations

import sys
import tempfile
import types
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]


class _Routes:
    def get(self, _path):
        return lambda function: function

    def post(self, _path):
        return lambda function: function


def _install_host_stubs() -> None:
    root_init = types.ModuleType("__init__")
    root_init.__file__ = str(ROOT / "__init__.py")
    root_init.__lf_nodes_test_stub__ = True
    sys.modules["__init__"] = root_init

    server = types.ModuleType("server")
    server.__lf_nodes_test_stub__ = True
    server.PromptServer = SimpleNamespace(
        instance=SimpleNamespace(
            routes=_Routes(),
            send_sync=lambda *_args, **_kwargs: None,
        )
    )
    sys.modules["server"] = server

    nodes = types.ModuleType("nodes")
    nodes.__lf_nodes_test_stub__ = True
    sys.modules["nodes"] = nodes

    comfy = types.ModuleType("comfy")
    comfy.__path__ = []
    comfy.__lf_nodes_test_stub__ = True
    sys.modules["comfy"] = comfy

    sample = types.ModuleType("comfy.sample")
    samplers = types.ModuleType("comfy.samplers")
    samplers.KSampler = type(
        "KSampler",
        (),
        {"SAMPLERS": [], "SCHEDULERS": []},
    )
    sd = types.ModuleType("comfy.sd")
    utils = types.ModuleType("comfy.utils")
    model_management = types.ModuleType("comfy.model_management")
    cli_args = types.ModuleType("comfy.cli_args")
    cli_args.args = SimpleNamespace(
        base_directory=None,
        models_directory=None,
        disable_metadata=False,
    )

    for name, module in {
        "sample": sample,
        "samplers": samplers,
        "sd": sd,
        "utils": utils,
        "model_management": model_management,
        "cli_args": cli_args,
    }.items():
        setattr(comfy, name, module)
        sys.modules[f"comfy.{name}"] = module

    host_root = Path(tempfile.gettempdir()) / "lf_nodes_pytest_host"
    folder_paths = types.ModuleType("folder_paths")
    folder_paths.__lf_nodes_test_stub__ = True
    folder_paths.models_dir = str(host_root / "models")
    folder_paths.get_input_directory = lambda: str(host_root / "input")
    folder_paths.get_output_directory = lambda: str(host_root / "output")
    folder_paths.get_temp_directory = lambda: str(host_root / "temp")
    folder_paths.get_user_directory = lambda: str(host_root / "user")
    folder_paths.get_directory_by_type = lambda _kind: None
    folder_paths.get_filename_list = lambda _kind: []
    folder_paths.get_folder_paths = lambda _kind: []
    folder_paths.get_full_path = lambda _kind, _name: None

    def _missing_model(kind, name):
        raise FileNotFoundError(f"No test {kind} resource named {name!r}.")

    folder_paths.get_full_path_or_raise = _missing_model
    folder_paths.get_save_image_path = lambda filename_prefix, *_args, **_kwargs: (
        str(host_root / "output"),
        filename_prefix,
        1,
        "",
        filename_prefix,
    )
    sys.modules["folder_paths"] = folder_paths


def main() -> int:
    sys.path.insert(0, str(ROOT))
    _install_host_stubs()

    import pytest

    forwarded = sys.argv[1:]
    if "-c" in forwarded or any(
        argument == "--rootdir" or argument.startswith("--rootdir=")
        for argument in forwarded
    ):
        raise SystemExit(
            "run_pytests.py owns pytest config/rootdir to keep Comfy host code "
            "outside the CPU test boundary"
        )

    return int(
        pytest.main(
            [
                "-c",
                str(ROOT / "pyproject.toml"),
                "--rootdir",
                str(ROOT),
                *forwarded,
            ]
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
