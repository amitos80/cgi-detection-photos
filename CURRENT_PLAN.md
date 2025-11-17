# Plan: Add New Features to CGI Detection Algorithm

## Objective

This plan outlines the addition of new forensic features to the CGI detection algorithm. The proposed features are based on techniques and concepts derived from the provided research sources and are intended to enhance the algorithm's accuracy and sophistication.

## Proposed Features

### 1. Advanced Noise and Texture Statistical Analysis
*   **Inspiration:** `eacooper/RAMBiNo` toolbox (source: https://github.com/eacooper/RAMBiNo). 
*   **Concept:** Implement a statistical analysis module that examines the bivariate distributions of pixel data (or data in a transformed domain like wavelets). By using radial and angular marginalization, we can create a more detailed signature of an image's noise pattern to better distinguish between authentic camera sensor noise and CGI textures.
*   **Implementation Steps:**
    1.  Research and adapt the core statistical methods from the RAMBiNo paper for Python.
    2.  Develop a new forensic module (`rambino.py`) in the `cgi-detector-service/forensics/` directory.
    3.  Integrate the module into the main `engine.py` to be run as part of the overall analysis.
    4.  Test against a known dataset of real and CGI images to validate the feature's effectiveness.

### 2. 3D Geometric Consistency Analysis
*   **Inspiration:** SPHARM software.
*   **Concept:** For images containing well-defined objects (e.g., faces, cars), attempt to infer the 3D shape and analyze its geometric properties. CGI models often exhibit unnatural smoothness or perfect symmetry that can be detected with spherical harmonic analysis.
*   **Implementation Steps (Research Spike):**
    1.  Investigate and select a suitable Python library for shape-from-shading or single-view 3D reconstruction.
    2.  Investigate Python libraries for spherical harmonic analysis of 3D meshes.
    3.  Create a proof-of-concept script that can take an image, segment an object, estimate its 3D mesh, and perform the analysis.
    4.  Based on the proof-of-concept, evaluate the feasibility of integrating this as a full feature.

### 3. Scene Lighting and Text Consistency

*   **Inspiration:** `btlorch/license-plates` project (source: https://github.com/btlorch/license-plates/blob/master/README.md).
*   **Concept:** Detect fine-grained text or patterns within an image and analyze the local lighting characteristics. Compare this local lighting to the estimated global scene lighting. Inconsistencies can be a strong indicator of a composite or CGI image.
*   **Implementation Steps:**
    1.  Integrate an OCR or text detection library to identify text regions.
    2.  Research and implement techniques to estimate lighting direction from a small image patch.
    3.  Research and implement a technique for estimating the dominant lighting direction for the entire scene.
    4.  Develop a scoring mechanism to quantify the consistency between local and global lighting.

