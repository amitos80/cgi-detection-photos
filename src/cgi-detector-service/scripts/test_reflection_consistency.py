"""
Test script for the Reflection Inconsistency Detection module
"""
import sys
import os
import pytest

# Add parent directory to path to allow importing forensics modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from io import BytesIO
from forensics import reflection_consistency

def create_dummy_image_bytes(size=(100, 100)) -> bytes:
    """
    Creates dummy image bytes for testing purposes.
    """
    img = Image.new('RGB', size, color = 'blue')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def test_reflection_inconsistency_detection_dummy_image():
    """
    Tests the reflection inconsistency detection with a dummy image.
    """
    print("\nTesting Reflection Inconsistency Detection Module with Dummy Image")
    print("=" * 60)

    dummy_image_bytes = create_dummy_image_bytes()
    result = reflection_consistency.detect_reflection_inconsistencies(dummy_image_bytes)

    print(f"Detection Result: {result}")

    # Assertions to check the structure and default values of the placeholder result
    assert isinstance(result, dict)
    assert "has_reflection_inconsistencies" in result
    assert isinstance(result["has_reflection_inconsistencies"], bool)
    assert "confidence" in result
    assert isinstance(result["confidence"], float)
    assert "details" in result
    assert isinstance(result["details"], str)

    print("Reflection Inconsistency Detection Module test completed successfully!")
    print("The reflection_consistency module is working and returning expected structure.")

if __name__ == "__main__":
    test_reflection_inconsistency_detection_dummy_image()
