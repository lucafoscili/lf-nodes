import cv2
import numpy as np
import svgwrite
import torch
import uuid
import xml.etree.ElementTree as ET

from dataclasses import dataclass, fields
from PIL import Image
from typing import Any, Dict, Tuple

try:
    import vtracer
    _VTRACER_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    vtracer = None
    _VTRACER_AVAILABLE = False

try:
    from skimage import color as sk_color
    _SKIMAGE_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    sk_color = None
    _SKIMAGE_AVAILABLE = False

@dataclass
class SVGTraceConfig:
    """
    Configuration options for the raster-to-SVG tracing pipeline. Values are tuned
    for icon-style artwork by default; presets can override them.
    """

    num_colors: int = 4
    threshold: float = 0.5
    simplify_tol: float = 0.05
    vector_mode: str = "fill"
    stroke_width: float = 0.0

    upsample_scale: int = 1
    mask_blur: float = 0.8
    mask_offset: int = 0
    mask_close_iters: int = 1
    mask_open_iters: int = 0
    smooth_passes: int = 1
    min_area_ratio: float = 0.00005

    pre_blur_sigma: float = 0.0
    bilateral_d: int = 7
    bilateral_sigma_color: float = 60.0
    bilateral_sigma_space: float = 60.0
    collinear_angle_tol: float = 4.0
    use_lab_colors: bool = False
    fill_color_override: str | None = None
    stroke_color_override: str | None = None
    background_color: str | None = None
    size_mode: str = "responsive"
    # Optional override for the SVG viewBox. Expected format: "minX minY width height"
    viewbox_override: str | None = None

    engine: str = "contour"
    vtracer_mode: str = "spline"
    vtracer_hierarchical: str = "stacked"
    vtracer_filter_speckle: int = 4
    vtracer_color_precision: int = 6
    vtracer_layer_difference: int = 16
    vtracer_corner_threshold: int = 80
    vtracer_length_threshold: float = 4.0
    vtracer_max_iterations: int = 10
    vtracer_splice_threshold: int = 45
    vtracer_path_precision: int = 3


def _rgb_to_hex(rgb: np.ndarray) -> str:
    if rgb is None or len(rgb) < 3:
        return "#000000"
    rgb = np.clip(np.round(rgb), 0, 255).astype(int)
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def _format_coord(value: float) -> str:
    value = float(value)
    rounded = round(value)
    if abs(value - rounded) < 1e-3:
        return str(int(rounded))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _ensure_uint8(arr: np.ndarray) -> np.ndarray:
    """Convert an image array to uint8 in-place when necessary."""
    if arr.dtype == np.uint8:
        return arr.copy()

    data = arr.astype(np.float32)
    if data.max() <= 1.0:
        data *= 255.0
    data = np.clip(data, 0, 255)
    return data.astype(np.uint8)


def _normalize_mask(mask: Any, height: int, width: int) -> np.ndarray | None:
    """
    Convert assorted mask representations (torch tensors, numpy arrays, Python sequences)
    into a binary uint8 mask with shape (height, width). Returns None when no mask is
    provided or the mask collapses to an empty selection.
    """
    if mask is None:
        return None

    try:
        if torch is not None and isinstance(mask, torch.Tensor):
            mask_array = mask.detach().cpu().numpy()
        else:
            mask_array = np.asarray(mask)
    except Exception:
        return None

    if mask_array.size == 0:
        return None

    mask_array = np.squeeze(mask_array)
    if mask_array.ndim == 0:
        return None

    if mask_array.ndim == 1:
        if mask_array.size != height * width:
            return None
        mask_array = mask_array.reshape((height, width))
    elif mask_array.ndim > 2:
        mask_array = np.squeeze(mask_array)
        if mask_array.ndim != 2:
            return None

    if mask_array.shape != (height, width):
        mask_array = cv2.resize(mask_array, (width, height), interpolation=cv2.INTER_NEAREST)

    if mask_array.dtype == np.bool_:
        mask_array = mask_array.astype(np.uint8) * 255
    elif np.issubdtype(mask_array.dtype, np.floating):
        mask_array = (np.clip(mask_array, 0.0, 1.0) * 255.0).round().astype(np.uint8)
    else:
        mask_array = np.clip(mask_array, 0, 255).astype(np.uint8)

    mask_array = np.where(mask_array > 127, 255, 0).astype(np.uint8)
    if cv2.countNonZero(mask_array) == 0:
        return None
    return mask_array


