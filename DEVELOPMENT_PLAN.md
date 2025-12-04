# Development Plan: Enable Multiple Image Analysis

## Analysis:
The current task is to extend the image analysis functionality to support multiple image uploads. This will involve modifications to both the frontend (Node.js Webservice) and the backend (Python AI Microservice). On the frontend, the existing upload mechanism needs to be adapted to handle multiple file selections. On the backend, the `/analyze` endpoint will need to be updated to detect multiple image uploads, enforce a limit of 5 images per request, and process these images in parallel using threads.

## Plan:
1.  **Frontend Modifications (Webservice):**
    *   Modify the `webservice/src/components/ImageUpload.tsx` component to allow multiple file selections via click and drag-and-drop. This will likely involve updating the `input` element to include the `multiple` attribute and adjusting the `onChange` event handler to process an array of files.
    *   Update the `webservice/src/api.ts` file to handle sending multiple image files in a single request to the `/analyze` endpoint. This will probably involve using `FormData` to append all selected files.

2.  **Backend Modifications (Python AI Microservice):**
    *   In `cgi-detector-service/main.py`, modify the `/analyze` endpoint to receive multiple image files. The request body will likely contain a list of files or a multipart form data with multiple file fields.
    *   Implement a check within the `/analyze` endpoint to determine if a single image or multiple images were uploaded.
    *   If multiple images are detected:
        *   Enforce a server-side limit of a maximum of 5 images per request. If more than 5 images are uploaded, return an appropriate error message.
        *   Utilize `concurrent.futures.ThreadPoolExecutor` (or similar threading mechanism) to process each image concurrently using the existing `extract_features_from_image_bytes` function and `ml_predictor`.
        *   Collect the analysis results for all processed images and return them as a list in the JSON response.
    *   If a single image is uploaded, the existing analysis flow should remain unchanged.

I will wait for your approval before proceeding with the implementation.