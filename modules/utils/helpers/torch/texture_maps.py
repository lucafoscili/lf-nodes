"""CPU texture-map operations: edge padding, masked Lab grading, detail transfer and normal maps.

Every function takes one image as an ``[H, W, C]`` float tensor of encoded
values in 0..1 (Comfy's IMAGE item without its batch axis) and a mask as an
``[H, W]`` tensor whose values weight or select pixels. Nothing here resizes,
downloads or touches the GPU; the node modules own input pairing and previews.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from .region_color_stats import lab_to_srgb, srgb_to_lab

MASK_THRESHOLD = 0.5
EDGE_PADDING_METHOD = "push-pull mip pyramid"
LAB_GRADE_SPREAD_FLOOR = 1e-6
# A detail measurement's pixels must sit this deep inside their mask: the box
# average of the mask over the blur radius reaches it, so the blur never mixes
# in pixels from outside the region.
DETAIL_INTERIOR = 0.999
# A fine-detail spread below this many L* units is rounding noise, not detail.
DETAIL_FLOOR = 1e-6
# Normal maps: an (X, Y) pair may leave the unit disc this far (block
# compression), and a stored vector shorter than this has no direction.
NORMAL_DISC_SLACK = 1.05
NORMAL_VANISHING_LENGTH = 0.2
NORMAL_UNIT_TOLERANCE = 0.02
NORMAL_GREEN = ("opengl", "directx")
NORMAL_Z_MODES = ("rebuild_z", "normalize_xyz")
NORMAL_LAYOUTS = ("xyz_rgb", "xy_ag")


def _check_mask(mask: torch.Tensor, image: torch.Tensor, name: str) -> torch.Tensor:
    if mask.ndim != 2 or tuple(mask.shape) != tuple(image.shape[:2]):
        raise ValueError(f"{name} {tuple(mask.shape)} does not match the image's H,W {tuple(image.shape[:2])}; "
                         "resizing is not supported.")
    if not torch.isfinite(mask).all():
        raise ValueError(f"{name} must hold finite values.")
    return mask.detach().to(device="cpu", dtype=torch.float64).clamp(0, 1)


# region Edge padding
def _halve(values: torch.Tensor) -> torch.Tensor:
    """Sum each 2x2 block; an odd last row or column is padded with zeros."""
    height, width = values.shape[:2]
    if height % 2 or width % 2:
        padded = values.new_zeros((height + height % 2, width + width % 2) + tuple(values.shape[2:]))
        padded[:height, :width] = values
        values = padded
    return values[0::2, 0::2] + values[1::2, 0::2] + values[0::2, 1::2] + values[1::2, 1::2]


def edge_pad(image: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, dict]:
    """Fill every pixel outside ``mask`` from the pixels inside it.

    Pull: each mip level sums the level below, counting only covered pixels.
    Push: from the 1x1 level back up, a pixel whose block holds no covered pixel
    takes its parent's colour. Each uncovered pixel so takes the average of the
    nearest covered pixels at the first scale that reaches any, and the mips of
    a padded texture keep the island's colour at its border. Covered pixels
    (mask above 0.5) are returned unchanged; every channel, alpha included, is
    filled the same way. The image's dtype is kept.
    """
    covered = _check_mask(mask, image, "mask") > MASK_THRESHOLD
    if not covered.any():
        raise ValueError("mask covers no pixel (none above 0.5): there is nothing to pad from.")
    total = covered.numel()
    receipt = {"width": int(image.shape[1]), "height": int(image.shape[0]),
               "covered_pixels": int(covered.sum()), "padded_pixels": int(total - covered.sum()),
               "covered_share": round(float(covered.sum()) / total, 6)}
    if covered.all():
        return image.clone(), {**receipt, "levels": 0}
    planes = image.detach().to(device="cpu", dtype=torch.float32)
    counts = [covered.to(torch.float32)]
    totals = [torch.where(covered[..., None], planes, planes.new_zeros(()))]
    while counts[-1].shape != (1, 1):
        counts.append(_halve(counts[-1]))
        totals.append(_halve(totals[-1]))
    colour = totals[-1] / counts[-1][..., None]
    for level_total, level_count in zip(reversed(totals[:-1]), reversed(counts[:-1])):
        height, width = level_count.shape
        parent = colour.repeat_interleave(2, 0).repeat_interleave(2, 1)[:height, :width]
        held = level_count > 0
        colour = torch.where(held[..., None], level_total / torch.where(held, level_count, 1.0)[..., None], parent)
    filled = colour.to(dtype=image.dtype, device=image.device)
    filled[covered.to(image.device)] = image[covered.to(image.device)]
    return filled, {**receipt, "levels": len(counts) - 1}
# endregion


# region Lab grade
def weighted_lab_moments(lab: torch.Tensor, weights: torch.Tensor, name: str) -> tuple[torch.Tensor, torch.Tensor]:
    """Weighted mean and population spread of each Lab channel."""
    total = float(weights.sum())
    if total <= 0:
        raise ValueError(f"{name} selects no pixel: there is no colour to measure.")
    mean = (lab * weights[..., None]).sum((0, 1)) / total
    spread = (((lab - mean) ** 2) * weights[..., None]).sum((0, 1)) / total
    return mean, spread.sqrt()


def lab_grade(image: torch.Tensor, mask: torch.Tensor, reference: torch.Tensor, reference_mask: torch.Tensor, *,
              min_stretch: float, max_stretch: float, amount: float,
              apply_to: str) -> tuple[torch.Tensor, dict]:
    """Move the masked pixels' Lab mean and spread to the reference region's.

    Each Lab channel is shifted and scaled: ``(lab - mean) * stretch + reference
    mean``, with ``stretch`` the spread ratio clamped to
    ``[min_stretch, max_stretch]`` (the defaults may narrow a spread, never widen
    it, so noise is not amplified). Mask values weight both the measurement and,
    with ``apply_to="mask"``, the blend; ``amount`` scales the change. Pixels
    with zero weight keep their exact input values, alpha is never changed, and
    colours graded outside the sRGB gamut are clipped and counted.
    """
    if min_stretch <= 0 or max_stretch < min_stretch:
        raise ValueError("min_stretch must be positive and no larger than max_stretch.")
    weights = _check_mask(mask, image, "mask")
    reference_weights = _check_mask(reference_mask, reference, "reference_mask")
    lab = srgb_to_lab(image[..., :3])
    mean, spread = weighted_lab_moments(lab, weights, "mask")
    reference_mean, reference_spread = weighted_lab_moments(srgb_to_lab(reference[..., :3]), reference_weights,
                                                            "reference_mask")
    stretch = (reference_spread / spread.clamp_min(LAB_GRADE_SPREAD_FLOOR)).clamp(min_stretch, max_stretch)
    blend = (weights if apply_to == "mask" else torch.ones_like(weights)) * amount
    graded = lab + ((lab - mean) * stretch + reference_mean - lab) * blend[..., None]
    rgb = lab_to_srgb(graded)
    changed = blend > 0
    clipped = ((rgb < 0) | (rgb > 1)).any(-1) & changed
    result = image.clone()
    result[..., :3] = torch.where(changed[..., None], rgb.clamp(0, 1), image[..., :3].to(torch.float64)).to(image.dtype)
    after_mean, after_spread = weighted_lab_moments(srgb_to_lab(result[..., :3]), weights, "mask")
    return result, {
        "target": {"lab_mean": mean.tolist(), "lab_std": spread.tolist(), "weight": float(weights.sum())},
        "reference": {"lab_mean": reference_mean.tolist(), "lab_std": reference_spread.tolist(),
                      "weight": float(reference_weights.sum())},
        "result": {"lab_mean": after_mean.tolist(), "lab_std": after_spread.tolist()},
        "stretch": stretch.tolist(), "changed_pixels": int(changed.sum()), "clipped_pixels": int(clipped.sum()),
    }
# endregion


# region Detail transfer
def box_blur(channel: torch.Tensor, radius: int) -> torch.Tensor:
    """Box-blurred copy of an ``[H, W]`` channel, ``radius`` pixels each side, edges replicated."""
    if radius <= 0:
        return channel.clone()
    padded = F.pad(channel[None, None], (radius + 1, radius, radius + 1, radius), mode="replicate")[0, 0]
    summed = padded.cumsum(0).cumsum(1)
    size = 2 * radius + 1
    return (summed[size:, size:] - summed[:-size, size:] - summed[size:, :-size]
            + summed[:-size, :-size]) / (size * size)


def high_pass(channel: torch.Tensor, radius: int) -> torch.Tensor:
    """The detail finer than ``radius`` pixels: the channel minus its box blur."""
    return channel - box_blur(channel, radius)


def high_pass_spread(channel: torch.Tensor, weights: torch.Tensor, radius: int) -> tuple[float | None, int]:
    """Population spread of the fine detail over the mask's interior, and the interior's pixel count."""
    inner = box_blur((weights > MASK_THRESHOLD).to(torch.float64), radius) > DETAIL_INTERIOR
    count = int(inner.sum())
    if not count:
        return None, 0
    return float(high_pass(channel, radius)[inner].std(correction=0)), count


def detail_transfer(image: torch.Tensor, detail: torch.Tensor, mask: torch.Tensor, *, radius: int, mode: str,
                    strength: float, reference: torch.Tensor | None,
                    reference_mask: torch.Tensor | None) -> tuple[torch.Tensor, dict]:
    """Add the detail source's fine lightness detail to the image.

    The detail is the source's L* minus its box blur over ``radius``. With
    ``mode="match_reference"``, the gain ``k`` is chosen so the result's fine L*
    spread over the mask's interior equals the reference region's ``r``: the
    non-negative root of ``k^2 s^2 + 2 k c + i^2 = r^2``, where ``i`` and ``s``
    are the image's and the source's fine spreads and ``c`` their covariance
    (a source unrelated to the image has ``c = 0`` and ``k = sqrt(r^2 - i^2) /
    s``). An image already as detailed as the reference gets ``k = 0``. With
    ``mode="fixed"``, ``strength`` is the gain. Mask values weight where the
    detail is added. Only L* changes; zero-weight pixels and alpha keep their
    exact input values.
    """
    if tuple(detail.shape[:2]) != tuple(image.shape[:2]):
        raise ValueError(f"detail_source {tuple(detail.shape[:2])} must have the image's H,W "
                         f"{tuple(image.shape[:2])}; resizing is not supported.")
    weights = _check_mask(mask, image, "mask")
    lab = srgb_to_lab(image[..., :3])
    source_lightness = srgb_to_lab(detail[..., :3])[..., 0]
    fine = high_pass(source_lightness, radius)
    image_spread, interior = high_pass_spread(lab[..., 0], weights, radius)
    source_spread, _ = high_pass_spread(source_lightness, weights, radius)
    report = {"radius": radius, "mode": mode, "interior_pixels": interior,
              "image_fine_l_std": image_spread, "source_fine_l_std": source_spread,
              "reference_fine_l_std": None}
    if mode == "match_reference":
        if reference is None:
            raise ValueError("mode match_reference needs reference_image.")
        reference_weights = (torch.ones(reference.shape[:2], dtype=torch.float64) if reference_mask is None
                             else _check_mask(reference_mask, reference, "reference_mask"))
        reference_spread, reference_interior = high_pass_spread(
            srgb_to_lab(reference[..., :3])[..., 0], reference_weights, radius)
        if reference_spread is None:
            raise ValueError(f"reference_mask has no pixel {radius} px inside its edge; lower the radius or "
                             "widen the region.")
        if image_spread is None or source_spread is None:
            raise ValueError(f"mask has no pixel {radius} px inside its edge; lower the radius or widen the region.")
        if source_spread < DETAIL_FLOOR:
            raise ValueError("detail_source has no detail finer than the radius inside the mask.")
        inner = box_blur((weights > MASK_THRESHOLD).to(torch.float64), radius) > DETAIL_INTERIOR
        image_fine = high_pass(lab[..., 0], radius)[inner]
        source_fine = fine[inner]
        covariance = float(((image_fine - image_fine.mean()) * (source_fine - source_fine.mean())).mean())
        shortfall = reference_spread ** 2 - image_spread ** 2
        strength = 0.0 if shortfall <= 0 else (
            (-covariance + math.sqrt(covariance ** 2 + source_spread ** 2 * shortfall)) / source_spread ** 2)
        report.update(reference_fine_l_std=reference_spread, reference_interior_pixels=reference_interior,
                      image_source_fine_covariance=covariance)
    elif mode != "fixed":
        raise ValueError(f"mode must be match_reference or fixed, not {mode!r}.")
    report["strength"] = strength
    changed = weights > 0
    lab[..., 0] = lab[..., 0] + strength * fine * weights
    rgb = lab_to_srgb(lab)
    clipped = ((rgb < 0) | (rgb > 1)).any(-1) & changed
    result = image.clone()
    result[..., :3] = torch.where(changed[..., None], rgb.clamp(0, 1), image[..., :3].to(torch.float64)).to(image.dtype)
    after, _ = high_pass_spread(srgb_to_lab(result[..., :3])[..., 0], weights, radius)
    report.update(result_fine_l_std=after, changed_pixels=int(changed.sum()), clipped_pixels=int(clipped.sum()))
    return result, report
# endregion


# region Normal maps
def normal_map_repack(image: torch.Tensor, mask: torch.Tensor | None, *, layout: str, green_in: str,
                      green_out: str, z_mode: str, max_invalid_share: float) -> tuple[torch.Tensor, dict]:
    """Check a tangent-space normal map, renormalise it and convert its green convention.

    Channels decode as ``value * 2 - 1``. ``layout`` names where X and Y are
    stored: ``xyz_rgb`` (X red, Y green, Z blue) or ``xy_ag`` (X alpha, Y green,
    the swizzled two-channel layout; Z is always rebuilt). ``rebuild_z`` keeps
    X and Y (pulled back onto the unit disc when they leave it) and rebuilds
    ``Z = sqrt(1 - X^2 - Y^2)``; an (X, Y) pair outside the disc by more than
    block compression explains counts as invalid. ``normalize_xyz`` scales the
    stored vector to unit length, keeping Z's sign; a vector facing away (Z
    below 0) or vanishing counts as invalid, and a vanishing one becomes
    (0, 0, 1). Validation runs over the mask (above 0.5), all pixels without
    one; more invalid pixels than ``max_invalid_share`` raises. The output is
    RGB (X, Y, Z); an ``xyz_rgb`` map's alpha passes through unchanged.
    """
    if layout not in NORMAL_LAYOUTS:
        raise ValueError(f"layout must be one of {NORMAL_LAYOUTS}, not {layout!r}.")
    if green_in not in NORMAL_GREEN or green_out not in NORMAL_GREEN:
        raise ValueError(f"green_in and green_out must be one of {NORMAL_GREEN}.")
    if z_mode not in NORMAL_Z_MODES:
        raise ValueError(f"z_mode must be one of {NORMAL_Z_MODES}, not {z_mode!r}.")
    if layout == "xy_ag" and image.shape[-1] != 4:
        raise ValueError("layout xy_ag reads X from alpha; the image has no alpha channel.")
    if layout == "xy_ag" and z_mode != "rebuild_z":
        raise ValueError("layout xy_ag stores no Z; use z_mode rebuild_z.")
    selected = (torch.ones(image.shape[:2], dtype=torch.bool) if mask is None
                else _check_mask(mask, image, "mask") > MASK_THRESHOLD)
    checked = int(selected.sum())
    if not checked:
        raise ValueError("mask selects no pixel (none above 0.5): there is nothing to check.")
    values = image.detach().to(device="cpu", dtype=torch.float64) * 2 - 1
    if layout == "xy_ag":
        vector = torch.stack((values[..., 3], values[..., 1], torch.zeros_like(values[..., 1])), -1)
    else:
        vector = values[..., :3].clone()
    planar = vector[..., 0] ** 2 + vector[..., 1] ** 2
    length = vector.norm(dim=-1)
    outside = planar > NORMAL_DISC_SLACK
    facing_away = vector[..., 2] < 0
    vanishing = length < NORMAL_VANISHING_LENGTH
    if z_mode == "rebuild_z":
        invalid = outside
        scale = torch.where(planar > 1, planar.clamp_min(1e-12).rsqrt(), torch.ones_like(planar))
        vector[..., :2] = vector[..., :2] * scale[..., None]
        vector[..., 2] = (1 - vector[..., 0] ** 2 - vector[..., 1] ** 2).clamp_min(0).sqrt()
        unit_off = (planar.sqrt() > 1 + NORMAL_UNIT_TOLERANCE) if layout == "xy_ag" else \
            ((length - 1).abs() > NORMAL_UNIT_TOLERANCE)
    else:
        invalid = facing_away | vanishing
        unit_off = (length - 1).abs() > NORMAL_UNIT_TOLERANCE
        forward = vector.new_tensor([0.0, 0.0, 1.0])
        vector = torch.where(vanishing[..., None], forward, vector / length.clamp_min(1e-12)[..., None])
    flipped = green_in != green_out
    if flipped:
        vector[..., 1] = -vector[..., 1]

    def share(flags: torch.Tensor) -> float:
        return round(float(flags[selected].double().mean()), 6)

    lengths = length[selected]
    report = {
        "layout": layout, "green_in": green_in, "green_out": green_out, "green_flipped": flipped,
        "z_mode": z_mode, "width": int(image.shape[1]), "height": int(image.shape[0]),
        "checked_pixels": checked, "outside_disc_share": share(outside),
        "facing_away_share": share(facing_away), "vanishing_share": share(vanishing),
        "invalid_share": share(invalid), "max_invalid_share": max_invalid_share,
        "renormalized_share": share(unit_off),
        "stored_length": {"mean": float(lengths.mean()), "min": float(lengths.min()), "max": float(lengths.max())},
    }
    if report["invalid_share"] > max_invalid_share:
        reason = ("(X, Y) outside the unit disc" if z_mode == "rebuild_z"
                  else "vectors facing away (Z below 0) or vanishing")
        raise ValueError(f"{report['invalid_share']:.2%} of the checked pixels hold {reason} (limit "
                         f"{max_invalid_share:.2%}): not a tangent normal map in layout {layout}.")
    encoded = (vector * 0.5 + 0.5).to(image.dtype)
    if layout == "xyz_rgb" and image.shape[-1] == 4:
        encoded = torch.cat((encoded, image[..., 3:].to(encoded.device)), -1)
    return encoded, report
# endregion
