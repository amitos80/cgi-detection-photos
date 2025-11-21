import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import io

"""
This module provides functions for detecting deepfakes in images.
Deepfake detection often involves analyzing inconsistencies in facial features
or texture that are indicative of AI-generated manipulation.
"""

def _analyze_landmark_motion(all_frame_landmarks: list[np.ndarray]) -> float:
    """
    Analyzes the motion of facial landmarks across frames for inconsistencies.
    This function is now designed for *future* video processing and is not used
    in the current `detect_deepfake` for static images.

    Args:
        all_frame_landmarks: A list of numpy arrays, where each array contains
                             the (x, y, z) coordinates of facial landmarks for a frame.

    Returns:
        A motion inconsistency score between 0.0 and 1.0.
    """
    if len(all_frame_landmarks) < 2:
        return 0.0 # Not enough frames for motion analysis

    NOSE_TIP_LANDMARK_IDX = 1 
    
    displacements = []
    for i in range(1, len(all_frame_landmarks)):
        if (len(all_frame_landmarks[i-1]) > NOSE_TIP_LANDMARK_IDX and
            len(all_frame_landmarks[i]) > NOSE_TIP_LANDMARK_IDX):
            
            prev_pos = all_frame_landmarks[i-1][NOSE_TIP_LANDMARK_IDX][:2] # Only use x, y for 2D displacement
            curr_pos = all_frame_landmarks[i][NOSE_TIP_LANDMARK_IDX][:2]
            
            displacement = np.linalg.norm(curr_pos - prev_pos)
            displacements.append(displacement)

    if not displacements:
        return 0.0

    avg_displacement = np.mean(displacements)
    std_displacement = np.std(displacements)

    inconsistency_score = 0.0
    if avg_displacement > 0: # Avoid division by zero
        inconsistency_score = std_displacement / avg_displacement
    
    return min(inconsistency_score * 0.5, 1.0) # Multiply by 0.5 to make it less aggressive initially

def detect_deepfake(image_bytes: bytes) -> dict:
    """
    Analyzes an image for characteristics of a deepfake, focusing on static image analysis.

    Args:
        image_bytes: The raw bytes of the image.

    Returns:
        A dictionary containing the detection results, including a confidence score
        and any identified artifacts.
    """
    try:
        image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image_pil)
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR) # Convert to BGR for MediaPipe
        
        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5) as face_mesh:
            results = face_mesh.process(image_rgb)
            
            if results.multi_face_landmarks:
                # Static image analysis (e.g., texture inconsistencies, facial geometry)
                # For now, just a placeholder. More advanced static analysis could be added here.
                static_score = 0.5 # Placeholder for static analysis
                return {
                    "is_deepfake": (static_score > 0.5),
                    "confidence": static_score,
                    "details": "Deepfake detection with static image analysis."
                }
            else:
                return {
                    "is_deepfake": False,
                    "confidence": 0.0,
                    "details": "No face detected in the image."
                }
    except Exception as e:
        return {
            "is_deepfake": False,
            "confidence": 0.0,
            "details": f"Error processing image bytes: {e}"
        }

