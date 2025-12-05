"""
Scene Lighting and Text Consistency Analysis Module

This module analyzes lighting consistency across an image to detect CGI or composite images.
CGI and manipulated images often exhibit inconsistent lighting between different regions,
particularly between inserted objects/text and the background scene.

Key Detection Strategies:
1. Lighting Direction Estimation: Estimates dominant light direction from gradients
2. Region-based Analysis: Compares lighting across different image regions
3. High-Contrast Region Detection: Identifies text and pattern areas without OCR
4. Shadow Consistency: Analyzes shadow direction consistency
"""

import numpy as np
from PIL import Image
from io import BytesIO
from scipy import ndimage
from scipy.stats import circmean, circstd
from skimage import filters, feature, morphology, measure
from skimage.util import img_as_float
import warnings

warnings.filterwarnings('ignore')


def analyze_lighting_consistency(image_bytes: bytes) -> float:
    """
    Analyzes lighting consistency across the image to detect CGI or composite artifacts.

    Args:
        image_bytes: Raw image bytes

    Returns:
        A score between 0 and 1, where higher values indicate lighting inconsistencies
        suggestive of CGI or image manipulation
    """
    try:
        # Load image
        image = Image.open(BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array
        img_array = np.array(image)

        # Convert to grayscale for analysis
        gray = np.mean(img_array, axis=2).astype(np.uint8)

        # Perform multiple lighting analyses
        direction_score = _analyze_lighting_direction_consistency(gray)
        region_score = _analyze_regional_lighting_consistency(gray, img_array)
        shadow_score = _analyze_shadow_consistency(gray)
        contrast_region_score = _analyze_high_contrast_regions(gray)

        # Weight the different components
        weights = {
            'direction': 0.30,
            'region': 0.30,
            'shadow': 0.25,
            'contrast': 0.15
        }

        # Calculate weighted average
        final_score = (
            direction_score * weights['direction'] +
            region_score * weights['region'] +
            shadow_score * weights['shadow'] +
            contrast_region_score * weights['contrast']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in lighting consistency analysis: {e}")
        return 0.0


def _analyze_lighting_direction_consistency(gray_image: np.ndarray) -> float:
    """
    Analyzes consistency of lighting direction across the image.
    Inconsistent lighting directions suggest composite or CGI images.

    Args:
        gray_image: Grayscale image as numpy array

    Returns:
        Inconsistency score (0-1), higher means inconsistent lighting
    """
    try:
        # Calculate gradients
        grad_x = ndimage.sobel(gray_image.astype(float), axis=1)
        grad_y = ndimage.sobel(gray_image.astype(float), axis=0)

        # Calculate gradient magnitude and direction
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_direction = np.arctan2(grad_y, grad_x)

        # Divide image into grid
        block_size = 64
        height, width = gray_image.shape

        # Collect dominant directions from blocks with significant gradients
        block_directions = []
        block_strengths = []

        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block_mag = gradient_magnitude[i:i+block_size, j:j+block_size]
                block_dir = gradient_direction[i:i+block_size, j:j+block_size]

                # Only consider blocks with significant gradients
                mean_magnitude = np.mean(block_mag)
                if mean_magnitude > 10:  # Threshold for significant gradients
                    # Estimate dominant direction using circular statistics
                    # Weight by magnitude
                    weights = block_mag.flatten()
                    directions = block_dir.flatten()

                    # Calculate weighted circular mean
                    weighted_cos = np.sum(weights * np.cos(directions))
                    weighted_sin = np.sum(weights * np.sin(directions))
                    dominant_direction = np.arctan2(weighted_sin, weighted_cos)

                    block_directions.append(dominant_direction)
                    block_strengths.append(mean_magnitude)

        if len(block_directions) < 4:  # Need at least 4 blocks
            return 0.0

        block_directions = np.array(block_directions)
        block_strengths = np.array(block_strengths)

        # Calculate circular standard deviation
        # Low std = consistent lighting (natural)
        # High std = inconsistent lighting (suspicious)
        circ_std = circstd(block_directions)

        # Natural images typically have consistent lighting: std < 0.8 radians
        # CGI/composite images often have inconsistent lighting: std > 1.2 radians
        if circ_std > 1.2:
            score = min((circ_std - 0.8) / 0.8, 1.0)
        elif circ_std > 0.8:
            score = (circ_std - 0.8) / 0.4 * 0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in lighting direction analysis: {e}")
        return 0.0


def _analyze_regional_lighting_consistency(gray_image: np.ndarray, color_image: np.ndarray) -> float:
    """
    Analyzes lighting consistency between different regions of the image.
    Compares bright and dark regions for consistent light sources.

    Args:
        gray_image: Grayscale image
        color_image: Color image

    Returns:
        Inconsistency score (0-1)
    """
    try:
        # Apply Gaussian blur to reduce noise
        blurred = filters.gaussian(gray_image, sigma=2)

        # Identify bright and dark regions
        threshold = filters.threshold_otsu(blurred)
        bright_regions = blurred > threshold
        dark_regions = blurred < threshold

        # Analyze gradient directions in bright vs dark regions
        grad_x = ndimage.sobel(gray_image.astype(float), axis=1)
        grad_y = ndimage.sobel(gray_image.astype(float), axis=0)
        gradient_direction = np.arctan2(grad_y, grad_x)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Calculate dominant direction in bright regions
        bright_mask = bright_regions & (gradient_magnitude > 10)
        if np.sum(bright_mask) > 100:
            bright_dirs = gradient_direction[bright_mask]
            bright_mean_dir = circmean(bright_dirs)
        else:
            return 0.0

        # Calculate dominant direction in dark regions
        dark_mask = dark_regions & (gradient_magnitude > 10)
        if np.sum(dark_mask) > 100:
            dark_dirs = gradient_direction[dark_mask]
            dark_mean_dir = circmean(dark_dirs)
        else:
            return 0.0

        # Calculate angular difference
        angle_diff = np.abs(bright_mean_dir - dark_mean_dir)
        # Normalize to [0, π]
        if angle_diff > np.pi:
            angle_diff = 2 * np.pi - angle_diff

        # Bright and dark regions should have related lighting directions
        # Large differences (> π/2) suggest inconsistent lighting
        if angle_diff > np.pi / 2:
            score = (angle_diff - np.pi / 3) / (np.pi / 2)
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in regional lighting analysis: {e}")
        return 0.0


def _analyze_shadow_consistency(gray_image: np.ndarray) -> float:
    """
    Analyzes shadow consistency across the image.
    Inconsistent shadow directions indicate composite or CGI images.

    Args:
        gray_image: Grayscale image

    Returns:
        Inconsistency score (0-1)
    """
    try:
        # Detect dark regions that could be shadows
        blurred = filters.gaussian(gray_image, sigma=3)

        # Use adaptive thresholding to find dark regions
        block_size = 51
        threshold = filters.threshold_local(blurred, block_size, offset=10)
        dark_regions = blurred < threshold

        # Clean up small noise
        dark_regions = morphology.remove_small_objects(dark_regions, min_size=100)

        # Label connected components
        labeled = measure.label(dark_regions)
        regions = measure.regionprops(labeled)

        if len(regions) < 2:  # Need at least 2 potential shadow regions
            return 0.0

        # Analyze orientation of shadow-like regions
        orientations = []
        for region in regions:
            # Only consider regions that could be shadows (not too circular)
            if region.area > 200 and region.eccentricity > 0.5:
                orientations.append(region.orientation)

        if len(orientations) < 2:
            return 0.0

        orientations = np.array(orientations)

        # Calculate circular standard deviation of orientations
        # Consistent shadows should have similar orientations
        circ_std = circstd(orientations)

        # Shadows from the same light source should be aligned (std < 0.5)
        # Multiple light sources or CGI may have varied shadows (std > 1.0)
        if circ_std > 1.0:
            score = min((circ_std - 0.5) / 1.0, 1.0)
        elif circ_std > 0.5:
            score = (circ_std - 0.5) / 0.5 * 0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in shadow consistency analysis: {e}")
        return 0.0


def _analyze_high_contrast_regions(gray_image: np.ndarray) -> float:
    """
    Detects and analyzes high-contrast regions (text, patterns) for lighting consistency.
    Text and patterns added to CGI often have inconsistent lighting with the scene.

    Args:
        gray_image: Grayscale image

    Returns:
        Inconsistency score (0-1)
    """
    try:
        # Detect edges which are prominent in text
        edges = feature.canny(gray_image, sigma=1.5)

        # Calculate local edge density
        kernel_size = 15
        kernel = morphology.disk(kernel_size)
        edge_density = ndimage.convolve(edges.astype(float), kernel.astype(float))

        # Find high-edge-density regions (potential text/patterns)
        if edge_density[edge_density > 0].size == 0:
            return 0.0
        high_density_threshold = np.percentile(edge_density[edge_density > 0], 90)
        text_like_regions = edge_density > high_density_threshold

        if np.sum(text_like_regions) < 100:  # Not enough text-like regions
            return 0.0

        # Calculate gradients
        grad_x = ndimage.sobel(gray_image.astype(float), axis=1)
        grad_y = ndimage.sobel(gray_image.astype(float), axis=0)
        gradient_direction = np.arctan2(grad_y, grad_x)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Analyze lighting in text regions vs non-text regions
        text_mask = text_like_regions & (gradient_magnitude > 10)
        non_text_mask = ~text_like_regions & (gradient_magnitude > 10)

        if np.sum(text_mask) < 50 or np.sum(non_text_mask) < 50:
            return 0.0

        # Calculate mean directions
        text_dir = circmean(gradient_direction[text_mask])
        non_text_dir = circmean(gradient_direction[non_text_mask])

        # Calculate angular difference
        angle_diff = np.abs(text_dir - non_text_dir)
        if angle_diff > np.pi:
            angle_diff = 2 * np.pi - angle_diff

        # Large differences suggest text was added with different lighting
        if angle_diff > np.pi / 2:
            score = (angle_diff - np.pi / 4) / (3 * np.pi / 4)
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in high-contrast region analysis: {e}")
        return 0.0
