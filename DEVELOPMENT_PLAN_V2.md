# Development Plan V2: Feature - Report Incorrect Detections

## 1. Executive Summary

To improve the long-term accuracy of our CGI detection model, we need a mechanism to collect and learn from its mistakes. This plan outlines the development of a "Report Incorrect Result" feature, which will allow users to provide feedback when the system makes a false prediction.

This feature will create a valuable feedback loop: users can flag misclassifications, and the system will save these images and the corresponding corrections. This curated data of "hard examples" will be instrumental in future model retraining efforts, as outlined in the primary `DEVELOPMENT_PLAN.md`.

The implementation is divided into two main parts: a backend endpoint for receiving and storing the reports, and a simple, intuitive user interface on the frontend for submitting them.

---

## Phase 1: Backend Setup - Report Handling

**Goal:** To create the necessary infrastructure and API endpoint to securely receive, process, and store user-submitted reports.

**Tasks:**

1.  **Create Directory Structure:**
    *   **Action:** In the project's root directory, create a new top-level folder named `feedback_data`.
    *   Inside `feedback_data`, create a subdirectory named `images`.
    *   **Security:** Add `feedback_data/` to the `.gitignore` file to prevent reported images from being committed to the repository.

2.  **Define the Report Log Format:**
    *   **Action:** A central log file, `feedback_data/reports.json`, will be created to store the metadata for all submitted reports. This file will be an array of JSON objects.
    *   **Structure of each JSON object:**
        ```json
        {
          "reportId": "a_unique_identifier_string",
          "timestamp": "ISO_8601_datetime_string",
          "savedImageFilename": "the_unique_filename_of_the_saved_image.jpg",
          "userCorrection": "one_of_['false_cgi', 'false_real']",
          "originalPrediction": {
            "prediction": "cgi_or_real",
            "confidence": 0.88,
            "analysis_breakdown": [
              // The full analysis breakdown from the initial report
            ]
          }
        }
        ```

3.  **Implement the `/report` API Endpoint in `webservice/main.py`:**
    *   **Action:** Create a new `POST` endpoint at the path `/report`.
    *   **Functionality:**
        *   The endpoint will accept a `multipart/form-data` request containing:
            *   The image file.
            *   The user's correction type (e.g., `false_cgi`).
            *   The original prediction data (as a JSON string).
        *   **Processing Logic:**
            1.  Generate a unique filename for the image using `uuid.uuid4()` to prevent conflicts and sanitize inputs.
            2.  Save the image file to the `feedback_data/images/` directory.
            3.  Create a new JSON entry with the structure defined above.
            4.  Read the existing `feedback_data/reports.json` file, append the new entry to the list, and write the file back to disk. Implement file locking to handle potential concurrent requests safely.
            5.  Return a success message to the client.
    *   **Error Handling:** Implement robust error handling for file I/O operations and invalid request data.

---

## Phase 2: Frontend Implementation - User Interface

**Goal:** To provide a simple and intuitive UI for users to submit a report after an analysis is complete.

**Tasks:**

1.  **Add UI Elements to `webservice/static/index.html`:**
    *   **Action:** Add the HTML for the reporting form.
    *   **Components:**
        *   A container `div` for the reporting section, initially hidden (`display: none`).
        *   A "Report Incorrect Result" button.
        *   A `form` element containing:
            *   A `<label>` and a `<select>` dropdown with two options:
                1.  `value="false_cgi"` -> "Incorrectly detected as CGI (this is a real photo)"
                2.  `value="false_real"` -> "Incorrectly detected as Real (this is a CGI photo)"
            *   A "Submit Report" `<button>`.
    *   **Styling:** Apply CSS to match the existing look and feel of the page.

2.  **Implement JavaScript Logic:**
    *   **Action:** Enhance the existing script in `webservice/static/index.html`.
    *   **Functionality:**
        1.  **State Management:** Store the most recent analysis result (the full JSON response from `/analyze`) and the original image `File` object in global JavaScript variables.
        2.  **UI Visibility:** After a successful analysis, make the "Report Incorrect Result" button visible.
        3.  **Event Listener (Report Button):** When the "Report" button is clicked, display the hidden reporting form.
        4.  **Event Listener (Submit Report Form):**
            *   Prevent the default form submission.
            *   Create a `FormData` object.
            *   Append the original image `File` object.
            *   Append the selected value from the dropdown.
            *   Append the stored analysis result (as a JSON string).
            *   Send a `POST` request to the `/report` endpoint.
            *   On success, hide the form and display a confirmation message (e.g., "Thank you for your feedback!").
            *   On failure, display an error message.

---

## Phase 3: System Integration & Refinement

**Goal:** To ensure the frontend and backend components work together seamlessly and securely.

**Tasks:**

1.  **End-to-End Testing:**
    *   **Action:** Manually test the entire workflow:
        1.  Upload an image and get a result.
        2.  Click the report button.
        3.  Select a correction and submit.
        4.  Verify that the image is saved correctly in `feedback_data/images/`.
        5.  Verify that a corresponding entry is added to `feedback_data/reports.json`.
        6.  Verify that the UI shows the correct confirmation message.

2.  **Security Review:**
    *   **Action:** Double-check that user-provided data (like filenames) is not used to construct file paths directly. Ensure a UUID or another secure method is used for naming saved files to prevent path traversal vulnerabilities.

3.  **UI/UX Polish:**
    *   **Action:** Refine the confirmation and error messages to be clear and user-friendly. Ensure the reporting section integrates smoothly into the existing page layout.
