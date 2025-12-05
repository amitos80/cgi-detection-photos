# Python Forensic Analysis Service

This FastAPI service provides the core CGI detection capabilities for the application. It implements a custom forensic analysis engine based on the research principles of Professor Hany Farid, designed to detect statistical and physical artifacts that differentiate real photographs from computer-generated or manipulated images.

## Architecture

The service is built around a modular forensic engine that combines the results of several distinct analysis techniques. This approach allows for a more robust and nuanced prediction than a single algorithm could provide.

The core components are:

*   **`main.py`**: The FastAPI application entry point. It defines the `/predict` endpoint that receives image uploads and orchestrates the analysis.
*   **`forensics/`**: A Python module containing the individual analysis algorithms, the unified scoring engine, and the machine learning predictor.
    *   **`engine.py`**: The central orchestrator. It runs the input image through all available forensic methods **concurrently using a `ProcessPoolExecutor`**, collects their scores, and then feeds these scores into an integrated machine learning model for a final prediction. This parallel execution significantly improves performance by reducing the overall analysis time.
    *   **`ml_predictor.py`**: Manages the loading and inference of the trained machine learning model, which makes the final CGI/real photo classification based on the features extracted by `engine.py`.
    *   **`ela.py`**: Implements **Error Level Analysis (ELA)**, which detects inconsistencies in JPEG compression levels.
    *   **`cfa.py`**: Implements **Color Filter Array (CFA) Analysis**, which looks for disruptions in the camera's unique sensor pattern.
    *   **`hos.py`**: Implements **Higher-Order Wavelet Statistics (HOS)**, which analyzes the image's statistical properties to identify synthetic origins.

## Machine Learning Integration

To enhance prediction accuracy, the forensic engine now integrates a machine learning classifier. The scores from all individual forensic analysis techniques are collected by `engine.py` and then fed as features to a pre-trained ML model (managed by `ml_predictor.py`). This model makes the final classification decision (CGI or real) and provides a confidence score.

### Model Retraining

The ML model (`ml_model.joblib`) can be retrained by providing a labeled dataset of forensic features. The `ml_predictor.py` module contains a placeholder `_train_and_save_dummy_model` function demonstrating how a model can be trained and saved. In a production environment, this would involve:

1.  **Data Collection:** Gathering a diverse dataset of images/videos with ground-truth labels.
2.  **Feature Extraction:** Running `engine.py` over this dataset to extract forensic scores as features.
3.  **Model Training:** Using a dedicated script or workflow to train a new ML model on these features and save it to `forensics/ml_model.joblib`.

## Detection Methods

The engine processes images through the following forensic methods. The outputs of these methods serve as features for the final machine learning prediction:

1.  **Error Level Analysis (ELA)**: This technique is effective at finding regions in an image that have a different compression history than the rest of the image, which is a common sign of digital splicing or editing.
2.  **Color Filter Array (CFA) Analysis**: Real digital cameras leave a specific, periodic pattern of color correlations due to the physical layout of their sensors (e.g., a Bayer filter). CGI and manipulated regions lack this authentic "fingerprint."
3.  **Higher-Order Wavelet Statistics (HOS)**: Natural images have very specific and predictable statistical distributions when decomposed using wavelet transforms. Synthetic images, on the other hand, tend to have "unnatural" or overly uniform statistics. This method is powerful for detecting images that are entirely computer-generated.
4.  **JPEG Ghost Analysis**: This method identifies inconsistencies in JPEG compression history across different regions of an image, which is a strong indicator of image splicing or manipulation.
5.  **Deepfake Detection**: This method analyzes images or videos for characteristics indicative of AI-generated manipulation, such as inconsistencies in facial features or motion.
6.  **Reflection Inconsistency**: This method detects inconsistencies in reflections within an image, which can indicate that elements have been added or altered without proper consideration for the scene's light sources and reflective surfaces.
7.  **Video Double Quantization**: This method identifies re-encoding artifacts in video frames, which are strong indicators of video manipulation where a video has been compressed multiple times.
