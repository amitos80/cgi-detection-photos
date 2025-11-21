"""
Test script for the Deepfake Detection module
"""
import sys
import os
import pytest

# Add parent directory to path to allow importing forensics modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from io import BytesIO
from forensics import deepfake_detector

def create_dummy_image_bytes(size=(100, 100)) -> bytes:
    """
    Creates dummy image bytes for testing purposes.
    """
    img = Image.new('RGB', size, color = 'red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def test_deepfake_detection_dummy_image():
    """
    Tests the deepfake detection with a dummy image.
    """
    print("\nTesting Deepfake Detection Module with Dummy Image")
    print("=" * 60)

    dummy_image_bytes = create_dummy_image_bytes()
    result = deepfake_detector.detect_deepfake(dummy_image_bytes)

    print(f"Detection Result: {result}")

    # Assertions to check the structure and default values of the placeholder result
    assert isinstance(result, dict)
    assert "is_deepfake" in result
    assert isinstance(result["is_deepfake"], bool)
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert "details" in result
    assert isinstance(result["details"], str)

    print("Deepfake Detection Module test completed successfully!")
    print("The deepfake_detector module is working and returning expected structure.")


# You can add more complex tests here once the deepfake_detector has actual logic.
# For instance, mocking a real deepfake input or a real image input and asserting
# specific confidence scores.

if __name__ == "__main__":
    # This allows running the test script directly for quick verification
    # In a full pytest setup, you'd just run 'pytest'
    test_deepfake_detection_dummy_image()
