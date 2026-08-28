from __future__ import annotations

import os
import threading
import weakref
from contextlib import contextmanager
from typing import Iterator


_LOCKS_GUARD = threading.Lock()
_LOCKS: weakref.WeakValueDictionary[str, threading.RLock] = weakref.WeakValueDictionary()


@contextmanager
def edit_dataset_lock(file_path: str) -> Iterator[None]:
    """Serialize updates and cleanup for one editing-session file."""
    key = os.path.normcase(os.path.realpath(os.path.abspath(file_path)))
    with _LOCKS_GUARD:
        lock = _LOCKS.setdefault(key, threading.RLock())
    with lock:
        yield


__all__ = ["edit_dataset_lock"]
