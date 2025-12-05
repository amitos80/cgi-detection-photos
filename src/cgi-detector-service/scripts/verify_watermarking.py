import numpy as np
from PIL import Image
from io import BytesIO
import sys
import os

# Add the project root to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.cgi_detector_service.forensics.watermarking import analyze_watermark, _analyze_lsb, _analyze_fft

# Helper function to create a dummy image
def create_dummy_image(width, height, color=(0, 0, 0)) -> Image.Image:
    return Image.new("RGB", (width, height), color)

# Helper function to embed a simple LSB watermark
def embed_lsb_watermark(image: Image.Image, message: bytes) -> Image.Image:
    img_copy = image.copy().convert("RGB")
    width, height = img_copy.size
    pixels = img_copy.load()
    bits = []
    for byte in message:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    max_bits = width * height * 3
    bits = bits[:max_bits]
    bit_idx = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            new_r, new_g, new_b = r, g, b
            if bit_idx < len(bits):
                new_r = (r & ~1) | bits[bit_idx]
                bit_idx += 1
            if bit_idx < len(bits):
                new_g = (g & ~1) | bits[bit_idx]
                bit_idx += 1
            if bit_idx < len(bits):
                new_b = (b & ~1) | bits[bit_idx]
                bit_idx += 1
            
            pixels[x, y] = (new_r, new_g, new_b)
            if bit_idx == len(bits):
                return img_copy
    return img_copy

def run_tests():
    print("Running watermark verification tests...")
    
    # Test 1: No watermark
    img = create_dummy_image(100, 100, (128, 128, 128))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()
    score = analyze_watermark(image_bytes)
    assert 0.0 <= score <= 1.0
    assert score < 0.5
    print("Test 1 (No Watermark): PASSED")

    # Test 2: With LSB watermark
    original_img = create_dummy_image(50, 50, (100, 150, 200))
    watermarked_img = embed_lsb_watermark(original_img, b"secret")
    buffered = BytesIO()
    watermarked_img.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()
    score = analyze_watermark(image_bytes)
    assert 0.0 <= score <= 1.0
    assert score > 0.5
    print("Test 2 (LSB Watermark): PASSED")

    # Test 3: Invalid image bytes
    invalid_bytes = b"this is not an image"
    score = analyze_watermark(invalid_bytes)
    assert score == 0.0
    print("Test 3 (Invalid Bytes): PASSED")

    print("All watermark verification tests passed!")

if __name__ == "__main__":
    run_tests()
