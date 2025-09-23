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

    grayp = cv2.cvtColor(proc, cv2.COLOR_RGB2GRAY)
    contours, _ = cv2.findContours(grayp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys = [cv2.approxPolyDP(c, simplify_tol, True) for c in contours]

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
    for poly in polys:
        pts = [(int(pt[0][0]), int(pt[0][1])) for pt in poly]
        dwg.add(dwg.polygon(
            pts,
            fill=fill_css,
            stroke=stroke_css,
            stroke_width=stroke_width
        ))

    return dwg.tostring(), proc, palette
# endregion