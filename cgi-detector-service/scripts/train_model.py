import os
import sys
import numpy as np
import json
import re
import joblib
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Adjust path to import from forensics
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forensics.ml_predictor import extract_features_from_image_bytes, train_and_save_model

# --- Configuration --- #
DATASET_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'train'))
PROGRESS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'training_progress.json'))
FEATURES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extracted_features.joblib'))
CHUNK_SIZE = 200

def clean_filename(filename):
    """Converts a filename to a safe key for the JSON progress file."""
    return re.sub(r'[\s\W]+', '_', filename)

def initialize_progress_file():
    """Scans the dataset and creates the initial progress file if it doesn't exist."""
    if os.path.exists(PROGRESS_FILE):
        return

    print("Initializing progress file...")
    all_files = []
    for label_dir_name in ['REAL', 'FAKE']:
        current_label_path = os.path.join(DATASET_ROOT, label_dir_name)
        if os.path.exists(current_label_path):
            for filename in os.listdir(current_label_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    all_files.append(os.path.join(current_label_path, filename))
    
    all_files.sort()
    chunks = [all_files[i:i + CHUNK_SIZE] for i in range(0, len(all_files), CHUNK_SIZE)]
    
    progress_data = {
        "chunks": chunks,
        "image_tracking": {},
        "currently_being_processed": None
    }

    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress_data, f, indent=4)
    print("Progress file initialized.")

def process_image(filepath):
    """Stateless worker function to process a single image file."""
    try:
        with open(filepath, "rb") as f:
            image_bytes = f.read()
        features = extract_features_from_image_bytes(image_bytes)
        if features.size > 0:
            return filepath, features.flatten(), None
    except Exception as e:
        return filepath, None, str(e)
    return filepath, None, "Unknown error"


def run_feature_extraction():
    """
    Manager function that loads images, orchestrates parallel feature extraction,
    and safely tracks and saves progress and extracted features.
    """
    if not os.path.exists(PROGRESS_FILE):
        initialize_progress_file()

    with open(PROGRESS_FILE, 'r') as f:
        progress_data = json.load(f)

    # Load previously extracted features
    if os.path.exists(FEATURES_FILE):
        print(f"Loading previously extracted features from {FEATURES_FILE}...")
        saved_data = joblib.load(FEATURES_FILE)
        all_features = saved_data.get('features', [])
        all_labels = saved_data.get('labels', [])
    else:
        all_features = []
        all_labels = []

    # Create a set of completed file paths for quick lookup
    completed_files = set()
    if all_features and 'processed_filepaths' in saved_data:
        completed_files = set(saved_data['processed_filepaths'])

    # Determine which files need processing
    tasks = []
    flat_chunks = [item for sublist in progress_data.get('chunks', []) for item in sublist]
    for filepath in flat_chunks:
        if filepath not in completed_files:
            tasks.append(filepath)

    if not tasks:
        print("All images have already been processed and features extracted.")
        return np.array(all_features), np.array(all_labels)
        
    print(f"Found {len(tasks)} new or unfinished images to process.")

    newly_extracted_features = []
    newly_extracted_labels = []
    processed_filepaths_this_run = []

    with ProcessPoolExecutor() as executor:
        future_to_filepath = {executor.submit(process_image, filepath): filepath for filepath in tasks}

        for future in tqdm(as_completed(future_to_filepath), total=len(tasks), desc="Processing Images"):
            filepath, features, error = future.result()
            file_key = clean_filename(os.path.basename(filepath))

            if features is not None:
                progress_data['image_tracking'][file_key] = {"status": "completed"}
                newly_extracted_features.append(features)
                newly_extracted_labels.append(1 if 'FAKE' in filepath else 0)
                processed_filepaths_this_run.append(filepath)
            else:
                progress_data['image_tracking'][file_key] = {"status": "error", "error": error}

            # Safely write the updated progress
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress_data, f, indent=4)

    if not newly_extracted_features:
        print("No new features were successfully extracted in this run.")
        return np.array(all_features), np.array(all_labels)

    # Combine old and new features and save
    print("Combining new features with previously saved features...")
    combined_features = all_features + newly_extracted_features
    combined_labels = all_labels + newly_extracted_labels
    combined_filepaths = list(completed_files) + processed_filepaths_this_run
    
    joblib.dump({
        'features': combined_features, 
        'labels': combined_labels,
        'processed_filepaths': combined_filepaths
    }, FEATURES_FILE)
    print(f"Saved {len(combined_features)} total features to {FEATURES_FILE}.")
        
    return np.array(combined_features), np.array(combined_labels)


if __name__ == "__main__":
    print("Starting ML model training script...")
    
    features, labels = run_feature_extraction()

    if features.size > 0:
        print(f"Training model with {len(features)} total samples.")
        train_and_save_model(features, labels)
        print("ML model training completed and model saved.")
    else:
        print("No data available for training. Model training aborted.")