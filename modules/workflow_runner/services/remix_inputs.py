"""Safe, owner-bound upload reuse for Workflow Runner remixes.

Job snapshots keep server-side upload paths so a later run can reuse the exact
bytes. Browser-facing detail responses receive opaque references instead; the
browser never learns or resubmits a host filesystem path.
"""

from __future__ import annotations

import os
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from .input_snapshot import sanitize_input_snapshot


UPLOAD_REFERENCE_SCHEMA = "lf.workflow-upload-ref.v1"
UPLOAD_PREFILL_SCHEMA = "lf.workflow-upload-prefill.v1"
ARTIFACT_REFERENCE_SCHEMA = "lf.workflow-artifact-ref.v1"
ARTIFACT_DESCRIPTOR_SCHEMA = "lf.workflow-artifact.v1"
_MAX_UPLOADS_PER_INPUT = 64
_MAX_NAME_CHARS = 255
_REDACTED_PATH = "[omitted: server file reference]"
_ARTIFACT_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class UploadRemixReferenceError(ValueError):
    """A retained upload cannot safely be materialized for a new run."""

    def __init__(self, input_name: str, *, malformed: bool = False) -> None:
        self.input_name = input_name
        self.error_code = (
            "invalid_upload_reference" if malformed else "upload_reference_unavailable"
        )
        message = (
            "The retained upload reference is invalid. Choose the file again."
            if malformed
            else "The retained upload is no longer available. Choose the file again."
        )
        super().__init__(message)


class OutputArtifactReferenceError(UploadRemixReferenceError):
    """A prior run artifact cannot safely feed a workflow upload input."""

    def __init__(
        self,
        input_name: str,
        *,
        malformed: bool = False,
        incompatible: bool = False,
    ) -> None:
        self.input_name = input_name
        if malformed:
            self.error_code = "invalid_artifact_reference"
            message = "The output reference is invalid. Choose a file instead."
        elif incompatible:
            self.error_code = "artifact_media_incompatible"
            message = "That output type is not accepted by this input."
        else:
            self.error_code = "artifact_reference_unavailable"
            message = "That output is no longer available. Choose a file instead."
        ValueError.__init__(self, message)


def _upload_input_ids(workflow_id: str) -> set[str] | None:
    """Return declared upload field ids, or ``None`` when the workflow is gone."""

    try:
        from .registry import get_workflow

        definition = get_workflow(workflow_id)
        if definition is None:
            return None
        return {
            str(cell.id)
            for cell in getattr(definition, "inputs", ())
            if getattr(cell, "shape", None) == "upload" and getattr(cell, "id", None)
        }
    except Exception:
        return None


def _upload_input_accept(workflow_id: str, input_id: str) -> str | None:
    """Return a declared HTML accept rule for one upload input, when present."""

    try:
        from .registry import get_workflow

        definition = get_workflow(workflow_id)
        if definition is None:
            return None
        for cell in getattr(definition, "inputs", ()):
            if getattr(cell, "id", None) != input_id or getattr(cell, "shape", None) != "upload":
                continue
            props = getattr(cell, "props", None)
            html = props.get("lfHtmlAttributes") if isinstance(props, Mapping) else None
            accept = html.get("accept") if isinstance(html, Mapping) else None
            return accept.strip() if isinstance(accept, str) and accept.strip() else ""
    except Exception:
        return None
    return None


def _stored_upload_paths(value: Any) -> list[str] | None:
    if isinstance(value, str):
        candidates: Sequence[Any] = (value,)
    elif isinstance(value, (list, tuple)):
        candidates = value
    else:
        return None
    if not candidates or len(candidates) > _MAX_UPLOADS_PER_INPUT:
        return None
    paths: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate.strip():
            return None
        paths.append(candidate.strip())
    return paths


def _allowed_comfy_roots() -> tuple[Path, ...]:
    import folder_paths

    roots = (
        folder_paths.get_input_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_output_directory(),
    )
    return tuple(
        Path(root).expanduser().resolve(strict=False)
        for root in roots
        if isinstance(root, (str, os.PathLike)) and os.fspath(root)
    )


