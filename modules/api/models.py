from aiohttp import web

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX
from ..utils.helpers.logic import clear_registered_caches

# region free
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/free")
async def lf_nodes_free(request: web.Request):
    """
    Clears LF Nodes in-process caches (e.g., selector caches) without touching core behavior.

    This endpoint is intended to be invoked alongside ComfyUI's native free memory
    actions to ensure LF Nodes' own caches are also reset.
    """
    try:
        clear_registered_caches()
        return web.json_response({"status": "success", "cleared": True})
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")
# endregion