# Development Plan: CGI Detection Service

**Analysis:**
The current service is a simple image feature extractor. To evolve it into a true CGI detector, we need to integrate a specialized machine learning model. The most practical approach is to create a dedicated Python microservice for the complex AI processing and have our existing Node.js service communicate with it. This plan outlines the steps to build this two-service architecture, update the frontend for a user-friendly display, and containerize the entire application for easy deployment.

**Plan:**

1.  **Research and Procure a Pre-trained CGI Detection Model:**
    *   Search for publicly available, pre-trained models for CGI vs. real image classification.
    *   Prioritize models compatible with common Python libraries (e.g., TensorFlow/Keras, PyTorch, ONNX).
    *   Download the model file and note its specific input requirements (image size, color channels, normalization).

2.  **Develop a Python AI Microservice:**
    *   Create a new directory, `cgi-detector-service`, alongside the `webservice` directory.
    *   Set up a lightweight Python web framework (e.g., FastAPI or Flask).
    *   Write a Python script to load the pre-trained model.
    *   Create a single API endpoint (e.g., `/predict`) that accepts an image file.
    *   Implement image pre-processing logic within the endpoint to resize, normalize, and format the image to match the model's input requirements.
    *   Run the processed image through the model to get a prediction (e.g., CGI/Real and a confidence score).
    *   Return the prediction as a JSON response (e.g., `{"prediction": "cgi", "confidence": 0.95}`).
    *   Add a `Dockerfile` for this new Python service.

3.  **Update the Node.js Webservice:**
    *   Modify the `/analyze` endpoint in `webservice/src/index.ts`.
    *   Instead of processing the image itself, it will now forward the uploaded image buffer to the Python AI microservice's `/predict` endpoint via an HTTP request.
    *   It will wait for the JSON response from the Python service and then relay it back to the client.
    *   Remove the now-unused `processImageBuffer` function and its dependencies (like `sharp`).

4.  **Enhance the Frontend for User-Friendly Results:**
    *   Update the JavaScript in `webservice/static/index.html`.
    *   On receiving the response from the `/analyze` endpoint, the script should parse the JSON.
    *   Instead of printing the raw JSON, it should display a clear, human-readable result (e.g., "Result: This image is likely **CGI** (95% confidence)").
    *   Add basic styling to highlight the result (e.g., green text for "Real", red for "CGI").

5.  **Containerize and Orchestrate with Docker Compose:**
    *   Create a `docker-compose.yml` file in the project root.
    *   Define two services in the file: the `webservice` (Node.js) and the `cgi-detector-service` (Python).
    *   Configure the services to build from their respective Dockerfiles and communicate with each other over a shared Docker network.

6.  **Update Documentation:**
    *   Update the main `README.md` and the `webservice/README.md` to reflect the new architecture.
    *   Provide clear instructions on how to run the entire application using a single `docker-compose up` command.
    *   Document the new API response structure.

7.  **Present for Approval:** Present the new, comprehensive plan to the user for review and approval.