def _contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _available_upload_paths(value: Any) -> list[str] | None:
    candidates = _stored_upload_paths(value)
    if candidates is None:
        return None
    try:
        roots = _allowed_comfy_roots()
    except Exception:
        return None
    if not roots:
        return None

    resolved: list[str] = []
    for candidate in candidates:
        candidate_path = Path(candidate).expanduser()
        # ``PureWindowsPath`` catches drive/UNC paths even in cross-platform
        # contract tests; the native Path is still required for real lookup.
        if not (candidate_path.is_absolute() or PureWindowsPath(candidate).is_absolute()):
            return None
        try:
            real_path = candidate_path.resolve(strict=True)
        except (OSError, RuntimeError):
            return None
        if not real_path.is_file() or not any(_contained(real_path, root) for root in roots):
            return None
        resolved.append(str(real_path))
    return resolved


def _artifact_path(artifact: Mapping[str, Any]) -> Path | None:
    """Resolve one validated manifest artifact below its declared Comfy root."""

    storage_type = artifact.get("storage_type")
    filename = artifact.get("filename")
    subfolder = artifact.get("subfolder", "")
    if storage_type not in {"input", "output", "temp"} or not isinstance(filename, str):
        return None
    if not filename or any(character in filename for character in ("/", "\\", "\x00")):
        return None
    if not isinstance(subfolder, str):
        return None
    normalized_subfolder = subfolder.replace("\\", "/")
    parts = normalized_subfolder.split("/") if normalized_subfolder else []
    if normalized_subfolder.startswith("/") or any(
        part in {"", ".", ".."} or ":" in part for part in parts
    ):
        return None

    try:
        import folder_paths

        root_value = {
            "input": folder_paths.get_input_directory,
            "output": folder_paths.get_output_directory,
            "temp": folder_paths.get_temp_directory,
        }[str(storage_type)]()
        root = Path(root_value).expanduser().resolve(strict=False)
        candidate = root.joinpath(*parts, filename).resolve(strict=True)
    except (KeyError, OSError, RuntimeError, TypeError, ValueError):
        return None
    if not candidate.is_file() or not _contained(candidate, root):
        return None
    return candidate


def _accepts_artifact(accept: str | None, artifact: Mapping[str, Any]) -> bool:
    """Apply the small HTML ``accept`` subset used by Runner upload cells."""

    if accept in {None, ""}:
        return True
    filename = str(artifact.get("filename") or "").lower()
    media_type = str(artifact.get("media_type") or "").lower()
    for raw_rule in accept.split(","):
        rule = raw_rule.strip().lower()
        if not rule:
            continue
        if rule.startswith(".") and filename.endswith(rule):
            return True
        if rule.endswith("/*") and media_type.startswith(rule[:-1]):
            return True
        if media_type and rule == media_type:
            return True
    return False


def _basename(value: str) -> str:
    normalized = value.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1].strip()
    return (name or "previous upload")[:_MAX_NAME_CHARS]


def _reference(run_id: str, input_id: str) -> dict[str, str]:
    return {
        "schema": UPLOAD_REFERENCE_SCHEMA,
        "sourceRunId": run_id,
        "inputId": input_id,
    }


def _prefill(run_id: str, input_id: str, value: Any) -> dict[str, Any] | None:
    paths = _stored_upload_paths(value)
    if paths is None:
        return None
    return {
        "schema": UPLOAD_PREFILL_SCHEMA,
        "reference": _reference(run_id, input_id),
        "names": [_basename(path) for path in paths],
        "available": _available_upload_paths(paths) is not None,
    }


def _stored_artifact_prefill(value: Any, input_id: str) -> dict[str, Any] | None:
    """Re-project lineage retained in a downstream run's private snapshot."""

    if not isinstance(value, Mapping) or value.get("schema") != UPLOAD_PREFILL_SCHEMA:
        return None
    if set(value) != {"schema", "reference", "names", "available"}:
        return None
    reference = value.get("reference")
    try:
        parsed = _parse_artifact_reference(reference, input_id)
    except OutputArtifactReferenceError:
        return None
    names = value.get("names")
    if (
        parsed is None
        or not isinstance(names, list)
        or not names
        or len(names) > _MAX_UPLOADS_PER_INPUT
        or any(
            not isinstance(name, str)
            or not name.strip()
            or len(name) > _MAX_NAME_CHARS
            for name in names
        )
    ):
        return None
    return {
        "schema": UPLOAD_PREFILL_SCHEMA,
        "reference": dict(reference),
        "names": [name.strip() for name in names],
        # Availability can change after this status response. Queue-time
        # resolution remains authoritative and fails closed.
        "available": bool(value.get("available")),
    }


