import os
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import List

_LOG = logging.getLogger(__name__)

# region Helpers
def _maybe_load_dotenv(path: Path) -> None:
    """
    Load a simple .env file into os.environ without external deps.

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

def _int_env(key: str, default: int) -> int:
    v = os.environ.get(key)
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default

def _str_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)
# endregion

# region Settings
@dataclass(frozen=True)
class Settings:
    ENABLE_GOOGLE_OAUTH: bool
    GOOGLE_CLIENT_IDS: List[str]
    ALLOWED_USERS_FILE: str
    ALLOWED_USERS: List[str]
    REQUIRE_ALLOWED_USERS: bool
    GOOGLE_IDTOKEN_CACHE_SECONDS: int
    SESSION_TTL_SECONDS: int
    WORKFLOW_RUNNER_DEBUG: bool
    DEV_ENV: bool
    PROXY_FRONTEND_PORT: int
    COMFY_BACKEND_URL: str
    LF_PROXY_SERVICE_FILE: str
    KOBOLDCPP_BASE_FILE: str
    GEMINI_API_KEY_FILE: str
    OPENAI_API_KEY_FILE: str
    PROXY_ALLOWED_PREFIXES: List[str]
    PROXY_RATE_LIMIT_REQUESTS: int
    PROXY_RATE_LIMIT_WINDOW_SECONDS: int
    JOB_TTL_SECONDS: int
    JOB_PRUNE_INTERVAL_SECONDS: int
    SESSION_PRUNE_INTERVAL_SECONDS: int


_pkg_root = Path(__file__).parent
_maybe_load_dotenv(_pkg_root / ".env")


_SETTINGS = Settings(
    ENABLE_GOOGLE_OAUTH=_bool_env("ENABLE_GOOGLE_OAUTH", False),
    GOOGLE_CLIENT_IDS=_list_env("GOOGLE_CLIENT_IDS"),
    ALLOWED_USERS_FILE=_str_env("ALLOWED_USERS_FILE", ""),
    ALLOWED_USERS=_list_env("ALLOWED_USERS"),
    REQUIRE_ALLOWED_USERS=_bool_env("REQUIRE_ALLOWED_USERS", True),
    GOOGLE_IDTOKEN_CACHE_SECONDS=_int_env("GOOGLE_IDTOKEN_CACHE_SECONDS", 3600),
    SESSION_TTL_SECONDS=_int_env("SESSION_TTL_SECONDS", _int_env("GOOGLE_IDTOKEN_CACHE_SECONDS", 3600)),
    WORKFLOW_RUNNER_DEBUG=_bool_env("WORKFLOW_RUNNER_DEBUG", False),
    DEV_ENV=_bool_env("DEV_ENV", False),
    PROXY_FRONTEND_PORT=_int_env("PROXY_FRONTEND_PORT", 0),
    COMFY_BACKEND_URL=_str_env("COMFY_BACKEND_URL", ""),
    LF_PROXY_SERVICE_FILE=_str_env("LF_PROXY_SERVICE_FILE", ""),
    KOBOLDCPP_BASE_FILE=_str_env("KOBOLDCPP_BASE_FILE", ""),
    GEMINI_API_KEY_FILE=_str_env("GEMINI_API_KEY_FILE", ""),
    OPENAI_API_KEY_FILE=_str_env("OPENAI_API_KEY_FILE", ""),
    PROXY_ALLOWED_PREFIXES=_list_env("PROXY_ALLOWED_PREFIXES"),
    PROXY_RATE_LIMIT_REQUESTS=_int_env("PROXY_RATE_LIMIT_REQUESTS", 60),
    PROXY_RATE_LIMIT_WINDOW_SECONDS=_int_env("PROXY_RATE_LIMIT_WINDOW_SECONDS", 60),
    JOB_TTL_SECONDS=_int_env("JOB_TTL_SECONDS", 300),
    JOB_PRUNE_INTERVAL_SECONDS=_int_env("JOB_PRUNE_INTERVAL_SECONDS", 60),
    SESSION_PRUNE_INTERVAL_SECONDS=_int_env("SESSION_PRUNE_INTERVAL_SECONDS", 60),
)

def get_settings() -> Settings:
    return _SETTINGS
import json
import logging

from dataclasses import dataclass
from pathlib import Path

API_ROUTE_PREFIX = "/lf-nodes" # Match the same in utils.constants
MODULE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = MODULE_ROOT / "web" / "workflow-runner" / "src" / "runner.config.json"
# endregion

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
    # Import constants lazily inside the try/except so that heavy dependencies pulled in by
    # `utils.constants` (for example `comfy` / `torch`) don't run at import-time here.
    from ..utils.constants import API_ROUTE_PREFIX

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
