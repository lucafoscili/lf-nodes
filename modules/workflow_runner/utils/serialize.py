import logging

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit

from .media import media_type_for_filename

LOG = logging.getLogger(__name__)

# region Serialize job
def build_output_preview(result: Any, max_artifacts: int = 24) -> dict:
    """Return a small, URL-addressable preview of a Comfy result.

    History/list responses must never echo arbitrary node payloads: metadata
    nodes can contain multi-megabyte base64 strings.  The only output data that
    belongs in those responses is Comfy's file descriptor contract.  This
    helper extracts that contract and groups it by node id so the web client
    can render the same ``/view`` URLs it uses on the detail page.
    """

    if not isinstance(result, Mapping) or max_artifacts <= 0:
        return {}

    body = result.get("body")
    payload = body.get("payload") if isinstance(body, Mapping) else None
    history = payload.get("history") if isinstance(payload, Mapping) else None
    outputs = history.get("outputs") if isinstance(history, Mapping) else None
    if not isinstance(outputs, Mapping):
        return {}

    preview: dict[str, dict[str, list[dict[str, str]]]] = {}
    seen: set[tuple[str, str, str, str]] = set()
    remaining = max_artifacts

    def add(
        node_id: str,
        filename: Any,
        subfolder: Any = "",
        storage_type: Any = "output",
    ) -> None:
        nonlocal remaining
        if remaining <= 0 or not isinstance(filename, str):
            return
        filename = filename.strip()
        if (
            not filename
            or len(filename) > 1024
            or any(ord(character) < 32 for character in filename)
            or ":" in filename
            or "/" in filename
            or "\\" in filename
            or filename in {".", ".."}
        ):
            return

        # Comfy emits native separators in history descriptors. Normalize the
        # Windows form before applying the same relative-path checks used for
        # browser-facing ``/view`` URLs.
        subfolder = str(subfolder or "").replace("\\", "/")
        storage_type = str(storage_type or "output")
        subfolder_parts = subfolder.split("/") if subfolder else []
        if (
            len(subfolder) > 1024
            or any(ord(character) < 32 for character in subfolder)
            or subfolder.startswith("/")
            or any(
                part in {"", ".", ".."} or ":" in part
                for part in subfolder_parts
            )
            or len(storage_type) > 32
            or storage_type not in {"input", "output", "temp"}
        ):
            return
        key = (node_id, filename, subfolder, storage_type)
        if key in seen:
            return
        seen.add(key)

        descriptor = {
            "filename": filename,
            "subfolder": subfolder,
            "type": storage_type,
            "url": f"/view?{urlencode({'filename': filename, 'subfolder': subfolder, 'type': storage_type})}",
        }
        media_type = media_type_for_filename(filename) or ""
        if media_type.startswith("audio/"):
            bucket = "audios"
        elif media_type.startswith("model/") or filename.lower().endswith(
            (".ply", ".splat", ".spz", ".ksplat")
        ):
            bucket = "3d"
        else:
            # Comfy video savers historically publish their descriptors in the
            # image bucket, and the browser renderer already distinguishes the
            # concrete media type or extension.
            bucket = "images"
        preview.setdefault(node_id, {}).setdefault(bucket, []).append(descriptor)
        remaining -= 1

    def add_lf_file_names(node_id: str, value: Mapping[str, Any]) -> None:
        """Project LF's portable output-relative paths into Comfy descriptors."""

        lf_output = value.get("lf_output")
        if not isinstance(lf_output, Sequence) or isinstance(
            lf_output, (str, bytes, bytearray)
        ):
            return
        for output in lf_output:
            if remaining <= 0:
                return
            if not isinstance(output, Mapping):
                continue
            file_names = output.get("file_names")
            if not isinstance(file_names, Sequence) or isinstance(
                file_names, (str, bytes, bytearray)
            ):
                continue
            for relative_name in file_names:
                if remaining <= 0:
                    return
                if (
                    not isinstance(relative_name, str)
                    or not relative_name
                    or len(relative_name) > 1024
                    or "\\" in relative_name
                    or relative_name.startswith("/")
                    or any(ord(character) < 32 for character in relative_name)
                ):
                    continue
                parts = relative_name.split("/")
                if any(part in {"", ".", ".."} or ":" in part for part in parts):
                    continue
                add(node_id, parts[-1], "/".join(parts[:-1]), "output")

    def add_view_url(node_id: str, value: Any) -> None:
        if not isinstance(value, str) or len(value) > 4096 or not value.startswith("/view?"):
            return
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or parsed.path != "/view":
            return
        query = parse_qs(parsed.query, keep_blank_values=True)
        filename = (query.get("filename") or [None])[0]
        if not isinstance(filename, str) or not filename:
            return
        add(
            node_id,
            filename,
            (query.get("subfolder") or [""])[0],
            (query.get("type") or ["output"])[0],
        )

    def walk(node_id: str, value: Any) -> None:
        if remaining <= 0:
            return
        if isinstance(value, Mapping):
            add_lf_file_names(node_id, value)
            if isinstance(value.get("filename"), str):
                add(
                    node_id,
                    value.get("filename"),
                    value.get("subfolder", ""),
                    value.get("type", "output"),
                )
            for key, item in value.items():
                if key in {"url", "value", "lfValue"}:
                    add_view_url(node_id, item)
                walk(node_id, item)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for item in value:
                walk(node_id, item)

    for raw_node_id, node_output in outputs.items():
        walk(str(raw_node_id), node_output)
        if remaining <= 0:
            break

    return preview


