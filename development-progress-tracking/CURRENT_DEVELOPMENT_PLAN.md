# Development Plan: Comprehensive Model Testing with `my_dataset`

**Objective:** Establish a comprehensive testing framework to evaluate the performance of the CGI detection models using the images provided in the `my_dataset` directory. This includes setting up the environment, defining test scenarios, executing tests, and reporting results.

**Analysis:**
The project structure indicates that individual forensic modules are being developed and tested, as evidenced by files like `cgi-detector-service/forensics/engine.py`, `cgi-detector-service/scripts/test_*.py` files, and the presence of `my_dataset/` with `real/` and `fake/` subdirectories. The user's error regarding `cgi-detector-service:8000/analyze` and `ENOTFOUND cgi-detector-service` suggests that the service is intended to be run and accessed over the network, likely within a Dockerized environment, and that the current test execution might be failing due to network resolution issues or the service not being available. This plan will focus on establishing a comprehensive testing strategy that can either target individual modules directly or interact with the service if necessary, ensuring tests are run against the provided dataset and results are reported.

The existing `cgi-detector-service/scripts/run_dataset_tests.py` script provides a solid foundation for module-level testing. This plan will extend it to support service-level and ML predictor testing, and also focus on improving documentation and reporting.

**Plan:**

1.  **Enhance `run_dataset_tests.py` to Support Service-Level Testing:**
    *   Implement the `service` strategy in `run_dataset_tests.py`.
    *   This will involve sending HTTP requests to the `cgi-detector-service`'s `/analyze` endpoint.
    *   The script should be configurable to point to the correct service URL (e.g., `http://localhost:8000`).
    *   Add error handling for network issues and service unavailability.

2.  **Enhance `run_dataset_tests.py` to Support ML Predictor Testing:**
    *   Implement the `ml_predictor` strategy in `run_dataset_tests.py`.
    *   This will involve loading the trained ML model and using it to make predictions on the dataset images.
    *   The script should extract the necessary features from the images before feeding them to the model.

3.  **Create Comprehensive Test Reporting:**
    *   Enhance the reporting functionality in `run_dataset_tests.py`.
    *   In addition to the console output, generate a JSON or CSV file with detailed test results.
    *   The report should include image-level results, as well as overall metrics like accuracy, precision, recall, and F1-score.

4.  **Create `TESTING.md` Documentation:**
    *   Create a `TESTING.md` file in the `docs` directory.
    *   This file will provide clear and concise instructions on how to run the tests.
    *   It will cover prerequisites, setup, and execution for all three testing strategies (module, service, and ml_predictor).
    *   It will also explain how to interpret the test results.

5.  **Update `TASKS_BREAKDOWN.md`:**
    *   Update the `development-progress-tracking/TASKS_BREAKDOWN.md` file to reflect the tasks outlined in this plan.

6.  **Execute and Validate:**
    *   Execute the developed tests against `my_dataset`.
    *   Debug any failures encountered in the tests, the runner script, or the underlying models/service.
    *   Validate that the test results accurately reflect the model's performance.
