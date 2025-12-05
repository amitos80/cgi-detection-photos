import numpy as np
import cv2
from scipy.stats import entropy
from typing import Tuple

def _apply_grayscale_and_resize(image: np.ndarray) -> np.ndarray:
    """Applies grayscale and resizes the image to a standard size for analysis."""
    if len(image.shape) == 3 and image.shape[2] == 3:  # Check if it's a color image
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image
    return cv2.resize(gray_image, (256, 256), interpolation=cv2.INTER_AREA)

def _least_significant_bit_analysis(image_bytes: bytes) -> float:
    """
    Performs Least Significant Bit (LSB) analysis on the image.
    A non-random distribution of LSBs can indicate simple steganography or watermarking.
    The analysis calculates the entropy of the LSB plane and compares it to a threshold.
    Returns a score from 0.0 to 1.0, where a higher score indicates a higher likelihood of LSB manipulation.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return 0.0  # Could not decode image

        gray_image = _apply_grayscale_and_resize(image)

        # Extract the LSB plane
        lsb_plane = (gray_image & 1).flatten()

        # Calculate the histogram of the LSB plane (should be close to 0.5 for 0s and 1s if random)
        hist, _ = np.histogram(lsb_plane, bins=[0, 1, 2])
        probabilities = hist / hist.sum()

        # Calculate entropy of the LSB plane
        lsb_entropy = entropy(probabilities, base=2)

        # A perfectly random LSB plane would have an entropy close to 1 (for two outcomes).
        # A lower entropy suggests non-randomness, possibly due to LSB-based watermarking.
        # This threshold might need tuning based on a dataset of watermarked/non-watermarked images.
        # For now, a simple heuristic:
        # If entropy is very low, it's highly likely to be manipulated.
        # If entropy is close to 1, it's likely not LSB watermarked.
        
        # Normalize the entropy to a 0-1 score, where 1 means high likelihood of watermark
        # A lower entropy value (closer to 0) means higher likelihood of manipulation.
        # So we want to invert this: 1 - lsb_entropy / max_possible_entropy (which is 1 for binary)
        lsb_score = 1.0 - lsb_entropy if lsb_entropy <= 1.0 else 0.0
        return lsb_score

    except Exception as e:
        print(f"Error during LSB analysis: {e}")
        return 0.0

def _frequency_domain_analysis(image_bytes: bytes) -> float:
    """
    Performs Frequency Domain (FFT) analysis on the image.
    Analyzes the magnitude spectrum for unnatural peaks or periodic patterns,
    characteristic of some frequency-domain watermarking techniques.
    Returns a score from 0.0 to 1.0, where a higher score indicates a higher likelihood of a frequency-domain watermark.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return 0.0  # Could not decode image

        gray_image = _apply_grayscale_and_resize(image)

        # Convert to float32 for FFT
        f = np.fft.fft2(gray_image)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-10) # Add epsilon to prevent log(0)

        # Analyze magnitude_spectrum for abnormal peaks or patterns.
        # This is a complex area and often requires domain-specific knowledge or ML.
        # For a basic detection, we can look for high variance or unusual concentrated energy.
        # A simple approach is to look for peaks that deviate significantly from the general spectrum.

        # Let's try to detect strong, localized peaks in the high-frequency areas
        # which might indicate embedded patterns.
        # We can normalize the spectrum and look for values significantly above the mean.
        
        mean_magnitude = np.mean(magnitude_spectrum)
        std_magnitude = np.std(magnitude_spectrum)

        # Count pixels that are significantly brighter than average (e.g., 3 standard deviations above mean)
        # These could correspond to strong frequency components of a watermark.
        threshold = mean_magnitude + 3 * std_magnitude
        peak_count = np.sum(magnitude_spectrum > threshold)

        # Normalize peak_count by image size to get a score.
        # The exact normalization and threshold might need tuning.
        max_possible_peaks = gray_image.size
        if max_possible_peaks == 0:
            return 0.0
        
        fft_score = min(1.0, peak_count / (max_possible_peaks * 0.01)) # Heuristic scaling

        return fft_score

    except Exception as e:
        print(f"Error during FFT analysis: {e}")
        return 0.0

def analyze_watermark(image_bytes: bytes) -> float:
    """
    Analyzes an image for the presence of digital watermarks using multiple techniques.
    Combines Least Significant Bit (LSB) analysis and Frequency Domain (FFT) analysis.

    Args:
        image_bytes: The raw bytes of the image to analyze.

    Returns:
        A score from 0.0 to 1.0, indicating the likelihood of a watermark being present.
        A higher score means a higher probability of a watermark.
    """
    lsb_score = _least_significant_bit_analysis(image_bytes)
    fft_score = _frequency_domain_analysis(image_bytes)

    # Combine scores. A simple average for now, but can be weighted based on
    # empirical performance of each method.
    combined_score = (lsb_score + fft_score) / 2.0

    return combined_score

if __name__ == '__main__':
    # Example usage with dummy image bytes for testing
    # In a real scenario, you would load an actual image file.
    
    # Create a dummy blank image (e.g., a black square)
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    _, encoded_image = cv2.imencode('.png', dummy_image)
    dummy_image_bytes = encoded_image.tobytes()

    print("--- Testing with a blank image (expected low score) ---")
    score_blank = analyze_watermark(dummy_image_bytes)
    print(f"Watermark score for blank image: {score_blank:.4f}")
    assert score_blank < 0.5, "Blank image should have a low watermark score"

    # Example of a simple LSB-watermarked image (not robust, for demo)
    # Create a simple image and modify its LSBs
    img_clean = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    
    # Embed a "watermark" by setting a pattern in LSBs
    img_watermarked_lsb = img_clean.copy()
    for i in range(img_watermarked_lsb.shape[0]):
        for j in range(img_watermarked_lsb.shape[1]):
            if (i + j) % 2 == 0:
                img_watermarked_lsb[i, j] = (img_watermarked_lsb[i, j] & ~1) | 1 # Set LSB to 1
            else:
                img_watermarked_lsb[i, j] = (img_watermarked_lsb[i, j] & ~1) | 0 # Set LSB to 0
    
    _, encoded_lsb_image = cv2.imencode('.png', img_watermarked_lsb)
    lsb_watermarked_image_bytes = encoded_lsb_image.tobytes()

    print("
--- Testing with a simple LSB-watermarked image (expected higher LSB score) ---")
    score_lsb_watermarked = analyze_watermark(lsb_watermarked_image_bytes)
    print(f"Watermark score for LSB watermarked image: {score_lsb_watermarked:.4f}")
    assert score_lsb_watermarked > 0.5, "LSB watermarked image should have a higher score"

    # You would typically load actual image files here for more realistic testing
    # with open('path/to/watermarked_image.png', 'rb') as f:
    #     watermarked_image_bytes_real = f.read()
    # score_real_watermarked = analyze_watermark(watermarked_image_bytes_real)
    # print(f"Watermark score for real watermarked image: {score_real_watermarked:.4f}")

    # with open('path/to/clean_image.png', 'rb') as f:
    #     clean_image_bytes_real = f.read()
    # score_real_clean = analyze_watermark(clean_image_bytes_real)
    # print(f"Watermark score for real clean image: {score_real_clean:.4f}")