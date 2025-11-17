# Python Forensic Analysis Service

This FastAPI service provides the core CGI detection capabilities for the application. It implements a custom forensic analysis engine based on the research principles of Professor Hany Farid, designed to detect statistical and physical artifacts that differentiate real photographs from computer-generated or manipulated images.

## Architecture

The service is built around a modular forensic engine that combines the results of several distinct analysis techniques. This approach allows for a more robust and nuanced prediction than a single algorithm could provide.

The core components are:

*   **`main.py`**: The FastAPI application entry point. It defines the `/predict` endpoint that receives image uploads and orchestrates the analysis.
*   **`forensics/`**: A Python module containing the individual analysis algorithms and the unified scoring engine.
    *   **`engine.py`**: The central orchestrator. It runs the input image through all available forensic methods, combines their scores using a weighted average, and formats the final JSON response.
    *   **`ela.py`**: Implements **Error Level Analysis (ELA)**, which detects inconsistencies in JPEG compression levels.
    *   **`cfa.py`**: Implements **Color Filter Array (CFA) Analysis**, which looks for disruptions in the camera's unique sensor pattern.
    *   **`hos.py`**: Implements **Higher-Order Wavelet Statistics (HOS)**, which analyzes the image's statistical properties to identify synthetic origins.

## Detection Methods

The engine currently combines the following four methods:

1.  **Error Level Analysis (ELA)**: This technique is effective at finding regions in an image that have a different compression history than the rest of the image, which is a common sign of digital splicing or editing.
2.  **Color Filter Array (CFA) Analysis**: Real digital cameras leave a specific, periodic pattern of color correlations due to the physical layout of their sensors (e.g., a Bayer filter). CGI and manipulated regions lack this authentic "fingerprint."
3.  **Higher-Order Wavelet Statistics (HOS)**: Natural images have very specific and predictable statistical distributions when decomposed using wavelet transforms. Synthetic images, on the other hand, tend to have "unnatural" or overly uniform statistics. This method is powerful for detecting images that are entirely computer-generated.
4.  **JPEG Ghost Analysis**: This method identifies inconsistencies in JPEG compression history across different regions of an image, which is a strong indicator of image splicing or manipulation.

## Extending the Engine

The modular design makes it easy to add new forensic techniques. To add a new method:

1.  Create a new Python file in the `forensics/` directory (e.g., `forensics/new_method.py`).
2.  Implement your analysis function in that file, ensuring it takes `image_bytes` as input and returns a score between 0.0 and 1.0.
3.  Import the new function into `forensics/engine.py`.
4.  Call the new function within the `run_analysis` method.
5.  Add the new score to the weighted-average calculation and include its results in the `analysis_breakdown` dictionary.
