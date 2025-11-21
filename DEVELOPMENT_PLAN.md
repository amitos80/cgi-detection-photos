# Development Plan for New Forensic Analysis Methods

## Analysis:
I have learned about various forensic analysis methods from Hany Farid's website, including deepfake detection, photo forensics (e.g., inconsistent shadows, JPEG artifacts, 3D lighting), video forensics, audio forensics, and distinguishing CGI from photos. The existing project structure indicates a `cgi-detector-service` with a `forensics` directory, suggesting a focus on image/video analysis. The current modules in `cgi-detector-service/forensics` include `cfa.py`, `ela.py`, `geometric_3d.py`, `hos.py`, `jpeg_ghost.py`, `lighting_text.py`, `rambino.py`, and `specialized_detectors.py`, which align with many of the methods described by Farid.

Based on this, a development plan for new forensic analysis methods should focus on expanding the existing capabilities by incorporating more sophisticated techniques, particularly in deepfake detection, advanced photo/video manipulation detection (e.g., inconsistent reflections, double quantization), and further refinement of CGI-vs-photo differentiation. It's crucial to integrate these new methods into the existing service and ensure they are well-tested.

## Plan:
1.  **Research and Prioritize New Methods:**
    *   Review the existing `forensics` modules and identify gaps or areas for improvement based on the methods detailed on Hany Farid's website (e.g., deepfake detection, advanced lighting inconsistencies, reflections, etc.).
    *   Prioritize 2-3 most promising new forensic analysis methods that can be integrated into the `cgi-detector-service`.
2.  **Design and Implement New Modules:**
    *   For each prioritized method, create a new Python module (e.g., `deepfake_detector.py`, `reflection_consistency.py`) within the `cgi-detector-service/forensics` directory.
    *   Implement the core logic for each new forensic analysis method, ensuring adherence to the existing coding style (2 spaces indentation, underscore prefix for private members, strict equality).
    *   Include JSDoc comments for all new functions and classes.
3.  **Integrate with `engine.py`:**
    *   Modify `cgi-detector-service/forensics/engine.py` to incorporate the new detection methods. This will likely involve adding new functions or extending existing ones to call the methods from the newly created modules.
    *   Ensure proper error handling and logging for the new integrations.
4.  **Develop Unit and Integration Tests:**
    *   For each new module and the updated `engine.py`, create corresponding test files (e.g., `test_deepfake_detector.py`, `test_engine_new_methods.py`) in an appropriate test directory (e.g., `cgi-detector-service/tests`).
    *   Write comprehensive unit tests to verify the correctness of the new forensic analysis algorithms.
    *   Write integration tests to ensure the new methods are correctly integrated into the `cgi-detector-service` and function as expected within the overall system.
5.  **Update `README.md` and Documentation:**
    *   Update the `README.md` for `cgi-detector-service` to describe the new forensic analysis methods, their capabilities, and any new configuration options.
    *   If applicable, add or update documentation in `docs/architecture/` to reflect the new methods and their architectural implications.
6.  **Review and Refine:**
    *   Conduct a self-review of the implemented code, tests, and documentation to ensure quality, consistency, and adherence to project standards.
    *   Refine any areas identified during the review.
7.  Present the plan for approval.
