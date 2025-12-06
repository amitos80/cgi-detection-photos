# Testing Guidelines for CGI Detection Models

This document provides instructions for setting up and running tests for the CGI detection models using the `run_dataset_tests.py` script.

## 1. Prerequisites

Before running the tests, ensure you have the following:

*   **Python 3.x:** Installed on your system.
*   **Required Python Packages:** Install dependencies listed in `cgi-detector-service/requirements.txt`.
    ```bash
    pip install -r cgi-detector-service/requirements.txt
    ```
*   **CGI Detector Service (for `service` strategy):** If you plan to use the `service` strategy, ensure the `cgi-detector-service` is running and accessible at the specified URL (default: `http://localhost:8000`). You can start it using Docker Compose:
    ```bash
    docker-compose build cgi-detector-service
    docker-compose up -d cgi-detector-service
    ```
    If a new ML model was trained, you might need to rebuild and restart the service to use it.
*   **Dataset:** A dataset organized into `real` and `fake` subdirectories within a root directory (e.g., `my_dataset/real/` and `my_dataset/fake/`).

## 2. Running Tests

The `run_dataset_tests.py` script supports different strategies for analyzing images. You can specify the dataset directory, strategy, optional modules to test, and sample size using command-line arguments.

### Usage:

```bash
python cgi-detector-service/scripts/run_dataset_tests.py \
    --dataset_dir <path_to_dataset> \
    --strategy <module|service|ml_predictor> \
    [--modules <module1> <module2> ...] \
    [--sample_size <N>] \
    [--sampling_strategy <stratified|random>] \
    [--service_url <url_of_service>]
```

### Arguments:

*   `--dataset_dir`: (Required) The root directory of your dataset (e.g., `my_dataset`). Defaults to `my_dataset`.
*   `--strategy`: (Required) The testing strategy to use. Choose from:
    *   `module`: Runs individual forensic modules directly within the script.
    *   `service`: Sends images to a running `cgi-detector-service` via HTTP requests.
    *   `ml_predictor`: Utilizes the `forensics.engine.run_analysis` which includes the ML model for classification.
*   `--modules`: (Optional) A space-separated list of specific forensic module names to test (e.g., `ela hos`). If not provided, all available modules will be tested for the `module` strategy.
*   `--sample_size`: (Optional) The number of images to sample from each class (real/fake) for testing. If not provided, all images will be used.
*   `--sampling_strategy`: (Optional) Strategy for sampling images. Choose from `stratified` (default) or `random`.
*   `--service_url`: (Optional) The URL of the `cgi-detector-service` to test against. Defaults to `http://localhost:8000`.

### Examples:

#### A. Running with `module` strategy (all modules, full dataset):

```bash
python cgi-detector-service/scripts/run_dataset_tests.py \
    --dataset_dir my_dataset \
    --strategy module
```

#### B. Running with `module` strategy (specific modules, sampled images):

```bash
python cgi-detector-service/scripts/run_dataset_tests.py \
    --dataset_dir my_dataset \
    --strategy module \
    --modules ela jpeg_ghost \
    --sample_size 10
```

#### C. Running with `service` strategy:

```bash
python cgi-detector-service/scripts/run_dataset_tests.py \
    --dataset_dir my_dataset \
    --strategy service \
    --service_url http://localhost:8000
```

#### D. Running with `ml_predictor` strategy:

```bash
python cgi-detector-service/scripts/run_dataset_tests.py \
    --dataset_dir my_dataset \
    --strategy ml_predictor \
    --sample_size 20
```

## 3. Interpreting Test Results

After execution, the script will print a summary to the console and generate a JSON report file (e.g., `test_run_results.json`) in the current working directory.

### Console Output:

The console output provides a summary including:

*   Total real/fake images correctly classified.
*   Overall Accuracy, Precision (Fake), Recall (Fake), and F1-Score (Fake).
*   Assertion pass/fail count and details for failed assertions (first 3 shown).
*   Errors encountered during testing (first 3 shown).

### `test_run_results.json` Report Structure:

The JSON report file contains a detailed breakdown of the test run:

```json
{
    "dataset_root": "my_dataset",
    "strategy": "module",
    "modules_tested": ["ela", "hos", ...],
    "sample_size_per_class": 100, // or null if not sampled
    "sampling_strategy": "stratified",
    "real_images": {
        "total": 100,
        "correctly_classified": 85,
        "details": [
            {
                "filename": "real_image_1.jpg",
                "scores": {"ela": 0.1, "hos": 0.05, ...},
                "classification": "real",
                "is_correct": true,
                "assertions_met": true,
                "failed_assertions_count": 0
            },
            // ... more real image details
        ]
    },
    "fake_images": {
        "total": 100,
        "correctly_classified": 92,
        "details": [
            {
                "filename": "fake_image_1.jpg",
                "scores": {"ela": 0.8, "hos": 0.7, ...},
                "classification": "fake",
                "is_correct": true,
                "assertions_met": true,
                "failed_assertions_count": 0
            },
            // ... more fake image details
        ]
    },
    "overall_metrics": {
        "accuracy": 0.885,
        "precision_fake": 0.90,
        "recall_fake": 0.92,
        "f1_score_fake": 0.91
    },
    "test_assertions": {
        "passed": 177,
        "failed": 23,
        "details": [
            {
                "image": "failed_real_image.jpg",
                "ground_truth": "real",
                "classification": "fake",
                "scores": {"ela": 0.6, ...},
                "failed_assertions": ["Module 'ela' assertion failed for real image..."]
            },
            // ... more failed assertion details
        ]
    },
    "errors": [
        {
            "image": "problem_image.jpg",
            "ground_truth": "real",
            "type": "module_analysis",
            "details": ["Module 'ela': An error occurred during analysis..."]
        }
        // ... more error details
    ]
}
```

### Interpreting Scores and Assertions:

*   **Scores:** Each module returns a score, typically between 0.0 and 1.0, indicating the likelihood of manipulation or CGI generation. Higher scores generally suggest manipulation/CGI.
*   **Assertions:** The script checks if individual module scores meet predefined criteria for 'real' or 'fake' images. Failed assertions highlight cases where a module did not perform as expected against the ground truth.
*   **Classification:** The overall classification (`real` or `fake`) is derived from a simple rule (if any module's score exceeds `fake_min_score`, it's classified as `fake`). This can be further refined.

By analyzing this report, you can gain insights into the performance of individual modules and the overall system, identify images that are problematic for the detectors, and debug potential issues.