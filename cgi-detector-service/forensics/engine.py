import numpy as np
from PIL import Image
from io import BytesIO
from . import ela, cfa, hos, jpeg_ghost, rambino, geometric_3d, lighting_text
from . import specialized_detectors  # <-- ADD THIS IMPORT

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
    # Open and downsize the image
    try:
        original_image = Image.open(BytesIO(image_bytes))
        downsized_image = downsize_image_to_480p(original_image)

        # Convert the downsized image back to bytes for analysis functions
        buffered = BytesIO()
        downsized_image.save(buffered, format="PNG")  # Use PNG to avoid re-compression artifacts for analysis
        processed_image_bytes = buffered.getvalue()
    except Exception as e:
        # Handle potential errors during image processing/downsizing
        print(f"Error processing or downsizing image: {e}")
        # Fallback to original image_bytes if downsizing fails
        processed_image_bytes = image_bytes

    # Run each analysis
    ela_score = ela.analyze_ela(processed_image_bytes)
    cfa_score = cfa.analyze_cfa(processed_image_bytes)
    hos_score = hos.analyze_hos(processed_image_bytes)
    jpeg_ghost_score = jpeg_ghost.analyze_jpeg_ghost(processed_image_bytes)
    geometric_score = geometric_3d.analyze_geometric_consistency(processed_image_bytes)
    lighting_score = lighting_text.analyze_lighting_consistency(processed_image_bytes)

    # Convert image_bytes to a NumPy array for RAMBiNo analysis
    try:
        image = Image.open(BytesIO(processed_image_bytes)).convert('L')  # Convert to grayscale
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

    # --- Normalize RAMBiNo score to a sane range ---
    # Keep a copy of the raw, unscaled score for debugging/tuning
    rambino_raw_score = rambino_score
    # Heuristic scaling: large values (e.g. ~30k) get mapped into [0, 1]
    # Adjust 30000.0 if you later have better empirical stats.
    scale = 30000.0
    rambino_score = float(np.clip(rambino_raw_score / scale, 0.0, 1.0))
    # --- end normalization ---

    # --- Specialized Detectors ---
    try:
        specialized_result = specialized_detectors.analyze_specialized_cgi_types(processed_image_bytes)
        specialized_score = specialized_result.get('overall_score', 0.0)
        specialized_detector_scores = specialized_result.get('detector_scores', {})  # Dict for breakdown
        specialized_likely_type = specialized_result.get('likely_type', 'Unknown')
    except Exception as e:
        specialized_score = 0.0
        specialized_detector_scores = {}
        specialized_likely_type = 'Unknown'

    # --- Update the weights to include specialized detector ---
    weights = {
        'ela': 0.10,
        'cfa': 0.10,
        'hos': 0.15,
        'jpeg_ghost': 0.15,
        'rambino': 0.10,
        'geometric': 0.15,
        'lighting': 0.15,
        'specialized': 0.10
    }
    # Sum = 1.0

    # Calculate the final weighted-average score
    final_score = (
        ela_score * weights['ela'] +
        cfa_score * weights['cfa'] +
        hos_score * weights['hos'] +
        jpeg_ghost_score * weights['jpeg_ghost'] +
        rambino_score * weights['rambino'] +
        geometric_score * weights['geometric'] +
        lighting_score * weights['lighting'] +
        specialized_score * weights['specialized']
    )

    # Determine the final prediction
    # Summing features that are out of normal range - meaning cgi
    features_point_cgi = 0
    # if ela_score > 0.2: features_point_cgi = features_point_cgi + 1
    #
    # if cfa_score > 0.3: features_point_cgi = features_point_cgi + 1
    #
    # if hos_score > 0.4: features_point_cgi = features_point_cgi + 1
    #
    # if jpeg_ghost_score > 0.2: features_point_cgi = features_point_cgi + 1
    #
    # if rambino_score > 0.1: features_point_cgi = features_point_cgi + 1
    #
    # if geometric_score > 0.3: features_point_cgi = features_point_cgi + 1
    #
    # if lighting_score > 0.3: features_point_cgi = features_point_cgi + 1
    #
    # if rambino_score > 0.1: features_point_cgi = features_point_cgi + 1
    #
    # if features_point_cgi > 4:
    #     prediction_label = 'cgi'
    # else:
    #     prediction_label = "cgi" if final_score > 0.5 else "real"

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
            "normal_range": [0.0, 0.2],
            "insight": "Identifies inconsistencies in JPEG compression history, indicating potential image splicing.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "RAMBiNo Statistical Analysis",
            "score": rambino_score,
            "normal_range": [0.0, 0.1],
            "insight": "Analyzes noise and texture patterns using bivariate distributions. High scores suggest CGI.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "3D Geometric Consistency",
            "score": geometric_score,
            "normal_range": [0.0, 0.3],
            "insight": "Analyzes geometric properties including symmetry, smoothness, edge regularity, and gradient consistency. High scores indicate unnatural geometric patterns typical of CGI.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "Scene Lighting Consistency",
            "score": lighting_score,
            "normal_range": [0.0, 0.3],
            "insight": "Analyzes lighting direction consistency across regions, shadow alignment, and lighting in high-contrast areas. High scores indicate inconsistent lighting typical of composites or CGI.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/"
        },
        {
            "feature": "Specialized CGI/AIGC Detector",
            "score": specialized_score,
            "normal_range": [0.0, 0.4],
            "insight": (
                "Runs specialized detection for GAN, diffusion, face synthesis, and 3D rendering artifacts. "
                "High scores indicate evidence of generative-AI or CGI. "
                f"Type most likely: {specialized_likely_type}. "
                f"Breakdown: {specialized_detector_scores}"
            ),
            "url": ""
        }
    ]


    result = {
        "prediction": prediction_label,
        "confidence": final_score,
        "analysis_breakdown": analysis_breakdown,
        "rambino_raw_score": rambino_raw_score,  # optional: raw, unscaled value
    }

    # Attach truncated rambino features for inspection if available
    if rambino_features_list is not None:
        result["rambino_features"] = rambino_features_list

    # Attach full specialized detector breakdown for inspection, if desired
    result["specialized_detector_scores"] = specialized_detector_scores
    result["specialized_likely_type"] = specialized_likely_type

    return result
