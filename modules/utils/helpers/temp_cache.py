from __future__ import annotations

import os
from typing import Iterable, Set

class TempFileCache:
    """Temporary file cache used to track and remove stale temp files between executions.

    This class maintains an in-memory set of filesystem paths (strings) for temporary
    files created during a node's execution. Files can be added via register() or
    extend(), and cleanup() will attempt to delete all remembered files. Paths that
    cannot be deleted due to recoverable OS errors are preserved in the cache so
    that future cleanup attempts can retry deletion.

    Behavior summary:
    - register(*paths): Add one or more file paths to the cache. Falsy values
        (None, empty string, etc.) are ignored.
    - extend(paths): Add an iterable of paths to the cache; falsy values are
        ignored.
    - cleanup(): Attempt to delete every remembered path. If os.remove succeeds
        the path is discarded. FileNotFoundError is treated as a successful delete
        and the path is discarded. For other OSError errors (e.g. permission denied,
        file locked) the path is preserved in the cache so it may be retried later.
        If the cache is empty, cleanup() is a no-op.

    Notes and limitations:
    - The cache is held in memory only; it is not persistent across process restarts.
    - The implementation is not thread-safe; if multiple threads may register or
        clean up simultaneously, external synchronization is required.
    - Paths are stored as provided (strings); callers are responsible for passing
        absolute or normalized paths if required by their application.

    Example:
            cache = TempFileCache()
            cache.register('/tmp/foo.png', '/tmp/bar.png')
            # ... use temp files ...
            cache.cleanup()  # best-effort removal of remembered temp files
    """

    def __init__(self) -> None:
        self._paths: Set[str] = set()

# region register
    def register(self, *paths: str) -> None:
        """
        Register one or more filesystem paths for later cleanup.

        Each provided non-empty path string is added to the instance's internal
        set of tracked paths (self._paths). Duplicate entries are ignored
        because a set is used. Falsy values (e.g. None or empty strings) are
        skipped.

        Args:
            *paths: One or more filesystem path strings to remember.

        Returns:
            None

        Side effects:
            Mutates self._paths so that the listed paths will be considered for
            deletion during the next cleanup operation.
        """
        for path in paths:
            if path:
                self._paths.add(path)
# endregion

# region extend
    def extend(self, paths: Iterable[str]) -> None:
        """
        Add multiple path strings to the internal cache.

        Parameters:
        paths : Iterable[str]
            An iterable of path strings to add. Empty or falsy values are ignored.
            Entries are added verbatim and duplicates are naturally de-duplicated
            because the underlying storage is a set.

        Returns:
        None

        Side effects:
        Mutates the instance's self._paths set by adding each non-empty path.
        No normalization or validation of path strings is performed.
        """
        for path in paths:
            if path:
                self._paths.add(path)
# endregion

# region cleanup
    def cleanup(self) -> None:
        """Attempt to delete files remembered from a previous run.

        If there are no remembered paths, this method returns immediately.
        It works by taking a snapshot of the current internal path collection
        (self._paths), clearing that collection, and iterating over the snapshot
        to remove each non-empty path via os.remove().

        Behavior details:
        - Skips falsy/empty path values.
        - Ignores FileNotFoundError (the file was already removed).
        - On other OSError instances (e.g., permission denied, file locked),
            the path is re-added to self._paths so a future call can retry removal.

        Side effects:
        - Mutates self._paths (cleared, but some failed-to-remove paths may be restored).
        - Returns None.
        """
        if not self._paths:
            return

        stale = list(self._paths)
        self._paths.clear()
        for path in stale:
            if not path:
                continue
            try:
                os.remove(path)
            except FileNotFoundError:
                continue
            except OSError:
                # Preserve the path for another attempt later.
                self._paths.add(path)
# endregion

__all__ = ["TempFileCache"]
