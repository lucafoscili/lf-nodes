"""Lightweight public option inventory shared by DDS nodes and Runner forms."""

PIXEL_FORMATS = ("RGB24", "RGBA32", "BC1", "BC3")
MIP_POLICIES = ("none", "full_chain")


__all__ = ["MIP_POLICIES", "PIXEL_FORMATS"]
