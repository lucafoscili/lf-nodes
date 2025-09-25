from aiohttp import web

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX
from ..utils.helpers.logic import clear_registered_caches


@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/refresh-node-defs")
async def lf_nodes_refresh_node_defs(request: web.Request):
    """
    Clears LF Nodes selector caches so new resources are picked up when ComfyUI
    refreshes node definitions.
    """
    try:
        clear_registered_caches()
        return web.json_response({"status": "success", "cleared": True})
    except Exception as exc:  # pragma: no cover - logged to UI instead
        return web.Response(status=500, text=f"Error: {exc}")
