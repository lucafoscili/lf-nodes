import cv2
import numpy as np
import torch

from scipy.interpolate import CubicSpline

# region apply_gaussian_blur
def apply_gaussian_blur(image: np.ndarray, kernel_size: int, sigma: float) -> np.ndarray:
    """
    Apply Gaussian blur to an image.

    Args:
        image (np.ndarray): Input image.
        kernel_size (int): Size of the kernel.
        sigma (float): Standard deviation of the Gaussian kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
# endregion

# region apply_sharpen
def apply_sharpen(image, sharpen_amount):
    """
    Apply sharpening to an image using a weighted sum.
    Args:
        image (numpy.ndarray): The input image in BGR format.
        sharpen_amount (float): The amount of sharpening to apply.
    Returns:
        numpy.ndarray: The image after applying the sharpening effect.
    """
    gaussian_blur = cv2.GaussianBlur(image, (9, 9), 10.0)
    sharpened_image = cv2.addWeighted(image, 1.0 + sharpen_amount, gaussian_blur, -sharpen_amount, 0)
    return sharpened_image
# endregion

# region blend_overlay
def blend_overlay(image: torch.Tensor, overlay: torch.Tensor, alpha_mask: torch.Tensor) -> torch.Tensor:
    """
    Blend an overlay image with a base image using an alpha mask.

    Args:
        image (torch.Tensor): The base image tensor. Shape: [1, H, W, 3].
        overlay (torch.Tensor): The overlay image tensor. Shape: [1, H, W, 3] or [1, H, W, 4].
        alpha_mask (torch.Tensor): The alpha mask tensor. Shape: [1, H, W, 1].

    Returns:
        torch.Tensor: The resulting blended image tensor. Shape: [1, H, W, 3].
    """
    if overlay.shape[-1] > image.shape[-1]:
        overlay_alpha = overlay[..., 3:4]
        overlay = overlay[..., :3]

        alpha_mask = alpha_mask * overlay_alpha

    elif overlay.shape[-1] < image.shape[-1]:
        raise ValueError(f"Overlay image has fewer channels ({overlay.shape[-1]}) than base image ({image.shape[-1]}).")

    if alpha_mask.dim() == 4 and alpha_mask.shape[-1] == 1:
        adjusted_alpha = alpha_mask
    elif alpha_mask.dim() == 3 and alpha_mask.shape[-1] == 1:
        adjusted_alpha = alpha_mask.unsqueeze(-1)
    elif alpha_mask.dim() == 3 and alpha_mask.shape[-1] != 1:
        raise ValueError(f"Alpha mask has unexpected shape: {alpha_mask.shape}")
    else:
        raise ValueError(f"Unsupported alpha_mask dimensions: {alpha_mask.dim()}")

    blended_image = image * (1 - adjusted_alpha) + overlay * adjusted_alpha
    return blended_image
# endregion

# region blend_with_alpha
def blend_with_alpha(image, rgb, alpha_mask):
    """
    Blend an RGB color with an image using an alpha mask.

    Args:
        image (torch.Tensor): The base image tensor.
        rgb (torch.Tensor): Tensor containing the RGB color to blend.
        alpha_mask (torch.Tensor): The alpha mask indicating blending proportions.

    Returns:
        torch.Tensor: The resulting blended image tensor.
    """
    blended_image = image * (1 - alpha_mask.unsqueeze(-1)) + rgb * alpha_mask.unsqueeze(-1)
    return blended_image
# endregion

# region detect_edges
def detect_edges(image: np.ndarray, method: str = 'sobel', normalize: bool = True) -> np.ndarray:
    """
    Detect edges in an image using the specified method.

    Args:
        image (np.ndarray): Grayscale input image.
        method (str): Edge detection method ('sobel' or 'laplacian').
        normalize (bool): Whether to normalize the edge map to [0, 1].

    Returns:
        np.ndarray: Edge map of the input image.
    """
    if method == 'sobel':
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobel_x**2 + sobel_y**2)
    elif method == 'laplacian':
        edges = cv2.Laplacian(image, cv2.CV_64F)
    else:
        raise ValueError(f"Unsupported edge detection method: {method}")
    
    if normalize:
        edges = edges / edges.max() if edges.max() != 0 else edges
    
    return edges
# endregion

# region draw_smooth_curve
def draw_smooth_curve(alpha_mask, points, size, opacity, num_samples=200):
    """
    Draws a smooth curve through the given points on the alpha mask.

    Args:
        alpha_mask (torch.Tensor): Alpha mask to draw on.
        points (list[tuple]): List of (x, y) control points for the curve.
        size (int): Brush diameter in pixels.
        opacity (float): Opacity of the curve.
        num_samples (int): Number of points to sample along the curve.

    Returns:
        torch.Tensor: Updated alpha mask.
    """
    points = np.array(points)

    t = np.linspace(0, 1, len(points))
    spline_x = CubicSpline(t, points[:, 0], bc_type='clamped')
    spline_y = CubicSpline(t, points[:, 1], bc_type='clamped')

    distances = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
    total_length = np.sum(distances)
    num_samples = max(num_samples, int(total_length * 50))

    t_new = np.linspace(0, 1, num_samples)
    curve_x = spline_x(t_new)
    curve_y = spline_y(t_new)

    for i in range(len(curve_x) - 1):
        x1, y1 = int(curve_x[i]), int(curve_y[i])
        x2, y2 = int(curve_x[i + 1]), int(curve_y[i + 1])
        alpha_mask = draw_straight_line(alpha_mask, x1, y1, x2, y2, size, opacity)

    return alpha_mask
# endregion

# region draw_straight_line
def draw_straight_line(alpha_mask, x1, y1, x2, y2, size, opacity):
    """
    Draws a straight line between two points (x1, y1) and (x2, y2) on the alpha mask.

    Args:
        alpha_mask (torch.Tensor): Alpha mask to draw on.
        x1, y1, x2, y2 (int): Coordinates of the two points.
        size (int): Brush diameter in pixels.
        opacity (float): Opacity of the line.

    Returns:
        torch.Tensor: Updated alpha mask.
    """
    steps = max(abs(x2 - x1), abs(y2 - y1))
    xs = torch.linspace(x1, x2, steps, device=alpha_mask.device)
    ys = torch.linspace(y1, y2, steps, device=alpha_mask.device)

    for x, y in zip(xs, ys):
        x, y = int(x), int(y)
        y_grid, x_grid = torch.meshgrid(
            torch.arange(alpha_mask.shape[0], device=alpha_mask.device),
            torch.arange(alpha_mask.shape[1], device=alpha_mask.device),
            indexing='ij'
        )
        dist_squared = (x_grid - x) ** 2 + (y_grid - y) ** 2
        stroke_mask = (dist_squared <= (size / 2) ** 2).float() * opacity
        alpha_mask = torch.clamp(alpha_mask + stroke_mask, max=1.0)

    return alpha_mask
# endregion

# region interpolate_curve
def interpolate_curve(points, num_samples=100):
    """
    Interpolates a smooth curve through given points using Catmull-Rom splines.
    Args:
        points (list[tuple]): List of (x, y) points.
        num_samples (int): Number of samples for the interpolated curve.
    Returns:
        list[tuple]: Interpolated points.
    """
    points = np.array(points)
    t = np.linspace(0, 1, len(points))

    spline_x = CubicSpline(t, points[:, 0], bc_type='clamped')
    spline_y = CubicSpline(t, points[:, 1], bc_type='clamped')

    distances = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
    total_length = np.sum(distances)
    num_samples = max(num_samples, int(total_length * 200))

    t_new = np.linspace(0, 1, num_samples)
    return list(zip(spline_x(t_new), spline_y(t_new)))
# endregion

# region merge_channels
def merge_channels(channels: tuple, color_space: str = 'RGB') -> np.ndarray:
    """
    Merge individual channels into an image.

    Args:
        channels (tuple): Individual image channels.
        color_space (str): The target color space ('RGB' or 'LAB').

    Returns:
        np.ndarray: Merged image.
    """
    if color_space == 'RGB':
        return cv2.merge(channels)
    elif color_space == 'LAB':
        merged_lab = cv2.merge(channels)
        return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    else:
        raise ValueError(f"Unsupported color space: {color_space}")
# endregion
    
# region split_channels
def split_channels(image: np.ndarray, color_space: str = 'RGB') -> tuple:
    """
    Split image into individual channels.

    Args:
        image (np.ndarray): Input image.
        color_space (str): The color space of the input image ('RGB' or 'LAB').

    Returns:
        tuple: Splitted channels (e.g., R, G, B or L, A, B).
    """
    if color_space == 'RGB':
        return cv2.split(image)
    elif color_space == 'LAB':
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        return cv2.split(lab_image)
    else:
        raise ValueError(f"Unsupported color space: {color_space}")
# endregion

# region validate_image
def validate_image(image: torch.Tensor, expected_shape: tuple = (3,)) -> None:
    """
    Validate that the image tensor has the expected shape and dimensions.

    Args:
        image (torch.Tensor): Input image tensor.
        expected_shape (tuple): Expected shape of the image channels (e.g., 3 for RGB).

    Raises:
        ValueError: If the image doesn't match the expected dimensions.
    """
    if image.shape[0] != 1 or image.ndim != 4 or image.shape[-1] != expected_shape[0]:
        raise ValueError(f"Expected image shape (1, H, W, {expected_shape[0]}), got {image.shape}")
# endregion