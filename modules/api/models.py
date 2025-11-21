from aiohttp import web

from server import PromptServer

from ..utils.constants import (
    API_ROUTE_PREFIX,
    SAMPLERS,
    SAMPLER_MAP,
    SCHEDULERS,
    SCHEDULER_MAP,
)
from ..utils.helpers.logic import clear_registered_caches

# region Helpers
def _build_options_dataset(options, label_map):
    """
    Build a lightweight LfDataDataset-like structure for sampler/scheduler options.

    Each option is exposed as a node where:
      - node.id = internal code (e.g. "dpmpp_2m")
      - node.value = human-friendly label (e.g. "DPM++ 2M")

    Columns are kept minimal so the dataset can be reused for other widgets later.
    """
    nodes = []
    for code in options or []:
        label = label_map.get(code, str(code))
        nodes.append(
            {
                "id": str(code),
                "value": label,
            }
        )

    dataset = {
        "columns": [
            {"id": "label", "title": "Label"},
        ],
        "nodes": nodes,
    }
    return dataset
# endregion

# region free (clear) caches
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


# region sampling options
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-samplers")
async def lf_nodes_get_samplers(request: web.Request):
    """
    Expose available diffusion samplers to the frontend as a LfDataDataset-shaped JSON payload.

    The response structure is:
      {
        "status": "success",
        "data": {
          "columns": [{ "id": "label", "title": "Label" }],
          "nodes": [
            { "id": "<code>", "value": "<label>" },
            ...
          ]
        }
      }
    """
    try:
        dataset = _build_options_dataset(SAMPLERS, SAMPLER_MAP)
        return web.json_response({"status": "success", "data": dataset}, status=200)
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")
# endregion

# region scheduler options
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-schedulers")
async def lf_nodes_get_schedulers(request: web.Request):
    """
    Expose available diffusion schedulers to the frontend as a LfDataDataset-shaped JSON payload.

    The response structure mirrors /get-samplers.
    """
    try:
        dataset = _build_options_dataset(SCHEDULERS, SCHEDULER_MAP)
        return web.json_response({"status": "success", "data": dataset}, status=200)
    except Exception as e:
        return web.Response(status=500, text=f"Error: {e}")
# endregion
