from . import ela, cfa, hos, jpeg_ghost

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

    # Define weights for each technique (these can be tuned)
    weights = {
        'ela': 0.25,
        'cfa': 0.25,
        'hos': 0.25,
        'jpeg_ghost': 0.25
    }

    # Calculate the final weighted-average score
    final_score = (
        ela_score * weights['ela'] +
        cfa_score * weights['cfa'] +
        hos_score * weights['hos'] +
        jpeg_ghost_score * weights['jpeg_ghost']
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
        }
    ]

    return {
        "prediction": prediction_label,
        "confidence": final_score,
        "analysis_breakdown": analysis_breakdown
    }
