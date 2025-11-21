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
import os
import numpy as np
import joblib

MODEL_PATH = "forensics/ml_model.joblib"

def train_and_save_model(features: np.ndarray, labels: np.ndarray):
    """
    Trains a RandomForestClassifier and saves it to a file.
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

def load_model():
    """
    Loads the trained ML model from disk.

    Returns:
        The loaded scikit-learn model.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Training a dummy RandomForestClassifier model...")
        # Create dummy data for training if no model exists (12 features as per engine.py)
        dummy_features = np.random.rand(100, 12) # 100 samples, 12 features
        dummy_labels = np.random.randint(0, 2, 100) # Binary labels
        train_and_save_model(dummy_features, dummy_labels)

    print(f"Loading ML model from {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

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
    # Example of how to train and save a model if run directly
    dummy_features = np.random.rand(100, 12)
    dummy_labels = np.random.randint(0, 2, 100)
    train_and_save_model(dummy_features, dummy_labels)
    
    # Example of loading and predicting
    loaded_model = load_model()
    sample_features = np.random.rand(12) # Single sample
    prediction_result = predict(loaded_model, sample_features)
    print(f"Sample prediction: {prediction_result}")
