from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import numpy as np
import io
import tensorflow as tf

app = FastAPI()

# Load the pre-trained ResNet50 model
# We'll use a pre-trained ResNet50 for demonstration.
# In a real scenario, this would be fine-tuned for CGI detection.
try:
    model = tf.keras.applications.ResNet50(weights='imagenet')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.post("/predict")
async def predict_cgi(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")

    # 1. Read image
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    # 2. Pre-process image
    # ResNet50 expects 224x224 images
    image = image.resize((224, 224))
    image_array = np.asarray(image)
    image_array = np.expand_dims(image_array, axis=0)
    image_array = tf.keras.applications.resnet50.preprocess_input(image_array)

    # 3. Make prediction
    predictions = model.predict(image_array)
    # For demonstration, we'll just return a dummy prediction
    # In a real scenario, you'd interpret the ResNet50 output for CGI detection
    # For now, let's just say it's "real" with high confidence.
    # A more sophisticated approach would involve a binary classification layer
    # and training on a CGI/real dataset.
    
    # Dummy logic: if the image contains a cat (class 281 in ImageNet), let's pretend it's CGI
    # This is purely illustrative and not actual CGI detection.
    decoded_predictions = tf.keras.applications.resnet50.decode_predictions(predictions, top=1)[0]
    
    # Find the top prediction
    top_prediction = decoded_predictions[0]
    
    # Assign a dummy CGI/Real prediction based on the top ImageNet class
    # This is a placeholder. A real CGI detector would have its own output layer.
    if 'cat' in top_prediction[1]: # Example: if it's a cat, pretend it's CGI
        prediction_label = "cgi"
        confidence = 0.85 # Dummy confidence
        analysis_breakdown = [
            {"feature": "Lighting Consistency", "score": 0.88, "normal_range": [0.0, 0.5], "insight": "Highlights and shadows appear inconsistent with a single light source."},
            {"feature": "Shadow Authenticity", "score": 0.92, "normal_range": [0.0, 0.4], "insight": "Shadows lack realistic softness and penumbra, suggesting they were rendered."},
            {"feature": "Texture Analysis (PRNU)", "score": 0.75, "normal_range": [0.0, 0.6], "insight": "High-frequency noise patterns are too uniform, which is uncharacteristic of a real camera sensor."}
        ]
    else:
        prediction_label = "real"
        confidence = 0.95 # Dummy confidence
        analysis_breakdown = [
            {"feature": "Lighting Consistency", "score": 0.15, "normal_range": [0.0, 0.5], "insight": "Lighting and shadows are consistent with a natural light source."},
            {"feature": "Shadow Authenticity", "score": 0.20, "normal_range": [0.0, 0.4], "insight": "Shadows exhibit realistic properties expected from a physical scene."},
            {"feature": "Texture Analysis (PRNU)", "score": 0.30, "normal_range": [0.0, 0.6], "insight": "Sensor noise patterns are consistent across the image, indicating a single capture origin."}
        ]

    return {
        "prediction": prediction_label,
        "confidence": confidence,
        "analysis_breakdown": analysis_breakdown
    }

