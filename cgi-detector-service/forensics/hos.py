import numpy as np
import pywt
from PIL import Image
import io
from scipy.stats import kurtosis, skew

def analyze_hos(image_bytes: bytes):
    """
    Performs Higher-Order Wavelet Statistics (HOS) analysis.
    Natural images have predictable statistical distributions in the wavelet
    domain. Synthetic images often deviate from these norms.

    Args:
        image_bytes: The raw bytes of the image.

    Returns:
        A score between 0.0 and 1.0, where a higher score indicates a higher
        probability of the image being synthetic.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('L') # Grayscale
        image_array = np.array(image, dtype=np.float32)
    except Exception:
        return 0.0

    # Perform a 2-level wavelet decomposition
    coeffs = pywt.dwt2(image_array, 'db1')
    cA, (cH, cV, cD) = coeffs

    # We will analyze the detail coefficients (horizontal, vertical, diagonal)
    detail_coeffs = np.concatenate([cH.flatten(), cV.flatten(), cD.flatten()])

    # Calculate higher-order statistics
    # Natural images tend to have highly non-Gaussian distributions (high kurtosis)
    # in their wavelet coefficients.
    k = kurtosis(detail_coeffs)
    
    # Heuristic: Kurtosis for natural images is typically high (e.g., > 5).
    # A low kurtosis suggests a more uniform, less "peaky" distribution,
    # which can be a sign of a synthetic image.
    
    # We'll define a "natural" range for kurtosis and score based on deviation.
    # Let's say a natural image has kurtosis > 5.
    
    if k < 3: # Very low kurtosis, highly suspicious
        score = 1.0
    elif k < 5:
        score = 0.7
    else:
        score = 0.1

    return score
