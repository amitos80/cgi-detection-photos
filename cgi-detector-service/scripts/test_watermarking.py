import pytest
import numpy as np
import cv2
from io import BytesIO
from cgi_detector_service.forensics import watermarking

# Helper function to create a dummy image for testing
def create_dummy_image_bytes(width=100, height=100, color=(0, 0, 0), format='png') -> bytes:
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = color
    _, encoded_image = cv2.imencode(f'.{format}', img)
    return encoded_image.tobytes()

# Helper function to create a simple LSB watermarked image
def create_lsb_watermarked_image_bytes(width=100, height=100, format='png') -> bytes:
    img_clean = np.random.randint(0, 256, (height, width), dtype=np.uint8)
    img_watermarked_lsb = img_clean.copy()
    for i in range(img_watermarked_lsb.shape[0]):
        for j in range(img_watermarked_lsb.shape[1]):
            # Embed a checkerboard pattern in LSBs
            if (i + j) % 2 == 0:
                img_watermarked_lsb[i, j] = (img_watermarked_lsb[i, j] & ~1) | 1 # Set LSB to 1
            else:
                img_watermarked_lsb[i, j] = (img_watermarked_lsb[i, j] & ~1) | 0 # Set LSB to 0
    
    _, encoded_lsb_image = cv2.imencode(f'.{format}', img_watermarked_lsb)
    return encoded_lsb_image.tobytes()

# Test cases for _least_significant_bit_analysis
def test_lsb_analysis_blank_image():
    image_bytes = create_dummy_image_bytes()
    score = watermarking._least_significant_bit_analysis(image_bytes)
    assert score < 0.5 # Expect a low score for a blank image

def test_lsb_analysis_random_image():
    random_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    _, encoded_image = cv2.imencode('.png', random_image)
    image_bytes = encoded_image.tobytes()
    score = watermarking._least_significant_bit_analysis(image_bytes)
    assert score < 0.5 # Expect a low score for a truly random LSB plane

def test_lsb_analysis_watermarked_image():
    image_bytes = create_lsb_watermarked_image_bytes()
    score = watermarking._least_significant_bit_analysis(image_bytes)
    assert score > 0.5 # Expect a higher score for a watermarked image

# Test cases for _frequency_domain_analysis
def test_fft_analysis_blank_image():
    image_bytes = create_dummy_image_bytes()
    score = watermarking._frequency_domain_analysis(image_bytes)
    assert score < 0.5 # Expect a low score for a blank image

def test_fft_analysis_textured_image():
    # Create an image with some natural texture (e.g., noise) but no explicit frequency watermark
    textured_image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    _, encoded_image = cv2.imencode('.png', textured_image)
    image_bytes = encoded_image.tobytes()
    score = watermarking._frequency_domain_analysis(image_bytes)
    assert score < 0.5 # Expect a low score for natural texture

# Test cases for analyze_watermark (integrates both)
def test_analyze_watermark_blank_image():
    image_bytes = create_dummy_image_bytes()
    score = watermarking.analyze_watermark(image_bytes)
    assert score < 0.5 # Overall low score for a blank image

def test_analyze_watermark_lsb_watermarked_image():
    image_bytes = create_lsb_watermarked_image_bytes()
    score = watermarking.analyze_watermark(image_bytes)
    assert score > 0.5 # Overall higher score due to LSB watermark

# Test with an invalid image (corrupted or non-image bytes)
def test_invalid_image_bytes():
    invalid_bytes = b"this is not an image"
    score_lsb = watermarking._least_significant_bit_analysis(invalid_bytes)
    score_fft = watermarking._frequency_domain_analysis(invalid_bytes)
    score_combined = watermarking.analyze_watermark(invalid_bytes)
    assert score_lsb == 0.0
    assert score_fft == 0.0
    assert score_combined == 0.0
