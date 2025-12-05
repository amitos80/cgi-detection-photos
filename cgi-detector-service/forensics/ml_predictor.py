"""
This module provides functionalities for training, saving, loading,
and making predictions with a machine learning model for forensic analysis.
"""
import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor
from . import ela, cfa, hos, jpeg_ghost, rambino, geometric_3d, lighting_text, jpeg_dimples
from . import specialized_detectors
from . import deepfake_detector, reflection_consistency, double_quantization
from . import watermarking
import uuid # For generating unique filenames

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.joblib")
FEEDBACK_DATASET_DIR = "/app/forensics_data/feedback_dataset"

_current_ml_model = None # Global variable to hold the loaded model


def downsize_image_to_480p(image: Image.Image) -> Image.Image:
    """
    Downsizes the input image to a maximum height of 480 pixels, maintaining aspect ratio.

    Args:
        image: A PIL Image object.

    Returns:
        A new PIL Image object resized to 480p or smaller if the original height is less than 480p.
    """
    max_height = 480
    width, height = image.size

    if height <= max_height:
        return image  # No downsizing needed if already 480p or smaller

    # Calculate the new width while maintaining the aspect ratio
    new_width = int(width * (max_height / height))
    resized_image = image.resize((new_width, max_height), Image.LANCZOS)
    return resized_image

def run_rambino_analysis(image_bytes_for_rambino):
    try:
        image = Image.open(BytesIO(image_bytes_for_rambino)).convert('L')  # Convert to grayscale
        image_data = np.array(image)
    except Exception:
        image_data = None
        return {'score': 0.0, 'features': None, 'raw_score': 0.0}

    rambino_score = 0.0
    rambino_features_list = None
    try:
        if image_data is not None:
            rambino_result = rambino.analyze_rambino_features(image_data)
            try:
                raw_feats = rambino.compute_rambino_features(image_data)
                max_return = 128
                rambino_features_list = raw_feats.flatten()[:max_return].astype(float).tolist()
            except Exception:
                rambino_features_list = None

            if isinstance(rambino_result, dict):
                if "error" in rambino_result:
                    rambino_score = 0.0
                else:
                    rambino_score = float(rambino_result.get("rambino_feature_mean_noise", 0.0))
            else:
                rambino_score = float(np.mean(rambino_result))
    except Exception:
        rambino_score = 0.0
        rambino_features_list = None

    rambino_raw_score = rambino_score
    scale = 30000.0
    rambino_score = float(np.clip(rambino_raw_score / scale, 0.0, 1.0))
    return {'score': rambino_score, 'features': rambino_features_list, 'raw_score': rambino_raw_score}

