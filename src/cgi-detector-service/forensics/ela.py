from PIL import Image
import numpy as np
import io

def analyze_ela(image_bytes: bytes, quality=95):
    """
    Performs Error Level Analysis (ELA) on an image.

    Args:
        image_bytes: The raw bytes of the image.
        quality: The JPEG quality to re-save the image at.

    Returns:
        A score between 0.0 and 1.0, where a higher score indicates a higher
        probability of manipulation.
    """
    try:
        original_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception:
        return 0.0 # Cannot process image

    # Re-save the image at a specific quality
    resaved_buffer = io.BytesIO()
    original_image.save(resaved_buffer, 'JPEG', quality=quality)
    resaved_image = Image.open(resaved_buffer)

    # Calculate the difference
    original_array = np.array(original_image, dtype=np.float32)
    resaved_array = np.array(resaved_image, dtype=np.float32)
    
    diff = np.abs(original_array - resaved_array)
    
    # Scale the difference to be more visible
    diff = diff * 10
    diff = np.clip(diff, 0, 255)

    # A simple metric: high variance in the diff suggests manipulation
    mean_diff = np.mean(diff)
    
    # Normalize the score (this is a heuristic)
    # A mean difference above a certain threshold could indicate tampering.
    # For this example, we'll say a mean diff over 10 is suspicious.
    score = min(mean_diff / 20.0, 1.0)

    return score
