import json
import os
import re
import stat
import tempfile
import time

from aiohttp import web

from server import PromptServer
from ..utils.constants import API_ROUTE_PREFIX
from ..utils.helpers.comfy.get_comfy_dir import get_comfy_dir
from ..utils.helpers.editing.file_lock import edit_dataset_lock
from ..utils.helpers.editing.ownership import (
    CALLER_CLIENT_ID_FIELD,
    OWNER_CLIENT_ID_KEY,
    caller_owns_context,
    get_owner_client_id,
    normalize_client_id,
)


_EDIT_DATASET_SUFFIX = "_edit_dataset.json"
_REPLACE_ATTEMPTS = 20
_REPLACE_RETRY_SECONDS = 0.01


def _atomic_write_json(file_path: str, data: object) -> None:
    """Replace an existing JSON file without exposing partially written bytes."""
    target_path = os.path.realpath(os.path.abspath(file_path))
    target_mode = stat.S_IMODE(os.stat(target_path).st_mode)
    target_dir = os.path.dirname(target_path)

    descriptor, temporary_path = tempfile.mkstemp(
        dir=target_dir,
        prefix=f".{os.path.basename(target_path)}.",
        suffix=".tmp",
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as json_file:
            descriptor = -1
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            json_file.flush()
            os.fsync(json_file.fileno())

        os.chmod(temporary_path, target_mode)
        for attempt in range(_REPLACE_ATTEMPTS):
            try:
                os.replace(temporary_path, target_path)
                break
            except PermissionError:
                if attempt + 1 == _REPLACE_ATTEMPTS:
                    raise
                time.sleep(_REPLACE_RETRY_SECONDS)
        temporary_path = ""
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass


def _resolve_regular_file_under_root(root_dir: str, file_path: str) -> str | None:
    """Return a resolved regular file only when it remains below ``root_dir``."""
    resolved_root = os.path.realpath(os.path.abspath(root_dir))
    resolved_path = os.path.realpath(os.path.abspath(file_path))
    root_key = os.path.normcase(resolved_root)
    path_key = os.path.normcase(resolved_path)

    try:
        if os.path.commonpath((root_key, path_key)) != root_key:
            return None
    except ValueError:
        return None

    return resolved_path if os.path.isfile(resolved_path) else None


def _read_json_after_replace(file_path: str) -> object | None:
    """Read JSON while tolerating Windows' brief replacement sharing denial."""
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            with open(file_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except PermissionError:
            if attempt + 1 == _REPLACE_ATTEMPTS:
                return None
            time.sleep(_REPLACE_RETRY_SECONDS)
        except (OSError, json.JSONDecodeError):
            return None
    return None


def _resolve_bound_edit_dataset_path(
    temp_dir: str,
    file_path: str,
    dataset: object,
    node_id: str,
) -> str | None:
    """Resolve one regular editing dataset whose internal identity matches its path."""
    if not isinstance(dataset, dict) or not node_id:
        return None

    resolved_path = _resolve_regular_file_under_root(temp_dir, file_path)
    if resolved_path is None:
        return None

    path_key = os.path.normcase(resolved_path)

    expected_name = re.compile(
        rf"^{re.escape(node_id)}_[0-9a-fA-F]{{32}}{re.escape(_EDIT_DATASET_SUFFIX)}$"
    )
    if expected_name.fullmatch(os.path.basename(resolved_path)) is None:
        return None

    if str(dataset.get("lf_node_id", "")).strip() != node_id:
        return None

    context_id = dataset.get("context_id")
    if not isinstance(context_id, str) or not context_id.strip():
        return None
    if os.path.normcase(os.path.realpath(os.path.abspath(context_id))) != path_key:
        return None

    path_columns = _dataset_columns(dataset, "path")
    if len(path_columns) != 1:
        return None
    path_title = path_columns[0].get("title")
    if not isinstance(path_title, str) or not path_title.strip():
        return None
    if os.path.normcase(os.path.realpath(os.path.abspath(path_title))) != path_key:
        return None

    return resolved_path


def _dataset_columns(dataset: dict, column_id: str) -> list[dict]:
    columns = dataset.get("columns")
    if not isinstance(columns, list):
        return []
    return [
        column
        for column in columns
        if isinstance(column, dict) and column.get("id") == column_id
    ]


def _dataset_status(dataset: dict) -> str | None:
    status_columns = _dataset_columns(dataset, "status")
    if len(status_columns) != 1:
        return None
    title = status_columns[0].get("title")
    return str(title) if title is not None else None


def _is_load_and_edit_dataset(dataset: dict) -> bool:
    prefix = dataset.get("prefix", dataset.get("filename_prefix"))
    return prefix == "load_and_edit"


def _is_owner_bound_to_caller(dataset: dict, caller_client_id: str) -> bool:
    """Return true only for an explicitly owned dataset and its exact caller."""
    try:
        owner_client_id = get_owner_client_id(dataset)
    except ValueError:
        return False
    return (
        owner_client_id is not None
        and normalize_client_id(caller_client_id) == owner_client_id
    )


def _latest_pending_edit_dataset(
    temp_dir: str,
    node_id: str,
    caller_client_id: str,
) -> dict | None:
    """Return the newest pending breakpoint owned by this exact Comfy tab."""
    if not normalize_client_id(caller_client_id):
        return None
    expected_name = re.compile(
        rf"^{re.escape(node_id)}_[0-9a-fA-F]{{32}}{re.escape(_EDIT_DATASET_SUFFIX)}$"
    )
    candidates: list[tuple[float, str]] = []

    for entry in os.listdir(temp_dir):
        if expected_name.fullmatch(entry) is None:
            continue

        full_path = os.path.join(temp_dir, entry)
        resolved_path = _resolve_regular_file_under_root(temp_dir, full_path)
        if resolved_path is None:
            continue
        if expected_name.fullmatch(os.path.basename(resolved_path)) is None:
            continue
        try:
            candidates.append((os.path.getmtime(resolved_path), resolved_path))
        except OSError:
            continue

    ordered_candidates = sorted(
        candidates,
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    for _, candidate_path in ordered_candidates:
        with edit_dataset_lock(candidate_path):
            dataset = _read_json_after_replace(candidate_path)

            if not isinstance(dataset, dict):
                continue

            resolved_path = _resolve_bound_edit_dataset_path(
                temp_dir,
                candidate_path,
                dataset,
                node_id,
            )
            if resolved_path is None:
                continue

            status = _dataset_status(dataset)
            if _is_load_and_edit_dataset(dataset):
                continue
            if status == "pending" and _is_owner_bound_to_caller(
                dataset,
                caller_client_id,
            ):
                return dataset

    return None


def _recover_bound_edit_dataset(
    temp_dir: str,
    node_id: str,
    context_id: str,
    caller_client_id: str,
) -> dict | None:
    """Recover one exact context without scanning same-numbered workflow nodes."""
    resolved_path = _resolve_regular_file_under_root(temp_dir, context_id)
    if resolved_path is None:
        return None

    expected_name = re.compile(
        rf"^{re.escape(node_id)}_[0-9a-fA-F]{{32}}{re.escape(_EDIT_DATASET_SUFFIX)}$"
    )
    if expected_name.fullmatch(os.path.basename(resolved_path)) is None:
        return None

    with edit_dataset_lock(resolved_path):
        dataset = _read_json_after_replace(resolved_path)
        if not isinstance(dataset, dict):
            return None
        if (
            _resolve_bound_edit_dataset_path(
                temp_dir,
                resolved_path,
                dataset,
                node_id,
            )
            is None
        ):
            return None

        status = _dataset_status(dataset)
        if not caller_owns_context(dataset, caller_client_id):
            return None
        if _is_load_and_edit_dataset(dataset):
            if status in {"pending", "completed"}:
                return dataset
            return None
        if status == "pending":
            return dataset
        return None

# region get-json
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-json")
async def get_json_data(request):
    try:
        r: dict = await request.post()

        file_path: str = r.get("file_path")

        if not file_path or not os.path.exists(file_path):
            return web.Response(status=404, text="JSON file not found.")

        # Classify the resolved target, not the caller-controlled spelling.
        # Windows accepts aliases with trailing dots/spaces for the same file;
        # checking the raw basename would let those aliases skip editor-owner
        # authorization and fall through to the generic JSON reader.
        resolved_target = os.path.realpath(os.path.abspath(file_path))
        if os.path.basename(resolved_target).endswith(_EDIT_DATASET_SUFFIX):
            temp_dir = get_comfy_dir("temp")
            resolved_path = _resolve_regular_file_under_root(temp_dir, resolved_target)
            if resolved_path is None:
                return web.Response(status=404, text="Editing dataset not found.")
            with edit_dataset_lock(resolved_path):
                data = _read_json_after_replace(resolved_path)
                node_id = (
                    str(data.get("lf_node_id", "")).strip()
                    if isinstance(data, dict)
                    else ""
                )
                if (
                    not node_id
                    or _resolve_bound_edit_dataset_path(
                        temp_dir,
                        resolved_path,
                        data,
                        node_id,
                    )
                    is None
                ):
                    return web.Response(
                        status=409,
                        text="Editing dataset changed unexpectedly.",
                    )
                if not caller_owns_context(data, r.get(CALLER_CLIENT_ID_FIELD)):
                    return web.Response(
                        status=403,
                        text="Editing dataset belongs to another client.",
                    )
        else:
            with open(file_path, "r", encoding="utf-8") as json_file:
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
        if not file_path:
            return web.Response(status=404, text="JSON file not found.")
        dataset_raw = r.get("dataset")
        try:
            new_data = json.loads(dataset_raw)
        except (TypeError, json.JSONDecodeError):
            return web.Response(status=400, text="Editing dataset must be valid JSON.")
        if not isinstance(new_data, dict):
            return web.Response(status=400, text="Editing dataset must be an object.")

        temp_dir = get_comfy_dir("temp")
        resolved_path = _resolve_regular_file_under_root(temp_dir, file_path)
        if resolved_path is None:
            return web.Response(status=404, text="JSON file not found.")

        caller_client_id = r.get(CALLER_CLIENT_ID_FIELD)
        with edit_dataset_lock(resolved_path):
            current_data = _read_json_after_replace(resolved_path)
            if not isinstance(current_data, dict):
                if not os.path.exists(resolved_path):
                    return web.Response(status=404, text="JSON file not found.")
                return web.Response(
                    status=409,
                    text="Editing dataset changed unexpectedly.",
                )

            node_id = str(current_data.get("lf_node_id", "")).strip()
            if (
                not node_id
                or _resolve_bound_edit_dataset_path(
                    temp_dir,
                    resolved_path,
                    current_data,
                    node_id,
                )
                is None
            ):
                return web.Response(
                    status=409,
                    text="Editing dataset changed unexpectedly.",
                )

            try:
                get_owner_client_id(current_data)
            except ValueError:
                return web.Response(
                    status=409,
                    text="Editing dataset has invalid ownership metadata.",
                )
            if not caller_owns_context(current_data, caller_client_id):
                return web.Response(
                    status=403,
                    text="Editing dataset belongs to another client.",
                )

            if (
                _resolve_bound_edit_dataset_path(
                    temp_dir,
                    resolved_path,
                    new_data,
                    node_id,
                )
                is None
            ):
                return web.Response(status=400, text="Editing dataset binding mismatch.")

            missing = object()
            for immutable_key in (
                "lf_node_id",
                "context_id",
                "prefix",
                "filename_prefix",
                OWNER_CLIENT_ID_KEY,
            ):
                if current_data.get(immutable_key, missing) != new_data.get(
                    immutable_key,
                    missing,
                ):
                    return web.Response(
                        status=409,
                        text=f"Editing dataset {immutable_key} is immutable.",
                    )

            current_path_title = _dataset_columns(current_data, "path")[0].get(
                "title"
            )
            new_path_title = _dataset_columns(new_data, "path")[0].get("title")
            if current_path_title != new_path_title:
                return web.Response(
                    status=409,
                    text="Editing dataset path is immutable.",
                )

            current_status = _dataset_status(current_data)
            new_status = _dataset_status(new_data)
            allowed_transitions = {
                "pending": {"pending", "completed"},
                "completed": {"completed"},
            }
            if current_status not in allowed_transitions or new_status not in {
                "pending",
                "completed",
            }:
                return web.Response(
                    status=400,
                    text="Editing dataset requires exactly one valid status column.",
                )
            if new_status not in allowed_transitions[current_status]:
                return web.Response(
                    status=409,
                    text=(
                        f"Editing dataset status cannot change from "
                        f"{current_status} to {new_status}."
                    ),
                )

            _atomic_write_json(resolved_path, new_data)

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

    An owner-bound session requires the exact current ``caller_client_id``.
    Ownerless headless sessions can be recovered only by exact ``context_id``;
    numeric node IDs alone are never authority for them.

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

        context_id_raw = r.get("context_id")
        context_id = (
            str(context_id_raw).strip() if context_id_raw is not None else ""
        )
        caller_client_id_raw = r.get(CALLER_CLIENT_ID_FIELD)
        caller_client_id = (
            str(caller_client_id_raw).strip()
            if caller_client_id_raw is not None
            else ""
        )
        dataset = (
            _recover_bound_edit_dataset(
                temp_dir,
                node_id,
                context_id,
                caller_client_id,
            )
            if context_id
            else _latest_pending_edit_dataset(
                temp_dir,
                node_id,
                caller_client_id,
            )
        )

        return web.json_response(
            {
                "status": "success",
                "data": dataset,
            },
            status=200,
        )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")

# endregion
