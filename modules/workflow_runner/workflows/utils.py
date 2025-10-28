from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator, List

from ..registry import InputValidationError

_CANDIDATE_KEYS = ("path", "file", "name", "value")

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