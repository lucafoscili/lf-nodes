import importlib.util
import logging
import os
import sys

from pathlib import Path

try:
    from .modules.utils.env import maybe_load_dotenv, bool_env
except ImportError:
    # Handle case where relative imports fail (e.g., when imported by pytest)
    def maybe_load_dotenv(*args, **kwargs):
        pass
    def bool_env(*args, **kwargs):
        return False

VERSION = "2.5.0"

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

LOG = logging.getLogger(__name__)

repo_root = Path(__file__).resolve().parent
maybe_load_dotenv(repo_root / ".env")
_WF_ENABLED = bool_env("WORKFLOW_RUNNER_ENABLED", False)

sys.modules["lf_nodes"] = sys.modules[__name__]

for dirpath, _, filenames in os.walk(MODULES_DIR):
    if "tests" in dirpath or "test" in dirpath or "__pycache__" in dirpath:
        continue

    for filename in filenames:
        if not filename.endswith(".py") or filename == "__init__.py" or filename.startswith("test_"):
            continue

        relative_path = os.path.relpath(os.path.join(dirpath, filename), MODULES_DIR)
        first_component = relative_path.split(os.path.sep)[0]
        if first_component == "workflow_runner" and not _WF_ENABLED:
            continue
        module_name = os.path.splitext(relative_path.replace(os.path.sep, "."))[0]
        full_module_name = f"lf_nodes.modules.{module_name}"

        try:
            spec = importlib.util.spec_from_file_location(full_module_name, os.path.join(dirpath, filename))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                NODE_CLASS_MAPPINGS.update(getattr(module, "NODE_CLASS_MAPPINGS", {}))
                NODE_DISPLAY_NAME_MAPPINGS.update(getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {}))
        except Exception as e:
            LOG.error(f"❌ Failed to import {full_module_name}: {e}")

WEB_DIRECTORY = "./web/deploy"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

LOG.info("\033[34m*-----------------------------------------------------------*\033[0m")
LOG.info(f"\033[34m*             ✨ LF Nodes initialized - v{VERSION}              *\033[0m")
if _WF_ENABLED:
    try:
        import comfy.cli_args as _cli

        _args = getattr(_cli, "args", None)
        host = None
        port = None
        if _args is not None:
            host = getattr(_args, "listen", None)
            port = getattr(_args, "port", None)

        if host:
            host = str(host).split(",", 1)[0]
            if host in ("0.0.0.0", "::"):
                host = "localhost"

        if port:
            wr_url = f"http://{host}:{port}"
    except Exception:
        wr_url = None

    if wr_url:
        full = wr_url.rstrip("/") + "/api/lf-nodes/workflow-runner"
        LOG.info("\033[34m*                                                           *\033[0m")
        LOG.info(f"\033[34m*  WR: {full}   *\033[0m")
LOG.info("\033[34m*-----------------------------------------------------------*\033[0m")
