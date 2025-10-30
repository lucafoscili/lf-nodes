"""
Lightweight API constants that can be safely imported by controllers
without pulling in heavy ComfyUI dependencies.

This module should only contain constants that are needed at import time
and don't require any heavy imports.
"""

API_ROUTE_PREFIX = "/lf-nodes" # Match the same in utils.constants