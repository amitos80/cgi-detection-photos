# Development Plan: Adaptive Image Downsizing Strategy

## 1. Objective

To replace the current fixed-height (480p) image downsizing function with a more intelligent, adaptive strategy. The goal is to optimize performance by reducing image size while simultaneously preserving the critical high-frequency artifacts and pixel-level data required for accurate forensic analysis. This new approach will prevent the excessive destruction of forensic evidence in images with non-standard aspect ratios or smaller initial dimensions.

---

## 2. Analysis of the Current System

*   **File to Modify:** `cgi-detector-service/forensics/engine.py`
*   **Current Function:** `downsize_image_to_480p(image: Image.Image)`
*   **Current Logic:** Resizes any image with a height greater than 480 pixels to have a height of 480 pixels, maintaining the aspect ratio.
*   **Limitation:** This approach can be too aggressive. For example, a wide panoramic image (e.g., 2000x500) would be downsized, while a tall, narrow image (e.g., 400x1200) would be aggressively shrunk, potentially destroying more data than necessary. It does not account for the total pixel area or the shortest dimension, which is critical for high-frequency analysis.

---

## 3. Proposed Adaptive Downsizing Logic

The new function, `adaptive_downsize_image`, will operate based on a set of rules designed to balance performance and data integrity:

1.  **Define Thresholds:**
    *   `TARGET_LONG_EDGE = 800` (pixels): The target size for the longest dimension of the image.
    *   `MINIMUM_SHORT_EDGE = 256` (pixels): The absolute minimum allowable size for the shortest dimension. No resizing operation will be allowed to produce an image where the shortest side is smaller than this.

2.  **Implementation Logic:**
    *   Given a PIL image, determine its width and height.
    *   **Check 1: No Action Needed.** If the longest dimension of the image is already less than or equal to `TARGET_LONG_EDGE`, do not perform any resizing. The image is small enough.
    *   **Check 2: Perform Standard Resizing.** If the longest dimension is greater than `TARGET_LONG_EDGE`, calculate the new dimensions that would scale the longest side down to `TARGET_LONG_EDGE` while maintaining the aspect ratio.
    *   **Check 3: Validate Against Minimum.** Before performing the resize, check if the calculated new *shortest* dimension would be less than `MINIMUM_SHORT_EDGE`.
        *   If it is **greater than or equal to** the minimum, proceed with the calculated resizing.
        *   If it is **less than** the minimum, the standard resizing is too aggressive. Recalculate the dimensions to make the *shortest* side equal to `MINIMUM_SHORT_EDGE`, maintaining the aspect ratio. This becomes the final resize operation.

---

## 4. Phased Implementation Plan

### Phase 1: Code Implementation
1.  **Locate Target File:** Open `cgi-detector-service/forensics/engine.py`.
2.  **Create New Function:** Implement a new Python function `adaptive_downsize_image(image: Image.Image)` within the file, containing the adaptive logic described above.
3.  **Integrate Function:** In the `run_analysis` function, replace the call to `downsize_image_to_480p(original_image)` with a call to the new `adaptive_downsize_image(original_image)`. The original `downsize_image_to_480p` function can be deprecated or removed.

### Phase 2: Verification and Testing
1.  **Create Test Script:** Develop a standalone Python script (`/Users/amit/Projects/llm-coding-agent/workspace/scripts/test_adaptive_downsizing.py`) to rigorously test the new function.
2.  **Assemble Test Cases:** The script will test the function against a variety of image scenarios:
    *   **Case A (Large Landscape):** A 1920x1080 image. Expected: Resized to 800x450.
    *   **Case B (Large Portrait):** A 1080x1920 image. Expected: Resized to 450x800.
    *   **Case C (Small Image):** A 600x400 image. Expected: No change (600x400).
    *   **Case D (Panoramic / Extreme Aspect Ratio):** A 3000x600 image. Standard resize would be 800x160, which is below the minimum. Expected: Resized to 1280x256 (to preserve the 256px short edge).
    *   **Case E (Tall / Extreme Aspect Ratio):** A 600x3000 image. Expected: Resized to 256x1280.
3.  **Execute Tests:** Run the test script to confirm that the output dimensions for all cases are correct.

### Phase 3: Documentation
1.  **Update Docstrings:** Add a clear and concise docstring to the new `adaptive_downsize_image` function explaining its logic and the rules it follows.
2.  **Update Project Documentation:** If any project-level documentation (e.g., a README in the `cgi-detector-service` directory) describes the preprocessing pipeline, update it to reflect the new adaptive downsizing strategy.

---

## 5. Approval

This plan has been successfully implemented and verified.