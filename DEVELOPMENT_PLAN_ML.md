# Development Plan for Machine Learning Integration in Forensic Analysis

## Analysis:
The current `cgi-detector-service` uses a weighted-average approach to combine scores from various forensic techniques. While effective, this linear combination might not capture complex, non-linear relationships or interactions between different forensic features that could indicate CGI or manipulation more accurately. Machine learning models are adept at learning such intricate patterns from data.

By leveraging the output of the existing forensic methods as features, we can train a supervised machine learning model (e.g., a classifier) to make a more nuanced and potentially more accurate final prediction. This approach treats the existing `forensics/engine.py` as a powerful feature extractor, with the ML model providing a more sophisticated decision-making layer.

The development plan will focus on data preparation, model training and evaluation, and seamless integration into the existing service architecture, ensuring that the ML component is modular and testable.

## Plan:
1.  **Phase 1: Data Preparation**
    1.  **Acquire/Curate Labeled Dataset:** Identify and acquire a diverse dataset of images/videos with definitive labels (e.g., "real," "CGI," "deepfake," "manipulated"). This dataset will be crucial for training and evaluating the ML model.
    2.  **Generate Features from Existing Engine:** Process the labeled dataset through the current `run_analysis` function in `cgi-detector-service/forensics/engine.py`. Store the detailed `analysis_breakdown` scores and other relevant outputs (e.g., `rambino_raw_score`, `specialized_detector_scores`) along with their corresponding ground-truth labels. This will form the feature set for the ML model.
    3.  **Data Storage:** Store the generated features and labels in a structured format (e.g., CSV, Parquet, or a simple database) for easy access during model training.

2.  **Phase 2: Machine Learning Model Development**
    1.  **Feature Preprocessing:** Perform necessary preprocessing on the extracted features, such as scaling (e.g., `MinMaxScaler`, `StandardScaler`) or normalization, to prepare them for the ML model.
    2.  **Model Selection and Initial Training:** Choose an appropriate classification algorithm (e.g., Logistic Regression, Support Vector Machine, Random Forest, Gradient Boosting Classifier like XGBoost). Train an initial model using a portion of the prepared dataset.
    3.  **Model Evaluation:** Evaluate the trained model's performance using standard metrics like accuracy, precision, recall, F1-score, and ROC AUC on a held-out validation set.
    4.  **Hyperparameter Tuning & Cross-Validation:** Optimize the model's hyperparameters using techniques like GridSearchCV or RandomizedSearchCV with k-fold cross-validation to ensure robust performance and prevent overfitting.
    5.  **Model Serialization:** Once an optimal model is found, serialize it (e.g., using `joblib` or `pickle`) into a file that can be loaded by the `cgi-detector-service`.

3.  **Phase 3: Integration and Deployment**
    1.  **Create ML Module:** Create a new Python module (e.g., `cgi-detector-service/forensics/ml_predictor.py`) to encapsulate the ML model loading and prediction logic.
    2.  **Load Model in Engine:** Modify `cgi-detector-service/forensics/engine.py` to:
        *   Import the new `ml_predictor` module.
        *   Load the serialized ML model once at service startup (or the first call) to avoid re-loading for every request.
        *   Feed the collected forensic scores to the loaded ML model.
    3.  **Update Prediction Logic:** Replace the existing `final_score` and `prediction_label` calculation in `engine.py` with the output of the ML model's prediction. The ML model can output a probability score that can serve as the new `confidence`.
    4.  **Update `README.md` and Documentation:** Document the integration of the ML model, including its purpose, the features it uses, and how to update/retrain it. Update any relevant architecture documentation in `docs/architecture/`.

4.  **Phase 4: Testing and Validation**
    1.  **Develop ML-specific Tests:** Create new test cases that specifically validate the ML model's predictions using a separate, untouched test dataset. Ensure these tests cover various scenarios (real, CGI, different manipulation types).
    2.  **Performance Benchmarking:** After integration, conduct new performance benchmarks for the entire `run_analysis` function to ensure that the ML inference step does not introduce unacceptable latency. If necessary, explore optimizations like ONNX export or specialized inference engines.

