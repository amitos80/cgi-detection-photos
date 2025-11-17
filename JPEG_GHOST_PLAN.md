# Development Plan: Add JPEG Ghost Analysis

**Analysis:**

To improve the accuracy and reliability of the forensic engine, we will add a fourth detection method: JPEG Ghost Analysis. This technique is a powerful way to detect image splicing by identifying inconsistencies in JPEG compression history across different regions of an image. It complements the existing ELA, CFA, and HOS methods by providing a distinct signal focused on compression artifacts. The implementation is straightforward and does not require complex libraries.

**Plan:**

1.  **Implement the JPEG Ghost Algorithm:**
    *   Create a new file: `cgi-detector-service/forensics/jpeg_ghost.py`.
    *   In this file, create a function `analyze_jpeg_ghost(image_bytes)`.
    *   The function will loop through a range of JPEG quality levels (e.g., from 75 to 100).
    *   In each iteration, it will re-compress the input image at that quality and calculate the Sum of Squared Differences (SSD) between the original and the re-compressed version.
    *   It will identify the quality level that produces the *minimum* SSD. This is the likely original compression quality.
    *   At this minimum-SSD quality, it will analyze the difference map. A high variance in this map suggests that some regions matched the compression level perfectly (the original parts) while others did not (the spliced parts).
    *   The function will return a score from 0.0 to 1.0, where a higher score indicates a higher variance and thus a higher probability of manipulation.

2.  **Integrate into the Forensic Engine:**
    *   Modify `cgi-detector-service/forensics/engine.py`.
    *   Import the new `analyze_jpeg_ghost` function.
    *   Call the new function within the `run_analysis` method.
    *   Update the `weights` dictionary to include the new method and re-balance the weights for all four techniques (e.g., set them all to `0.25`).
    *   Add the results of the JPEG Ghost analysis to the `analysis_breakdown` list, including a descriptive `insight` and the `url`.

3.  **Update Documentation:**
    *   Update the `README.md` in the `cgi-detector-service` directory to include JPEG Ghost Analysis as one of the implemented detection methods.
    *   Update the main `README.md` to briefly mention the new technique in the "Project Architecture" section.
