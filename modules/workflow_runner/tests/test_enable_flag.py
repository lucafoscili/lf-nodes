import importlib.util
import sys

from pathlib import Path

def _import_lf_nodes_and_list_workflow_modules(init_path: Path):
    # Clean any previous import state
    for k in list(sys.modules.keys()):
        if k.startswith("lf_nodes"):
            del sys.modules[k]

    spec = importlib.util.spec_from_file_location("lf_nodes", str(init_path))
    module = importlib.util.module_from_spec(spec)
    # Ensure the package name is available to the module at import time
    sys.modules["lf_nodes"] = module
    # Execute the module (this will run the import loop in lf-nodes/__init__.py)
    spec.loader.exec_module(module)

    mods = [m for m in sys.modules.keys() if m.startswith("lf_nodes.modules.workflow_runner")]
    return mods

def test_workflow_runner_not_imported_when_disabled(monkeypatch):
    # Ensure the runner is disabled regardless of any .env files by explicitly setting a falsey value.
    monkeypatch.setenv("WORKFLOW_RUNNER_ENABLED", "0")

    init_path = Path(__file__).resolve().parents[3] / "__init__.py"
    mods = _import_lf_nodes_and_list_workflow_modules(init_path)
    assert len(mods) == 0, f"Expected no workflow_runner modules when disabled, found: {mods}"

def test_workflow_runner_imported_when_enabled(monkeypatch):
    monkeypatch.setenv("WORKFLOW_RUNNER_ENABLED", "true")

    init_path = Path(__file__).resolve().parents[3] / "__init__.py"
    mods = _import_lf_nodes_and_list_workflow_modules(init_path)
    assert len(mods) > 0, "Expected workflow_runner modules to be imported when enabled"
