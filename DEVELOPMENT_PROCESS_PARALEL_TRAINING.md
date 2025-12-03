# Development Plan: Parallel and Thread-Safe Training Process

## Analysis:
The primary goal is to significantly accelerate the feature extraction phase of the model training pipeline by processing images in parallel. The main challenge is to do this without introducing race conditions that could corrupt the `training_progress.json` file, which is essential for the stop-and-resume functionality.

The implementation will be fully backward-compatible with the existing `training_progress.json` file. The script will read the current state and resume the process from exactly where it left off, ensuring no work is duplicated and no progress is lost.

The chosen architecture is a **Manager-Worker** pattern. A single, main manager process will be responsible for all interactions with the filesystem (reading and writing to `training_progress.json`). This manager will distribute the CPU-intensive image processing tasks to a pool of worker processes. The workers will report their results back to the manager but will never access the progress file directly. This centralization of file I/O completely prevents race conditions and guarantees that the progress file is always in a consistent, valid state.

## Plan:

1.  **Backward-Compatible Progress Loading and Task Creation:**
    *   The `run_feature_extraction` function will begin by loading the existing `training_progress.json` file into a single in-memory dictionary.
    *   It will create a set of all file paths that are already marked with a `"status": "completed"` in the `image_tracking` section.
    *   The script will then iterate through the `chunks` defined in the JSON file. It will build a new list of tasks to be processed, containing only the file paths that are **not** in the "completed" set.
    *   This ensures that if the script is restarted, it will only queue up work that has not already been successfully finished, preserving the "resume from where stopped" functionality.

2.  **Isolate the Stateless Worker Function:**
    *   The `process_image(filepath)` function will be a pure, stateless worker.
    *   Its only responsibility is to accept a single `filepath`, perform the computationally expensive feature extraction, and return a tuple containing the original `filepath`, the extracted `features`, and any `error` message.
    *   This function will be completely decoupled from the progress tracking logic and will not perform any file I/O on `training_progress.json`.

3.  **Implement the Manager and Worker Pool:**
    *   In the main `run_feature_extraction` function, after creating the list of pending tasks, a `concurrent.futures.ProcessPoolExecutor` will be initialized.
    *   The manager will submit all pending tasks to the executor, creating a pool of futures. This will immediately start the parallel processing of images on all available CPU cores.

4.  **Real-time, Thread-Safe Progress Handling:**
    *   The manager will enter a `for` loop using `concurrent.futures.as_completed()`, which yields results as soon as any worker finishes its task. This allows for real-time progress updates.
    *   **Inside this loop, the following critical, serialized operations will occur for each completed task:**
        1.  The manager receives the result (`filepath`, `features`, `error`) from a worker.
        2.  It generates the clean `file_key` from the `filepath`.
        3.  It updates the **in-memory** `progress_data` dictionary:
            *   The status for the corresponding `file_key` is set to `"completed"` or `"error"`.
            *   `ended_timestamp` and any `error` message are recorded.
        4.  The manager then performs a single, atomic **write operation**, saving the entire, updated `progress_data` dictionary back to the `training_progress.json` file.
    *   This ensures that for every image processed, the progress file is updated once and only once by the single manager process, making the operation inherently thread-safe and robust against interruptions.

5.  **Final Aggregation and Model Training:**
    *   The manager will collect the features from all successful results in memory.
    *   After the `as_completed` loop has processed all tasks, the script will check if any new features were successfully extracted.
    *   If so, it will proceed to the existing `train_and_save_model` function with the aggregated features and labels to train the final model.