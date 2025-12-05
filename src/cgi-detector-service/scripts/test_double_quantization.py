"""
Test script for the Video Double Quantization Detection module
"""
import sys
import os
import pytest

# Add parent directory to path to allow importing forensics modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forensics import double_quantization

def test_double_quantization_detection_dummy_video_path():
    """
    Tests the double quantization detection with a dummy video path.
    """
    print("\nTesting Video Double Quantization Detection Module with Dummy Video Path")
    print("=" * 60)

    dummy_video_path = "/path/to/dummy/video.mp4"
    result = double_quantization.detect_double_quantization(dummy_video_path)

    print(f"Detection Result: {result}")

    # Assertions to check the structure and default values of the placeholder result
    assert isinstance(result, dict)
    assert "has_double_quantization" in result
    assert isinstance(result["has_double_quantization"], bool)
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert "details" in result
    assert isinstance(result["details"], str)

    print("Video Double Quantization Detection Module test completed successfully!")
    print("The double_quantization module is working and returning expected structure.")

if __name__ == "__main__":
    test_double_quantization_detection_dummy_video_path()

