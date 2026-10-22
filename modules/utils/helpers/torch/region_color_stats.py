"""CPU color measurements for registered sRGB image regions (alpha ignored)."""
from __future__ import annotations

import math

import torch


def srgb_to_lab(rgb: torch.Tensor) -> torch.Tensor:
    """Decode IEC sRGB and convert to CIE Lab with the D65 2-degree white."""
    rgb = rgb.detach().to(device="cpu", dtype=torch.float64)
    linear = torch.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    matrix = rgb.new_tensor([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = (linear @ matrix.T) / rgb.new_tensor([0.95047, 1.0, 1.08883])
    delta = 6 / 29
    f = torch.where(xyz > delta ** 3, xyz.clamp_min(0).pow(1 / 3),
                    xyz / (3 * delta ** 2) + 4 / 29)
    return torch.stack((116 * f[..., 1] - 16,
                        500 * (f[..., 0] - f[..., 1]),
                        200 * (f[..., 1] - f[..., 2])), dim=-1)


def ciede2000(lab_a: torch.Tensor, lab_b: torch.Tensor) -> torch.Tensor:
    """CIEDE2000 per matched Lab pair, with kL=kC=kH=1."""
    l1, a1, b1 = lab_a.to(torch.float64).unbind(-1)
    l2, a2, b2 = lab_b.to(torch.float64).unbind(-1)
    c1, c2 = torch.hypot(a1, b1), torch.hypot(a2, b2)
    cbar7 = ((c1 + c2) / 2).pow(7)
    g = 0.5 * (1 - (cbar7 / (cbar7 + 25 ** 7)).sqrt())
    ap1, ap2 = (1 + g) * a1, (1 + g) * a2
    cp1, cp2 = torch.hypot(ap1, b1), torch.hypot(ap2, b2)
    hp1 = torch.remainder(torch.atan2(b1, ap1) * 180 / math.pi, 360)
    hp2 = torch.remainder(torch.atan2(b2, ap2) * 180 / math.pi, 360)
    hp1, hp2 = torch.where(cp1 == 0, 0, hp1), torch.where(cp2 == 0, 0, hp2)
    dl, dc = l2 - l1, cp2 - cp1
    dh = hp2 - hp1
    dh = torch.where(dh > 180, dh - 360, torch.where(dh < -180, dh + 360, dh))
    zero_chroma = cp1 * cp2 == 0
    dh = torch.where(zero_chroma, 0, dh)
    dH = 2 * (cp1 * cp2).sqrt() * torch.sin(dh * math.pi / 360)
    lbar, cbar = (l1 + l2) / 2, (cp1 + cp2) / 2
    hsum = hp1 + hp2
    hbar = torch.where((hp1 - hp2).abs() <= 180, hsum / 2,
                       torch.where(hsum < 360, (hsum + 360) / 2, (hsum - 360) / 2))
    hbar = torch.where(zero_chroma, hsum, hbar)
    radians = math.pi / 180
    t = (1 - 0.17 * torch.cos((hbar - 30) * radians)
         + 0.24 * torch.cos(2 * hbar * radians)
         + 0.32 * torch.cos((3 * hbar + 6) * radians)
         - 0.20 * torch.cos((4 * hbar - 63) * radians))
    sl = 1 + 0.015 * (lbar - 50).square() / (20 + (lbar - 50).square()).sqrt()
    sc, sh = 1 + 0.045 * cbar, 1 + 0.015 * cbar * t
    rc = 2 * (cbar.pow(7) / (cbar.pow(7) + 25 ** 7)).sqrt()
    rt = -rc * torch.sin(60 * torch.exp(-((hbar - 275) / 25).square()) * radians)
    x, y, z = dl / sl, dc / sc, dH / sh
    return (x.square() + y.square() + z.square() + rt * y * z).clamp_min(0).sqrt()


def luminance_banding(luminance: torch.Tensor, mask: torch.Tensor) -> dict:
    """A diagnostic for sparse levels in spatially smooth, non-flat regions.

    L* is tested on native horizontal/vertical neighbours inside the mask.
    Histogram bins span that region's observed L* range, not an 8-bit RGB proxy.
    Texture, tiny regions and flat fills are ineligible; this is not a detector
    of visible artifacts and a sparse palette can produce false positives.
    """
    values = luminance[mask]
    result = {"heuristic": True, "eligible": False, "suspected": False,
              "bin_count": 64, "occupied_bins": 0, "empty_bin_fraction": None,
              "neighbor_p90_delta_l": None, "plateau_fraction": None,
              "reason": "Insufficient region pixels or neighbouring pairs."}
    if values.numel() < 64:
        return result
    edges = []
    for axis in (0, 1):
        first = [slice(None), slice(None)]
        second = [slice(None), slice(None)]
        first[axis], second[axis] = slice(None, -1), slice(1, None)
        first, second = tuple(first), tuple(second)
        valid = mask[first] & mask[second]
        edges.append((luminance[first] - luminance[second]).abs()[valid])
    differences = torch.cat(edges)
    if differences.numel() < 32:
        return result
    p90 = float(torch.quantile(differences, 0.9))
    plateau = float((differences < 0.05).double().mean())
    result.update(neighbor_p90_delta_l=p90, plateau_fraction=plateau)
    low, high = float(values.min()), float(values.max())
    if high - low < 4:
        result["reason"] = "Region luminance range is below 4 L* (flat/near-flat)."
        return result
    if p90 > 4 or float(differences.mean()) > 2:
        result["reason"] = "Region failed the spatial smoothness test."
        return result
    bins = ((values - low) / (high - low) * 63).round().to(torch.int64)
    occupied = int(torch.unique(bins).numel())
    empty = 1 - occupied / 64
    suspected = occupied >= 4 and empty >= 0.35 and plateau >= 0.5
    result.update(eligible=True, occupied_bins=occupied, empty_bin_fraction=empty,
                  suspected=suspected,
                  reason=("Sparse luminance levels in a spatially smooth region; inspect visually."
                          if suspected else "Spatially smooth region without a sparse-level plateau signal."))
    return result


def _region_measurement(lab: torch.Tensor, mask: torch.Tensor) -> dict:
    area = int(mask.sum())
    pixels = lab[mask]
    return {"area": area, "area_fraction": area / mask.numel(), "empty": area == 0,
            "lab_mean": pixels.mean(0).tolist() if area else None,
            "lab_median": torch.quantile(pixels, 0.5, dim=0).tolist() if area else None,
            "banding": luminance_banding(lab[..., 0], mask)}


def region_color_measurements(image_a, image_b, mask_sets, document) -> dict:
    """Measure all pixels per side; compare a deterministic coordinate sample."""
    if len(mask_sets) not in (1, 2):
        raise ValueError("masks must contain one shared set or exactly two image_a/image_b sets.")
    labs = [srgb_to_lab(image[0, ..., :3]) for image in (image_a, image_b)]
    masks_a = mask_sets[0] > 0.5
    masks_b = mask_sets[-1] > 0.5
    rows = []
    for index, region in enumerate(document["regions"]):
        a = _region_measurement(labs[0], masks_a[index])
        b = _region_measurement(labs[1], masks_b[index])
        coordinates = torch.nonzero((masks_a[index] & masks_b[index]).flatten()).flatten()
        intersection_count = int(coordinates.numel())
        if intersection_count > 65536:
            coordinates = coordinates[(torch.arange(65536) * intersection_count) // 65536]
        matched = int(coordinates.numel())
        delta_e = None
        if matched:
            distances = ciede2000(labs[0].reshape(-1, 3)[coordinates],
                                 labs[1].reshape(-1, 3)[coordinates])
            quantiles = torch.quantile(distances, distances.new_tensor([0.1, 0.5, 0.9])).tolist()
            delta_e = dict(zip(("p10", "p50", "p90"), quantiles))
            delta_e["mean"] = float(distances.mean())
        warnings = []
        if a["empty"] or b["empty"]:
            warnings.append("Empty region on image A or B; per-image measurements are null on that side.")
        if not matched:
            warnings.append("No same-coordinate mask intersection; CIEDE2000 is null.")
        deltas = {key: [bv - av for av, bv in zip(a[key], b[key])]
                  if a[key] is not None and b[key] is not None else None
                  for key in ("lab_mean", "lab_median")}
        rows.append({"id": region["id"], "prompt": region["prompt"],
                     "priority": region["priority"], "a": a, "b": b,
                     "delta_b_minus_a": deltas, "ciede2000": delta_e,
                     "intersection_count": intersection_count, "matched_count": matched,
                     "warnings": warnings})
    return {"schema": "lf.region-color-stats.v1", "source_size": document["source_size"],
            "color_space": "CIE Lab, D65 2-degree white, decoded sRGB; alpha ignored",
            "lab_channels": ["L*", "a*", "b*"], "mask_membership": "value > 0.5",
            "mask_mode": "shared" if len(mask_sets) == 1 else "per_image",
            "lab_summary_method": "All pixels in each image's own mask; componentwise arithmetic mean and linear-interpolated median",
            "delta_direction": "B minus A",
            "ciede2000_method": {"matching": "same-coordinate mask intersection; registered images required",
                                 "sampling": "row-major, at most 65536 evenly spaced indices floor(i*N/65536); all when smaller",
                                 "quantile_interpolation": "linear",
                                 "max_samples": 65536, "kL": 1, "kC": 1, "kH": 1},
            "banding_method": {"warning": "Heuristic only; sparse palettes may give false positives. Inspect visually.",
                               "minimum_pixels": 64, "minimum_neighbor_pairs": 32,
                               "minimum_range_l": 4, "maximum_neighbor_p90_l": 4,
                               "maximum_neighbor_mean_l": 2, "bins": 64,
                               "minimum_empty_fraction": 0.35, "minimum_plateau_fraction": 0.5,
                               "plateau_delta_l": 0.05}, "regions": rows}


