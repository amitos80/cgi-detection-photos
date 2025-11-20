# Development Plan: Parallel Forensic Analysis Execution

## 1. Objective

To significantly improve the performance and reduce the latency of the forensic analysis service by converting the current sequential feature analysis process into a parallel one. Each distinct forensic analysis function (e.g., ELA, CFA, HOS) will be executed in a separate thread, allowing for concurrent processing.

---

## 2. Analysis of the Current System

*   **File to Modify:** `cgi_detector_service/forensics/engine.py`
*   **Current Function:** `run_analysis(image_bytes: bytes)`
*   **Current Logic:** The `run_analysis` function calls each of the forensic analysis functions one by one, in a blocking, sequential manner. The total execution time is the sum of the execution times of all individual analyses.
*   **Limitation:** This sequential execution model is inefficient, especially as more analysis modules are added. Since the analyses are CPU-bound and independent, they are perfect candidates for parallelization, which will reduce the overall time the system waits for I/O and processing.

---

## 3. Proposed Parallel Execution Logic

The refactored `run_analysis` function will use Python's `concurrent.futures.ThreadPoolExecutor` to manage a pool of threads and execute the analysis tasks concurrently.

1.  **Instantiate ThreadPoolExecutor:** Create an instance of `ThreadPoolExecutor` to manage the worker threads.
2.  **Submit Tasks:** Instead of calling each analysis function directly, submit them as tasks to the executor. Each `executor.submit()` call will return a `Future` object, which represents the pending result of the computation.
3.  **Manage Futures:** Store the `Future` objects in a dictionary, mapping each feature name (e.g., 'ela', 'cfa') to its corresponding future. This will make it easy to retrieve the results.
4.  **Retrieve Results:** Iterate through the dictionary of futures and call `future.result()` on each one. This call will block until the specific analysis is complete, but since the tasks are running in parallel, the total wait time will be dictated by the longest-running analysis, not the sum of all of them.
5.  **Exception Handling:** Wrap the `future.result()` calls in a `try...except` block to gracefully handle any exceptions that might occur within a thread during an analysis.

---

## 4. Phased Implementation Plan

### Phase 1: Code Implementation
1.  **Import Necessary Module:** Add `from concurrent.futures import ThreadPoolExecutor` to the top of `cgi_detector_service/forensics/engine.py`.
2.  **Refactor `run_analysis`:**
    *   Inside the function, create a `ThreadPoolExecutor` context manager (`with ThreadPoolExecutor() as executor:`).
    *   Create a dictionary to hold the submitted tasks, e.g., `futures = {}`.
    *   For each analysis (ELA, CFA, HOS, JPEG Ghost, etc.), submit it to the executor:
        ```python
        futures['ela'] = executor.submit(ela.analyze_ela, processed_image_bytes)
        futures['cfa'] = executor.submit(cfa.analyze_cfa, processed_image_bytes)
        # ... and so on for all other analyses.
        ```
    *   Create a new dictionary to store the results, e.g., `results = {}`.
    *   Iterate through the `futures` dictionary, retrieve the result for each, and store it in the `results` dictionary, including error handling:
        ```python
        for name, future in futures.items():
            try:
                results[name] = future.result()
            except Exception as e:
                print(f"Error running {name} analysis: {e}")
                results[name] = 0.0 # Default/error value
        ```
    *   Update the rest of the function to use the scores from the `results` dictionary instead of the sequentially-called function variables.

### Phase 2: Verification and Testing
1.  **Run Existing Tests:** The existing test suite for the `adaptive_downsize_image` function should still pass, as it is unaffected.
2.  **Manual Verification:**
    *   Prepare a small set of test images (e.g., one known real, one known CGI).
    *   Run the service *before* the changes and record the JSON output for each test image.
    *   After implementing the parallel logic, run the service again with the *same* test images.
    *   **Compare the JSON outputs.** The scores and final predictions should be identical (or nearly identical, accounting for any minor floating-point variations). The primary difference should be a noticeable decrease in the response time.
3.  **Performance Measurement (Optional):** Add timing decorators or simple `time.time()` calls before and after the analysis block in both the old and new versions to empirically measure and confirm the performance improvement.

### Phase 3: Documentation
1.  **Update `README.md`:** Modify the `cgi_detector_service/README.md` to describe the new parallel processing architecture. Explain that the forensic analyses are run concurrently to improve performance.
2.  **Add Code Comments:** Add comments in the `run_analysis` function to explain the use of `ThreadPoolExecutor` for any future developers.

---

## 5. Approval

This plan is now ready for review. I will **not** proceed with any implementation or file modifications until I receive your explicit written approval.
