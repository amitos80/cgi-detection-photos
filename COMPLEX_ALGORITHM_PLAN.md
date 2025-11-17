# Development Plan: Complex Algorithm based on Hany Farid's Research

**Analysis:**

The current CGI detection mechanism uses a generic, pre-trained ResNet50 model, which serves as a placeholder and is not based on the specialized forensic techniques developed by Professor Hany Farid. The objective is to replace this placeholder with a sophisticated, multi-faceted algorithm that leverages the core principles of Professor Farid's research.

Implementing these advanced forensic methods is a complex, research-intensive task. It requires deep analysis of image statistics, compression artifacts, and sensor patterns, rather than high-level object recognition. This plan outlines a phased approach to build a custom forensic analysis engine from the ground up. We will implement several of the key techniques mentioned in the `README.md` and combine their outputs into a unified, more reliable prediction.

**Plan:**

1.  **Establish a Forensic Analysis Module:**
    *   Within the `cgi-detector-service` project, create a new Python module named `forensics`.
    *   This module will contain separate sub-modules for each distinct analysis technique (e.g., `ela.py`, `cfa.py`, `hos.py`). This modular structure will keep the complex algorithms organized and maintainable.

2.  **Implement Error Level Analysis (ELA):**
    *   In `forensics/ela.py`, create a function that takes an image as input.
    *   The function will re-save the image at a known, high JPEG quality (e.g., 95%).
    *   It will then calculate the absolute difference between the original image and the re-compressed version on a per-pixel basis.
    *   The resulting "error level" map will be analyzed. Regions with significant variance in error levels suggest manipulation.
    *   The function will output a numerical score from 0.0 to 1.0, where a higher score indicates a higher probability of manipulation due to inconsistent compression history.

3.  **Implement Color Filter Array (CFA) Artifact Analysis:**
    *   In `forensics/cfa.py`, create a function to analyze the specific periodic correlations left by a camera's demosaicing algorithm.
    *   This involves examining the relationships between the R, G, and B channels at a low level.
    *   The algorithm will look for the expected, consistent pattern of a real camera capture.
    *   Computer-generated content or spliced elements will lack or disrupt this pattern.
    *   The function will output a score from 0.0 to 1.0, where a higher score indicates a disruption of the natural CFA pattern, suggesting a forgery.

4.  **Implement Higher-Order Wavelet Statistics (HOS):**
    *   This is the most advanced component. In `forensics/hos.py`, create a function that applies a wavelet transform to the image (using a library like `PyWavelets`).
    *   Calculate higher-order statistical moments (e.g., variance, skewness, kurtosis) from the wavelet coefficients across various sub-bands.
    *   Compare these statistical distributions against established mathematical models for natural, un-manipulated images.
    *   Significant deviations from these natural image models suggest the image is synthetic.
    *   The function will output a score from 0.0 to 1.0, where a higher score indicates that the image's statistics are unnatural and likely computer-generated.

5.  **Develop a Unified Scoring and Reporting Engine:**
    *   Create a new module, `forensics/engine.py`, to orchestrate the analysis.
    *   This engine will run an input image through all implemented forensic methods (ELA, CFA, HOS).
    *   It will collect the individual scores from each method.
    *   A weighted-average algorithm will be developed to combine these scores into a single, final confidence score. The weights will be determined based on the relative reliability of each technique.
    *   The engine will also populate the `analysis_breakdown` structure with the *actual* results from each forensic test, providing genuine insights for the frontend report.

6.  **Integrate the Forensic Engine into the FastAPI Service:**
    *   Modify `cgi-detector-service/main.py`.
    *   Remove the existing ResNet50 model loading and prediction logic entirely.
    *   In the `/predict` endpoint, call the new forensic engine with the uploaded image.
    *   The endpoint will receive the final score and the detailed breakdown from the engine and return it in the JSON response, maintaining the same structure as before.

7.  **Update Documentation:**
    *   Update the main `README.md` and `webservice/README.md` to accurately describe the new, sophisticated detection methods being used, explicitly stating that they are based on the principles of digital image forensics.