def extract_features_from_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Extracts all forensic features from an image, given its bytes.
    This is a streamlined version of engine.run_analysis, focused solely on feature extraction.
    """
    try:
        original_image = Image.open(BytesIO(image_bytes))
        downsized_image = downsize_image_to_480p(original_image)
        buffered = BytesIO()
        downsized_image.save(buffered, format="PNG")
        processed_image_bytes = buffered.getvalue()
    except Exception as e:
        print(f"Error processing or downsizing image for feature extraction: {e}")
        processed_image_bytes = image_bytes

    futures = {}
    with ProcessPoolExecutor() as executor:
        futures['ela'] = executor.submit(ela.analyze_ela, processed_image_bytes)
        futures['cfa'] = executor.submit(cfa.analyze_cfa, processed_image_bytes)
        futures['hos'] = executor.submit(hos.analyze_hos, processed_image_bytes)
        futures['jpeg_ghost'] = executor.submit(jpeg_ghost.analyze_jpeg_ghost, processed_image_bytes)
        futures['jpeg_dimples'] = executor.submit(jpeg_dimples.detect_jpeg_dimples, processed_image_bytes)
        futures['geometric'] = executor.submit(geometric_3d.analyze_geometric_consistency, processed_image_bytes)
        futures['lighting'] = executor.submit(lighting_text.analyze_lighting_consistency, processed_image_bytes)
        futures['specialized_detector'] = executor.submit(specialized_detectors.analyze_specialized_cgi_types, processed_image_bytes)
        futures['deepfake'] = executor.submit(deepfake_detector.detect_deepfake, processed_image_bytes)
        futures['reflection_inconsistency'] = executor.submit(reflection_consistency.detect_reflection_inconsistencies, processed_image_bytes)
        futures['double_quantization'] = executor.submit(double_quantization.detect_double_quantization, processed_image_bytes)
        futures['rambino'] = executor.submit(run_rambino_analysis, processed_image_bytes)
        futures['watermark'] = executor.submit(watermarking.analyze_watermark, processed_image_bytes)

        results = {}
        for name, future in futures.items():
            try:
                if name == 'rambino':
                    rambino_result = future.result()
                    results['rambino'] = rambino_result['score']
                elif name == 'specialized_detector':
                    specialized_result = future.result()
                    results['specialized'] = specialized_result.get('overall_score', 0.0)
                elif name == 'watermark':
                    results['watermark'] = future.result()
                else:
                    results[name] = future.result()
            except Exception as e:
                print(f"Error running {name} analysis for feature extraction: {e}")
                results[name] = 0.0

    ela_score = results.get('ela', 0.0)
    cfa_score = results.get('cfa', 0.0)
    hos_score = results.get('hos', 0.0)
    jpeg_ghost_score = results.get('jpeg_ghost', 0.0)
    jpeg_dimples_score = results.get('jpeg_dimples', 0.0)
    geometric_score = results.get('geometric', 0.0)
    lighting_score = results.get('lighting', 0.0)
    rambino_score = results.get('rambino', 0.0)
    specialized_score = results.get('specialized', 0.0)
    deepfake_score = results.get('deepfake', {}).get('confidence', 0.0)
    reflection_score = results.get('reflection_inconsistency', {}).get('confidence', 0.0)
    double_quantization_score = results.get('double_quantization', {}).get('confidence', 0.0)
    watermark_score = results.get('watermark', 0.0)

    ml_features = [
        ela_score, cfa_score, hos_score, jpeg_ghost_score, jpeg_dimples_score, rambino_score,
        geometric_score, lighting_score, specialized_score,
        deepfake_score, reflection_score, double_quantization_score, watermark_score
    ]
    return np.asarray(ml_features).reshape(1, -1)

def save_feedback_image_and_label(image_bytes: bytes, true_label: str):
    """
    Saves an image and its true label to the feedback dataset directory.
    """
    label_dir = os.path.join(FEEDBACK_DATASET_DIR, true_label)
    os.makedirs(label_dir, exist_ok=True)
    image_filename = os.path.join(label_dir, f"{uuid.uuid4()}.png")
    with open(image_filename, "wb") as f:
        f.write(image_bytes)
    print(f"Saved feedback image to {image_filename} with label {true_label}")

def load_feedback_data():
    """
    Loads all feedback images, extracts features, and returns them with labels.
    """
    all_features = []
    all_labels = []
    if not os.path.exists(FEEDBACK_DATASET_DIR):
        return np.array([]), np.array([])

    for label_dir_name in ['real', 'cgi']:
        current_label_path = os.path.join(FEEDBACK_DATASET_DIR, label_dir_name)
        if os.path.exists(current_label_path):
            for filename in os.listdir(current_label_path):
                if filename.lower().endswith( ('.png', '.jpg', '.jpeg') ):
                    image_path = os.path.join(current_label_path, filename)
                    try:
                        with open(image_path, "rb") as f:
                            image_bytes = f.read()
                        features = extract_features_from_image_bytes(image_bytes)
                        all_features.append(features.flatten())
                        all_labels.append(1 if label_dir_name == 'cgi' else 0)
                    except Exception as e:
                        print(f"Error processing feedback image {image_path}: {e}")

    if not all_features:
        return np.array([]), np.array([])

    return np.array(all_features), np.array(all_labels)

def _get_base_training_data():
    """
    Provides a base set of features and labels for initial model training.
    If a model exists, it loads it to extend the training data. Otherwise,
    it generates dummy data.
    """
    training_data_path = MODEL_PATH.replace('.joblib', '_training_data.joblib')
    if os.path.exists(training_data_path):
        print(f"Loading base training data from {training_data_path}...")
        try:
            training_data = joblib.load(training_data_path)
            return training_data['features'], training_data['labels']
        except Exception as e:
            print(f"Could not load training data, starting fresh: {e}")
            # Fallback to dummy data if loading fails
            base_features = np.random.rand(100, 12)
            base_labels = np.random.randint(0, 2, 100)
            return base_features, base_labels
    else:
        print("Generating initial dummy training data...")
        base_features = np.random.rand(100, 12)
        base_labels = np.random.randint(0, 2, 100)
        return base_features, base_labels

def retrain_with_feedback():
    """
    Orchestrates retraining the ML model using the base training data and all accumulated feedback data.
    """
    print("Retraining ML model with feedback data...")

    # Get base training data (e.g., from an initial fixed dataset or generated dummy data)
    base_features, base_labels = _get_base_training_data()

    # Load all feedback data
    feedback_features, feedback_labels = load_feedback_data()

    # Combine base data with feedback data
    if feedback_features.size > 0:
        if base_features.size > 0:
            combined_features = np.vstack((base_features, feedback_features))
            combined_labels = np.concatenate((base_labels, feedback_labels))
        else:
            combined_features = feedback_features
            combined_labels = feedback_labels
    else:
        combined_features = base_features
        combined_labels = base_labels

    if combined_features.size > 0:
        train_and_save_model(combined_features, combined_labels)
        print("ML model trained and saved after retraining.")
    else:
        print("No combined features for training. Skipping model update.")

def load_model():
    """
    Loads the trained ML model from disk into the global _current_ml_model.
    If no model exists, it triggers an initial training via retrain_with_feedback.
    """
    global _current_ml_model
    if _current_ml_model is None or not os.path.exists(MODEL_PATH):
        if not os.path.exists(MODEL_PATH):
            print(f"Model not found at {MODEL_PATH}. Performing initial training...")
            retrain_with_feedback() # Perform initial training
        _current_ml_model = joblib.load(MODEL_PATH)
        print(f"ML model loaded from {MODEL_PATH}")
    return _current_ml_model

def get_model():
    """
    Returns the currently loaded ML model, ensuring it's loaded if not already.
    """
    if _current_ml_model is None:
        load_model()
    return _current_ml_model

def reload_model():
    """
    Forces a reload of the ML model from disk and updates the global _current_ml_model.
    """
    global _current_ml_model
    _current_ml_model = joblib.load(MODEL_PATH)
    print(f"ML model reloaded from {MODEL_PATH}")
    return _current_ml_model

def train_and_save_model(features: np.ndarray, labels: np.ndarray):
    """
    Trains a RandomForestClassifier and saves it and its training data to files.
    """
    print("Training RandomForestClassifier ML model...")
    # Split data for demonstration
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"RandomForestClassifier model accuracy: {accuracy_score(y_test, y_pred):.2f}")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"RandomForestClassifier ML model saved to {MODEL_PATH}")

    # Save training data
    training_data_path = MODEL_PATH.replace('.joblib', '_training_data.joblib')
    joblib.dump({'features': features, 'labels': labels}, training_data_path)
    print(f"Training data saved to {training_data_path}")

def predict(model, features: list) -> dict:
    """
    Makes a prediction using the loaded ML model.

    Args:
        model: The loaded scikit-learn model.
        features: A list of numerical features extracted by the forensic engine.

    Returns:
        A dictionary containing the prediction label and confidence score.
    """
    if not isinstance(features, np.ndarray):
        features_array = np.asarray(features).reshape(1, -1) # Reshape for single sample prediction
    else:
        features_array = features.reshape(1, -1)

    prediction = model.predict(features_array)[0]
    # Get probability for the predicted class
    confidence = model.predict_proba(features_array)[0, prediction]

    label = "cgi" if prediction == 1 else "real" # Assuming 1 for CGI, 0 for real

    return {"prediction_label": label, "confidence": float(confidence)}


# This block will run when ml_predictor.py is executed directly
if __name__ == "__main__":
    # Example usage:
    # Ensure initial model is trained or re-train with existing feedback
    retrain_with_feedback()

    # Example of loading and predicting
    loaded_model = get_model()
    sample_features = np.random.rand(12) # Single sample
    prediction_result = predict(loaded_model, sample_features)
    print(f"Sample prediction: {prediction_result}")
