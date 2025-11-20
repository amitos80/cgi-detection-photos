import numpy as np
from PIL import Image
import io
from skimage.feature import graycomatrix, graycoprops

def analyze_cfa(image_bytes: bytes):
    """
    Performs a simplified Color Filter Array (CFA) artifact analysis.
    A real image from a camera has a specific pattern of correlations between
    color channels due to the demosaicing process. This function looks for
    anomalies in these correlations.

    Args:
        image_bytes: The raw bytes of the image.

    Returns:
        A score between 0.0 and 1.0, where a higher score indicates a higher
        probability of manipulation.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_array = np.array(image, dtype=np.uint8)
    except Exception:
        return 0.0

    # We'll use a simplified approach: analyze the texture of the green channel,
    # which typically contains the most detail in a Bayer filter.
    # A synthetic image may have an unnaturally uniform or different texture.
    
    green_channel = image_array[:, :, 1]

    # Calculate Gray-Level Co-occurrence Matrix (GLCM)
    # This is a way to measure texture.
    glcm = graycomatrix(green_channel, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    
    # Calculate texture properties
    contrast = graycoprops(glcm, 'contrast')[0, 0]
    correlation = graycoprops(glcm, 'correlation')[0, 0]
    
    # Heuristic: Natural images tend to have high contrast and low correlation
    # in their green channel texture. CGI might be the opposite.
    # We'll create a score based on this assumption.
    
    # Normalize the values (these are heuristics)
    normalized_contrast = min(contrast / 1000.0, 1.0)
    normalized_correlation = max(0, correlation)

    # If correlation is high and contrast is low, it's more likely to be CGI
    score = (normalized_correlation * (1 - normalized_contrast))
    
    return min(score * 2.0, 1.0) # Amplify the score a bit
