import hashlib
import os
import shutil
from typing import NamedTuple, Union

from ...constants import EXTERNAL_PREVIEW_SUBDIR
from ..logic import SAFE_EXT_FALLBACK, SAFE_FILENAME_FALLBACK, sanitize_filename
from .get_comfy_dir import get_comfy_dir

class ResolvedDirectory(NamedTuple):
    """Container describing a directory resolved against a ComfyUI base."""

    absolute_path: str | None
    relative_path: str
    is_external: bool

# region Helpers
def _sanitize_path_component(value: str) -> str | None:
    """
    Sanitize a single filesystem path component.

    Parameters:
    value : str
        The candidate path component to sanitize. Special values "", ".", and ".." are
        treated as invalid and will cause the function to return None.

    Returns:
    str | None
        A filename-safe component with any temporary extension removed, or None if the
        input is invalid or sanitization fails. The implementation appends a temporary
        extension for sanitization and strips it before returning the result.

    Notes:
    - This function expects a single path segment (no path separators) and does not
      create or access any files on disk.
    - Behavior depends on the underlying sanitize_filename implementation for how
      unsafe characters are replaced or removed.
    """
    if value in ("", ".", ".."):
        return None

    sanitized = sanitize_filename(f"{value}.tmp", default_ext="tmp")
    if sanitized is None:
        return None

    return os.path.splitext(sanitized)[0]
# endregion

