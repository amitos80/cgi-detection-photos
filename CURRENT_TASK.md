# Plan: Add New Features to CGI Detection Algorithm

## Objective

This plan outlines the addition of new forensic features to the CGI detection algorithm. The proposed features are based on techniques and concepts derived from the provided research sources and are intended to enhance the algorithm's accuracy and sophistication.

## Currently working on:

### 1. Advanced Noise and Texture Statistical Analysis
*   **Inspiration:** `eacooper/RAMBiNo` toolbox (source: https://github.com/eacooper/RAMBiNo). 
*   **Concept:** Implement a statistical analysis module that examines the bivariate distributions of pixel data (or data in a transformed domain like wavelets). By using radial and angular marginalization, we can create a more detailed signature of an image's noise pattern to better distinguish between authentic camera sensor noise and CGI textures.
*   **Implementation Steps:**
    1.  Research and adapt the core statistical methods from the RAMBiNo paper for Python.
    2.  Develop a new forensic module (`rambino.py`) in the `cgi-detector-service/forensics/` directory.
    3.  Integrate the module into the main `engine.py` to be run as part of the overall analysis.
    4.  Test against a known dataset of real and CGI images to validate the feature's effectiveness.

    