def serialize_job(
    job: Any,
    include_result_for_terminal: bool = False,
    *,
    summary_only: bool = False,
    include_output_preview: bool = False,
) -> dict:
    """Serialize a Job-like object into the JSON-friendly dict used by APIs and SSE.

    Accepts either the in-memory `Job` dataclass, adapter record objects from
    persistence layers, or simple dict-like objects.
    """
    try:
        def read(name: str, default: Any = None) -> Any:
            if isinstance(job, Mapping):
                return job.get(name, default)
            return getattr(job, name, default)

        if isinstance(job, Mapping):
            run_id = read("run_id") or read("id")
        else:
            run_id = read("id") or read("run_id")
        workflow_id = read("workflow_id")
        status_raw = read("status")
        if hasattr(status_raw, "value"):
            status = status_raw.value
        else:
            status = str(status_raw) if status_raw is not None else None

        created_at = read("created_at")
        updated_at = read("updated_at")
        error = read("error")
        result = read("result")
        owner_id = read("owner_id")
        submission_id = read("submission_id")
        seq = read("seq", 0) or 0

        output_preview = build_output_preview(result) if include_output_preview else None

        terminal_statuses = {"succeeded", "failed", "cancelled", "timeout"}
        if not include_result_for_terminal and (status not in terminal_statuses):
            result = None
        if summary_only:
            result = None

        # Only build id if run_id exists
        job_id = f"{run_id}:{seq}" if run_id else None

        serialized = {
            "id": job_id,
            "run_id": run_id,
            "workflow_id": workflow_id,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at,
            "error": error,
            "result": result,
            "owner_id": owner_id,
            "submission_id": submission_id,
            "seq": seq,
        }
        if include_output_preview:
            serialized["outputs"] = output_preview or {}
        return serialized
    except Exception:
        LOG.exception("serialize_job: failed to serialize job")
        return {}
# endregion


def serialize_run_summary(job: Any) -> dict:
    """Serialize the exact bounded contract used by history cards and SSE."""

    summary = serialize_job(
        job,
        summary_only=True,
        include_output_preview=True,
    )
    error = summary.get("error")
    if isinstance(error, str) and len(error) > 4096:
        error = f"{error[:4093]}..."
    return {
        "id": summary.get("id"),
        "run_id": summary.get("run_id"),
        "workflow_id": summary.get("workflow_id"),
        "status": summary.get("status"),
        "seq": summary.get("seq"),
        "owner_id": summary.get("owner_id"),
        "submission_id": summary.get("submission_id"),
        "created_at": summary.get("created_at"),
        "updated_at": summary.get("updated_at"),
        "outputs": summary.get("outputs") or {},
        "error": error,
    }


__all__ = ["build_output_preview", "serialize_job", "serialize_run_summary"]
