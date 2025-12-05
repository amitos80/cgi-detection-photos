# Development Plan Tasks: Watermark Detection Feature

This document breaks down the tasks required to implement the watermark detection feature as outlined in the [CURRENT_DEVELOPMENT_PLAN.md](./CURRENT_DEVELOPMENT_PLAN.md).

## 1. New Module: `watermarking.py`
- [ ] Create the file `cgi-detector-service/forensics/watermarking.py`.
- [ ] Implement the main `analyze_watermark(image_bytes: bytes) -> float` function.
- [ ] Implement Least Significant Bit (LSB) analysis within the `analyze_watermark` function.
- [ ] Implement Frequency Domain (FFT) analysis within the `analyze_watermark` function.

## 2. Integration with Analysis Engine (`engine.py`)
- [ ] Import the `watermarking` module in `cgi-detector-service/forensics/engine.py`.
- [ ] Add a call to `watermarking.analyze_watermark` within the `ProcessPoolExecutor` in `run_analysis`.
- [ ] Retrieve the `watermark_score` from the completed task.
- [ ] Add the `watermark_score` to the `ml_features` list.
- [ ] Add a new dictionary to the `analysis_breakdown` list for the watermark analysis results.

## 3. Machine Learning Model Update (`ml_predictor.py`)
- [ ] Update `extract_features_from_image_bytes` in `cgi-detector-service/forensics/ml_predictor.py` to include the `watermark_score`.
- [ ] Retrain the ML model (`ml_model.joblib`) with a dataset that includes the new watermark feature.

## 4. Testing and Profiling
- [ ] Create the test file `cgi-detector-service/scripts/test_watermarking.py`.
- [ ] Add test cases to `test_watermarking.py` using images with and without watermarks.
- [ ] Create the profiling file `cgi-detector-service/forensics/profile_watermarking.py`.

## 5. Project Scaffolding
- [ ] Update `cgi-detector-service/forensics/__init__.py` to expose the new `watermarking` module.