# Development Plan: ML Model Training

## Prerequisites for Performance Improvement
Based on an analysis of the feature extraction process, there is a significant opportunity to improve performance before starting the full training process.

*   **Parallelize Feature Extraction:** The current `extract_features_from_image_bytes` function parallelizes the analysis of a *single* image. However, the training script processes images from the dataset sequentially. To significantly speed up data preparation, the `train_model.py` script should be modified to process multiple images in parallel using a process pool (e.g., `concurrent.futures.ProcessPoolExecutor`).

## Analysis:
The goal is to train an ML model for CGI detection using a provided dataset. The dataset is located at `dataset/train/FAKE/**` for CGI images and `dataset/train/REAL/**` for real images. The existing project structure suggests a Python-based machine learning workflow, with model serialization using `joblib` (as indicated by `forensics/ml_model.joblib`) and a separate feature extraction step (from `cgi-detector-service/scripts/extract_features.py`). Prediction logic is likely housed in `cgi-detector-service/forensics/ml_predictor.py`. Python dependencies are managed via `cgi-detector-service/requirements.txt`.

## Plan:
1.  **Implement Performance Improvements:**
    *   Modify the `load_images_and_extract_features` function in `cgi-detector-service/scripts/train_model.py` to use a `ProcessPoolExecutor`. This will allow it to extract features from multiple images concurrently, drastically reducing the total data preparation time.
2.  **Inspect Existing ML Code:** Read `cgi-detector-service/forensics/ml_predictor.py` and `cgi-detector-service/scripts/extract_features.py` to understand the current model architecture, input expectations, and feature extraction methodology.
3.  **Environment Setup:** Ensure all necessary Python dependencies are installed by reviewing `cgi-detector-service/requirements.txt` and installing them.
4.  **Data Loading with Progress Tracking:** Modify the `cgi-detector-service/scripts/train_model.py` script to:
    *   Use a JSON file (`training_progress.json`) to track which image files have already been processed and had features extracted.
    *   On startup, the script will load the list of processed files from the JSON file.
    *   Before processing an image, it will check if the file path is in the list of processed files. If so, it will be skipped.
    *   After successfully extracting features from a new image, the script will append its file path to the list and save the updated list back to `training_progress.json`.
    *   Load images from `dataset/train/FAKE` and `dataset/train/REAL`.
    *   Assign numerical labels (e.g., 0 for REAL, 1 for FAKE).
5.  **Dataset Splitting:** Split the processed data into training, validation, and testing sets to properly evaluate model performance and prevent overfitting.
6.  **Model Definition and Training:** Within the `train_model.py` script:
    *   Define the machine learning model architecture.
    *   Implement the training loop using the training data.
    *   Monitor performance on the validation set.
7.  **Model Evaluation:** Evaluate the trained model's performance on the unseen test set using appropriate metrics (e.g., accuracy, precision, recall, F1-score).
8.  **Model Saving:** Save the trained model to `forensics/ml_model.joblib` using `joblib.dump()`. Ensure this file is tracked by Git.
9.  **Update Prediction Logic:** If necessary, modify `cgi-detector-service/forensics/ml_predictor.py` to ensure it correctly loads and utilizes the newly trained model from `forensics/ml_model.joblib`.
10. **Testing:** Create or update unit tests (e.g., in `cgi-detector-service/scripts/test_train_model.py` and `cgi-detector-service/scripts/test_ml_predictor.py`) to verify the training script's functionality and the updated model's prediction accuracy.