# region resolve_input_directory_path
def resolve_input_directory_path(
    directory: Union[str, os.PathLike[str], None],
    *,
    base_type: str = "input",
) -> ResolvedDirectory:
    """
    Resolve a user-supplied directory string against ComfyUI's configured base directory.

    This function attempts to interpret 'directory' in a user-friendly way and returns a
    :class:`ResolvedDirectory` describing the resolved directory.

    Where:
    - absolute_path (str | None)
        The absolute filesystem path that was resolved. If the resolution fails
        (invalid component, missing path or inaccessible directory), this is None.
        When an existing directory is found, this is the absolute path to that
        directory.

    - relative_path (str)
        If the resolved_abs_path is located inside the configured base directory
        corresponding to base_type, this is the path from the base directory to the
        resolved directory using forward slashes. If the resolved directory is the
        base itself, this is an empty string. If the resolved directory is outside
        the base (or resolution failed), this is an empty string.

    - is_external (bool)
        True if an existing absolute directory was found but it is outside the
        configured base directory; False otherwise. When resolution fails or the
        result is inside the base (including the base itself), this is False.

        Behavior summary:
        - If directory is None or only whitespace: returns ``ResolvedDirectory(abs_base_dir, "", False)``.
        - If directory is an existing filesystem directory (absolute or relative):
                - If the directory is located inside the base directory, returns a
                    ``ResolvedDirectory`` with the absolute path and relative path populated.
                - If the directory exists but is outside the base, ``is_external`` is ``True``
                    and ``relative_path`` is empty.
        - If directory is a non-existing absolute path: resolution fails and the result is
            ``ResolvedDirectory(None, "", False)``.
        - If directory is a relative path, it is interpreted as a sequence of components
      under the base directory. Each component is matched against actual directory
      entries in the filesystem:
        - Exact name matches win.
        - Otherwise a sanitized comparison (e.g., case/Unicode normalization depending
          on _sanitize_path_component) is used to find a matching directory entry.
        - If any component cannot be matched or any filesystem access fails (OSError),
        resolution fails and the helper returns ``ResolvedDirectory(None, "", False)``.
    - The returned relative path uses forward slashes and uses "" for the base
      directory itself (not ".").

    Notes and edge cases:
    - This function depends on get_comfy_dir(base_type) to obtain the base directory.
    - Directory names are normalized for matching using _sanitize_path_component;
      this allows tolerant matching (for example, case-insensitive or accent-insensitive
      matches depending on that sanitizer).
        - The function never raises on normal failure modes (missing entries, permission
            errors); instead it returns ``ResolvedDirectory(None, "", False)`` for failure cases.

    Examples:
        - directory = None -> ``ResolvedDirectory(abs_base_dir, "", False)``
        - directory = "subdir/inner" -> ``ResolvedDirectory(abs_base_dir/subdir/inner, "subdir/inner", False)`` if matched
        - directory = "C:/Other/Folder" (exists outside base) -> ``ResolvedDirectory("C:/Other/Folder", "", True)``
        - directory = "/non/existent/dir" -> ``ResolvedDirectory(None, "", False)``
    """
    base_dir = get_comfy_dir(base_type)
    base_abs = os.path.abspath(base_dir)

    if directory is None:
        return ResolvedDirectory(base_abs, "", False)

    if isinstance(directory, os.PathLike):
        directory = os.fspath(directory)

    if not isinstance(directory, str):
        return ResolvedDirectory(None, "", False)

    candidate_path = directory.strip()
    if not candidate_path:
        return ResolvedDirectory(base_abs, "", False)

    abs_candidate = os.path.abspath(candidate_path)
    if os.path.isdir(abs_candidate):
        try:
            common = os.path.commonpath([base_abs, abs_candidate])
        except ValueError:
            common = None

        if common == base_abs:
            rel_path = os.path.relpath(abs_candidate, base_abs)
            rel_path = "" if rel_path == "." else rel_path.replace("\\", "/")
            return ResolvedDirectory(abs_candidate, rel_path, False)

        return ResolvedDirectory(abs_candidate, "", True)

    normalized = candidate_path.strip().strip("\\/")
    if not normalized:
        return ResolvedDirectory(base_abs, "", False)

    if os.path.isabs(normalized):
        return ResolvedDirectory(None, "", False)

    components = [part for part in normalized.replace("\\", "/").split("/") if part]
    current_dir = base_dir
    actual_components: list[str] = []

    for component in components:
        target = _sanitize_path_component(component)
        if target is None:
            return ResolvedDirectory(None, "", False)

        try:
            entries = os.listdir(current_dir)
        except OSError:
            return ResolvedDirectory(None, "", False)

        match_entry = None
        for entry in entries:
            entry_path = os.path.join(current_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry == component:
                match_entry = entry
                break
            if _sanitize_path_component(entry) == target:
                match_entry = entry
                break

        if match_entry is None:
            return ResolvedDirectory(None, "", False)

        current_dir = os.path.join(current_dir, match_entry)
        actual_components.append(match_entry)

    rel_path = "/".join(actual_components)
    return ResolvedDirectory(current_dir, rel_path, False)


def ensure_external_preview(source_dir: str, filename: str, *, base_type: str = "input") -> tuple[str, str]:
    """
    Copy a file from an external directory into a deterministic ComfyUI preview folder.

    The preview folder lives under the configured input or output directory and is keyed by a hash
    of the source directory to avoid collisions.

    Args:
        source_dir: Absolute or relative path to the external directory that contains the file.
        filename: Name of the file to copy into the preview directory.
        base_type: ComfyUI base directory type to use ("input" or "output"). Defaults to "input".

    Returns:
        tuple[str, str]: Relative preview subfolder (with forward slashes) and the sanitized filename.

    Raises:
        FileNotFoundError: If the requested file cannot be found or accessed.
    """
    source_path = os.path.join(source_dir, filename)
    base_input = get_comfy_dir(base_type)

    if not os.path.isfile(source_path):
        raise FileNotFoundError(source_path)

    digest = hashlib.sha256(os.path.abspath(source_dir).encode("utf-8")).hexdigest()[:16]
    subfolder = os.path.join(EXTERNAL_PREVIEW_SUBDIR, digest)
    target_dir = os.path.join(base_input, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    _, ext = os.path.splitext(filename)
    sanitized_name = sanitize_filename(
        filename,
        default_ext=ext.lstrip(".") or SAFE_EXT_FALLBACK,
    )
    if not sanitized_name:
        sanitized_name = f"{SAFE_FILENAME_FALLBACK}.{SAFE_EXT_FALLBACK}"

    target_path = os.path.join(target_dir, sanitized_name)

    try:
        src_mtime = os.path.getmtime(source_path)
    except OSError as exc:
        raise FileNotFoundError(source_path) from exc

    try:
        dst_mtime = os.path.getmtime(target_path)
    except OSError:
        dst_mtime = -1

    if dst_mtime < 0 or src_mtime > dst_mtime:
        shutil.copy2(source_path, target_path)

    return subfolder.replace("\\", "/"), sanitized_name
# endregion