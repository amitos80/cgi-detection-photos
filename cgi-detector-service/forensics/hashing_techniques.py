import hashlib
from tkinter import Image


def compute_hash(image_path):
    hasher = hashlib.new('sha256')
    with open(image_path, 'rb') as file:
        while chunk := file.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def test_hashing_techniques():
    # Compute hashes for different parts of the image
    img1 = Image.open("image1.jpg")
    img2 = Image.open("image2.jpg")
    hash1 = compute_hash("image1.jpg")
    hash2 = compute_hash("image2.jpg")

    # Verify uniqueness and collision avoidance
    assert hash1 != hash2, "Hashes should be different"
    print("Hashing techniques testing passed.")

# Run tests
test_hashing_techniques()
