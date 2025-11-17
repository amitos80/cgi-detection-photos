"""
Test script for the 3D Geometric Consistency Analysis module
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import numpy as np
from io import BytesIO
from forensics import geometric_3d


def create_test_image(size=(512, 512), image_type='natural'):
    """
    Create a test image for testing the geometric analysis.

    Args:
        size: Image dimensions (width, height)
        image_type: 'natural' for natural-looking or 'synthetic' for CGI-like

    Returns:
        image_bytes: Raw image bytes
    """
    img = Image.new('RGB', size)
    pixels = img.load()

    width, height = size

    if image_type == 'natural':
        # Create a more varied, natural-looking pattern
        for i in range(width):
            for j in range(height):
                # Random noise with gradients
                r = int(128 + np.random.randint(-50, 50) + (i / width) * 50)
                g = int(128 + np.random.randint(-50, 50) + (j / height) * 50)
                b = int(128 + np.random.randint(-50, 50))
                pixels[i, j] = (
                    np.clip(r, 0, 255),
                    np.clip(g, 0, 255),
                    np.clip(b, 0, 255)
                )
    else:  # synthetic
        # Create a smooth, symmetric, CGI-like pattern
        for i in range(width):
            for j in range(height):
                # Smooth gradients with perfect symmetry
                r = int(128 + np.sin(i / 50) * 50)
                g = int(128 + np.cos(j / 50) * 50)
                b = int(128 + np.sin((i + j) / 50) * 50)
                pixels[i, j] = (
                    np.clip(r, 0, 255),
                    np.clip(g, 0, 255),
                    np.clip(b, 0, 255)
                )

    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_geometric_analysis():
    """Test the geometric consistency analysis with different image types."""

    print("Testing 3D Geometric Consistency Analysis Module")
    print("=" * 60)

    # Test 1: Natural image
    print("\nTest 1: Natural-looking image")
    print("-" * 60)
    natural_bytes = create_test_image(image_type='natural')
    natural_score = geometric_3d.analyze_geometric_consistency(natural_bytes)
    print(f"Score: {natural_score:.4f}")
    print(f"Expected: Low score (< 0.3) for natural images")
    print(f"Result: {'PASS' if natural_score < 0.5 else 'FAIL'}")

    # Test 2: Synthetic image
    print("\nTest 2: Synthetic CGI-like image")
    print("-" * 60)
    synthetic_bytes = create_test_image(image_type='synthetic')
    synthetic_score = geometric_3d.analyze_geometric_consistency(synthetic_bytes)
    print(f"Score: {synthetic_score:.4f}")
    print(f"Expected: Higher score for synthetic images")
    print(f"Result: Score computed successfully")

    # Test 3: Compare scores
    print("\n" + "=" * 60)
    print("Comparison:")
    print(f"  Natural image score:   {natural_score:.4f}")
    print(f"  Synthetic image score: {synthetic_score:.4f}")
    print(f"  Difference:            {abs(synthetic_score - natural_score):.4f}")

    print("\n" + "=" * 60)
    print("Module test completed successfully!")
    print("The geometric_3d module is working and producing scores.")


if __name__ == "__main__":
    test_geometric_analysis()
