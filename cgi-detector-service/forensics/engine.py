from . import ela, cfa, hos

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

    # Define weights for each technique (these can be tuned)
    weights = {
        'ela': 0.4,
        'cfa': 0.3,
        'hos': 0.3
    }

    # Calculate the final weighted-average score
    final_score = (
        ela_score * weights['ela'] +
        cfa_score * weights['cfa'] +
        hos_score * weights['hos']
    )

    # Determine the final prediction
    prediction_label = "cgi" if final_score > 0.5 else "real"

    # Create the analysis breakdown
    analysis_breakdown = [
        {
            "feature": "Error Level Analysis (ELA)",
            "score": ela_score,
            "normal_range": [0.0, 0.2],
            "insight": "Detects inconsistencies in JPEG compression artifacts. High scores suggest manipulation."
        },
        {
            "feature": "Color Filter Array (CFA)",
            "score": cfa_score,
            "normal_range": [0.0, 0.3],
            "insight": "Analyzes low-level sensor patterns. High scores indicate a disruption of natural camera patterns."
        },
        {
            "feature": "Wavelet Statistics (HOS)",
            "score": hos_score,
            "normal_range": [0.0, 0.4],
            "insight": "Measures statistical properties of the image. High scores suggest the image is synthetic."
        }
    ]

    return {
        "prediction": prediction_label,
        "confidence": final_score,
        "analysis_breakdown": analysis_breakdown
    }
