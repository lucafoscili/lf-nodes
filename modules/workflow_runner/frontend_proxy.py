"""Compatibility shim for the frontend proxy script.

The canonical script has moved to `scripts/frontend_proxy.py`. Importing this
module will re-export the original names for backwards compatibility. Running
this file as a script will invoke `scripts.frontend_proxy.start_app()` so
existing execution commands continue to work.

Deprecation: importers should migrate to `workflow_runner.scripts.frontend_proxy`.
"""

import warnings

warnings.warn(
    "workflow_runner.frontend_proxy is deprecated and will be moved to "
    "workflow_runner.scripts.frontend_proxy; import from the scripts package "
    "instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .scripts.frontend_proxy import *  # type: ignore


if __name__ == "__main__":
    # Preserve original behaviour when executed directly
    try:
        import asyncio
        asyncio.run(start_app())
    except KeyboardInterrupt:
        import logging
        logging.info("Shutting down frontend proxy")
