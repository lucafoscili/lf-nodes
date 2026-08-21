"""Lightweight socket constants for the CPU-only VN node pack.

Importing narrative authoring primitives must not initialize Torch, CUDA, or
Comfy's sampler registry. The strings intentionally mirror LF's shared Input
constants while keeping this package independently importable for headless
validation and compilation.
"""


CATEGORY = "✨ LF Nodes/Visual Novel"
FUNCTION = "on_exec"


class Input:
    JSON = "JSON"
    STRING = "STRING"
    LF_CODE = "LF_CODE"
    LF_ID = "LF_ID"
    LF_REF = "LF_REF"
    LF_TEXTAREA = "LF_TEXTAREA"
    LF_VN_BUNDLE = "LF_VN_BUNDLE"
    LF_VN_GRAPH = "LF_VN_GRAPH"
    LF_VN_STATE = "LF_VN_STATE"


__all__ = ["CATEGORY", "FUNCTION", "Input"]
