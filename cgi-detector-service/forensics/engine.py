import numpy as np
from PIL import Image
from io import BytesIO
from . import ela, cfa, hos, jpeg_ghost, rambino

def run_analysis(image_bytes: bytes):
    """
    Runs all forensic analysis techniques on an image and returns a
    unified result.

    Args:
        image_bytes: The raw bytes of the image.

    Returns:
        A dictionary containing the final prediction, confidence score,
        and a detailed breakdown of the analysis.
    """
    # Run each analysis
    ela_score = ela.analyze_ela(image_bytes)
    cfa_score = cfa.analyze_cfa(image_bytes)
    hos_score = hos.analyze_hos(image_bytes)
    jpeg_ghost_score = jpeg_ghost.analyze_jpeg_ghost(image_bytes)

    # Convert image_bytes to a NumPy array for RAMBiNo analysis
    image = Image.open(BytesIO(image_bytes)).convert('L') # Convert to grayscale
    image_data = np.array(image)
    rambino_features = rambino.analyze_rambino_features(image_data)
    rambino_score = rambino_features.get("rambino_feature_mean_noise", 0.0) # Using mean noise as a placeholder score

    # Define weights for each technique (these can be tuned)
    weights = {
        'ela': 0.2,
        'cfa': 0.2,
        'hos': 0.2,
        'jpeg_ghost': 0.2,
        'rambino': 0.2
    }

    # Calculate the final weighted-average score
    final_score = (
        ela_score * weights['ela'] +
        cfa_score * weights['cfa'] +
        hos_score * weights['hos'] +
        jpeg_ghost_score * weights['jpeg_ghost'] +
        rambino_score * weights['rambino']
    )

    # Determine the final prediction
    prediction_label = "cgi" if final_score > 0.5 else "real"

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
            "normal_range": [0.0, 0.2], # This range might need tuning based on empirical results
            "insight": "Identifies inconsistencies in JPEG compression history, indicating potential image splicing.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/" # Placeholder URL, can be updated if a specific JPEG Ghost resource is preferred
        },
        {
            "feature": "RAMBiNo Statistical Analysis",
            "score": rambino_score,
            "normal_range": [0.0, 0.1], # Placeholder range, needs empirical tuning
            "insight": "Analyzes noise and texture patterns using bivariate distributions. High scores suggest CGI.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/" # Placeholder URL, update with RAMBiNo specific resource
        }
    ]

    return {
        "prediction": prediction_label,
        "confidence": final_score,
        "analysis_breakdown": analysis_breakdown
    }
