"""Conservative cleanup for Workflow Runner history whose files are gone.

The cleanup deliberately operates on Runner records only.  It never deletes
Comfy history or artifact files, and successful records without a complete,
safe local-artifact description remain untouched.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, NamedTuple

from . import job_store
from .background import fetch_active_prompt_ids
from .job_contracts import job_status_value as _status_value
from .lifecycle import build_output_manifest


_FAILED_TERMINAL_STATUSES = {"failed", "cancelled", "timeout"}
_ACTIVE_STATUSES = {"pending", "running"}
_STANDARD_ARTIFACT_BUCKETS = {
    "3d",
    "audio",
    "audios",
    "files",
    "gifs",
    "images",
    "video",
    "videos",
}


class _CleanupCandidate(NamedTuple):
    run_id: str
    owner_id: str | None
    status: str
    seq: int
    updated_at: float | None
    result: Any = None


ArtifactState = Literal["exists", "missing", "unknown"]
SucceededState = Literal["resolvable", "missing", "unknown"]


def _valid_filename(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and len(value) <= 1024
        and not any(ord(character) < 32 for character in value)
        and ":" not in value
        and "/" not in value
        and "\\" not in value
        and value not in {".", ".."}
    )


def _valid_subfolder(value: Any) -> bool:
    normalized = str(value or "").replace("\\", "/")
    parts = normalized.split("/") if normalized else []
    return (
        len(normalized) <= 1024
        and not any(ord(character) < 32 for character in normalized)
        and not normalized.startswith("/")
        and not any(part in {"", ".", ".."} or ":" in part for part in parts)
    )


def _valid_legacy_file_name(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 1024
        or "\x00" in value
        or "\\" in value
        or value.startswith("/")
    ):
        return False
    parts = value.split("/")
    return not any(part in {"", ".", ".."} or ":" in part for part in parts)


def _inspect_artifact_descriptors(
    outputs: Any,
) -> tuple[set[tuple[str, str, str]], bool]:
    """Return explicit file descriptors plus an ambiguity flag.

    A generic node may legitimately return JSON containing a ``filename``
    field.  It becomes a Comfy file descriptor only inside a standard artifact
    bucket or when accompanied by descriptor fields (``type``/``subfolder``).
    This prevents metadata from becoming evidence that a successful run is
    stale.
    """

    if not isinstance(outputs, Mapping):
        return set(), True

    remaining = 20_000
    descriptors: set[tuple[str, str, str]] = set()

    def walk(value: Any, depth: int = 0, parent_key: str = "") -> bool:
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > 32:
            return True
        if isinstance(value, Mapping):
            if "filename" in value and (
                parent_key in _STANDARD_ARTIFACT_BUCKETS
                or "type" in value
                or "subfolder" in value
            ):
                filename = value.get("filename")
                subfolder = str(value.get("subfolder") or "").replace("\\", "/")
                storage_type = str(value.get("type") or "output")
                if not (
                    _valid_filename(filename)
                    and _valid_subfolder(subfolder)
                    and storage_type in {"input", "output", "temp"}
                ):
                    return True
                descriptors.add((filename, subfolder, storage_type))

            if "lf_output" in value:
                lf_output = value.get("lf_output")
                if not isinstance(lf_output, (list, tuple)):
                    return True
                for item in lf_output:
                    if not isinstance(item, Mapping):
                        return True
                    if "file_names" not in item:
                        continue
                    file_names = item.get("file_names")
                    if not isinstance(file_names, (list, tuple)):
                        return True
                    if any(not _valid_legacy_file_name(name) for name in file_names):
                        return True
                    for file_name in file_names:
                        parts = file_name.split("/")
                        descriptors.add(
                            (parts[-1], "/".join(parts[:-1]), "output")
                        )

            return any(
                walk(child, depth + 1, str(key))
                for key, child in value.items()
            )
        if isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            return any(walk(child, depth + 1, parent_key) for child in value)
        return False

    return descriptors, walk(outputs)


def _artifact_roots() -> dict[str, Path | None]:
    """Resolve each Comfy storage root independently.

    A broken or permission-denied root makes artifacts in only that storage
    class unknown; it must never turn them into deletion candidates.
    """

    import folder_paths

    getters = {
        "input": folder_paths.get_input_directory,
        "output": folder_paths.get_output_directory,
        "temp": folder_paths.get_temp_directory,
    }
    roots: dict[str, Path | None] = {}
    for storage_type, getter in getters.items():
        try:
            raw_root = getter()
            if not isinstance(raw_root, (str, os.PathLike)) or not os.fspath(raw_root):
                roots[storage_type] = None
                continue
            roots[storage_type] = Path(raw_root).expanduser().resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            roots[storage_type] = None
    return roots


def _is_contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _artifact_state(
    artifact: Mapping[str, Any],
    roots: Mapping[str, Path | None],
) -> ArtifactState:
    storage_type = artifact.get("storage_type")
    filename = artifact.get("filename")
    subfolder = artifact.get("subfolder", "")
    if (
        storage_type not in {"input", "output", "temp"}
        or not _valid_filename(filename)
        or not _valid_subfolder(subfolder)
    ):
        return "unknown"

    root = roots.get(str(storage_type))
    if root is None:
        return "unknown"
    parts = str(subfolder or "").replace("\\", "/").split("/") if subfolder else []
    candidate = root.joinpath(*parts, str(filename))
    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return "unknown"
    if not _is_contained(resolved, root):
        return "unknown"

    try:
        mode = resolved.stat().st_mode
    except (FileNotFoundError, NotADirectoryError):
        return "missing"
    except (PermissionError, OSError):
        return "unknown"
    return "exists" if stat.S_ISREG(mode) else "missing"


def classify_succeeded_result(
    run_id: str,
    result: Any,
    *,
    roots: Mapping[str, Path | None] | None = None,
) -> SucceededState:
    """Classify one successful run without guessing about ambiguous records."""

    body = result.get("body") if isinstance(result, Mapping) else None
    payload = body.get("payload") if isinstance(body, Mapping) else None
    history = payload.get("history") if isinstance(payload, Mapping) else None
    outputs = history.get("outputs") if isinstance(history, Mapping) else None
    descriptors, malformed = _inspect_artifact_descriptors(outputs)
    if malformed:
        return "unknown"

    manifest = build_output_manifest("history-cleanup", run_id, result)
    if manifest.get("manifest_truncated"):
        return "unknown"
    manifest_artifacts = manifest.get("artifacts")
    if not isinstance(manifest_artifacts, list):
        return "unknown"
    artifacts = [
        artifact
        for artifact in manifest_artifacts
        if isinstance(artifact, Mapping)
        and (
            artifact.get("filename"),
            artifact.get("subfolder", ""),
            artifact.get("storage_type"),
        )
        in descriptors
    ]
    if not artifacts:
        return "unknown"

    try:
        resolved_roots = dict(roots) if roots is not None else _artifact_roots()
    except Exception:
        return "unknown"

    states = [
        _artifact_state(artifact, resolved_roots)
        if isinstance(artifact, Mapping)
        else "unknown"
        for artifact in artifacts
    ]
    if "exists" in states:
        return "resolvable"
    if "unknown" in states:
        return "unknown"
    return "missing"


async def prune_missing_artifacts(
    *,
    owner_id: str | None,
    dry_run: bool,
    candidate_run_ids: Sequence[str] | None,
) -> dict[str, Any]:
    """Scan owner-visible history and optionally remove previewed rows by CAS.

    A destructive call is deliberately bounded to ``candidate_run_ids`` from a
    preceding dry run. Re-scanning still proves each selected row remains
    eligible, but a different row that became eligible in the meantime is
    never swept into the confirmed operation.
    """

    jobs = await job_store.list_jobs(owner_id=owner_id, status=None)
    requested_run_ids = None if dry_run else set(candidate_run_ids or ())
    candidates: list[_CleanupCandidate] = []
    skipped_unknown = 0
    try:
        roots = _artifact_roots()
    except Exception:
        roots = {"input": None, "output": None, "temp": None}

    for run_id, job in jobs.items():
        run_id = str(run_id)
        is_selected = requested_run_ids is None or run_id in requested_run_ids
        status = _status_value(job)
        if status in _ACTIVE_STATUSES:
            continue
        if status in _FAILED_TERMINAL_STATUSES:
            if is_selected:
                candidates.append(
                    _CleanupCandidate(
                        run_id=run_id,
                        owner_id=getattr(job, "owner_id", None),
                        status=status,
                        seq=int(getattr(job, "seq", 0) or 0),
                        updated_at=getattr(job, "updated_at", None),
                        result=getattr(job, "result", None),
                    )
                )
            continue
        if status != "succeeded":
            continue

        state = classify_succeeded_result(
            run_id,
            getattr(job, "result", None),
            roots=roots,
        )
        if state == "missing" and is_selected:
            candidates.append(
                _CleanupCandidate(
                    run_id=run_id,
                    owner_id=getattr(job, "owner_id", None),
                    status=status,
                    seq=int(getattr(job, "seq", 0) or 0),
                    updated_at=getattr(job, "updated_at", None),
                    result=getattr(job, "result", None),
                )
            )
        elif state == "unknown":
            skipped_unknown += 1

    candidates.sort(key=lambda candidate: candidate.run_id)
    removed_run_ids: list[str] = []
    skipped_changed = 0
    if not dry_run and candidates:
        # This snapshot is intentionally taken after the history scan. It
        # catches a prompt that became pending/running during the scan, while
        # the row CAS below catches local status/result changes.
        try:
            active_prompt_ids = await fetch_active_prompt_ids()
        except Exception:
            active_prompt_ids = None
        if active_prompt_ids is None:
            # Queue failure or malformed queue data is not proof of absence.
            # Preserve every candidate at the destructive boundary.
            active_prompt_ids = {candidate.run_id for candidate in candidates}

        for candidate in candidates:
            if candidate.run_id in active_prompt_ids:
                skipped_changed += 1
                continue
            # The row CAS below protects against history changes. Re-stat a
            # successful run's files at the destructive boundary as well, so
            # an artifact restored after the scan keeps its history record.
            if candidate.status == "succeeded" and classify_succeeded_result(
                candidate.run_id,
                candidate.result,
                roots=roots,
            ) != "missing":
                skipped_changed += 1
                continue
            removed = await job_store.hard_delete_job_if_unchanged(
                candidate.run_id,
                owner_id=candidate.owner_id,
                status=candidate.status,
                seq=candidate.seq,
                updated_at=candidate.updated_at,
            )
            if removed:
                removed_run_ids.append(candidate.run_id)
            else:
                skipped_changed += 1

    return {
        "dry_run": dry_run,
        "candidate_count": len(candidates),
        "candidate_run_ids": [candidate.run_id for candidate in candidates],
        "removed_count": len(removed_run_ids),
        "removed_run_ids": removed_run_ids,
        "skipped_unknown": skipped_unknown,
        "skipped_changed": skipped_changed,
    }


__all__ = ["classify_succeeded_result", "prune_missing_artifacts"]
