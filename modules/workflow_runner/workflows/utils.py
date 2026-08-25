from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Iterator, List, Sequence, Tuple

from ..services.registry import InputValidationError
from ...utils.youtube_url import parse_youtube_video_url

_CANDIDATE_KEYS = ("path", "file", "name", "value")
_STAGED_IMAGE_DIRECTORY = Path("lf-workflow-runner") / "staged-images"
_SAFE_SUFFIX = re.compile(r"^\.[a-z0-9]{1,16}$")
_COMFY_PATH_ANNOTATION = re.compile(
  r"^(?P<path>.+?)\s+\[(?P<storage>input|temp|output)\]\s*$"
)
_COPY_BUFFER_BYTES = 1024 * 1024


def canonical_youtube_url(value: Any, *, field: str = "youtube_url") -> str:
  """Validate one YouTube URL and return its canonical watch URL."""
  if not isinstance(value, str):
    raise InputValidationError(field)
  try:
    _video_id, canonical_url = parse_youtube_video_url(value)
  except ValueError as error:
    raise InputValidationError(field) from error
  if not canonical_url:
    raise InputValidationError(field)
  return canonical_url


def has_input_value(inputs: dict[str, Any], name: str) -> bool:
  """Return whether a Runner input contains a non-empty scalar or collection."""
  value = inputs.get(name)
  return not (
    value is None
    or (isinstance(value, str) and not value.strip())
    or (isinstance(value, (list, tuple)) and not value)
  )


def require_input_value(inputs: dict[str, Any], name: str) -> None:
  """Require a non-empty Runner input without constraining its transport shape."""
  if not has_input_value(inputs, name):
    raise InputValidationError(name)


def required_text(inputs: dict[str, Any], name: str) -> str:
  """Return one required, trimmed text input."""
  value = inputs.get(name)
  if not isinstance(value, str) or not value.strip():
    raise InputValidationError(name)
  return value.strip()


def choice(
  inputs: dict[str, Any],
  name: str,
  default: str,
  choices: Iterable[str],
) -> str:
  """Return a string constrained to the declared workflow choices."""
  value = inputs.get(name, default)
  if not isinstance(value, str) or value not in tuple(choices):
    raise InputValidationError(name)
  return value


def integer(
  inputs: dict[str, Any],
  name: str,
  default: int,
  *,
  minimum: int,
  maximum: int,
) -> int:
  """Parse one bounded integer using the Runner's stable error contract."""
  value = inputs.get(name, default)
  if value in (None, ""):
    value = default
  if isinstance(value, bool):
    raise InputValidationError(name)
  try:
    parsed = int(str(value).strip())
  except (TypeError, ValueError) as error:
    raise InputValidationError(name) from error
  if parsed < minimum or parsed > maximum:
    raise ValueError(f"{name} must be between {minimum} and {maximum}.")
  return parsed

# region Helpers
def _flatten_upload_value(value: Any) -> Iterator[Any]:
  if value is None:
    return

  if isinstance(value, dict):
    for key in _CANDIDATE_KEYS:
      if key in value:
        yield from _flatten_upload_value(value[key])
        return
    for nested in value.values():
      yield from _flatten_upload_value(nested)
    return

  if isinstance(value, (list, tuple, set)):
    for item in value:
      yield from _flatten_upload_value(item)
    return

  if isinstance(value, str):
    parts = [segment.strip() for segment in value.split(";")]
    trimmed = [segment for segment in parts if segment]
    if len(trimmed) > 1:
      for segment in trimmed:
        yield from _flatten_upload_value(segment)
      return
    yield value.strip()
    return

  if isinstance(value, Path):
    yield str(value)
    return

  yield value
# endregion

# region Upload path resolver
def resolve_upload_paths(
  inputs: dict[str, Any],
  name: str,
  *,
  allow_multiple: bool = False,
  must_exist: bool = True,
) -> List[str]:
  """
  Resolves upload paths from the given inputs dictionary.

  This function extracts and validates paths from the 'inputs' dictionary under the specified 'name' key.
  It flattens the raw value, filters out None and empty strings, and resolves each candidate path.
  Portable Comfy references such as ``portrait.png [input]`` are resolved
  beneath their named storage root with traversal and symlink containment.
  If 'must_exist' is True, it checks that each path exists on the filesystem.
  If 'allow_multiple' is False, only the first valid path is returned.

  Args:
    inputs (dict[str, Any]): The dictionary containing input values, where the value under 'name' is expected to be a path or list of paths.
    name (str): The key in the inputs dictionary to retrieve the path value from.
    allow_multiple (bool, optional): If True, allows returning multiple resolved paths. Defaults to False.
    must_exist (bool, optional): If True, raises an error if any resolved path does not exist. Defaults to True.

  Returns:
    List[str]: A list of resolved absolute paths as strings. If 'allow_multiple' is False, the list contains at most one element.

  Raises:
    InputValidationError: If the input value is None, empty, or contains invalid types (not str or Path).
    FileNotFoundError: If 'must_exist' is True and any resolved path does not exist.
  """
  raw_value = inputs.get(name)
  if raw_value is None:
    raise InputValidationError(name)

  candidates = [candidate for candidate in _flatten_upload_value(raw_value) if candidate not in (None, "")]
  if not candidates:
    raise InputValidationError(name)

  resolved: List[str] = []
  for candidate in candidates:
    if not isinstance(candidate, (str, Path)):
      raise InputValidationError(name)

    candidate_value = str(candidate).strip()
    annotated = _COMFY_PATH_ANNOTATION.fullmatch(candidate_value)
    if annotated is not None:
      relative_value = annotated.group("path").strip().replace("\\", "/")
      relative_path = Path(relative_value)
      if (
        not relative_value
        or relative_path.is_absolute()
        or PureWindowsPath(relative_value).is_absolute()
      ):
        raise InputValidationError(name)

      storage_type = annotated.group("storage")
      roots = dict(_comfy_image_directories())
      root = roots.get(storage_type)
      if root is None:
        raise InputValidationError(name)
      resolved_root = root.expanduser().resolve(strict=False)
      resolved_path = (resolved_root / relative_path).resolve(strict=False)
      if _contained_relative_path(resolved_path, resolved_root) is None:
        raise InputValidationError(name)
    else:
      resolved_path = Path(candidate).expanduser()

    if must_exist and not resolved_path.exists():
      raise FileNotFoundError(f"Input path does not exist: {resolved_path}")

    resolved.append(str(resolved_path))
    if not allow_multiple:
      break

  if not resolved:
    raise InputValidationError(name)

  return resolved
