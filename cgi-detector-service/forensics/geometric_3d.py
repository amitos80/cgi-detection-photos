"""
3D Geometric Consistency Analysis Module

This module analyzes geometric properties of objects in images to detect CGI.
CGI models often exhibit unnatural smoothness, perfect symmetry, or artificial
geometric patterns that can be distinguished from real-world objects.

Key Detection Strategies:
1. Symmetry Analysis: CGI often has near-perfect bilateral symmetry
2. Smoothness Detection: CGI surfaces are often overly smooth
3. Edge Regularity: CGI edges can be unnaturally regular and perfect
4. Gradient Consistency: Analyzes lighting gradient patterns
"""

import numpy as np
from PIL import Image
from io import BytesIO
from scipy import ndimage
from scipy.stats import entropy
from skimage import filters, feature, measure
from skimage.morphology import disk
import warnings

warnings.filterwarnings('ignore')


def analyze_geometric_consistency(image_bytes: bytes) -> float:
    """
    Performs geometric consistency analysis on an image to detect CGI artifacts.

    Args:
        image_bytes: Raw image bytes

    Returns:
        A score between 0 and 1, where higher values indicate higher likelihood of CGI
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

        # Perform multiple geometric analyses
        symmetry_score = _analyze_symmetry(gray)
        smoothness_score = _analyze_smoothness(gray)
        edge_regularity_score = _analyze_edge_regularity(gray)
        gradient_score = _analyze_gradient_consistency(gray)

        # Weight the different components
        weights = {
            'symmetry': 0.25,
            'smoothness': 0.30,
            'edge_regularity': 0.25,
            'gradient': 0.20
        }

        # Calculate weighted average
        final_score = (
            symmetry_score * weights['symmetry'] +
            smoothness_score * weights['smoothness'] +
            edge_regularity_score * weights['edge_regularity'] +
            gradient_score * weights['gradient']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in geometric consistency analysis: {e}")
        return 0.0


def _analyze_symmetry(gray_image: np.ndarray) -> float:
    """
    Analyzes bilateral symmetry. CGI often has unnaturally perfect symmetry.

    Args:
        gray_image: Grayscale image as numpy array

    Returns:
        Symmetry score (0-1), higher means more suspicious symmetry
    """
    try:
        height, width = gray_image.shape

        # Split image in half vertically
        mid = width // 2
        left_half = gray_image[:, :mid]
        right_half = gray_image[:, mid:2*mid]

        # Flip right half horizontally for comparison
        right_half_flipped = np.fliplr(right_half)

        # Ensure same dimensions
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]

        # Calculate correlation between halves
        correlation = np.corrcoef(left_half.flatten(), right_half_flipped.flatten())[0, 1]

        # Perfect symmetry (correlation close to 1) is suspicious in natural images
        # Natural images typically have correlation between 0.3-0.7
        # CGI often has correlation > 0.8
        if correlation > 0.85:
            score = (correlation - 0.7) / 0.3  # Scale 0.7-1.0 to 0-1
        elif correlation > 0.75:
            score = (correlation - 0.6) / 0.4 * 0.5  # Scale 0.6-1.0 to 0-0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in symmetry analysis: {e}")
        return 0.0


def _analyze_smoothness(gray_image: np.ndarray) -> float:
    """
    Analyzes surface smoothness. CGI often has unnaturally smooth surfaces.

    Args:
        gray_image: Grayscale image as numpy array

    Returns:
        Smoothness score (0-1), higher means unnaturally smooth
    """
    try:
        # Calculate local variance using a sliding window
        footprint = disk(5)
        local_mean = ndimage.generic_filter(gray_image.astype(float), np.mean, footprint=footprint)
        local_var = ndimage.generic_filter(gray_image.astype(float), np.var, footprint=footprint)

        # Calculate the coefficient of variation of local variance
        # Low variance across the image indicates unnatural smoothness
        variance_of_variance = np.var(local_var)
        mean_variance = np.mean(local_var)

        if mean_variance > 0:
            cv = np.sqrt(variance_of_variance) / mean_variance
        else:
            cv = 0

        # Natural images typically have CV > 0.5
        # CGI often has CV < 0.3 (more uniform smoothness)
        if cv < 0.3:
            score = 1.0 - (cv / 0.3)  # Scale 0-0.3 to 1-0
        elif cv < 0.5:
            score = (0.5 - cv) / 0.2 * 0.5  # Scale 0.3-0.5 to 0.5-0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in smoothness analysis: {e}")
        return 0.0


def _analyze_edge_regularity(gray_image: np.ndarray) -> float:
    """
    Analyzes edge regularity. CGI often has overly regular and perfect edges.

    Args:
        gray_image: Grayscale image as numpy array

    Returns:
        Edge regularity score (0-1), higher means suspiciously regular edges
    """
    try:
        # Detect edges using Canny
        edges = feature.canny(gray_image, sigma=2)

        # Find contours
        contours = measure.find_contours(edges, 0.5)

        if len(contours) == 0:
            return 0.0

        # Analyze curvature regularity of contours
        regularity_scores = []

        for contour in contours:
            if len(contour) < 10:  # Skip very short contours
                continue

            # Calculate curvature along the contour
            # Using finite differences
            dx = np.gradient(contour[:, 0])
            dy = np.gradient(contour[:, 1])

            # Second derivatives
            ddx = np.gradient(dx)
            ddy = np.gradient(dy)

            # Curvature formula
            curvature = np.abs(dx * ddy - dy * ddx) / (dx**2 + dy**2 + 1e-8)**1.5

            # Calculate entropy of curvature distribution
            # Low entropy = regular curvature = suspicious for CGI
            hist, _ = np.histogram(curvature, bins=20, density=True)
            hist = hist + 1e-10  # Avoid log(0)
            curv_entropy = entropy(hist)

            # Natural contours have high entropy (varied curvature)
            # CGI contours often have low entropy (uniform curvature)
            if curv_entropy < 1.5:
                regularity_scores.append(1.0 - (curv_entropy / 1.5))
            else:
                regularity_scores.append(0.0)

        if len(regularity_scores) == 0:
            return 0.0

        # Return average regularity score
        return float(np.clip(np.mean(regularity_scores), 0.0, 1.0))

    except Exception as e:
        print(f"Error in edge regularity analysis: {e}")
        return 0.0


def _analyze_gradient_consistency(gray_image: np.ndarray) -> float:
    """
    Analyzes gradient consistency. CGI often has overly consistent lighting gradients.

    Args:
        gray_image: Grayscale image as numpy array

    Returns:
        Gradient consistency score (0-1), higher means suspiciously consistent
    """
    try:
        # Calculate image gradients
        grad_x = ndimage.sobel(gray_image, axis=1)
        grad_y = ndimage.sobel(gray_image, axis=0)

        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)

        # Calculate gradient direction
        gradient_direction = np.arctan2(grad_y, grad_x)

        # Divide image into blocks and analyze gradient consistency
        block_size = 32
        height, width = gray_image.shape

        direction_variances = []

        for i in range(0, height - block_size, block_size):
            for j in range(0, width - block_size, block_size):
                block_dir = gradient_direction[i:i+block_size, j:j+block_size]
                block_mag = gradient_magnitude[i:i+block_size, j:j+block_size]

                # Only consider blocks with significant gradients
                if np.mean(block_mag) > 10:
                    # Calculate circular variance of gradient directions
                    # Convert to unit vectors
                    cos_sum = np.sum(np.cos(block_dir))
                    sin_sum = np.sum(np.sin(block_dir))
                    r = np.sqrt(cos_sum**2 + sin_sum**2) / block_dir.size

                    # Circular variance (0 = all same direction, 1 = random)
                    circ_var = 1 - r
                    direction_variances.append(circ_var)

        if len(direction_variances) == 0:
            return 0.0

        # Calculate variance of the block variances
        overall_variance = np.var(direction_variances)

        # Natural images have varied gradient patterns (high variance)
        # CGI often has consistent gradient patterns (low variance)
        if overall_variance < 0.02:
            score = 1.0 - (overall_variance / 0.02)
        elif overall_variance < 0.05:
            score = (0.05 - overall_variance) / 0.03 * 0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in gradient consistency analysis: {e}")
        return 0.0
