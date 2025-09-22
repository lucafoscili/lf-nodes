import numpy as np

# region get_otsu_threshold
def get_otsu_threshold(image: np.ndarray, nbins: int = 256) -> float:
    """
    Compute Otsu's threshold for a grayscale image.
    Otsu's method determines an optimal global threshold value from the image histogram
    by maximizing the between-class variance. The function assumes the input image is
    normalized to the range [0.0, 1.0].

    Args:
        image (np.ndarray): Input grayscale image as a NumPy array with values in [0.0, 1.0].
        nbins (int, optional): Number of bins to use for the histogram. Default is 256.
        
    Returns:
        float: The computed threshold value in the range [0.0, 1.0].
    """
    hist, bins = np.histogram(image.ravel(), bins=nbins, range=(0.0,1.0))
    bin_centers = (bins[:-1] + bins[1:]) * 0.5

    total = image.size
    sum_total = (hist * bin_centers).sum()

    sum_b = 0.0
    w_b   = 0.0
    max_var = 0.0
    thresh = 0.0

    for i in range(nbins):
        w_b += hist[i]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break

        sum_b += hist[i] * bin_centers[i]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f

        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            thresh = bin_centers[i]

    return thresh
# endregion