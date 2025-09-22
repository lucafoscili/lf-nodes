import torch

from ._common import blend_with_alpha, draw_smooth_curve, draw_straight_line, validate_image
from ...utils.helpers import hex_to_tuple

# region line_effect
def line_effect(
    image: torch.Tensor,
    points: list[tuple],
    size: int,
    color: str,
    opacity: float,
    smooth: bool
) -> torch.Tensor:
    """
    Draws a straight line or smooth curve on an image tensor.

    Args:
        image (torch.Tensor): Input image tensor of shape [1, H, W, C], values in [0, 1].
        points (list[tuple]): List of normalized (x, y) points.
        size (int): Diameter of the line in pixels.
        color (str): Hex color of the line.
        opacity (float): Opacity of the line (0.0 to 1.0).
        smooth (bool): Whether to draw a smooth curve.

    Returns:
        torch.Tensor: Image tensor with the applied line/curve.
    """
    validate_image(image, expected_shape=(3,))

    device = image.device
    _, height, width, channels = image.shape

    rgb = torch.tensor([c / 255.0 for c in hex_to_tuple(color)], dtype=torch.float32, device=device)
    rgb = rgb.view(1, 1, channels)

    alpha_mask = torch.zeros((height, width), dtype=torch.float32, device=device)

    if smooth:
        if len(points) < 3:
            raise ValueError("Smooth curve requires at least 3 points.")
        start_point = points[0]
        end_point = points[-1]
        middle_index = len(points) // 2
        middle_point = points[middle_index]

        control_points = [start_point, middle_point, end_point]
    else:
        if len(points) < 2:
            raise ValueError("Straight line requires at least 2 points.")
        control_points = [points[0], points[-1]]

    pixel_points = [(int(x * width), int(y * height)) for x, y in control_points]

    if smooth:
        alpha_mask = draw_smooth_curve(alpha_mask, pixel_points, size, opacity)
    else:
        x1, y1 = pixel_points[0]
        x2, y2 = pixel_points[1]
        alpha_mask = draw_straight_line(alpha_mask, x1, y1, x2, y2, size, opacity)

    if alpha_mask.sum().item() == 0:
        raise ValueError("Alpha mask is empty!")

    blended_image = blend_with_alpha(image.squeeze(0), rgb, alpha_mask)
    return blended_image.unsqueeze(0)
# endregion