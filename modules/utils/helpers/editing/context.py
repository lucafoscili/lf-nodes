from __future__ import annotations

from typing import Any, Dict, Optional

_EDITING_CONTEXTS: Dict[str, Dict[str, Any]] = {}


def register_editing_context(identifier: str, **context: Any) -> None:
    """
    Registers an editing context with the given identifier and any related values.

    Args:
        identifier (str): A unique string to identify the editing context.
        **context (Any): Arbitrary key/value pairs to associate with the context (e.g. model, sampler, prompts).

    Returns:
        None
    """
    if not identifier:
        return

    _EDITING_CONTEXTS[identifier] = context


def get_editing_context(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the editing context associated with a given identifier.

    Args:
        identifier (str): The unique identifier for the editing context.

    Returns:
        Optional[Dict[str, Any]]: The editing context dictionary if found, otherwise None.
    """
    if not identifier:
        return None

    return _EDITING_CONTEXTS.get(identifier)


def clear_editing_context(identifier: str) -> None:
    """
    Removes the editing context associated with the given identifier.

    Args:
        identifier (str): The unique identifier for the editing context to be cleared.

    Returns:
        None

    Notes:
        If the identifier is empty or None, the function does nothing.
        If the identifier does not exist in the editing contexts, no error is raised.
    """
    if not identifier:
        return

    _EDITING_CONTEXTS.pop(identifier, None)
