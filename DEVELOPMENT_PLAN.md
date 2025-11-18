# Development Plan: Improving CGI Detection Accuracy

## 1. Executive Summary

The current CGI detection engine relies on a collection of forensic analysis algorithms, the outputs of which are combined using a hardcoded, weighted-average formula. While this provides a solid baseline, it has significant limitations in accuracy and adaptability, as the weights are not empirically optimized and cannot capture complex relationships between features.

This plan outlines a strategic, phased approach to evolve the system from a heuristic-based model to a data-driven, machine learning-powered solution. By systematically curating a dataset, establishing a rigorous evaluation framework, and incrementally integrating more sophisticated models, we can significantly improve the accuracy, reliability, and robustness of our CGI detection capabilities.

---

## Phase 1: Foundational Setup - Data Curation & Baseline Evaluation

**Goal:** To establish a standardized dataset and an evaluation framework to measure the performance of the current system and all future improvements. We cannot improve what we cannot measure.

**Tasks:**

1.  **Dataset Curation:**
    *   **Action:** Assemble a diverse and balanced dataset of images.
    *   **Requirements:**
        *   **Real Images:** Minimum 5,000 high-quality photographs from various sources (e.g., personal photos, stock images).
        *   **CGI Images:** Minimum 5,000 CGI images covering different categories:
            *   3D Renders (e.g., architectural visualizations, product mockups).
            *   Video Game Screenshots.
            *   AI-Generated Images (e.g., from Stable Diffusion, Midjourney, DALL-E).
            *   Composited images (photo-realistic CGI mixed with real elements).
    *   **Structure:** Organize the dataset into a clear directory structure, such as `/dataset/train/real`, `/dataset/train/cgi`, `/dataset/test/real`, etc.

2.  **Create an Evaluation Script (`evaluate.py`):**
    *   **Action:** Develop a Python script that iterates through the test portion of the curated dataset.
    *   **Functionality:**
        *   For each image, it will call the existing `cgi-detector-service/forensics/engine.py`'s `run_analysis` function.
        *   It will compare the model's prediction (`cgi` or `real`) against the ground truth label.
        *   It will calculate and report key performance metrics:
            *   Accuracy
            *   Precision
            *   Recall
            *   F1-Score
            *   Confusion Matrix
    *   **Outcome:** This script will provide a quantitative baseline for the current system's performance.

---

## Phase 2: Integrating a Machine Learning Classifier

**Goal:** To replace the simple weighted-average logic with a trained machine learning model that can learn the optimal way to combine the existing forensic features.

**Tasks:**

1.  **Develop a Feature Extraction Pipeline:**
    *   **Action:** Create a script that runs every image in the dataset through the individual forensic analysis functions (`ela`, `cfa`, `hos`, etc.).
    *   **Output:** Generate a CSV or Parquet file containing the extracted features (scores) for each image, along with its ground truth label. This will be our training data.

2.  **Train a Classifier Model:**
    *   **Action:** Use the generated feature set to train a classical machine learning model.
    *   **Tools:** Utilize `scikit-learn` or `XGBoost`.
    *   **Process:**
        *   Load the feature dataset.
        *   Split the data into training and validation sets.
        *   Train several candidate models (e.g., `RandomForestClassifier`, `GradientBoostingClassifier`, `SVC`).
        *   Perform hyperparameter tuning to find the best-performing model.
        *   Save the trained model artifact (e.g., using `joblib` or `pickle`).

3.  **Integrate the Trained Model into the Engine:**
    *   **Action:** Modify `cgi-detector-service/forensics/engine.py`.
    *   **Changes:**
        *   Load the saved ML model during application startup.
        *   In `run_analysis`, after collecting all the individual forensic scores, feed them into the loaded model.
        *   The model's output will now be the final prediction and confidence score, replacing the weighted average and heuristic rules.

---

## Phase 3: Advanced Deep Learning for End-to-End Detection

**Goal:** To implement a state-of-the-art deep learning model that can learn features directly from image pixels, potentially outperforming the handcrafted forensic feature set.

**Tasks:**

1.  **Research and Select a CNN Architecture:**
    *   **Action:** Investigate common and effective Convolutional Neural Network (CNN) architectures for image classification.
    *   **Candidates:** `ResNet50`, `EfficientNetV2`, `ConvNeXt`.
    *   **Decision Criteria:** Balance performance, model size, and inference speed.

2.  **Develop a Deep Learning Training Pipeline:**
    *   **Action:** Create a new set of scripts for training the CNN.
    *   **Tools:** Use a deep learning framework like `PyTorch` or `TensorFlow/Keras`.
    *   **Functionality:**
        *   Data loaders for the image dataset with appropriate augmentations (e.g., flips, rotations, color jitter) to improve model robustness.
        *   A training loop that implements backpropagation, optimization, and learning rate scheduling.
        *   Validation loop to monitor performance and prevent overfitting.
        *   Save the best-performing model weights.

3.  **Integrate the CNN Model:**
    *   **Action:** The trained CNN can be integrated in two ways:
        1.  **As a Standalone Predictor:** It can replace the entire Phase 2 ensemble, providing the final prediction directly.
        2.  **As a Feature Extractor:** The CNN's prediction score can be added as a new, powerful feature to the Phase 2 model, allowing the classifier to weigh the CNN's opinion against the traditional forensic signals.
    *   **Implementation:** Create a new module (`cnn_detector.py`) and incorporate it into the main `engine.py`.

---

## Phase 4: Continuous Improvement & Deployment

**Goal:** To ensure the detection model remains accurate and up-to-date with the evolving landscape of CGI and AI-generated imagery.

**Tasks:**

1.  **Continuous Dataset Augmentation:**
    *   **Action:** Develop a process for regularly adding new, challenging, and diverse images to the dataset.
    *   **Source:** Actively seek out images created with the latest generative models and rendering techniques.

2.  **Model Retraining and Monitoring:**
    *   **Action:** Establish a CI/CD pipeline for periodically retraining the models (both the classic classifier and the CNN) on the augmented dataset.
    *   **Monitoring:** Implement logging to track model predictions and confidence scores in a production environment. This can help identify performance degradation or concept drift over time.