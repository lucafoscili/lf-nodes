"""Tone reading: how two renders of one scene differ, and how regions of one render stand against each other.

Every measure works in display values (sRGB code values in 0..1, Rec. 709 luma weights), the space a viewer sees.
Intrinsic layers' albedo, shading and residual are linear (the residual signed): profile a layer against the same
layer of another image, not beside a frame's display values; the residual's ratios (fill, R/B) mean nothing.
"""
from .common import LUMA, as_rgb, luma, one_image, saturation
from .grade_split import grade_split
from .ratio_map import DEFAULT_EDGES, luma_ratio_map
from .region_reads import DEFAULT_READS, evaluate_reads, parse_reads, tone_profile
