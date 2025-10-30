"""Compatibility shim for the frontend proxy script.

The canonical script has moved to `scripts/frontend_proxy.py`. Importing this
module will re-export the original names for backwards compatibility. Running
this file as a script will invoke `scripts.frontend_proxy.start_app()` so
existing execution commands continue to work.
"""

from .scripts.frontend_proxy import *  # type: ignore


if __name__ == "__main__":
    # Preserve original behaviour when executed directly
    try:
        import asyncio
        asyncio.run(start_app())
    except KeyboardInterrupt:
        import logging
        logging.info("Shutting down frontend proxy")
