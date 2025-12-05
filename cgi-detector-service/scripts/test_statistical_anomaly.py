import pytest
import numpy as np
from PIL import Image
from io import BytesIO
from cgi_detector_service.forensics import statistical_anomaly

# Helper to create dummy image bytes
def create_dummy_image_bytes(width, height, color=0):
    image = Image.new('L', (width, height), color)
    byte_io = BytesIO()
    image.save(byte_io, format='PNG')
    return byte_io.getvalue()

# Test cases for analyze_statistical_anomaly
def test_analyze_statistical_anomaly_uniform_image():
    """Test with a uniform image (expected low anomaly score)."""
    dummy_image_bytes = create_dummy_image_bytes(64, 64, 128)
    score = statistical_anomaly.analyze_statistical_anomaly(dummy_image_bytes)
    assert isinstance(score, float)
    assert 0.0 <= score <= 0.5  # Uniform images should have low anomaly scores

def test_analyze_statistical_anomaly_noisy_image():
    """Test with a noisy image (expected higher anomaly score)."""
    # Create a noisy image
    noisy_array = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
    noisy_image = Image.fromarray(noisy_array, 'L')
    byte_io = BytesIO()
    noisy_image.save(byte_io, format='PNG')
    noisy_image_bytes = byte_io.getvalue()

    score = statistical_anomaly.analyze_statistical_anomaly(noisy_image_bytes)
    assert isinstance(score, float)
    assert score >= 0.5  # Noisy images should have higher anomaly scores

def test_analyze_statistical_anomaly_invalid_input():
    """Test with invalid input bytes (expected 0.0 score)."""
    invalid_bytes = b"this is not an image"
    score = statistical_anomaly.analyze_statistical_anomaly(invalid_bytes)
    assert score == 0.0

def test_analyze_statistical_anomaly_small_image():
    """Test with a very small image that might not have enough data for full analysis."""
    small_image_bytes = create_dummy_image_bytes(5, 5, 100)
    score = statistical_anomaly.analyze_statistical_anomaly(small_image_bytes)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0  # Should still return a valid score

def test_analyze_statistical_anomaly_complex_pattern():
    """Test with a complex synthetic pattern (expected higher anomaly score)."""
    # Create a simple checkerboard pattern
    img_array = np.zeros((64, 64), dtype=np.uint8)
    img_array[::2, 1::2] = 255
    img_array[1::2, ::2] = 255
    pattern_image = Image.fromarray(img_array, 'L')
    byte_io = BytesIO()
    pattern_image.save(byte_io, format='PNG')
    pattern_image_bytes = byte_io.getvalue()

    score = statistical_anomaly.analyze_statistical_anomaly(pattern_image_bytes)
    assert isinstance(score, float)
    assert score > 0.6  # Complex patterns should ideally yield higher anomaly scores
