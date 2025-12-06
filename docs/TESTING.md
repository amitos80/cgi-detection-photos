# Testing Guide

This document provides instructions on how to run the comprehensive test suite for the CGI detection models.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for service-level testing)
- Required Python packages (install with `pip install -r cgi-detector-service/requirements.txt`)

## Dataset

The tests are designed to run against a dataset of real and fake images. The expected directory structure is:

```
my_dataset/
├── real/
│   ├── image1.jpg
│   └── ...
└── fake/
    ├── image2.png
    └── ...
```

The default dataset directory is `my_dataset`, but you can specify a different directory using the `--dataset_dir` argument.

## Running the Tests

The main test script is `cgi-detector-service/scripts/run_dataset_tests.py`. It supports three testing strategies: `module`, `service`, and `ml_predictor`.

### Module-Level Testing

This strategy tests the individual forensic modules directly. It's the fastest strategy and is useful for verifying the correctness of the individual analysis components.

**To run the module-level tests:**

```bash
python cgi-detector-service/scripts/run_dataset_tests.py --strategy module
```

You can also specify which modules to test:

```bash
python cgi-detector-service/scripts/run_dataset_tests.py --strategy module --modules ela hos
```

### Service-Level Testing

This strategy tests the running `cgi-detector-service`. It sends HTTP requests to the `/analyze` endpoint and is useful for verifying the end-to-end functionality of the service.

**Prerequisites:**

- The `cgi-detector-service` must be running. You can start it with Docker Compose:
  ```bash
  docker-compose up -d cgi-detector-service
  ```

**To run the service-level tests:**

```bash
python cgi-detector-service/scripts/run_dataset_tests.py --strategy service
```

If the service is running on a different URL, you can specify it with the `--service_url` argument:

```bash
python cgi-detector-service/scripts/run_dataset_tests.py --strategy service --service_url http://my-service:8001
```

### ML Predictor Testing

This strategy tests the trained machine learning model. It runs the full analysis engine on the dataset images and uses the model to make predictions. This is useful for evaluating the overall performance of the model.

**To run the ML predictor tests:**

```bash
python cgi-detector-service/scripts/run_dataset_tests.py --strategy ml_predictor
```

## Test Reports

The test script will print a summary of the results to the console. It will also generate a `test_run_results.json` file with detailed results for each image. This file can be used for further analysis.
