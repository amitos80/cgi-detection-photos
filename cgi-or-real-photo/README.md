# Digital Image Forensics and CGI/Photo Feature Extraction

This document provides a summary of the field of digital image forensics, specifically related to the detection of deepfakes and computer-generated imagery (CGI), drawing on the work of Hany Farid, and presents a README for the MATLAB feature extraction code `cgorphoto.m`.

***

## 1. Digital Image Forensics and Deepfake/CGI Detection

The work of Hany Farid, particularly at Berkeley, is central to the field of **digital image forensics** and the detection of manipulated media, including computer-generated imagery (CGI) and deepfakes.

### Core Concepts

Digital forensics aims to determine the **provenance** and **integrity** of digital media (photos, videos, audio) by analyzing intrinsic cues and statistical anomalies that are often invisible to the human eye.

* **CGI/Photorealistic Distinction:** Early work, such as the paper related to the uploaded code, focused on distinguishing between real photographs and computer-rendered images (CGI). This approach analyzes the statistical properties of noise and high-frequency content (often using wavelet analysis) to find subtle differences introduced during the rendering process versus the physical process of light hitting a camera sensor.
* **Physics-Based Forensics:** This involves detecting inconsistencies that violate the laws of physics:
    * **Inconsistent Lighting:** Analyzing shading, shadows, and reflections to determine if all objects in a scene were lit by the same light source(s).
    * **Geometric Inconsistency:** Checking for violations of perspective or 3D scene structure.
* **Deepfake Detection (AI-Synthesized Media):** Modern forensics primarily targets deepfakes (videos and images created using Generative Adversarial Networks (GANs) or diffusion models). Detection methods include:
    * **Aural and Oral Dynamics:** Analyzing mismatches between a subject's spoken phonemes and their corresponding visemes (lip movements) in video deepfakes.
    * **Statistical Footprints:** Identifying artifacts or statistical "signatures" left behind by the generative model itself.

***

## 2. README: `cgorphoto.m`

This file describes the MATLAB code provided in `cgorphoto.m`, which implements a feature extraction technique used to classify images as either photorealistic (Photo) or computer-generated (CG). The code is based on higher-order wavelet coefficient statistics.

### Project Details

| Detail | Description |
| :--- | :--- |
| **Title** | How Realistic is Photorealistic? |
| **Authors** | S. Lyu and H. Farid |
| **Publication** | IEEE Transactions on Signal Processing, 2005 |
| **Purpose** | To extract a statistical feature vector used as input for classification (e.g., SVM or LDA) for distinguishing between CG and Photo images. |
| **Copyright** | Copyright (c), 2005, Trustees of Dartmouth College. All rights reserved. |

### Prerequisites and Dependencies

The core functionality requires the following tools:

1.  **Wavelet Toolbox (`matlabPyrTools`)**:
    * Required for building the wavelet pyramid (`buildWpyr`, `wpyrLev`).
    * Available from E.P. Simoncelli.
2.  **MATLAB Toolboxes**:
    * Image Processing Toolbox (e.g., for `imcrop`).
    * Statistics Toolbox (e.g., for `var`, `kurtosis`, and `skewness`).
3.  **Classification Tools (Required for Classification, not just Feature Extraction)**:
    * **SVM:** The `libsvm` package by C.J. Lin.
    * **LDA:** Linear Discriminant Analysis code (e.g., `steg.m`) from Hany Farid's research.

### Usage

The main function is `cgorphoto`.

**Function Signature:**
```matlab
[ftr] = cgorphoto( im )

## Function Parameters and Output 💻

| Parameter/Output | Description |
| :--- | :--- |
| **`im` (Input)** | The input image (grayscale or color). **Must be at least 256 x 256 pixels.** |
| **`ftr` (Output)** | The extracted feature vector. |

---

## Output Feature Vector Dimensions

| Image Type | Feature Dimension |
| :--- | :--- |
| **Grayscale** (`TYPE = 'g'`) | 72-dimensional |
| **Color** (`TYPE = 'c'`) | 216-dimensional (72 features per R, G, B channel) |

## 3. Sources and Links

This section provides links for the foundational paper and required dependencies mentioned in the code and the context.

### Foundational Research

* **Paper Reference (S. Lyu and H. Farid)**: *How Realistic is Photorealistic?*
    * `http://www.cs.dartmouth.edu/farid/publications/sp05b.html`
* **General Digital Forensics and Research (H. Farid)**:
    * `https://farid.berkeley.edu/`

### Code Dependencies

* **Wavelet Toolbox (matlabPyrTools, E.P. Simoncelli)**:
    * `http://www.cns.nyu.edu/~lcv/software.html`
* **Support Vector Machine (SVM) Library (libsvm, C.J. Lin)**:
    * `http://www.csie.ntu.edu.tw/~cjlin/libsvm/`
* **Linear Discriminant Analysis (LDA) Code (H. Farid)**:
    * `http://www.cs.dartmouth.edu/farid/research/steg.m`
