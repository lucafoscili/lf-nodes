from __future__ import annotations

import os
from typing import Iterable, Set

class TempFileCache:
    """Temporary file cache used to track and remove stale temp files between executions.

    This class maintains rolling sets of filesystem paths belonging to the current
    and previous executions of a node. Files registered during the latest run are
    held in an "active" set; upon calling cleanup() the previously active paths are
    deleted and the current set is promoted to stale for the next cycle. Paths that
    cannot be deleted due to recoverable OS errors are preserved so that future
    cleanup attempts can retry removal.

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
        self._active_paths: Set[str] = set()
        self._stale_paths: Set[str] = set()

# region register
    def register(self, *paths: str) -> None:
        """
        Register one or more filesystem paths for later cleanup.

    Each provided non-empty path string is added to the instance's active
    set of tracked paths. Duplicate entries are ignored
        because a set is used. Falsy values (e.g. None or empty strings) are
        skipped.

        Args:
            *paths: One or more filesystem path strings to remember.

        Returns:
            None

        Side effects:
            Mutates the active path cache so the listed paths will be considered for
            deletion during the next cleanup rotation.
        """
        for path in paths:
            if path:
                self._active_paths.add(path)
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
    Mutates the instance's active path set by adding each non-empty path.
        No normalization or validation of path strings is performed.
        """
        for path in paths:
            if path:
                self._active_paths.add(path)
# endregion

# region cleanup
    def cleanup(self) -> None:
        """Attempt to delete files remembered from a previous run.

    If there are no remembered paths, this method returns immediately.
    It works by first attempting to delete paths marked as stale from the
    previous cleanup cycle, then promoting the active paths to become stale
    for the next invocation.

        Behavior details:
        - Skips falsy/empty path values.
        - Ignores FileNotFoundError (the file was already removed).
        - On other OSError instances (e.g., permission denied, file locked),
            the path is preserved for a future retry.

        Side effects:
    - Mutates the internal caches to rotate active paths into a deferred "stale" set.
    - Returns None.
        """
        if self._stale_paths:
            stale_snapshot = list(self._stale_paths)
            self._stale_paths.clear()
            failed: Set[str] = set()
            for path in stale_snapshot:
                if not path:
                    continue
                try:
                    os.remove(path)
                except FileNotFoundError:
                    continue
                except OSError:
                    failed.add(path)
            if failed:
                self._stale_paths.update(failed)

        if self._active_paths:
            # Defer removal of currently tracked paths until the next cleanup cycle
            self._stale_paths.update(self._active_paths)
            self._active_paths.clear()
# endregion

__all__ = ["TempFileCache"]
