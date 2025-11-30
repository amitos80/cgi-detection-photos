import sys
import numpy as np
from PIL import Image
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor
from . import ela, cfa, hos, jpeg_ghost, rambino, geometric_3d, lighting_text, jpeg_dimples
from . import specialized_detectors  # <-- ADD THIS IMPORT
from . import deepfake_detector, reflection_consistency, double_quantization, ml_predictor

_ml_model = ml_predictor.get_model() # Load ML model once at startup via get_model

def reload_ml_model():
    """
    Reloads the ML model into the engine from ml_predictor.
    """
    global _ml_model
    _ml_model = ml_predictor.reload_model()
    print("ML model reloaded in engine.")

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

    # Initialize a dictionary to hold future results from parallel tasks.
    futures = {}
    # Use ThreadPoolExecutor for concurrent execution of forensic analysis functions.
    # This allows multiple CPU-bound tasks to run in separate threads,
    # potentially reducing overall execution time.
    with ProcessPoolExecutor() as executor:
        # Submit each analysis function to the executor.
        # Each .submit() call returns a Future object representing the eventual result.
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

        # RAMBiNo analysis requires specific image preprocessing (grayscale conversion to NumPy array).
        # This helper function encapsulates the RAMBiNo-specific logic, including image conversion,
        # and is submitted as a separate task to the executor.
        futures['rambino'] = executor.submit(run_rambino_analysis, processed_image_bytes)

        # Collect results from all futures.
        # .result() blocks until the corresponding task is complete.
        # Exception handling is included for robust error management in each analysis.
        results = {}
        rambino_raw_score = 0.0
        rambino_features_list = None
        specialized_detector_scores = {}
        specialized_likely_type = 'Unknown'

        for name, future in futures.items():
            try:
                if name == 'rambino':
                    try:
                        rambino_result = future.result()
                        results['rambino'] = rambino_result['score']
                        rambino_raw_score = rambino_result['raw_score']
                        rambino_features_list = rambino_result['features']
                    except Exception as e:
                        print(f"Error running rambino analysis subprocess: {e}")
                        results['rambino'] = 0.0
                        rambino_raw_score = 0.0
                        rambino_features_list = None
                elif name == 'specialized_detector':
                    try:
                        specialized_result = future.result()
                        results['specialized'] = specialized_result.get('overall_score', 0.0)
                        specialized_detector_scores = specialized_result.get('detector_scores', {})
                        specialized_likely_type = specialized_result.get('likely_type', 'Unknown')
                    except Exception as e:
                        print(f"Error running specialized_detector analysis subprocess: {e}")
                        results['specialized'] = 0.0
                        specialized_detector_scores = {}
                        specialized_likely_type = 'Unknown'
                else:
                    try:
                        results[name] = future.result()
                    except Exception as e:
                        print(f"Error running {name} analysis subprocess: {e}")
                        results[name] = 0.0 # Default/error value
            except Exception as e:
                print(f"Error running {name} analysis: {e}")
                results[name] = 0.0 # Default/error value

    # Assign collected scores to individual variables for downstream calculations.
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

    # Create feature vector for ML model
    ml_features = [
        ela_score, cfa_score, hos_score, jpeg_ghost_score, jpeg_dimples_score, rambino_score,
        geometric_score, lighting_score, specialized_score,
        deepfake_score, reflection_score, double_quantization_score
    ]

    # Replace any NaN values in ml_features with 0.0 to prevent prediction errors
    ml_features = [0.0 if np.isnan(f) else f for f in ml_features]

    # Make prediction using the loaded ML model
    ml_prediction_result = ml_predictor.predict(_ml_model, ml_features)
    prediction_label = ml_prediction_result["prediction_label"]
    final_score = ml_prediction_result["confidence"]

    print(f"DEBUG: ela_score: {ela_score}")
    print(f"DEBUG: cfa_score: {cfa_score}")
    print(f"DEBUG: hos_score: {hos_score}")
    print(f"DEBUG: jpeg_ghost_score: {jpeg_ghost_score}")
    print(f"DEBUG: jpeg_dimples_score: {jpeg_dimples_score}")
    print(f"DEBUG: rambino_score: {rambino_score}")
    print(f"DEBUG: geometric_score: {geometric_score}")
    print(f"DEBUG: lighting_score: {lighting_score}")
    print(f"DEBUG: specialized_score: {specialized_score}")
    print(f"DEBUG: deepfake_score: {deepfake_score}")
    print(f"DEBUG: reflection_score: {reflection_score}")
    print(f"DEBUG: double_quantization_score: {double_quantization_score}")

    # Make prediction using the loaded ML model
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
            "feature": "JPEG Dimples Analysis",
            "score": jpeg_dimples_score,
            "normal_range": [0.0, 0.2],
            "insight": "Detects periodic artifacts from JPEG compression. Disruption of these patterns indicates manipulation.",
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
        },
        {
            "feature": "Deepfake Detection",
            "score": deepfake_score,
            "normal_range": [0.0, 0.5],
            "insight": "Detects AI-generated manipulation in faces or motion. High scores suggest a deepfake.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/deepfakes/"
        },
        {
            "feature": "Reflection Inconsistency",
            "score": reflection_score,
            "normal_range": [0.0, 0.6],
            "insight": "Analyzes images for inconsistencies in reflections. High scores suggest image manipulation.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/photo-forensics/"
        },
        {
            "feature": "Video Double Quantization",
            "score": double_quantization_score,
            "normal_range": [0.0, 0.7],
            "insight": "Detects re-encoding artifacts in video frames. High scores suggest video manipulation.",
            "url": "https://farid.berkeley.edu/research/digital-forensics/video-forensics/"
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
