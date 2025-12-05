"""
watermarking.py

This module provides functions for detecting digital watermarks in images.
It includes methods for Least Significant Bit (LSB) analysis and Frequency Domain (FFT) analysis.
"""

from io import BytesIO
from typing import Tuple

import numpy as np
from PIL import Image


def _analyze_lsb(image: Image.Image) -> float:
    """
    Performs Least Significant Bit (LSB) analysis on the image to detect hidden data.
    A non-random distribution of LSBs can indicate steganography or watermarking.

    Args:
        image: The Pillow Image object.

    Returns:
        A score from 0.0 to 1.0 indicating the likelihood of LSB manipulation.
    """
    # Convert image to grayscale for simpler LSB analysis if it's not already
    gray_image = image.convert("L")
    
    # Get LSBs of each pixel
    lsb_plane = np.array(gray_image) & 1

    # Calculate the entropy of the LSB plane
    # A perfectly random LSB plane would have an entropy close to 1 (for binary data)
    # A manipulated LSB plane might have lower entropy or specific patterns
    hist, _ = np.histogram(lsb_plane, bins=[0, 1, 2])
    probabilities = hist / hist.sum()
    probabilities = probabilities[probabilities > 0]  # Remove zero probabilities
    entropy = -np.sum(probabilities * np.log2(probabilities))

    # Normalize entropy to a score from 0 to 1.
    # Lower entropy might suggest manipulation, but this is a simplification.
    # A more sophisticated analysis would involve statistical tests.
    # For now, we'll use a heuristic: higher entropy means less likely to be LSB watermarked
    # We invert this for a "likelihood of watermark" score.
    max_entropy = 1.0  # For a binary plane with equal 0s and 1s
    if max_entropy == 0: # Avoid division by zero
        return 0.0
    
    # Simple heuristic: if entropy is low, score is high.
    # This might need fine-tuning with actual watermark examples.
    lsb_score = 1.0 - (entropy / max_entropy) if entropy < max_entropy else 0.0

    return lsb_score


def _analyze_fft(image: Image.Image) -> float:
    """
    Performs Frequency Domain (FFT) analysis on the image to detect periodic patterns
    characteristic of some frequency-domain watermarking techniques.

    Args:
        image: The Pillow Image object.

    Returns:
        A score from 0.0 to 1.0 indicating the likelihood of frequency domain watermark.
    """
    # Convert image to grayscale
    gray_image = image.convert("L")
    img_array = np.array(gray_image)

    # Perform 2D Fast Fourier Transform
    f_transform = np.fft.fft2(img_array)
    f_transform_shifted = np.fft.fftshift(f_transform)
    
    # Get the magnitude spectrum (log scale for better visualization and analysis)
    magnitude_spectrum = 20 * np.log(np.abs(f_transform_shifted) + 1e-9) # Added epsilon to avoid log(0)

    # Analyze the magnitude spectrum for unnatural peaks or periodic patterns.
    # This is a complex task and usually involves advanced image processing
    # techniques like statistical analysis of peaks, or correlation with known watermark patterns.
    # For a simple heuristic, we can look at the variance or standard deviation
    # of high-frequency components. Watermarks often introduce structured noise.
    
    # A very basic approach: look for high variance in the magnitude spectrum,
    # especially in regions where natural images typically have less energy (higher frequencies).
    
    # Define a region for high frequencies (e.g., outer parts of the spectrum)
    rows, cols = magnitude_spectrum.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create a mask for high-frequency areas (a simple ring or corners)
    # This is a simplification and might need adjustment based on watermark characteristics.
    mask = np.ones(magnitude_spectrum.shape, dtype=bool)
    # Remove a central low-frequency square region
    mask[crow - rows // 8 : crow + rows // 8, ccol - cols // 8 : ccol + cols // 8] = False
    
    high_freq_magnitudes = magnitude_spectrum[mask]
    
    # If there's significant variance in these high-frequency areas, it *could* indicate
    # structured patterns like watermarks. This is a very rough heuristic.
    fft_score = np.var(high_freq_magnitudes) / (np.max(magnitude_spectrum) ** 2) if np.max(magnitude_spectrum) > 0 else 0.0
    
    # Normalize to 0-1 range (this scaling factor is heuristic)
    fft_score = min(fft_score * 50, 1.0) # Scale and cap at 1.0

    return fft_score


def analyze_watermark(image_bytes: bytes) -> float:
    """
    The main function for watermark detection. It takes image bytes, performs
    LSB and FFT analysis, and returns a combined score indicating the likelihood
    of a watermark being present.

    Args:
        image_bytes: The image content as bytes.

    Returns:
        A score from 0.0 to 1.0, indicating the likelihood of a watermark being present.
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        image.load() # Ensure image data is loaded into memory
    except Exception as e:
        print(f"Error opening image for watermark analysis: {e}")
        return 0.0 # Return 0 if image cannot be opened

    lsb_score = _analyze_lsb(image)
    fft_score = _analyze_fft(image)

    # Combine scores. This can be a simple average or a weighted sum.
    # The weighting might need to be determined through experimentation.
    # For now, a simple average.
    combined_score = (lsb_score + fft_score) / 2.0

    return combined_score