def _unique_palette_from_image(img: np.ndarray, max_colors: int = 32) -> list[str]:
    flat = img.reshape(-1, img.shape[-1])
    unique = np.unique(flat, axis=0)
    if unique.shape[0] > max_colors:
        unique = unique[:max_colors]
    return [_rgb_to_hex(color) for color in unique]


def _quantize_via_lab(img_uint8: np.ndarray, num_colors: int, attempts: int = 5) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Quantise an RGB image to num_colors using k-means in Lab space for improved
    perceptual fidelity. Returns (preview_rgb, label_map, centers_rgb).
    """
    h, w = img_uint8.shape[:2]
    rgb_norm = img_uint8.astype(np.float32) / 255.0
    lab = sk_color.rgb2lab(rgb_norm)
    lab_reshaped = lab.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 1.0)
    _, labels, centers_lab = cv2.kmeans(lab_reshaped, num_colors, None, criteria, attempts, cv2.KMEANS_PP_CENTERS)
    centers_lab = centers_lab.astype(np.float32)
    centers_rgb = sk_color.lab2rgb(centers_lab.reshape(1, -1, 3)).reshape(-1, 3)
    centers_rgb = np.clip(centers_rgb * 255.0, 0, 255).astype(np.uint8)
    preview = centers_rgb[labels.flatten()].reshape((h, w, 3))

    flat_lab = lab_reshaped
    for idx in range(num_colors):
        mask = labels.flatten() == idx
        if not np.any(mask):
            continue
        weighted_lab = flat_lab[mask]
        centers_lab[idx] = weighted_lab.mean(axis=0)

    centers_rgb = sk_color.lab2rgb(centers_lab.reshape(1, -1, 3)).reshape(-1, 3)
    centers_rgb = np.clip(centers_rgb * 255.0, 0, 255).astype(np.uint8)
    preview = centers_rgb[labels.flatten()].reshape((h, w, 3))
    label_map = labels.reshape(h, w)
    return preview, label_map, centers_rgb


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _apply_svg_overrides(svg_str: str, cfg: SVGTraceConfig, width: int, height: int) -> str:
    try:
        root = ET.fromstring(svg_str)
    except ET.ParseError:
        return svg_str

    # If the user provided a viewbox override string, try to parse and apply it.
    vb_minx, vb_miny, vb_w, vb_h = 0.0, 0.0, float(width), float(height)
    if getattr(cfg, "viewbox_override", None):
        try:
            parts = str(cfg.viewbox_override).strip().split()
            if len(parts) == 4:
                parsed = [float(p) for p in parts]
                if parsed[2] > 0 and parsed[3] > 0:
                    vb_minx, vb_miny, vb_w, vb_h = parsed
        except Exception:
            # If parsing fails, fall back to default values.
            pass

    root.set("viewBox", f"{_format_coord(vb_minx)} {_format_coord(vb_miny)} {_format_coord(vb_w)} {_format_coord(vb_h)}")

    # If an override is present, wrap the existing content (except defs)
    # into a transform group that maps the original width/height to the
    # requested viewBox. We assume the SVG originally used the provided
    # width/height passed to this function (width, height arguments).
    try:
        if getattr(cfg, "viewbox_override", None):
            # compute scale factors from original to target viewbox
            sx = float(vb_w) / float(width) if float(width) != 0 else 1.0
            sy = float(vb_h) / float(height) if float(height) != 0 else 1.0
            transform = f"scale({_format_coord(sx)} {_format_coord(sy)}) translate({_format_coord(vb_minx)} {_format_coord(vb_miny)})"

            # create a group and move non-defs children into it
            group = ET.Element(f"{{{SVG_NS}}}g")
            group.set("transform", transform)

            # Move children (preserving defs at front)
            children = list(root)
            insert_idx = 0
            if children and children[0].tag == f"{{{SVG_NS}}}defs":
                insert_idx = 1

            for i, child in enumerate(children):
                if i == insert_idx and insert_idx == 1:
                    # leave defs in place
                    continue
                # remove child from root and append to group
                root.remove(child)
                group.append(child)

            # append group at end (or after defs)
            if insert_idx == 1:
                root.insert(1, group)
            else:
                root.append(group)
    except Exception:
        # On any error, leave the tree unchanged
        pass
    root.set("preserveAspectRatio", "xMidYMid meet")

    if cfg.size_mode == "fixed":
        root.set("width", str(width))
        root.set("height", str(height))
    else:
        root.set("width", "100%")
        root.set("height", "100%")

    if cfg.background_color:
        rect_attrs = {
            "x": _format_coord(vb_minx),
            "y": _format_coord(vb_miny),
            "width": _format_coord(vb_w),
            "height": _format_coord(vb_h),
            "fill": cfg.background_color
        }
        background = ET.Element(f"{{{SVG_NS}}}rect", rect_attrs)
        insert_index = 0
        if len(root) > 0 and root[0].tag == f"{{{SVG_NS}}}defs":
            insert_index = 1
        root.insert(insert_index, background)

    ns = {"svg": SVG_NS}
    fill_mode = (cfg.vector_mode or "fill").lower()
    allow_fill = fill_mode in {"fill", "both"}
    allow_stroke = fill_mode in {"stroke", "both"}

    for path in root.findall(".//svg:path", ns):
        original_fill = path.get("fill")

        if allow_fill:
            if cfg.fill_color_override and original_fill != "none":
                path.set("fill", cfg.fill_color_override)
        else:
            path.set("fill", "none")

        if allow_stroke:
            fallback_color = cfg.stroke_color_override or path.get("stroke")
            if not fallback_color or fallback_color == "none":
                fallback_color = cfg.fill_color_override or original_fill
            if not fallback_color or fallback_color == "none":
                fallback_color = "#000000"
            path.set("stroke", cfg.stroke_color_override or fallback_color)
            path.set("stroke-width", str(cfg.stroke_width))
        else:
            path.set("stroke", "none")
            path.set("stroke-width", "0")

    return ET.tostring(root, encoding="unicode")


def _numpy_to_svg_vtracer(
    img_uint8: np.ndarray,
    cfg: SVGTraceConfig,
    num_colors: int,
    mask: np.ndarray | None = None,
) -> tuple[str, np.ndarray, list[str]]:
    pil_img = Image.fromarray(img_uint8)
    if num_colors > 0:
        quantized = pil_img.convert("RGB").quantize(colors=num_colors, method=Image.MEDIANCUT)
        preview_img = np.array(quantized.convert("RGB"))
        rgba_img = quantized.convert("RGBA")
    else:
        preview_img = np.array(pil_img)
        rgba_img = pil_img.convert("RGBA")

    if mask is not None:
        mask_bool = mask.astype(bool)
        preview_img = preview_img.copy()
        preview_img[~mask_bool] = 0

        rgba_array = np.array(rgba_img)
        rgba_array[..., 3] = np.where(mask_bool, rgba_array[..., 3], 0)
        rgba_img = Image.fromarray(rgba_array, mode="RGBA")

    pixels = list(rgba_img.getdata())
    size = rgba_img.size

    svg_str = vtracer.convert_pixels_to_svg(
        rgba_pixels=pixels,
        size=size,
        colormode="color",
        hierarchical=cfg.vtracer_hierarchical,
        mode=cfg.vtracer_mode,
        filter_speckle=int(cfg.vtracer_filter_speckle),
        color_precision=int(cfg.vtracer_color_precision),
        layer_difference=int(cfg.vtracer_layer_difference),
        corner_threshold=int(cfg.vtracer_corner_threshold),
        length_threshold=float(cfg.vtracer_length_threshold),
        max_iterations=int(cfg.vtracer_max_iterations),
        splice_threshold=int(cfg.vtracer_splice_threshold),
        path_precision=int(cfg.vtracer_path_precision),
    )

    palette = _unique_palette_from_image(preview_img)
    svg_str = _apply_svg_overrides(svg_str, cfg, size[0], size[1])
    return svg_str, preview_img, palette


def _coerce_config(config: Any) -> SVGTraceConfig:
    if isinstance(config, SVGTraceConfig):
        return config

    if isinstance(config, dict):
        allowed = {field.name for field in fields(SVGTraceConfig)}
        filtered: Dict[str, Any] = {k: v for k, v in config.items() if k in allowed}
        return SVGTraceConfig(**filtered)

    return SVGTraceConfig()


def _smooth_contour(contour: np.ndarray, passes: int) -> np.ndarray:
    if passes <= 0 or contour.shape[0] < 3:
        return contour

    pts = contour.reshape(-1, 2).astype(np.float32)
    for _ in range(passes):
        prev_pts = np.roll(pts, 1, axis=0)
        next_pts = np.roll(pts, -1, axis=0)
        pts = (prev_pts + pts + next_pts) / 3.0
    return pts.reshape(-1, 1, 2)


def _remove_collinear_points(contour: np.ndarray, angle_tolerance_deg: float) -> np.ndarray:
    """
    Remove points that lie nearly on a straight line to reduce stair-stepping
    while preserving polygon shape.
    """
    pts = contour.reshape(-1, 2).astype(np.float32)
    n = pts.shape[0]
    if n <= 3:
        return contour

    sin_thresh = np.sin(np.deg2rad(max(angle_tolerance_deg, 0.1)))
    keep = np.ones(n, dtype=bool)

    for i in range(n):
        prev_idx = (i - 1) % n
        next_idx = (i + 1) % n
        prev_vec = pts[i] - pts[prev_idx]
        next_vec = pts[next_idx] - pts[i]

        prev_len = np.linalg.norm(prev_vec)
        next_len = np.linalg.norm(next_vec)
        if prev_len < 1e-5 or next_len < 1e-5:
            continue

        prev_unit = prev_vec / prev_len
        next_unit = next_vec / next_len
        cross = abs(prev_unit[0] * next_unit[1] - prev_unit[1] * next_unit[0])

        if cross <= sin_thresh:
            keep[i] = False

    filtered = pts[keep]
    if filtered.shape[0] < 3:
        return contour
    return filtered.reshape(-1, 1, 2)


def _approximate_contour(contour: np.ndarray, simplify_tol: float, scale_factor: float) -> np.ndarray:
    if contour.shape[0] < 3:
        return np.empty((0, 1, 2), dtype=contour.dtype)

    if simplify_tol <= 0:
        return contour

    perim = cv2.arcLength(contour, True)
    if perim <= 0:
        return contour

    if 0 < simplify_tol < 1:
        epsilon = float(simplify_tol) * perim
    else:
        epsilon = float(simplify_tol) * max(scale_factor, 1.0)

    epsilon = max(epsilon, 0.25)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if approx.shape[0] < 3:
        return contour
    return approx


def _prepare_region_mask(mask: np.ndarray, config: SVGTraceConfig) -> Tuple[np.ndarray, float]:
    mask_proc = mask.astype("uint8")
    scale = max(1, int(round(config.upsample_scale)))

    if scale > 1:
        mask_proc = cv2.resize(
            mask_proc,
            (mask_proc.shape[1] * scale, mask_proc.shape[0] * scale),
            interpolation=cv2.INTER_CUBIC
        )

    _, mask_proc = cv2.threshold(mask_proc, 127, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    offset = int(config.mask_offset)
    if offset > 0:
        mask_proc = cv2.dilate(mask_proc, kernel, iterations=offset)
    elif offset < 0:
        mask_proc = cv2.erode(mask_proc, kernel, iterations=abs(offset))

    if config.mask_close_iters > 0:
        mask_proc = cv2.morphologyEx(mask_proc, cv2.MORPH_CLOSE, kernel, iterations=int(config.mask_close_iters))
    if config.mask_open_iters > 0:
        mask_proc = cv2.morphologyEx(mask_proc, cv2.MORPH_OPEN, kernel, iterations=int(config.mask_open_iters))

    if config.mask_blur > 0:
        sigma = float(config.mask_blur) * scale
        ksize = max(3, int(np.ceil(sigma * 3)) * 2 + 1)
        mask_proc = cv2.GaussianBlur(mask_proc, (ksize, ksize), sigmaX=sigma, sigmaY=sigma)
        _, mask_proc = cv2.threshold(mask_proc, 127, 255, cv2.THRESH_BINARY)

    return mask_proc, float(scale)


def _mask_to_paths(
    mask: np.ndarray,
    simplify_tol: float,
    min_area: float,
    scale_factor: float,
    smooth_passes: int,
    collinear_angle_tol: float
) -> list[str]:
    if mask.dtype != np.uint8:
        mask = mask.astype("uint8")

    if not np.any(mask):
        return []

    chain_mode = cv2.CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, chain_mode)

    if not contours:
        return []

    if hierarchy is None:
        hierarchy = np.full((len(contours), 4), -1, dtype=int)
    else:
        hierarchy = hierarchy.reshape(-1, 4)

    contour_map: dict[int, np.ndarray] = {}
    min_area_scaled = max(1.0, float(min_area))

    for idx, contour in enumerate(contours):
        approx = _approximate_contour(contour, simplify_tol, scale_factor)
        if approx.size == 0:
            continue

        approx = _smooth_contour(approx, smooth_passes)
        approx = _remove_collinear_points(approx, collinear_angle_tol)
        if approx.shape[0] < 3:
            continue

        area = float(abs(cv2.contourArea(approx)))
        if area < min_area_scaled:
            continue

        contour_map[idx] = approx

    if not contour_map:
        return []

    def contour_to_path(points: np.ndarray) -> str:
        pts = points.reshape(-1, 2).astype(np.float32) / max(scale_factor, 1.0)
        if pts.size == 0:
            return ""

        x0, y0 = pts[0]
        path = f"M{_format_coord(x0)},{_format_coord(y0)}"
        for x, y in pts[1:]:
            path += f" L{_format_coord(x)},{_format_coord(y)}"
        return path + " Z"

    accepted = sorted(contour_map.keys())
    top_level = []
    for idx in accepted:
        parent = hierarchy[idx, 3] if idx < hierarchy.shape[0] else -1
        if parent == -1 or parent not in contour_map:
            top_level.append(idx)

    paths: list[str] = []
    for idx in sorted(top_level, key=lambda i: cv2.contourArea(contour_map[i]), reverse=True):
        path_d = contour_to_path(contour_map[idx])

        stack = []
        first_child = hierarchy[idx, 2] if idx < hierarchy.shape[0] else -1
        if first_child != -1:
            stack.append(first_child)

        while stack:
            current = stack.pop()
            next_sibling = hierarchy[current, 0] if current < hierarchy.shape[0] else -1
            if next_sibling != -1:
                stack.append(next_sibling)

            if current in contour_map:
                path_d += contour_to_path(contour_map[current])

            child = hierarchy[current, 2] if current < hierarchy.shape[0] else -1
            if child != -1:
                stack.append(child)

        if path_d:
            paths.append(path_d)

    return paths


def numpy_to_svg(arr: np.ndarray, config: Any = None, mask: Any = None) -> tuple[str, np.ndarray, list[str]]:
    """
    Convert an RGB numpy image into SVG markup using contour tracing guided by the
    provided configuration. Returns (svg_string, preview_image, palette_hex_list).
    """
    cfg = _coerce_config(config)

    h, w = arr.shape[:2]
    img_uint8 = _ensure_uint8(arr)
    mask_uint8 = _normalize_mask(mask, h, w)
    keep_mask = None
    if mask_uint8 is not None:
        keep_mask = mask_uint8.copy()

    processing_img = img_uint8.copy()
    if keep_mask is not None:
        processing_img[keep_mask == 0] = 0

    try:
        cv2.setNumThreads(1)
    except Exception:
        pass

    try:
        cv2.setRNGSeed(0)
    except Exception:
        pass

    num_colors = max(1, min(int(cfg.num_colors), 256))
    simplify_tol = max(0.0, float(cfg.simplify_tol))
    min_area = max(1.0, float(cfg.min_area_ratio) * float(h * w))

    engine = (cfg.engine or "contour").lower()

    if engine == "vtracer" and _VTRACER_AVAILABLE:
        try:
            return _numpy_to_svg_vtracer(img_uint8, cfg, num_colors, keep_mask)
        except Exception as exc:
            # If vtracer fails, fall back to contour tracing.
            import traceback

            print("Warning: vtracer conversion failed, falling back to contour tracing.")
            traceback.print_exception(exc)
            pass

    if cfg.pre_blur_sigma > 0:
        blur_sigma = float(cfg.pre_blur_sigma)
        blur_size = max(3, int(np.ceil(blur_sigma * 3)) * 2 + 1)
        preproc_img = cv2.GaussianBlur(processing_img, (blur_size, blur_size), blur_sigma)
    else:
        preproc_img = processing_img.copy()

    if keep_mask is not None:
        preproc_img[keep_mask == 0] = 0

    color_regions: list[Dict[str, Any]] = []

    alpha_channel = keep_mask.copy() if keep_mask is not None else None

    if num_colors > 1:
        pixels = preproc_img.reshape(-1, 3).astype(np.float32)
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1.0)
        attempts = 5
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, crit, attempts, cv2.KMEANS_PP_CENTERS)
        centers = centers.astype(np.uint8)

        label_map = labels.reshape(h, w)
        preview = centers[labels.flatten()].reshape((h, w, 3))

        if cfg.bilateral_d > 0:
            preview = cv2.bilateralFilter(
                preview,
                int(cfg.bilateral_d),
                float(cfg.bilateral_sigma_color),
                float(cfg.bilateral_sigma_space)
            )

        flat_original = img_uint8.reshape(-1, 3)
        flat_labels = labels.flatten()
        mask_filter = keep_mask.reshape(-1) > 0 if keep_mask is not None else None

        for idx, center in enumerate(centers):
            mask = np.where(label_map == idx, 255, 0).astype("uint8")
            if keep_mask is not None:
                mask = cv2.bitwise_and(mask, keep_mask)
            area_px = int(cv2.countNonZero(mask))
            if area_px == 0:
                continue

            if mask_filter is not None:
                cluster_selector = mask_filter & (flat_labels == idx)
                cluster_pixels = flat_original[cluster_selector]
            else:
                cluster_pixels = flat_original[flat_labels == idx]
            mean_color = cluster_pixels.mean(axis=0) if cluster_pixels.size else center
            color_regions.append({
                "mask": mask,
                "color": _rgb_to_hex(mean_color),
                "area": area_px
            })

        if keep_mask is not None:
            preview[keep_mask == 0] = 0
    else:
        gray = cv2.cvtColor(preproc_img, cv2.COLOR_RGB2GRAY)
        threshold_value = int(np.clip(cfg.threshold, 0.0, 1.0) * 255)
        _, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        preview = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        if keep_mask is not None:
            mask = cv2.bitwise_and(mask, keep_mask)
            preview[keep_mask == 0] = 0

        area_px = int(cv2.countNonZero(mask))
        if area_px > 0:
            mean_color = img_uint8[mask == 255].mean(axis=0)
            color_regions.append({
                "mask": mask,
                "color": _rgb_to_hex(mean_color),
                "area": area_px
            })

    # Determine the viewBox to use for the generated drawing. Allow an override
    # string in the config in the form: "minX minY width height".
    vb_minx, vb_miny, vb_w, vb_h = 0.0, 0.0, float(w), float(h)
    if getattr(cfg, "viewbox_override", None):
        try:
            parts = str(cfg.viewbox_override).strip().split()
            if len(parts) == 4:
                parsed = [float(p) for p in parts]
                if parsed[2] > 0 and parsed[3] > 0:
                    vb_minx, vb_miny, vb_w, vb_h = parsed
        except Exception:
            pass

    dwg = svgwrite.Drawing(
        size=("100%", "100%"),
        viewBox=f"{_format_coord(vb_minx)} {_format_coord(vb_miny)} {_format_coord(vb_w)} {_format_coord(vb_h)}",
        preserveAspectRatio="xMidYMid meet"
    )
    dwg.attribs["shape-rendering"] = "geometricPrecision"
    dwg.attribs["stroke-linejoin"] = "round"
    dwg.attribs["stroke-linecap"] = "round"

    if cfg.size_mode == "fixed":
        dwg.attribs["width"] = str(w)
        dwg.attribs["height"] = str(h)
    else:
        dwg.attribs["width"] = "100%"
        dwg.attribs["height"] = "100%"

    if cfg.background_color and keep_mask is None:
        dwg.add(dwg.rect(insert=(_format_coord(vb_minx), _format_coord(vb_miny)), size=(_format_coord(vb_w), _format_coord(vb_h)), fill=cfg.background_color, stroke="none"))

    # If a viewbox override was provided, wrap geometry in a transform group so
    # the original coordinates are mapped into the requested viewBox. This
    # avoids rewriting path data and keeps the background rect as the canvas.
    content_group = None
    if getattr(cfg, "viewbox_override", None):
        try:
            sx = float(vb_w) / float(w)
            sy = float(vb_h) / float(h)
            transform_str = f"scale({_format_coord(sx)} {_format_coord(sy)}) translate({_format_coord(vb_minx)} {_format_coord(vb_miny)})"
            content_group = dwg.g(transform=transform_str)
            dwg.add(content_group)
        except Exception:
            content_group = None

    geometry_parent = content_group if content_group is not None else dwg

    if keep_mask is not None:
        clip_mask, clip_scale = _prepare_region_mask(keep_mask, cfg)
        clip_paths = _mask_to_paths(
            clip_mask,
            simplify_tol,
            min_area,
            clip_scale,
            cfg.smooth_passes,
            cfg.collinear_angle_tol,
        )
        if clip_paths:
            clip_id = f"clip_{uuid.uuid4().hex}"
            clip_node = dwg.defs.add(dwg.clipPath(id=clip_id, clipPathUnits="userSpaceOnUse"))
            for clip_path in clip_paths:
                clip_node.add(dwg.path(d=clip_path, fill="white"))
            clipped_group = dwg.g(clip_path=f"url(#{clip_id})")
            geometry_parent.add(clipped_group)
            geometry_parent = clipped_group
            print("[LF_ImageToSVG] clipPath applied with", len(clip_paths), "paths")

    palette: list[str] = []
    mode = (cfg.vector_mode or "fill").lower()
    fill_enabled = mode in {"fill", "both"}
    stroke_enabled = mode in {"stroke", "both"} and cfg.stroke_width > 0

    for region in sorted(color_regions, key=lambda item: item["area"], reverse=True):
        mask_proc, scale_factor = _prepare_region_mask(region["mask"], cfg)
        paths = _mask_to_paths(
            mask_proc,
            simplify_tol,
            min_area,
            scale_factor,
            cfg.smooth_passes,
            cfg.collinear_angle_tol,
        )
        if not paths:
            continue

        hex_color = region["color"]
        palette.append(hex_color)
        fill_color = hex_color if fill_enabled else "none"
        stroke_color = hex_color if stroke_enabled else "none"

        if fill_enabled and cfg.fill_color_override:
            fill_color = cfg.fill_color_override
        if stroke_enabled and cfg.stroke_color_override:
            stroke_color = cfg.stroke_color_override
        elif stroke_enabled and (not stroke_color or stroke_color == "none"):
            stroke_color = fill_color if fill_color != "none" else "#000000"

        for path_d in paths:
            path = dwg.path(d=path_d, fill=fill_color, stroke=stroke_color)
            if stroke_enabled:
                path.attribs["stroke-width"] = float(cfg.stroke_width)
            else:
                path.attribs["stroke-width"] = 0
                path.attribs["stroke"] = "none"
            path.attribs["style"] = "fill-rule:evenodd"
            geometry_parent.add(path)

    if not palette and color_regions:
        region = max(color_regions, key=lambda item: item["area"])
        hex_color = region["color"]
        rect = dwg.rect(insert=(0, 0), size=(w, h), fill=hex_color)
        if stroke_enabled:
            rect.attribs["stroke"] = hex_color
            rect.attribs["stroke-width"] = float(cfg.stroke_width)
        else:
            rect.attribs["stroke"] = "none"
        geometry_parent.add(rect)
        palette.append(hex_color)

    if alpha_channel is not None:
        preview = np.dstack([preview, alpha_channel])

    return dwg.tostring(), preview, palette


__all__ = ["SVGTraceConfig", "numpy_to_svg"]
