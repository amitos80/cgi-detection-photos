# Assumptions about `my_dataset` for Testing

This document outlines the assumptions made about the structure and content of the `my_dataset` directory, which is used for testing the CGI detection models.

## Dataset Structure:

*   The dataset is organized into two main subdirectories at its root:
    *   `real/`: Contains images that are considered authentic or not CGI-generated.
    *   `fake/`: Contains images that are considered CGI-generated or manipulated.
*   Each of these subdirectories (`real/`, `fake/`) contains image files in formats such as `.jpg`, `.jpeg`, `.png`, `.webp`, etc.

## Image Content:

*   The images within `real/` are expected to be authentic.
*   The images within `fake/` are expected to be CGI-generated or manipulated. The exact nature of manipulation may vary, but the overall goal is to distinguish them from real images.
*   The filenames within `fake/` might sometimes contain clues about their origin (e.g., `Gemini_Generated_Image_...`), but the primary classification is based on the directory structure.

## Testing Assumptions:

*   **Ground Truth:** The directory structure (`real/` vs. `fake/`) is the definitive source of ground truth for classifying images during testing.
*   **Module Compatibility:** The forensic modules located in `cgi-detector-service/forensics/` are compatible with the image formats found in the dataset and can process them correctly.
*   **Score Interpretation:** The `MODULE_ASSERTIONS` and `GENERAL_THRESHOLDS` defined in `run_dataset_tests.py` are reasonable starting points for interpreting module outputs, assuming higher scores generally indicate a higher likelihood of manipulation.
*   **Sampling:** When sampling is enabled (`--sample_size`), the `stratified` sampling strategy aims to maintain the class distribution by selecting an equal number of images from both `real/` and `fake/` directories, up to the specified `sample_size` for each.
