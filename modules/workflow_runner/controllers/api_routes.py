import logging
import importlib

from aiohttp import web

from server import PromptServer

from ..config import API_ROUTE_PREFIX, get_settings

# region Helpers
def _get_api_controllers():
    """
    Lazily import the API controllers module.

    Importing the controllers module at module-import time can pull in heavy
    dependencies (services, auth helpers) that should be deferred until a
    request actually needs them. This helper centralises the import and logs
    failures for easier debugging.
    """
    try:
        return importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_controllers")
    except Exception:
        logging.exception("Failed to import workflow_runner.api_controllers")
        raise
# endregion

if not get_settings().WORKFLOW_RUNNER_ENABLED:
    logging.info(
        "Workflow Runner disabled by WORKFLOW_RUNNER_ENABLED environment variable; skipping route registration."
    )
else:

    # IMPORTANT: Specific routes must be registered BEFORE catch-all routes!
    # aiohttp evaluates routes in registration order, so catch-alls must come last.

    # region Run Workflow
    @PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/run")
    async def route_run_workflow(request: web.Request) -> web.Response:
        # Lazily import and delegate to the controller to avoid heavy imports
        api_controllers = _get_api_controllers()
        return await api_controllers.start_workflow_controller(request)
    # endregion

    # region Run Status
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/run/{{run_id}}/status")
    async def route_run_status(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.get_workflow_status_controller(request)
    # endregion

    # region Run Events (SSE)
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/run/events")
    async def route_run_events(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.stream_runs_controller(request)
    # endregion

    # region Workflows
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows")
    async def route_list_workflows(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.list_workflows_controller(request)
    # endregion

    # region Workflow Details
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflows/{{workflow_id}}")
    async def route_get_workflow(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.get_workflow_controller(request)
    # endregion

    # region Workflow Runner - List Runs
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner/runs")
    async def route_list_runs(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.list_runs_controller(request)
    # endregion

    # region Workflow Runner - Events (SSE)
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner/events")
    async def route_workflow_runner_events(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.stream_runs_controller(request)
    # endregion

    # region Admin debug UI routes
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner/admin")
    async def route_admin_page(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.admin_runs_page(request)

    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/workflow-runner/admin/runs")
    async def route_admin_runs(request: web.Request) -> web.Response:
        api_controllers = _get_api_controllers()
        return await api_controllers.admin_runs_api(request)
    # endregion

    # region API Catch-All Routes (MUST BE LAST!)
    @PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/{{path:.*}}")
    async def route_api_catch_all_get(request: web.Request) -> web.Response:
        path = request.path
        if path.startswith(f"{API_ROUTE_PREFIX}/workflow-runner") or path.endswith("/verify"):
            return web.Response(status=404, text="Not found")

        logging.info("Denied unauthenticated GET to %s", path)
        return web.json_response({"detail": "forbidden"}, status=403)

    @PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/{{path:.*}}")
    async def route_api_catch_all_post(request: web.Request) -> web.Response:
        path = request.path
        if path.endswith("/verify"):
            return web.Response(status=404, text="Not found")

        logging.info("Denied unauthenticated POST to %s", path)
        return web.json_response({"detail": "forbidden"}, status=403)
    # endregion
