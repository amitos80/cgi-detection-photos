import sys
import os
# Add the project root to sys.path to allow absolute imports from cgi_detector_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import numpy as np
from PIL import Image
from io import BytesIO
from cgi_detector_service.forensics.watermarking import analyze_watermark, _analyze_lsb, _analyze_fft

# Helper function to create a dummy image
def create_dummy_image(width, height, color=(0, 0, 0)) -> Image.Image:
    return Image.new("RGB", (width, height), color)

# Helper function to embed a simple LSB watermark (for testing _analyze_lsb)
def embed_lsb_watermark(image: Image.Image, message: bytes) -> Image.Image:
    img_copy = image.copy().convert("RGB")
    width, height = img_copy.size
    pixels = img_copy.load()

    # Convert message to a bit stream
    bits = []
    for byte in message:
        for i in range(8):
            bits.append((byte >> i) & 1)
    
    # Pad bits if message is too short for image capacity (not strictly necessary for this test)
    # Or, truncate if message is too long
    max_bits = width * height * 3 # For RGB image
    bits = bits[:max_bits]

    bit_idx = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            new_r, new_g, new_b = r, g, b

            if bit_idx < len(bits):
                new_r = (r & ~1) | bits[bit_idx] # Clear LSB and set new LSB
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

class TestWatermarking:
    def test_analyze_watermark_no_watermark(self):
        # Create a simple image with no watermark
        img = create_dummy_image(100, 100, (128, 128, 128))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        score = analyze_watermark(image_bytes)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Expect a low score for a clean image
        # The exact threshold might need adjustment based on heuristic tuning
        assert score < 0.5 # Assuming a clean image should have a score less than 0.5

    def test_analyze_watermark_with_lsb_watermark(self):
        # Create an image and embed a simple LSB watermark
        original_img = create_dummy_image(50, 50, (100, 150, 200))
        watermarked_img = embed_lsb_watermark(original_img, b"secret")
        
        buffered = BytesIO()
        watermarked_img.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        score = analyze_watermark(image_bytes)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Expect a higher score for a watermarked image
        assert score > 0.5 # Assuming an LSB watermarked image should have a score greater than 0.5

    def test_analyze_lsb_clean_image(self):
        img = create_dummy_image(100, 100, (128, 128, 128))
        score = _analyze_lsb(img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score < 0.5

    def test_analyze_lsb_watermarked_image(self):
        original_img = create_dummy_image(50, 50, (100, 150, 200))
        watermarked_img = embed_lsb_watermark(original_img, b"another secret")
        score = _analyze_lsb(watermarked_img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.5

    def test_analyze_fft_clean_image(self):
        img = create_dummy_image(100, 100, (128, 128, 128))
        score = _analyze_fft(img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score < 0.5 # Expect a low score for a clean image

    # Note: Testing FFT-based watermarks is significantly more complex.
    # This test provides a baseline, but a true FFT watermark would require specific pattern embedding.
    def test_analyze_fft_complex_image(self):
        # A more complex image might naturally have higher FFT variance, but should still be below watermark levels.
        img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        score = _analyze_fft(img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # The threshold here is more speculative without a true FFT watermark to compare against.
        assert score < 0.8 # Should still be relatively low for a random image (no specific pattern)

    def test_analyze_watermark_invalid_image_bytes(self):
        # Test with invalid image bytes
        invalid_bytes = b"this is not an image"
        score = analyze_watermark(invalid_bytes)
        assert score == 0.0 # Expect 0.0 for invalid input

    def test_analyze_watermark_empty_image_bytes(self):
        # Test with empty image bytes
        empty_bytes = b""
        score = analyze_watermark(empty_bytes)
        assert score == 0.0 # Expect 0.0 for empty input

