import json
import os

from aiohttp import web

from server import PromptServer
from ..utils.constants import API_ROUTE_PREFIX
from ..utils.helpers.comfy.get_comfy_dir import get_comfy_dir

# region get-json
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-json")
async def get_json_data(request):
    try:
        r: dict = await request.post()

        file_path: str = r.get("file_path")

        if not file_path or not os.path.exists(file_path):
            return web.Response(status=404, text="JSON file not found.")

        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        return web.json_response({
            "status": "success",
            "data": data
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region update-json
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/update-json")
async def update_json_data(request):
    try:
        r: dict = await request.post()

        file_path: str = r.get("file_path")
        new_data: dict = json.loads(r.get("dataset"))

        if not file_path or not os.path.exists(file_path):
            return web.Response(status=404, text="JSON file not found.")

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(new_data, json_file, ensure_ascii=False, indent=4)

        return web.json_response(
            {
                "status": "success",
                "message": "JSON data updated successfully.",
            },
            status=200,
        )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region recover-edit-dataset
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/recover-edit-dataset")
async def recover_edit_dataset(request):
    """
    Attempt to recover a pending editing dataset JSON for the given node_id.

    This scans the ComfyUI temp directory for files matching the pattern
    ``{node_id}_*_edit_dataset.json`` and returns the most recently modified
    one whose status column is still marked as \"pending\".

    The response mirrors the shape of get-json:
      { "status": "success", "data": { ...dataset... } }
    """
    try:
        r: dict = await request.post()

        node_id_raw = r.get("node_id")
        node_id = str(node_id_raw).strip() if node_id_raw is not None else ""
        if not node_id:
            return web.json_response({"status": "success", "data": None}, status=200)

        temp_dir = get_comfy_dir("temp")
        if not os.path.isdir(temp_dir):
            return web.json_response({"status": "success", "data": None}, status=200)

        prefix = f"{node_id}_"
        suffix = "_edit_dataset.json"

        candidates: list[tuple[float, str]] = []

        for entry in os.listdir(temp_dir):
            if not (entry.startswith(prefix) and entry.endswith(suffix)):
                continue

            full_path = os.path.join(temp_dir, entry)
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue
            candidates.append((mtime, full_path))

        if not candidates:
            return web.json_response({"status": "success", "data": None}, status=200)

        _, latest_path = max(candidates, key=lambda item: item[0])

        with open(latest_path, "r", encoding="utf-8") as json_file:
            dataset = json.load(json_file)

        columns = dataset.get("columns") or []
        status_column = next(
            (col for col in columns if isinstance(col, dict) and col.get("id") == "status"),
            None,
        )
        if status_column and status_column.get("title") != "pending":
            return web.json_response({"status": "success", "data": None}, status=200)

        return web.json_response({"status": "success", "data": dataset}, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")

# endregion
