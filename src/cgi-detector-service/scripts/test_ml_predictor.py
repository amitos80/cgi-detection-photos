"""
Test script for the ML Predictor module
"""
import sys
import os
import pytest
import numpy as np

# Add parent directory to path to allow importing forensics modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forensics import ml_predictor

def test_ml_predictor_load_and_predict():
    """
    Tests the ML predictor's ability to load a model and make a prediction.
    """
    print("\nTesting ML Predictor Module - Load and Predict")
    print("=" * 60)

    # Ensure a dummy model exists for loading
    # The load_model function in ml_predictor.py will create one if it doesn't exist
    model = ml_predictor.load_model()
    assert model is not None, "ML model should be loaded or created."

    # Create dummy features for prediction (12 features as used in engine.py and ml_predictor.py)
    sample_features = np.random.rand(12) 
    prediction_result = ml_predictor.predict(model, sample_features)

    print(f"Sample features: {sample_features}")
    print(f"Prediction Result: {prediction_result}")

    # Assertions to check the structure and types of the prediction result
    assert isinstance(prediction_result, dict)
    assert "prediction_label" in prediction_result
    assert isinstance(prediction_result["prediction_label"], str)
    assert prediction_result["prediction_label"] in ["cgi", "real"]
    assert "confidence" in prediction_result
    assert isinstance(prediction_result["confidence"], float)
    assert 0.0 <= prediction_result["confidence"] <= 1.0

    print("ML Predictor Module test completed successfully!")
    print("The ml_predictor module is working and returning expected prediction structure.")

if __name__ == "__main__":
    test_ml_predictor_load_and_predict()
