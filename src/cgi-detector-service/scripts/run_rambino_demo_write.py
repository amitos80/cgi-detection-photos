#!/usr/bin/env python3
"""
Demo runner for RAMBiNo-inspired feature extractor that writes results to JSON.
This avoids stdout buffering issues in the environment and produces a reproducible
output file we can read back.
"""
import io
import json
import numpy as np
import numpy as np
from PIL import Image
from io import BytesIO
from . import ela, cfa, hos, jpeg_ghost, rambino


def _sigmoid(x: float) -> float:
    """Map a raw score to (0, 1) in a stable way."""
    # clamp to avoid extreme overflow
    x = max(min(x, 5.0), -5.0)
    return float(1.0 / (1.0 + np.exp(-x)))


def run_analysis(image_bytes: bytes):
    """
    Runs all forensic analysis techniques on an image and returns a
    unified result.
    """
    # Run each analysis
    ela_score = ela.analyze_ela(image_bytes)
    cfa_score = cfa.analyze_cfa(image_bytes)
    hos_score = hos.analyze_hos(image_bytes)
    jpeg_ghost_score = jpeg_ghost.analyze_jpeg_ghost(image_bytes)

    # Convert image_bytes to a NumPy array for RAMBiNo analysis
    try:
        image = Image.open(BytesIO(image_bytes)).convert('L')  # Convert to grayscale
        image_data = np.array(image)
    except Exception:
        image_data = None

    rambino_score = 0.0
    rambino_features_list = None
    try:
        if image_data is not None:
            # compute both the analysis summary and the raw feature vector
            rambino_result = rambino.analyze_rambino_features(image_data)
            # also compute raw features (may be large) but truncate before returning
            try:
                raw_feats = rambino.compute_rambino_features(image_data)
                # keep a truncated view (first 128 elements) to avoid huge payloads
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
                # If the analysis returned raw features, fall back to mean
                rambino_score = float(np.mean(rambino_result))
    except Exception:
        rambino_score = 0.0
        rambino_features_list = None

    # Define weights for each technique (these can be tuned)
    weights = {
        'ela': 0.2,
        'cfa': 0.2,
        'hos': 0.2,
        'jpeg_ghost': 0.2,
        'rambino': 0.2
    }

    # Calculate the final weighted-average score (raw, unbounded)
    raw_score = (
        ela_score * weights['ela'] +
        cfa_score * weights['cfa'] +
        hos_score * weights['hos'] +
        jpeg_ghost_score * weights['jpeg_ghost'] +
        rambino_score * weights['rambino']
    )

    # Map to [0, 1] confidence
    confidence = _sigmoid(raw_score)

    # Determine the final prediction using normalized confidence
    prediction_label = "cgi" if confidence > 0.5 else "real"

    # Create the analysis breakdown
    analysis_breakdown = [
        {
            "feature": "Error Level Analysis (ELA)",
            "score": ela_score,
            "normal_range": [0.0, 0.2],
            "insight": "Detects inconsistencies in JPEG compression artifacts. High scores suggest manipulation.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "Color Filter Array (CFA)",
            "score": cfa_score,
            "normal_range": [0.0, 0.3],
            "insight": "Analyzes low-level sensor patterns. High scores indicate a disruption of natural camera patterns.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "Wavelet Statistics (HOS)",
            "score": hos_score,
            "normal_range": [0.0, 0.4],
            "insight": "Measures statistical properties of the image. High scores suggest the image is synthetic.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "JPEG Ghost Analysis",
            "score": jpeg_ghost_score,
            "normal_range": [0.0, 0.2],  # This range might need tuning based on empirical results
            "insight": "Identifies inconsistencies in JPEG compression history, indicating potential image splicing.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"  # Placeholder URL
        },
        {
            "feature": "RAMBiNo Statistical Analysis",
            "score": rambino_score,
            "normal_range": [0.0, 0.1],  # Placeholder range, needs empirical tuning
            "insight": "Analyzes noise and texture patterns using bivariate distributions. High scores suggest CGI.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"  # Placeholder URL
        }
    ]

    result = {
        "prediction": prediction_label,
        "confidence": confidence,
        "analysis_breakdown": analysis_breakdown,
        "raw_score": raw_score,  # optional, useful for debugging/tuning
    }

    # Attach truncated rambino features for inspection if available
    if rambino_features_list is not None:
        result["rambino_features"] = rambino_features_list

    return result

