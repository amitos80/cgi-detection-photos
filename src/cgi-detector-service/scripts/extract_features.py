"""
Script to extract forensic features from a dataset of images using the cgi-detector-service engine.
This script assumes a simple dataset structure for demonstration purposes:
DATASET_ROOT/
├── real/
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
└── fake/
    ├── image_fake1.png
    ├── image_fake2.jpg
    └── ...
"""
import os
import sys
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO

# Adjust path to import from forensics
sys.path.insert(0, os.path.join(os.getcwd(), 'cgi-detector-service'))
from forensics.engine import run_analysis

# --- Configuration --- #
DATASET_ROOT = "./dummy_dataset"
OUTPUT_FEATURES_FILE = "./extracted_features.csv"

def create_dummy_dataset(num_real=5, num_fake=5):
    """
    Creates a dummy dataset structure with placeholder image files.
    """
    print(f"Creating dummy dataset at {DATASET_ROOT}...")
    os.makedirs(os.path.join(DATASET_ROOT, "real"), exist_ok=True)
    os.makedirs(os.path.join(DATASET_ROOT, "fake"), exist_ok=True)

    for i in range(num_real):
        img = Image.new('RGB', (200, 200), color=(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
        img.save(os.path.join(DATASET_ROOT, "real", f"real_image_{i}.png"))
    for i in range(num_fake):
        img = Image.new('RGB', (200, 200), color=(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)))
        img.save(os.path.join(DATASET_ROOT, "fake", f"fake_image_{i}.png"))
    print("Dummy dataset created.")

def extract_features(dataset_root: str) -> pd.DataFrame:
    """
    Extracts forensic features from images in the specified dataset root directory.

    Args:
        dataset_root: Path to the root of the dataset (e.g., contains 'real/' and 'fake/' subdirectories).

    Returns:
        A Pandas DataFrame containing extracted features and labels.
    """
    all_features = []
    labels = []
    filepaths = []

    for label_dir in ["real", "fake"]:
        current_label = 0 if label_dir == "real" else 1 # 0 for real, 1 for fake/cgi
        full_dir_path = os.path.join(dataset_root, label_dir)

        if not os.path.exists(full_dir_path):
            print(f"Warning: Directory {full_dir_path} not found. Skipping.")
            continue

        for filename in os.listdir(full_dir_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(full_dir_path, filename)
                print(f"Processing {filepath}...")
                try:
                    with open(filepath, 'rb') as f:
                        image_bytes = f.read()
                    
                    # Run analysis using the engine
                    analysis_result = run_analysis(image_bytes)
                    
                    # Extract relevant features from the analysis breakdown
                    features_dict = {}
                    for item in analysis_result["analysis_breakdown"]:
                        features_dict[item["feature"]] = item["score"]
                    
                    # Add other scores if needed
                    features_dict["rambino_raw_score"] = analysis_result.get("rambino_raw_score", 0.0)
                    # Add specialized detector scores as individual features if available
                    if "specialized_detector_scores" in analysis_result:
                        for det_name, det_score in analysis_result["specialized_detector_scores"].items():
                            features_dict[f"specialized_{det_name}"] = det_score

                    all_features.append(features_dict)
                    labels.append(current_label)
                    filepaths.append(filepath)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    if not all_features:
        print("No features extracted.")
        return pd.DataFrame()

    features_df = pd.DataFrame(all_features)
    features_df["label"] = labels
    features_df["filepath"] = filepaths
    return features_df

if __name__ == "__main__":
    # Create dummy dataset for demonstration
    create_dummy_dataset()

    print("Starting feature extraction...")
    extracted_features_df = extract_features(DATASET_ROOT)

    if not extracted_features_df.empty:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FEATURES_FILE), exist_ok=True)
        extracted_features_df.to_csv(OUTPUT_FEATURES_FILE, index=False)
        print(f"Features extracted and saved to {OUTPUT_FEATURES_FILE}")
        print(extracted_features_df.head())
    else:
        print("No features to save.")
