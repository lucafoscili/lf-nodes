import os
import shutil

from aiohttp import web
from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX, EXTERNAL_PREVIEW_SUBDIR
from ..utils.helpers.comfy import get_comfy_dir

# region get-preview-stats
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-preview-stats")
async def get_preview_stats(request):
    """
    Calculate disk usage statistics for the external preview cache.

    Returns:
        JSON response with total size in bytes and file count, or error.
    """
    try:
        base_input = get_comfy_dir("input")
        preview_dir = os.path.join(base_input, EXTERNAL_PREVIEW_SUBDIR)

        total_size = 0
        file_count = 0

        if os.path.exists(preview_dir) and os.path.isdir(preview_dir):
            for root, _, files in os.walk(preview_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except OSError:
                        # Skip files we can't access
                        pass

        return web.json_response(
            {
                "status": "success",
                "message": "Preview statistics retrieved successfully.",
                "data": {
                    "total_size_bytes": total_size,
                    "file_count": file_count,
                    "path": preview_dir,
                },
            },
            status=200,
        )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region clear-preview-cache
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/clear-preview-cache")
async def clear_preview_cache(request):
    """
    Delete the entire external preview cache directory.

    Returns:
        JSON response confirming deletion or error.
    """
    try:
        base_input = get_comfy_dir("input")
        preview_dir = os.path.join(base_input, EXTERNAL_PREVIEW_SUBDIR)

        if not os.path.exists(preview_dir):
            return web.json_response(
                {
                    "status": "success",
                    "message": "Preview cache directory does not exist. Nothing to clear.",
                },
                status=200,
            )

        # Remove the entire directory tree
        shutil.rmtree(preview_dir)

        return web.json_response(
            {
                "status": "success",
                "message": f"Preview cache cleared successfully from {preview_dir}",
            },
            status=200,
        )

    except PermissionError:
        return web.Response(
            status=403,
            text="Permission denied: Unable to delete preview cache directory.",
        )
    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion
