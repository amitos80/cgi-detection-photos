from PIL import Image
import pystego

def extract_hidden_data(image_path):
    img = Image.open(image_path)
    extracted_message, _ = pystego.reveal(img)
    return extracted_message

def test_image_steganography():
    original_message = "Secret Message"
    hide_data("input.jpg", original_message)

    # Extract hidden data
    extracted_message = extract_hidden_data("stego_image.png")
    assert extracted_message == original_message, f"Extracted: {extracted_message}, Expected: {original_message}"

    print("Image steganography testing passed.")

# Run tests
test_image_steganography()
