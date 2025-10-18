import json
import logging

from dataclasses import dataclass
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = MODULE_ROOT / "web" / "workflow-runner" / "src" / "runner.config.json"

@dataclass(frozen=True)
class WorkflowRunnerConfig:
    api_base: str
    api_route_prefix: str
    static_assets_path: str
    static_workflow_runner_path: str
    deploy_root: Path
    runner_root: Path
    js_dir: str

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

    return WorkflowRunnerConfig(
        api_base=data["apiBase"],
        api_route_prefix=data["apiRoutePrefix"],
        static_assets_path=data["staticPaths"]["assets"],
        static_workflow_runner_path=data["staticPaths"]["workflowRunner"],
        deploy_root=deploy_root,
        runner_root=runner_root,
        js_dir=data["deploy"]["jsDir"],
    )


CONFIG = _load_config()

try:
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