# endregion


# region Comfy LoadImage references
def _comfy_image_directories() -> Sequence[Tuple[str, Path]]:
  """Return the filesystem roots understood by Comfy's path annotations.

  ``folder_paths`` belongs to the Comfy host, so importing it lazily keeps the
  workflow declaration layer importable in offline tooling and contract tests.
  """
  import folder_paths

  return (
    ("input", Path(folder_paths.get_input_directory())),
    ("temp", Path(folder_paths.get_temp_directory())),
    ("output", Path(folder_paths.get_output_directory())),
  )


def _contained_relative_path(path: Path, root: Path) -> Path | None:
  """Return a real, relative path when ``path`` is contained by ``root``."""
  try:
    return path.relative_to(root)
  except ValueError:
    return None


def _annotated_reference(relative_path: Path, storage_type: str) -> str:
  # Forward slashes are accepted by Comfy on every host and make graph payloads
  # portable and deterministic.
  return f"{relative_path.as_posix()} [{storage_type}]"


def _hash_file(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as source:
    while chunk := source.read(_COPY_BUFFER_BYTES):
      digest.update(chunk)
  return digest.hexdigest()


def _stage_content_addressed_image(source_path: Path, input_root: Path) -> Path:
  """Atomically stage external bytes below Comfy input and return a relative path."""
  stage_root = input_root / _STAGED_IMAGE_DIRECTORY
  stage_root.mkdir(parents=True, exist_ok=True)
  resolved_stage_root = stage_root.resolve(strict=True)
  if _contained_relative_path(resolved_stage_root, input_root) is None:
    raise ValueError("The LF staging directory escapes Comfy's input directory.")

  suffix = source_path.suffix.lower()
  if not _SAFE_SUFFIX.fullmatch(suffix):
    suffix = ".image"

  temporary_path: Path | None = None
  descriptor, temporary_name = tempfile.mkstemp(
    dir=resolved_stage_root,
    prefix=".staging-",
    suffix=".tmp",
  )
  temporary_path = Path(temporary_name)
  digest = hashlib.sha256()
  try:
    with source_path.open("rb") as source, os.fdopen(descriptor, "wb") as target:
      descriptor = -1
      while chunk := source.read(_COPY_BUFFER_BYTES):
        digest.update(chunk)
        target.write(chunk)
      target.flush()
      os.fsync(target.fileno())

    target_path = resolved_stage_root / f"sha256-{digest.hexdigest()}{suffix}"
    if target_path.exists() and _hash_file(target_path) == digest.hexdigest():
      temporary_path.unlink()
      temporary_path = None
    else:
      # The temporary file lives on the same filesystem, so replace is atomic.
      # Concurrent runners may replace the same content address with identical
      # bytes, which is harmless and still leaves no partially written target.
      os.replace(temporary_path, target_path)
      temporary_path = None

    return target_path.relative_to(input_root)
  finally:
    if descriptor != -1:
      os.close(descriptor)
    if temporary_path is not None:
      temporary_path.unlink(missing_ok=True)


def resolve_load_image_reference(
  inputs: dict[str, Any],
  name: str,
) -> str:
  """Resolve one upload/local image to a secure core ``LoadImage`` reference.

  Core Comfy nodes do not accept arbitrary absolute paths: they accept a path
  relative to the input directory, optionally annotated as ``[input]``,
  ``[temp]``, or ``[output]``. Existing files already contained by one of those
  roots are reused. An external absolute file is copied once into a
  content-addressed LF namespace under Comfy input using an atomic rename.

  Resolving real paths before containment checks prevents a symlink inside a
  Comfy directory from being used to smuggle an outside path into the graph.
  """
  resolved_paths = resolve_upload_paths(
    inputs,
    name,
    allow_multiple=True,
    must_exist=True,
  )
  if len(resolved_paths) != 1:
    # LF Upload currently permits multi-selection at the widget level. These
    # LoadImage seams are deliberately singular, so reject ambiguity instead
    # of uploading everything and silently consuming only the first file.
    raise InputValidationError(name)

  raw_path = Path(resolved_paths[0]).expanduser()
  if not raw_path.is_absolute():
    raise InputValidationError(name)

  source_path = raw_path.resolve(strict=True)
  if not source_path.is_file():
    raise ValueError(f"Input path is not a file: {source_path}")

  directories = tuple(
    (storage_type, root.expanduser().resolve(strict=False))
    for storage_type, root in _comfy_image_directories()
  )
  for storage_type, root in directories:
    relative_path = _contained_relative_path(source_path, root)
    if relative_path is not None:
      return _annotated_reference(relative_path, storage_type)

  input_root = next(
    root for storage_type, root in directories if storage_type == "input"
  )
  staged_relative_path = _stage_content_addressed_image(source_path, input_root)
  return _annotated_reference(staged_relative_path, "input")
# endregion
