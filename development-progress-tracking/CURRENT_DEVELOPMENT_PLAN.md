# Current Development Plan

# Development Plan: Watermark Detection Feature

## 1. Objective

Implement a new forensic analysis module to detect the presence of digital watermarks in images. This will serve as an additional feature for the CGI detection engine, as watermarks can indicate authenticity or identify the source of an image. This is based on the discussion of watermarking and content provenance in the provided research paper.

## 2. New Module: `watermarking.py`

A new file will be created at `cgi-detector-service/forensics/watermarking.py`. This module will contain the core logic for watermark detection.

### Key functions:

-   `analyze_watermark(image_bytes: bytes) -> float`: The main function that takes image bytes and returns a score from 0.0 to 1.0, indicating the likelihood of a watermark being present.

### Detection Methods to Implement:

1.  **Least Significant Bit (LSB) Analysis**:
    -   Examine the LSBs of the pixel values in the image.
    -   A non-random distribution of LSBs can indicate simple steganography or watermarking.
    -   The analysis will calculate the entropy of the LSB plane and compare it to a threshold.

2.  **Frequency Domain (FFT) Analysis**:
    -   Perform a 2D Fast Fourier Transform on the image's grayscale representation.
    -   Analyze the magnitude spectrum for unnatural peaks or periodic patterns, which are characteristic of some frequency-domain watermarking techniques.

3.  **(Future Enhancement) Metadata Analysis**:
    -   Parse image metadata (e.g., EXIF) to look for specific tags related to content provenance standards like C2PA. This will be noted for future implementation.

## 3. Integration with the Analysis Engine (`engine.py`)

The new `watermarking.py` module needs to be integrated into the main analysis pipeline.

1.  **Import**: Import the `watermarking` module in `cgi-detector-service/forensics/engine.py`.
2.  **Execute in Parallel**: Add a call to `watermarking.analyze_watermark` within the `ProcessPoolExecutor` in the `run_analysis` function.
3.  **Collect Results**: Retrieve the `watermark_score` from the executed task.
4.  **Update Feature Vector**: Add the `watermark_score` to the `ml_features` list that is fed to the machine learning model.
5.  **Update Analysis Breakdown**: Add a new dictionary to the `analysis_breakdown` list to provide users with information about the watermark analysis, its score, and what it means.
    x
## 4. Machine Learning Model Update (`ml_predictor.py`)

The addition of a new feature requires an update to the ML model pipeline.

1.  **Update Feature Extraction**: The `extract_features_from_image_bytes` function in `cgi-detector-service/forensics/ml_predictor.py` must be updated to include the `watermark_score`.
2.  **Model Retraining**: The existing `ml_model.joblib` will be incompatible with the new feature vector. The model will need to be retrained with a dataset that includes this new feature.

## 5. Testing and Profiling

To ensure correctness and performance, testing and profiling scripts will be created.

1.  **Unit/Integration Test**: Create `cgi-detector-service/scripts/test_watermarking.py`. This will include test cases with sample images known to have and not have watermarks to validate the detector's accuracy.
2.  **Performance Profiling**: Create `cgi-detector-service/forensics/profile_watermarking.py` to profile the `analyze_watermark` function and ensure it performs within acceptable time limits.

## 6. Project Scaffolding Updates

- Update `cgi-detector-service/forensics/__init__.py` to expose the new `watermarking` module.
