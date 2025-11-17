import io
from PIL import Image
import numpy as np

def analyze_jpeg_ghost(image_bytes: bytes) -> float:
    """
    Analyzes an image using JPEG Ghost analysis to detect manipulation.

    This technique re-compresses the image at various JPEG quality levels
    and calculates the Sum of Squared Differences (SSD) to find the likely
    original compression quality. It then analyzes the difference map at
    this quality level to identify inconsistencies that suggest splicing.

    Args:
        image_bytes: The image content as bytes.

    Returns:
        A score from 0.0 to 1.0, where a higher score indicates a higher
        probability of manipulation.
    """
    try:
        original_image = Image.open(io.BytesIO(image_bytes)).convert("L")  # Convert to grayscale
    except Exception:
        return 0.0  # Return 0 if image cannot be opened or is not a JPEG

    width, height = original_image.size
    if width < 16 or height < 16:  # Images too small for meaningful analysis
        return 0.0

    min_ssd = float('inf')
    best_quality = -1
    ssd_map = None

    # Loop through a range of JPEG quality levels
    for quality in range(75, 101):  # Common range for original JPEG compression
        buffer = io.BytesIO()
        original_image.save(buffer, format="JPEG", quality=quality)
        recompressed_image = Image.open(buffer).convert("L")

        # Resize recompressed_image to match original_image if dimensions differ
        if recompressed_image.size != original_image.size:
            recompressed_image = recompressed_image.resize(original_image.size, Image.Resampling.LANCZOS)

        diff = np.array(original_image, dtype=np.float32) - np.array(recompressed_image, dtype=np.float32)
        current_ssd = np.sum(diff**2)

        if current_ssd < min_ssd:
            min_ssd = current_ssd
            best_quality = quality
            ssd_map = diff**2

    if ssd_map is None:
        return 0.0

    # Analyze the variance of the SSD map
    # A high variance suggests some regions matched the compression level perfectly
    # while others did not (spliced parts).
    variance = np.var(ssd_map)

    # Normalize the variance to a score between 0 and 1.
    # The normalization factor might need tuning based on empirical results.
    # For now, a simple heuristic: higher variance means higher score.
    # Max possible variance for 8-bit images (diff range -255 to 255, diff^2 range 0 to 65025)
    # is roughly (65025 - 0)^2 / 4 = 1.05 * 10^9 (if half pixels are 0 and half are 65025)
    # A more practical max variance for typical images might be much lower.
    # Let's use a heuristic threshold for normalization.
    max_expected_variance = 1000000.0 # This value might need adjustment
    score = min(1.0, variance / max_expected_variance)

    return score