def _looks_like_absolute_path(value: str) -> bool:
    try:
        return Path(value).expanduser().is_absolute() or PureWindowsPath(value).is_absolute()
    except (OSError, ValueError):
        return False


def _redact_unknown_paths(value: Any) -> Any:
    if isinstance(value, str):
        return _REDACTED_PATH if _looks_like_absolute_path(value) else value
    if isinstance(value, Mapping):
        return {str(key): _redact_unknown_paths(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_unknown_paths(child) for child in value]
    return value


def project_public_remix_inputs(
    run_id: str,
    workflow_id: str,
    inputs: Any,
) -> dict[str, Any]:
    """Project a private job snapshot into browser-safe remix controls."""

    if not isinstance(inputs, Mapping):
        return {}
    upload_ids = _upload_input_ids(workflow_id)
    if upload_ids is None:
        # A retired workflow cannot be remixed. Preserve harmless scalar context
        # for old history while never falling back to a raw absolute path.
        return sanitize_input_snapshot(_redact_unknown_paths(inputs))

    projected: dict[str, Any] = {}
    for raw_key, value in inputs.items():
        input_id = str(raw_key)
        if input_id in upload_ids:
            retained_artifact = _stored_artifact_prefill(value, input_id)
            if retained_artifact is not None:
                projected[input_id] = retained_artifact
                continue
            descriptor = _prefill(run_id, input_id, value)
            if descriptor is not None:
                projected[input_id] = descriptor
            continue
        # Job snapshots may outlive a workflow-schema change. A field that is
        # no longer declared as an upload must never fall back to exposing the
        # old server path merely because the current registry cannot classify
        # it as one.
        projected[input_id] = _redact_unknown_paths(value)
    return sanitize_input_snapshot(projected)


def _parse_reference(value: Any, input_name: str) -> tuple[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    schema = value.get("schema")
    if schema not in {UPLOAD_REFERENCE_SCHEMA, UPLOAD_PREFILL_SCHEMA}:
        return None
    if schema != UPLOAD_REFERENCE_SCHEMA or set(value) != {
        "schema",
        "sourceRunId",
        "inputId",
    }:
        raise UploadRemixReferenceError(input_name, malformed=True)
    source_run_id = value.get("sourceRunId")
    source_input_id = value.get("inputId")
    if (
        not isinstance(source_run_id, str)
        or not source_run_id
        or len(source_run_id) > 256
        or not isinstance(source_input_id, str)
        or not source_input_id
        or len(source_input_id) > 256
    ):
        raise UploadRemixReferenceError(input_name, malformed=True)
    return source_run_id, source_input_id


def _artifact_id(artifact: Mapping[str, Any]) -> str:
    """Return a stable opaque identity for one canonical manifest artifact."""

    authority = {
        "node_id": str(artifact.get("node_id") or ""),
        "filename": str(artifact.get("filename") or ""),
        "subfolder": str(artifact.get("subfolder") or "").replace("\\", "/"),
        "storage_type": str(artifact.get("storage_type") or ""),
    }
    encoded = json.dumps(
        authority,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_artifact_reference(value: Any, input_name: str) -> tuple[str, str, str] | None:
    if not isinstance(value, Mapping) or value.get("schema") != ARTIFACT_REFERENCE_SCHEMA:
        return None
    if set(value) != {"schema", "sourceRunId", "artifactId", "filename"}:
        raise OutputArtifactReferenceError(input_name, malformed=True)
    source_run_id = value.get("sourceRunId")
    artifact_id = value.get("artifactId")
    filename = value.get("filename")
    if (
        not isinstance(source_run_id, str)
        or not source_run_id
        or len(source_run_id) > 256
        or not isinstance(artifact_id, str)
        or not _ARTIFACT_ID_PATTERN.fullmatch(artifact_id)
        or not isinstance(filename, str)
        or not filename
        or len(filename) > _MAX_NAME_CHARS
        or any(character in filename for character in ("/", "\\", "\x00"))
    ):
        raise OutputArtifactReferenceError(input_name, malformed=True)
    return source_run_id, artifact_id, filename


def _artifact_manifest(run_id: str, result: Any) -> list[Mapping[str, Any]]:
    from .lifecycle import build_output_manifest

    manifest = build_output_manifest("artifact-handoff", run_id, result)
    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
    if not isinstance(artifacts, list):
        return []
    return [artifact for artifact in artifacts if isinstance(artifact, Mapping)]


def project_public_output_artifacts(run_id: str, result: Any) -> list[dict[str, Any]]:
    """Expose bounded artifact metadata and opaque handoff authority for one run."""

    projected: list[dict[str, Any]] = []
    for artifact in _artifact_manifest(run_id, result):
        filename = artifact.get("filename")
        if not isinstance(filename, str) or not filename:
            continue
        item: dict[str, Any] = {
            "schema": ARTIFACT_DESCRIPTOR_SCHEMA,
            "reference": {
                "schema": ARTIFACT_REFERENCE_SCHEMA,
                "sourceRunId": run_id,
                "artifactId": _artifact_id(artifact),
                "filename": filename[:_MAX_NAME_CHARS],
            },
            "filename": filename[:_MAX_NAME_CHARS],
            "nodeId": str(artifact.get("node_id") or "")[:128],
            "available": _artifact_path(artifact) is not None,
        }
        media_type = artifact.get("media_type")
        if isinstance(media_type, str) and media_type:
            item["mediaType"] = media_type[:128]
        projected.append(item)
    return projected


async def materialize_upload_references(
    payload: Mapping[str, Any],
    owner_id: str | None,
) -> dict[str, Any]:
    """Resolve opaque upload references after lifecycle reservation, before queueing."""

    raw_inputs = payload.get("inputs", {})
    if not isinstance(raw_inputs, Mapping):
        return dict(payload)
    if not any(
        isinstance(value, Mapping)
        and value.get("schema")
        in {UPLOAD_REFERENCE_SCHEMA, UPLOAD_PREFILL_SCHEMA, ARTIFACT_REFERENCE_SCHEMA}
        for value in raw_inputs.values()
    ):
        return dict(payload)

    workflow_id = str(payload.get("workflowId") or "")
    upload_ids = _upload_input_ids(workflow_id)
    if upload_ids is None:
        first_input = next(iter(raw_inputs), "inputs")
        raise UploadRemixReferenceError(str(first_input), malformed=True)

    from .job_store import get_job

    effective_inputs = dict(raw_inputs)
    source_cache: dict[str, Any] = {}
    for raw_input_id, value in raw_inputs.items():
        input_id = str(raw_input_id)
        artifact_reference = _parse_artifact_reference(value, input_id)
        if artifact_reference is not None:
            if input_id not in upload_ids:
                raise OutputArtifactReferenceError(input_id, malformed=True)
            source_run_id, artifact_id, reference_filename = artifact_reference
            if source_run_id not in source_cache:
                source_cache[source_run_id] = await get_job(source_run_id)
            source = source_cache[source_run_id]
            source_status = getattr(source, "status", None) if source is not None else None
            if hasattr(source_status, "value"):
                source_status = source_status.value
            if (
                source is None
                or getattr(source, "owner_id", None) != owner_id
                or source_status != "succeeded"
            ):
                raise OutputArtifactReferenceError(input_id)
            artifacts = _artifact_manifest(
                source_run_id,
                getattr(source, "result", None),
            )
            artifact = next(
                (candidate for candidate in artifacts if _artifact_id(candidate) == artifact_id),
                None,
            )
            if artifact is None:
                raise OutputArtifactReferenceError(input_id)
            if artifact.get("filename") != reference_filename:
                raise OutputArtifactReferenceError(input_id, malformed=True)
            if not _accepts_artifact(
                _upload_input_accept(workflow_id, input_id), artifact
            ):
                raise OutputArtifactReferenceError(input_id, incompatible=True)
            artifact_path = _artifact_path(artifact)
            if artifact_path is None:
                raise OutputArtifactReferenceError(input_id)
            effective_inputs[input_id] = str(artifact_path)
            continue

        parsed = _parse_reference(value, input_id)
        if parsed is None:
            continue
        if input_id not in upload_ids:
            raise UploadRemixReferenceError(input_id, malformed=True)
        source_run_id, source_input_id = parsed
        if source_input_id != input_id:
            raise UploadRemixReferenceError(input_id, malformed=True)

        if source_run_id not in source_cache:
            source_cache[source_run_id] = await get_job(source_run_id)
        source = source_cache[source_run_id]
        if (
            source is None
            or getattr(source, "owner_id", None) != owner_id
            or str(getattr(source, "workflow_id", "")) != workflow_id
        ):
            raise UploadRemixReferenceError(input_id)
        source_inputs = getattr(source, "inputs", None)
        if not isinstance(source_inputs, Mapping) or source_input_id not in source_inputs:
            raise UploadRemixReferenceError(input_id)
        resolved_paths = _available_upload_paths(source_inputs[source_input_id])
        if resolved_paths is None:
            raise UploadRemixReferenceError(input_id)
        effective_inputs[input_id] = (
            resolved_paths[0]
            if isinstance(source_inputs[source_input_id], str)
            else resolved_paths
        )

    effective_payload = dict(payload)
    effective_payload["inputs"] = effective_inputs
    return effective_payload


def build_durable_input_snapshot(
    submitted_payload: Mapping[str, Any],
    effective_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Keep execution paths private while retaining cross-workflow lineage."""

    submitted_inputs = submitted_payload.get("inputs")
    effective_inputs = effective_payload.get("inputs")
    if not isinstance(effective_inputs, Mapping):
        return {}
    snapshot = dict(effective_inputs)

    # Fresh Runner uploads arrive as portable ``name [input]`` references so
    # the browser never receives Comfy's host path. Resolve only declared
    # upload fields back to private absolute paths at the persistence boundary;
    # public remix projection will expose owner-bound opaque references again.
    workflow_id = str(submitted_payload.get("workflowId") or "")
    upload_ids = _upload_input_ids(workflow_id) or set()
    if upload_ids:
        from ..workflows.utils import resolve_upload_paths

        for input_id in upload_ids:
            value = effective_inputs.get(input_id)
            if value is None:
                continue
            try:
                resolved = resolve_upload_paths(
                    {input_id: value},
                    input_id,
                    allow_multiple=True,
                    must_exist=True,
                )
            except (FileNotFoundError, OSError, TypeError, ValueError):
                # Preparation already validated the execution value. If the
                # file disappears in the small post-queue window, preserve the
                # original snapshot; its later remix projection fails closed.
                continue
            snapshot[input_id] = resolved[0] if isinstance(value, str) else resolved

    if not isinstance(submitted_inputs, Mapping):
        return snapshot
    for raw_input_id, value in submitted_inputs.items():
        input_id = str(raw_input_id)
        try:
            parsed = _parse_artifact_reference(value, input_id)
        except OutputArtifactReferenceError:
            continue
        if parsed is None:
            continue
        _, _, filename = parsed
        snapshot[input_id] = {
            "schema": UPLOAD_PREFILL_SCHEMA,
            "reference": dict(value),
            "names": [filename],
            "available": True,
        }
    return snapshot


__all__ = [
    "ARTIFACT_DESCRIPTOR_SCHEMA",
    "ARTIFACT_REFERENCE_SCHEMA",
    "UPLOAD_PREFILL_SCHEMA",
    "UPLOAD_REFERENCE_SCHEMA",
    "OutputArtifactReferenceError",
    "UploadRemixReferenceError",
    "build_durable_input_snapshot",
    "materialize_upload_references",
    "project_public_output_artifacts",
    "project_public_remix_inputs",
]
