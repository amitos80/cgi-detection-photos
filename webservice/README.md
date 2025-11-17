# CGI Detection Photos Webservice (Node.js Version)

This Node.js webservice acts as the frontend and API gateway for the CGI detection application. It serves the static web interface and forwards image analysis requests to the Python AI microservice.

## What This Means for Our Current Code

The Node.js server now primarily handles file uploads and acts as a proxy, forwarding the image buffer to the `cgi-detector-service` (Python AI microservice) for actual CGI detection. It then relays the prediction result back to the client.

## Prerequisites

To run this service locally for development or testing (outside of Docker Compose):

*   Node.js (v18 or later)
*   npm

For running the entire application, refer to the main `README.md` in the project root for Docker Compose instructions.

## Installation (for local development)

1.  Navigate to the `webservice` directory:
    ```bash
    cd webservice
    ```
2.  Install the dependencies:
    ```bash
    npm install
    ```

## Building the Application

To compile the TypeScript code to JavaScript (for local development or before Docker build), run:

```bash
npm run build
```

This will output the compiled JavaScript files to the `dist` directory.

## Running the Application (for local development)

To start the server (using `ts-node` for development), run the following command:

```bash
npm start
```

The server will start on `http://localhost:8000`.

## Running Tests

To run the unit tests, use:

```bash
npm test
```

## API Endpoints

*   `GET /`: Serves the main HTML page (`static/index.html`).
*   `POST /analyze`: Accepts an image file upload, forwards it to the Python AI microservice, and returns the prediction.
    *   **Method:** `POST`
    *   **Endpoint:** `/analyze`
    *   **Content-Type:** `multipart/form-data`
    *   **Form Field:** `file` (for the image file)
    *   **Response:** JSON object containing `filename` and `prediction`.

    ```json
    {
      "filename": "your_uploaded_image.jpg",
      "prediction": {
        "prediction": "cgi" | "real",
        "confidence": 0.0 - 1.0
      }
    }
    ```

## Running with Docker Compose

For instructions on how to build and run the entire application using Docker Compose, please refer to the main `README.md` in the project root directory.
