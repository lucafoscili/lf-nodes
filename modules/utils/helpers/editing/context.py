from __future__ import annotations

import logging
import threading
from contextlib import contextmanager
from typing import Any, Dict, Iterator, Optional

_EDITING_CONTEXTS: Dict[str, Dict[str, Any]] = {}

# Editor work (a filter call) running on each context, and the contexts whose paused graph has
# resumed. ComfyUI's prompt worker resets shared model and GPU state after every node, so a model
# call left running on another thread while the graph moves on has its buffers taken from under
# it: the graph resumes only once its context's work has ended, and takes no new work after.
_WORK_CONDITION = threading.Condition()
_WORK_IN_FLIGHT: Dict[str, int] = {}
_RESUMED_CONTEXTS: set[str] = set()


class EditingContextResumedError(RuntimeError):
    """Raised when editor work asks for a context whose paused graph has already resumed."""

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
    with _WORK_CONDITION:
        if not _WORK_IN_FLIGHT.get(identifier):
            _RESUMED_CONTEXTS.discard(identifier)


@contextmanager
def editing_context_work(identifier: str) -> Iterator[None]:
    """
    Marks editor work running on a context for as long as the block runs.

    Run it on the thread doing the work: a request handler cancelled by its client's disconnect
    does not stop a thread it started.

    Raises:
        EditingContextResumedError: If the context's paused graph has already resumed.
    """
    if not identifier:
        yield
        return

    with _WORK_CONDITION:
        if identifier in _RESUMED_CONTEXTS:
            raise EditingContextResumedError(
                "The editing session already resumed its workflow; open the editor again on its next pause."
            )
        _WORK_IN_FLIGHT[identifier] = _WORK_IN_FLIGHT.get(identifier, 0) + 1
    try:
        yield
    finally:
        with _WORK_CONDITION:
            remaining = _WORK_IN_FLIGHT.get(identifier, 1) - 1
            if remaining > 0:
                _WORK_IN_FLIGHT[identifier] = remaining
            else:
                _WORK_IN_FLIGHT.pop(identifier, None)
                if identifier not in _EDITING_CONTEXTS:
                    _RESUMED_CONTEXTS.discard(identifier)
            _WORK_CONDITION.notify_all()


def resume_editing_context(identifier: str, *, poll_interval: float = 0.5) -> None:
    """
    Refuses new editor work on a context, then waits for the work in flight to end.

    Call it before a paused graph moves on, so no editor model call runs beside the nodes after it.
    """
    if not identifier:
        return

    with _WORK_CONDITION:
        _RESUMED_CONTEXTS.add(identifier)
        if _WORK_IN_FLIGHT.get(identifier):
            logging.warning(
                "[lf-nodes] Editing session %s resumes once its %d running editor call(s) end.",
                identifier,
                _WORK_IN_FLIGHT[identifier],
            )
        while _WORK_IN_FLIGHT.get(identifier):
            _WORK_CONDITION.wait(poll_interval)
