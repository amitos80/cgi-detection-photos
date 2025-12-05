# Current Development Plan

# Development Plan: Statistical Anomaly Detection (SAD) Feature

## 1. Objective

Implement a new forensic analysis module called "Statistical Anomaly Detection (SAD)" to identify subtle visual statistical inconsistencies that deviate from natural image characteristics. This feature will provide a strong, distinct indicator for CGI and will complement the current metric features in `cgi-detector-service/forensics/engine.py`, based on the "Perceptual Inconsistencies" insights from Hany Farid's research.

## Tasks and TODO Steps:

### Task 1: Implement Statistical Anomaly Detection Module

*   **Step 1: Create `statistical_anomaly.py`**
    *   **TODO:** Create the file `cgi-detector-service/forensics/statistical_anomaly.py`.
*   **Step 2: Implement `analyze_statistical_anomaly` function**
    *   **TODO:** Implement the `analyze_statistical_anomaly(image_bytes: bytes) -> float` function within `statistical_anomaly.py`. This function will contain the core logic for statistical anomaly detection, returning a score between 0.0 and 1.0.

### Task 2: Integrate SAD with Analysis Engine (`engine.py`)

*   **Step 1: Import `statistical_anomaly`**
    *   **TODO:** Add `import .statistical_anomaly` to `cgi-detector-service/forensics/engine.py`.
*   **Step 2: Execute in Parallel**
    *   **TODO:** Add `futures['statistical_anomaly'] = executor.submit(statistical_anomaly.analyze_statistical_anomaly, processed_image_bytes)` within the `ProcessPoolExecutor` in the `run_analysis` function in `engine.py`.
*   **Step 3: Collect Results**
    *   **TODO:** Retrieve the `statistical_anomaly_score` from the `futures` results in `engine.py`.
*   **Step 4: Update Feature Vector**
    *   **TODO:** Add `statistical_anomaly_score` to the `ml_features` list in `engine.py`.
*   **Step 5: Update Analysis Breakdown**
    *   **TODO:** Add a new dictionary to the `analysis_breakdown` list in `engine.py` to describe the "Statistical Anomaly Detection" feature, its score, normal range, and insight.

### Task 3: Update Machine Learning Model Pipeline (`ml_predictor.py`)

*   **Step 1: Update Feature Extraction**
    *   **TODO:** Modify `cgi-detector-service/forensics/ml_predictor.py` to include `statistical_anomaly_score` in the `extract_features_from_image_bytes` function.
*   **Step 2: Model Retraining**
    *   **TODO:** (Manual Step) The existing `ml_model.joblib` will be incompatible with the new feature vector. The model will need to be retrained with a dataset that includes this new feature after all code changes are complete.

### Task 4: Create Testing and Profiling Scripts

*   **Step 1: Create Unit/Integration Test**
    *   **TODO:** Create `cgi-detector-service/scripts/test_statistical_anomaly.py`. This will include test cases with sample images to validate the detector's accuracy.
*   **Step 2: Create Performance Profiling Script**
    *   **TODO:** Create `cgi-detector-service/forensics/profile_statistical_anomaly.py` to profile the `analyze_statistical_anomaly` function and ensure it performs within acceptable time limits.

### Task 5: Update Project Scaffolding

*   **Step 1: Expose New Module in `__init__.py`**
    *   **TODO:** Add `from . import statistical_anomaly` to `cgi-detector-service/forensics/__init__.py`.
