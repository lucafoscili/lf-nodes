import cv2
import numpy as np
import svgwrite

# region numpy_to_svg
def numpy_to_svg(arr: np.ndarray, num_colors: int, threshold: float, simplify_tol: float, mode: str, stroke_width: float) -> tuple[str, np.ndarray, list[str]]:
    """
    Converts a NumPy image array into an SVG string representation by extracting and simplifying contours.

    Args:
        arr (np.ndarray): An RGB image represented as a NumPy array with shape (height, width, 3).
        num_colors (int): The number of colors to reduce the image to. If greater than 1, k-means clustering is applied
                          for color quantization.
        threshold (float): A threshold value (between 0 and 1) used to generate a binary mask when num_colors is 1.
        simplify_tol (float): The tolerance parameter for polygonal curve approximation used to simplify contours.
        mode (str): The mode of vectorization. Currently "fill", "stroke", and "both" are supported.
        stroke_width (float): The width of the stroke for the SVG polygons.

    Returns:
        tuple:
            - str: An SVG string generated from the simplified contours of the processed image.
            - np.ndarray: The processed image array after applying color quantization or thresholding.
            - list[str]: A list of color hex codes representing the palette used in the SVG.

    Notes:
        This function processes the provided image as follows:
          1. If num_colors > 1:
               - Reshapes the image array and performs k-means clustering to reduce the number of colors.
               - Reconstructs the image using the quantized colors.
          2. Otherwise, converts the image to grayscale, applies a threshold to create a binary mask, and converts it back to RGB.
          3. Converts the processed RGB image to grayscale.
          4. Extracts external contours from the grayscale image.
          5. Simplifies each contour using the specified simplify_tol.
          6. Creates an SVG drawing with polygons corresponding to the simplified contours using the svgwrite library.
    """
    h, w = arr.shape[:2]

    img = arr.copy()

    palette = []
    if num_colors > 1:
        pixels = img.reshape(-1,3).astype(np.float32)
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, crit, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = centers.astype(np.uint8)
        proc = centers[labels.flatten()].reshape((h, w, 3))
        palette = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in centers]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, int(threshold*255), 255, cv2.THRESH_BINARY)
        proc = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    # create a binary mask to detect shapes; ensure foreground shapes are
    # white (255) and background black (0). For quantized images we treat
    # any non-black pixel as foreground; for single-color thresholding we
    # used the earlier 'mask'. Then invert the mask if it covers most of
    # the image (likely the background), which prevents the full-canvas
    # contour from being detected.
    grayp = cv2.cvtColor(proc, cv2.COLOR_RGB2GRAY)

    if num_colors > 1:
        # any non-zero pixel is considered foreground
        _, mask = cv2.threshold(grayp, 1, 255, cv2.THRESH_BINARY)
    else:
        # for single-color mode we already computed a mask earlier; use it
        # but make sure we're using the processed gray image
        _, mask = cv2.threshold(grayp, int(threshold*255), 255, cv2.THRESH_BINARY)

    # If the mask is mostly white (background), invert so objects are white
    nonzero = cv2.countNonZero(mask)
    if nonzero > (w * h) * 0.5:
        mask = cv2.bitwise_not(mask)

    # Use RETR_TREE so we get the full contour hierarchy (parents and holes).
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Simplify contours and filter out ones that are either too small or
    # cover (almost) the entire image — the latter causes the undesired
    # full-canvas polygon when the mask is empty/full.
    # polys will store tuples of (contour_index, approx_contour)
    polys = []
    total_area = float(w * h)
    for idx, c in enumerate(contours):
        # compute a perimeter-relative epsilon when simplify_tol is specified
        # as a fractional tolerance (<1). If simplify_tol >= 1 we treat it as
        # an absolute pixel epsilon (backwards compatible).
        perim = cv2.arcLength(c, True)
        if simplify_tol > 0 and simplify_tol < 1:
            eps = float(simplify_tol) * perim
        else:
            eps = float(simplify_tol)

        # Avoid eps being zero or extremely small which can cause
        # approxPolyDP to collapse contours; enforce a small absolute
        # minimum (in pixels).
        eps = max(eps, 0.5)

        # approximate the contour
        approx = cv2.approxPolyDP(c, eps, True)
        area = cv2.contourArea(approx)

        # skip tiny contours
        if area <= 1.0:
            continue

        # skip contours that effectively cover the whole image (common when
        # the mask is entirely foreground/background)
        if area >= total_area * 0.999:
            continue

        # skip contours whose bounding box covers the image area (touching
        # all borders) — this avoids full-canvas polygons created by border
        # artifacts. Allow a 1-pixel tolerance. Only skip when the contour is
        # also very large (near the whole image); this prevents removing
        # legitimate shapes that touch the border.
        x, y, bw, bh = cv2.boundingRect(approx)
        border_touching = (x <= 1 and y <= 1 and (x + bw) >= (w - 2) and (y + bh) >= (h - 2))
        if border_touching and area >= total_area * 0.95:
            continue

        polys.append((idx, approx))

    if mode == "fill":
        fill_css, stroke_css = "currentColor", "none"
    elif mode == "stroke":
        fill_css, stroke_css = "none", "currentColor"
    else:  # both
        fill_css, stroke_css = "currentColor", "currentColor"

    dwg = svgwrite.Drawing(
        size=("100%","100%"),
        viewBox=f"0 0 {w} {h}",
        preserveAspectRatio="xMidYMid meet"
    )
    # If there are no valid polygons after filtering, attempt a fallback
    # pass using a small absolute epsilon to avoid empty SVGs when the
    # fractional simplify_tol produced eps that's still too small or
    # removed contours unintentionally. If fallback also finds nothing,
    # return an empty SVG.
    if not polys:
        fallback_polys = []
        for idx, c in enumerate(contours):
            approx = cv2.approxPolyDP(c, 0.5, True)
            area = cv2.contourArea(approx)
            if area <= 1.0:
                continue
            # skip contours that effectively cover the whole image
            if area >= total_area * 0.999:
                continue
            x, y, bw, bh = cv2.boundingRect(approx)
            border_touching = (x <= 1 and y <= 1 and (x + bw) >= (w - 2) and (y + bh) >= (h - 2))
            if border_touching and area >= total_area * 0.95:
                continue
            fallback_polys.append((idx, approx))

        if fallback_polys:
            polys = fallback_polys
        else:
            return dwg.tostring(), proc, palette

    # Create path elements using contour hierarchy so holes are preserved.
    # Build a mapping from contour index -> approx points for accepted polys.
    idx_to_approx = {idx: approx for idx, approx in polys}

    # Helper to convert a contour array to an SVG subpath string
    def contour_to_subpath(approx):
        pts = [(int(pt[0][0]), int(pt[0][1])) for pt in approx]
        if not pts:
            return ""
        d = f"M{pts[0][0]},{pts[0][1]}"
        for x, y in pts[1:]:
            d += f" L{x},{y}"
        d += " Z"
        return d

    # hierarchy shape is (1, n, 4) or (n,4); normalize to (n,4).
    # OpenCV may return None for hierarchy when there are no contours,
    # guard against that by creating a default -1 array.
    if hierarchy is None:
        hier = np.full((len(contours), 4), -1, dtype=int)
    else:
        hier = np.array(hierarchy).reshape(-1, 4)

    # Find top-level contours among accepted indices (parent == -1 or parent not accepted)
    accepted_idxs = set(idx_to_approx.keys())
    top_level = []
    for idx in accepted_idxs:
        parent = int(hier[idx, 3]) if idx < hier.shape[0] else -1
        if parent == -1 or parent not in accepted_idxs:
            top_level.append(idx)

    # For each top-level contour, build a combined path with its child contours as subpaths
    for tidx in top_level:
        d = ""
        # add the top-level contour
        d += contour_to_subpath(idx_to_approx[tidx])

        # search children (simple breadth-first over hierarchy)
        stack = []
        first_child = int(hier[tidx, 2]) if tidx < hier.shape[0] else -1
        if first_child != -1:
            stack.append(first_child)
        while stack:
            cidx = stack.pop()
            # push siblings
            next_sib = int(hier[cidx, 0])
            if next_sib != -1:
                stack.append(next_sib)
            # include contour if it's accepted
            if cidx in idx_to_approx:
                d += contour_to_subpath(idx_to_approx[cidx])
            # push this contour's first child
            fc = int(hier[cidx, 2])
            if fc != -1:
                stack.append(fc)

        path = dwg.path(d=d, fill=fill_css, stroke=stroke_css, stroke_width=stroke_width)
        path.attribs["style"] = "fill-rule:evenodd"
        dwg.add(path)

    return dwg.tostring(), proc, palette
# endregion
