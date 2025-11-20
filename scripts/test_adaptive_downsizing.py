import pytest
from PIL import Image
import os
import sys

# Add the parent directory of cgi_detector_service to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cgi_detector_service.forensics.engine import adaptive_downsize_image

@pytest.fixture
def create_image():
    def _create_image(width, height):
        return Image.new('RGB', (width, height), color = 'red')
    return _create_image

def test_large_landscape_image(create_image):
    # Case A (Large Landscape): A 1920x1080 image. Expected: Resized to 800x450.
    image = create_image(1920, 1080)
    resized_image = adaptive_downsize_image(image)
    assert resized_image.size == (800, 450)

def test_large_portrait_image(create_image):
    # Case B (Large Portrait): A 1080x1920 image. Expected: Resized to 450x800.
    image = create_image(1080, 1920)
    resized_image = adaptive_downsize_image(image)
    assert resized_image.size == (450, 800)

def test_small_image(create_image):
    # Case C (Small Image): A 600x400 image. Expected: No change (600x400).
    image = create_image(600, 400)
    resized_image = adaptive_downsize_image(image)
    assert resized_image.size == (600, 400)

def test_panoramic_image(create_image):
    # Case D (Panoramic / Extreme Aspect Ratio): A 3000x600 image. Standard resize would be 800x160, which is below the minimum. Expected: Resized to 1280x256 (to preserve the 256px short edge).
    image = create_image(3000, 600)
    resized_image = adaptive_downsize_image(image)
    assert resized_image.size == (1280, 256)

def test_tall_image(create_image):
    # Case E (Tall / Extreme Aspect Ratio): A 600x3000 image. Expected: Resized to 256x1280.
    image = create_image(600, 3000)
    resized_image = adaptive_downsize_image(image)
    assert resized_image.size == (256, 1280)