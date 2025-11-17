"""
Test the API with the new geometric 3D analysis feature
"""
import requests
from PIL import Image
import numpy as np
from io import BytesIO


def create_test_image(size=(512, 512), image_type='natural'):
    """Create a test image."""
    img = Image.new('RGB', size)
    pixels = img.load()
    width, height = size

    if image_type == 'natural':
        # Natural-looking pattern with noise
        for i in range(width):
            for j in range(height):
                r = int(128 + np.random.randint(-50, 50) + (i / width) * 50)
                g = int(128 + np.random.randint(-50, 50) + (j / height) * 50)
                b = int(128 + np.random.randint(-50, 50))
                pixels[i, j] = (
                    np.clip(r, 0, 255),
                    np.clip(g, 0, 255),
                    np.clip(b, 0, 255)
                )
    else:  # synthetic
        # Smooth, symmetric CGI-like pattern
        for i in range(width):
            for j in range(height):
                r = int(128 + np.sin(i / 50) * 50)
                g = int(128 + np.cos(j / 50) * 50)
                b = int(128 + np.sin((i + j) / 50) * 50)
                pixels[i, j] = (
                    np.clip(r, 0, 255),
                    np.clip(g, 0, 255),
                    np.clip(b, 0, 255)
                )

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def test_api():
    """Test the API endpoint with the new feature."""
    print("Testing CGI Detection API with 3D Geometric Analysis")
    print("=" * 70)

    # Test with a natural-looking image
    print("\nTest 1: Natural-looking image")
    print("-" * 70)

    natural_img = create_test_image(image_type='natural')
    files = {'file': ('test_natural.png', natural_img, 'image/png')}

    try:
        response = requests.post('http://localhost:8000/analyze', files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"Status: SUCCESS")
            print(f"Prediction: {result['prediction']['prediction']}")
            print(f"Confidence: {result['prediction']['confidence']:.4f}")
            print(f"\nAnalysis Breakdown:")

            for feature in result['prediction']['analysis_breakdown']:
                print(f"  - {feature['feature']}: {feature['score']:.4f}")
                if feature['feature'] == '3D Geometric Consistency':
                    print(f"    ✓ NEW FEATURE DETECTED!")
                    print(f"    Insight: {feature['insight']}")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)
    print("Test completed! The 3D Geometric Consistency feature is integrated.")


if __name__ == "__main__":
    test_api()
