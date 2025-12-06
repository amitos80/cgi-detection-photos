import joblib
import sys
import os
from PIL import Image
from io import BytesIO

# Add the cgi-detector-service directory to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cgi-detector-service')))

from forensics.ml_predictor import extract_features_from_image_bytes

def verify_model(model_path, image_path):
    """
    Loads a trained model and an image, extracts features, and runs a prediction.
    """
    print(f"Loading model from: {model_path}")
    model = joblib.load(model_path)

    print(f"Loading image from: {image_path}")
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print("Extracting features from the image...")
    features = extract_features_from_image_bytes(image_bytes)

    if features.size == 0:
        print("Could not extract features from the image.")
        return

    # The model expects a 2D array
    features = features.reshape(1, -1)

    print("Running prediction...")
    prediction = model.predict(features)
    prediction_proba = model.predict_proba(features)

    print(f"\nPrediction result for {os.path.basename(image_path)}:")
    print(f"  - Label (0=real, 1=fake): {prediction[0]}")
    print(f"  - Prediction probabilities: {prediction_proba[0]}")

if __name__ == "__main__":
    MODEL_FILE = 'cgi-detector-service/forensics/ml_model.joblib'
    # Using a known fake image from the training set
    IMAGE_FILE = 'my_dataset/fake/Gemini_Generated_Image_122dic122dic122d.png'

    if not os.path.exists(MODEL_FILE):
        print(f"Error: Model file not found at {MODEL_FILE}")
    elif not os.path.exists(IMAGE_FILE):
        print(f"Error: Image file not found at {IMAGE_FILE}")
    else:
        verify_model(MODEL_FILE, IMAGE_FILE)
