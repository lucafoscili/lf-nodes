from __future__ import annotations
import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

_LOG = logging.getLogger(__name__)


def _maybe_load_dotenv(path: Path) -> None:
    """Load a simple .env file into os.environ without external deps.

    This function will not override existing environment variables.
    """
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and os.environ.get(k) is None:
                os.environ[k] = v
    except Exception:
        _LOG.exception("failed to load .env at %s", path)


def _bool_env(key: str, default: bool = False) -> bool:
    v = os.environ.get(key)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


def _list_env(key: str) -> List[str]:
    v = os.environ.get(key, "")
    if not v:
        return []
    parts = [p.strip() for p in v.replace(";", ",").split(",") if p.strip()]
    return parts


@dataclass(frozen=True)
class Settings:
    ENABLE_GOOGLE_OAUTH: bool
    GOOGLE_CLIENT_IDS: List[str]
    WF_DEBUG: bool
    # other settings can be added here


# Load local .env placed next to this file (dev convenience). Do not override real env vars.
_pkg_root = Path(__file__).parent
_maybe_load_dotenv(_pkg_root / ".env")


# Compute settings once at import
_SETTINGS = Settings(
    ENABLE_GOOGLE_OAUTH=_bool_env("ENABLE_GOOGLE_OAUTH", False),
    GOOGLE_CLIENT_IDS=_list_env("GOOGLE_CLIENT_IDS"),
    WF_DEBUG=_bool_env("WF_DEBUG", False),
)

_LOG.info(
    "workflow-runner settings: ENABLE_GOOGLE_OAUTH=%s, GOOGLE_CLIENT_IDS=%s, WF_DEBUG=%s",
    _SETTINGS.ENABLE_GOOGLE_OAUTH,
    _SETTINGS.GOOGLE_CLIENT_IDS,
    _SETTINGS.WF_DEBUG,
)


def get_settings() -> Settings:
    return _SETTINGS
import json
import logging

from dataclasses import dataclass
from pathlib import Path

from ..utils.constants import API_ROUTE_PREFIX

MODULE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = MODULE_ROOT / "web" / "workflow-runner" / "src" / "runner.config.json"

# region Workflow config
@dataclass(frozen=True)
class WorkflowRunnerConfig:
    api_base: str
    api_route_prefix: str
    static_assets_path: str
    static_workflow_runner_path: str
    deploy_root: Path
    runner_root: Path
    js_dir: str
    prompt_timeout_seconds: float | None

    @property
    def shared_js_root(self) -> Path:
        return self.deploy_root / self.js_dir

    @property
    def workflow_html(self) -> Path:
        return self.runner_root / "workflow-runner.html"

def _load_config() -> WorkflowRunnerConfig:
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    deploy_root = (MODULE_ROOT / data["deploy"]["root"]).resolve()
    runner_root = (deploy_root / data["deploy"]["runnerSubdir"]).resolve()

    raw_prompt_timeout = data.get("promptTimeoutSeconds")
    prompt_timeout: float | None
    try:
        prompt_timeout = float(raw_prompt_timeout)
        if prompt_timeout <= 0:
            prompt_timeout = None
    except (TypeError, ValueError):
        prompt_timeout = None

    return WorkflowRunnerConfig(
        api_base=data["apiBase"],
        api_route_prefix=data["apiRoutePrefix"],
        static_assets_path=data["staticPaths"]["assets"],
        static_workflow_runner_path=data["staticPaths"]["workflowRunner"],
        deploy_root=deploy_root,
        runner_root=runner_root,
        js_dir=data["deploy"]["jsDir"],
        prompt_timeout_seconds=prompt_timeout,
    )

CONFIG = _load_config()

try:
    if CONFIG.api_route_prefix != API_ROUTE_PREFIX:
        logging.warning(
            "Workflow runner configuration mismatch: JSON apiRoutePrefix '%s' != constants.API_ROUTE_PREFIX '%s'",
            CONFIG.api_route_prefix,
            API_ROUTE_PREFIX,
        )
except Exception:
    # constants import may fail in some tooling contexts; swallow to avoid circular import errors during package introspection.
    pass
# endregion
