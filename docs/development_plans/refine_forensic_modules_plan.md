# Plan for Refining Existing Forensic Modules

## Analysis:
This plan outlines a methodology for identifying and optimizing computational bottlenecks within the existing forensic analysis modules. The primary goal is to improve the performance of these modules, contributing to the overall efficiency of the CGI detection service.

## Plan:
1.  **Identify Forensic Modules for Profiling:**
    *   List all Python files in `cgi-detector-service/forensics/` (e.g., `cfa.py`, `ela.py`, `double_quantization.py`, `geometric_3d.py`, `hos.py`, `jpeg_ghost.py`, `lighting_text.py`, `ml_predictor.py`, `rambino.py`, `reflection_consistency.py`, `specialized_detectors.py`). Exclude `__init__.py`, `engine.py`, `execute_tests.py`, and `__pycache__`.
2.  **Profiling Methodology:**
    *   For each identified module, create or adapt a dedicated script or test case that calls its primary analysis function with a representative sample image (e.g., `dummy_dataset/fake/fake_image_0.png`).
    *   Execute these scripts using Python's built-in `cProfile` to get function-level performance statistics.
    *   For more granular, line-by-line analysis of identified slow functions, suggest using `kernprof` with `line_profiler`.
    *   Analyze the profiling reports to pinpoint specific functions or sections of code consuming the most CPU time.
3.  **Optimization Strategies (General):**
    *   **Algorithmic Refinements:**
        *   For CPU-bound operations (e.g., loops, complex calculations), investigate if more efficient algorithms or mathematical approaches can be applied.
        *   Replace explicit Python loops with vectorized operations using `NumPy` where possible, especially for image pixel manipulations.
    *   **Library Enhancements:**
        *   If image processing operations are bottlenecks, explore replacing custom implementations with highly optimized functions from libraries like `OpenCV` (cv2) or `Pillow` (PIL, or its faster `Pillow-SIMD` fork).
        *   Consider `Numba` for Just-In-Time (JIT) compilation of critical Python functions that cannot be easily vectorized or offloaded to C-optimized libraries.
    *   **Resource Management:**
        *   Ensure efficient memory usage, especially when handling large images, to avoid unnecessary copying or excessive memory allocation.
        *   Evaluate if any modules can benefit from parallel processing (e.g., `multiprocessing` for independent tasks within a module) if the bottleneck is not I/O-bound.
4.  **Present this detailed plan for "Refine Existing Forensic Modules" for approval.**