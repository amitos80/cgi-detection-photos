# AI? CGI? DEEPFAKE? Digital Forensics in Images: Detection of CGIs and Deepfakes in digital images 🕵️

![Deepfake Detection Cover](./.github/cover.png)

This project is a web-based application for detecting digital forgeries in images, with a focus on identifying Computer-Generated Imagery (CGI). It uses a sophisticated backend engine based on the digital image forensics research of Professor Hany Farid.

When an image is uploaded, the application performs a series of forensic tests and presents a detailed report, including a final prediction, a confidence score, and a breakdown of each test's results. The report includes a table with insights and a simple infographic to help visualize the findings.

## Project Architecture

This project utilizes a two-service architecture for robust CGI detection, based on the principles of digital image forensics research by Professor Hany Farid.

1.  **Node.js Webservice (Frontend & API Gateway):** This service handles user requests, serves the static frontend, and acts as an API gateway. It forwards uploaded images to the Python AI microservice for processing and relays the results back to the client.
2.  **Python AI Microservice (CGI Detector):** This service is responsible for the core forensic analysis. It utilizes a custom-built engine that integrates a comprehensive suite of forensic techniques to detect digital forgeries, including CGIs and deepfakes:
    *   **Error Level Analysis (ELA):** Detects inconsistencies in JPEG compression artifacts.
    *   **Color Filter Array (CFA) Analysis:** Identifies disruptions in the camera's sensor pattern.
    *   **Higher-Order Statistics (HOS):** Analyzes statistical properties in the wavelet domain to distinguish natural from synthetic imagery.
    *   **JPEG Artifact Analysis:** Includes detection of JPEG Ghost, JPEG Dimples, and Double Quantization, identifying inconsistencies in compression history and re-saving artifacts.
    *   **3D Geometric Consistency:** Verifies the geometric plausibility of objects within the image.
    *   **Lighting and Reflection Consistency:** Analyzes light sources, shadows, and reflections for physical inconsistencies.
    *   **Specialized AI-Generated Content (AIGC) Detectors:** Targets specific artifacts left by GANs, Diffusion Models, and other generative AI techniques.
    *   **Deepfake Detection:** Identifies manipulations specific to deepfake generation.
    *   **RAMBiNo Statistical Analysis:** Applies advanced statistical methods for robust image source attribution and forgery detection.

    The engine processes the image through these methods in parallel, combining their scores into a unified input for a machine learning model to produce a final, reliable prediction.
## How to Run

To run the entire application, ensure you have Docker and Docker Compose installed. Then, navigate to the project root directory and execute the following command:

```bash
docker-compose up --build
```

This command will:
*   Build the Docker images for both the Node.js webservice and the Python AI microservice.
*   Start both services, allowing them to communicate over a shared Docker network.
*   Expose the Node.js webservice on port `8000`.

Once the services are up, open your web browser and navigate to `http://localhost:8000` to access the application:)

## API Response Structure

The `/analyze` endpoint of the Node.js webservice now returns a JSON object with the following structure:

```json
{
  "filename": "your_uploaded_image.jpg",
  "prediction": {
    "prediction": "cgi" | "real",
    "confidence": 0.0 - 1.0,
    "analysis_breakdown": [
      {
        "feature": "Error Level Analysis (ELA)",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.2],
        "insight": "Detects inconsistencies in JPEG compression artifacts. High scores suggest manipulation.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "Color Filter Array (CFA)",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.3],
        "insight": "Analyzes low-level sensor patterns. High scores indicate a disruption of natural camera patterns.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "Wavelet Statistics (HOS)",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.4],
        "insight": "Measures statistical properties of the image. High scores suggest the image is synthetic.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "JPEG Ghost Analysis",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.2],
        "insight": "Identifies inconsistencies in JPEG compression history, indicating potential image splicing.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "JPEG Dimples Analysis",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.2],
        "insight": "Detects periodic artifacts from JPEG compression. Disruption of these patterns indicates manipulation.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "RAMBiNo Statistical Analysis",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.1],
        "insight": "Analyzes noise and texture patterns using bivariate distributions. High scores suggest CGI.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "3D Geometric Consistency",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.3],
        "insight": "Analyzes geometric properties including symmetry, smoothness, edge regularity, and gradient consistency. High scores indicate unnatural geometric patterns typical of CGI.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "Scene Lighting Consistency",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.3],
        "insight": "Analyzes lighting direction consistency across regions, shadow alignment, and lighting in high-contrast areas. High scores indicate inconsistent lighting typical of composites or CGI.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/"
      },
      {
        "feature": "Specialized CGI/AIGC Detector",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.4],
        "insight": "Runs specialized detection for GAN, diffusion, face synthesis, and 3D rendering artifacts. High scores indicate evidence of generative-AI or CGI. Type most likely: [type]. Breakdown: [scores]",
        "url": ""
      },
      {
        "feature": "Deepfake Detection",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.5],
        "insight": "Detects AI-generated manipulation in faces or motion. High scores suggest a deepfake.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/deepfakes/"
      },
      {
        "feature": "Reflection Inconsistency",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.6],
        "insight": "Analyzes images for inconsistencies in reflections. High scores suggest image manipulation.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/photo-forensics/"
      },
      {
        "feature": "Video Double Quantization",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.7],
        "insight": "Detects re-encoding artifacts in video frames. High scores suggest video manipulation.",
        "url": "https://farid.berkeley.edu/research/digital-forensics/video-forensics/"
      }
    ],
    "rambino_raw_score": 0.0,  // Raw, unscaled RAMBiNo score
    "rambino_features": [],    // Truncated list of RAMBiNo features (if available)
    "specialized_detector_scores": {}, // Detailed scores from specialized detectors
    "specialized_likely_type": "Unknown" // Most likely type detected by specialized CGI/AIGC detector
  }
}
```

---

## Machine Learning Integration

The system leverages machine learning to synthesize the results from various forensic detectors into a cohesive and accurate final prediction.

*   **Model:** A `RandomForestClassifier` (from scikit-learn) is used to process the scores generated by each individual forensic method. This ensemble model is adept at identifying complex patterns and interactions between different forensic indicators to determine whether an image is a CGI or a real photograph, along with a confidence score.
*   **Continuous Learning & Feedback Loop:** The `/feedback` API endpoint is a crucial component for the system's continuous improvement. When users provide feedback on misclassified images, the system securely stores these corrected samples.
*   **Automated Retraining:** This feedback data is periodically used to trigger an automated retraining process for the `RandomForestClassifier` model. After retraining, the updated model is seamlessly reloaded into the service, allowing the system to learn from its mistakes and progressively enhance its detection capabilities over time without requiring manual intervention.

---

## Deepfake Detection

**Deepfakes** are highly realistic synthetic media generated using **deep learning models**, primarily **Generative Adversarial Networks (GANs)**. The main detection strategies exploit flaws in how AI recreates complex human physiology and the physical environment:

### A. Physiological Inconsistencies
AI often struggles with complex or small human features. Forensic analysis looks for discrepancies in:
* **Eye Blinking:** Deepfakes may exhibit unnatural, absent, or inconsistent blinking patterns because AI training data often lacks images of eyes closed.
* **Anatomy:** Imperfections in rendering **hands, ears, teeth, or hair** can expose a deepfake.
* **Biological Signals:** Analyzing subtle skin color changes (via remote **Photoplethysmography** or **rPPG**) can detect inconsistencies in the synthesized person's simulated heart rate, a feature AI often fails to perfectly replicate.

### B. Environmental Inconsistencies
* **Lighting and Shadows:** When a forged face is spliced onto a new scene, the light intensity, direction, or corresponding shadows on the face may not align with the rest of the image.

### C. Statistical Artifacts
* Advanced detection uses **Convolutional Neural Networks (CNNs)** or **Vision Transformers** to analyze invisible statistical **fingerprints** left behind by the specific generative model (GAN or Diffusion Model) used to create the fake.

***

## CGI and General Forgery Detection

General image manipulation, including splicing (copy-paste) or **Computer-Generated Imagery (CGI)** insertion, is detected by examining low-level artifacts:

* **Noise Analysis (PRNU):** Every digital camera sensor has a unique microscopic pattern noise called **Photo-Response Non-Uniformity (PRNU)**. This is a unique "fingerprint." If a region of an image has a PRNU pattern that is different from a the rest of the photo, it is likely a spliced or inserted fake.
* **Error Level Analysis (ELA):** ELA highlights areas of an image that have a different level of JPEG compression history. Spliced-in content, not compressed as often as the original image, will often stand out with a much lower "error level."
* **Color Filter Array (CFA) Artifacts:** Digital cameras use a **CFA** (e.g., Bayer filter) to capture color and then use a process called **demosaicing** to interpolate the full-color image. This process leaves a unique, periodic statistical pattern. Any manipulation disrupts this pattern, which can be detected.
* **Metadata (EXIF) Forensics:** Although metadata can be easily faked or stripped, the **Exchangeable Image File Format (EXIF)** can contain the camera model, date, time, and even the history of software used to process the file, providing initial clues.

## 🕵️ Different Ways to Detect CGI/Deepfakes in Digital Images

Professor Hany Farid's research focuses on exploiting the subtle physical and statistical inconsistencies that human eyes miss but that digital analysis can uncover in manipulated or computer-generated imagery.

Here are four distinct detection methods and the core reasoning behind them:

---

### 1. Physics-Based Lighting and Geometry Inconsistencies

This method verifies an image's integrity against the laws of **physics**.

| Aspect Detected | Reasoning/Thought Process |
| :--- | :--- |
| **Inconsistent Lighting** | In a real photograph, every object is illuminated by the same light source(s). When a person or object is digitally inserted (a forgery/deepfake), it is extremely difficult to match the light direction, color, and intensity perfectly to the background scene. |
| **Specular Highlights/Shadows** | The analysis focuses on cues like the geometry of shadows or the position of reflections (specular highlights) on glossy surfaces (like the eye). If the light source implied by a shadow does not match the light source implied by the reflection, the image is likely a composite. |

---

### 2. Digital Fingerprints (JPEG Quantization & Re-sampling)

This method focuses on identifying residual **artifacts** that reveal an image's processing history.

| Aspect Detected | Reasoning/Thought Process |
| :--- | :--- |
| **Re-sampling Traces** | When an image is manipulated (resized, rotated, or warped), the software must **interpolate** (re-sample) pixels. This process leaves behind faint, periodic statistical correlations in the pixel data that differ from a pristine original, signaling manipulation. |
| **JPEG Artifact Analysis (Ghost, Dimples, Double Quantization)** | Every time an image is saved in a lossy format like JPEG, a specific compression pattern (**quantization**) is applied. A pasted element often comes from a source that was compressed differently, resulting in an area that exhibits **double-quantization** (two compression grids) which is statistically inconsistent with the rest of the image. **JPEG Ghost** analysis detects inconsistencies in JPEG block matching, often revealing spliced areas. **JPEG Dimples** refers to characteristic smooth, dimple-like patterns in the DCT coefficients that can indicate re-saving or manipulation. |

---

### 3. Camera Sensor Artifacts (Color Filter Array - CFA)

This method leverages the unique way a digital camera's sensor captures color information, creating a **sensor fingerprint**.

| Aspect Detected | Reasoning/Thought Process |
| :--- | :--- |
| **Disrupted CFA Pattern** | Most digital cameras use a Color Filter Array (CFA) that requires mathematical interpolation (**demosaicing**) to create a full-color image. This interpolation introduces a predictable, periodic correlation pattern between neighboring pixels. |
| **Bypassing the Camera Pipeline** | When a deepfake or manipulated region is created by an algorithm, it bypasses the physical camera capture and interpolation process. The synthetic region will either lack this expected CFA correlation pattern or have an inconsistent one, clearly marking it as non-original to the source image. |

---

### 4. Higher-Order Statistical Analysis





This is a powerful technique for distinguishing between statistically "natural" images and statistically "unnatural" synthetic images.



| Aspect Detected | Reasoning/Thought Process |

| :--- | :--- |

| **Statistical Model Deviations** | While deepfakes look visually realistic, Generative AI models often fail to perfectly replicate the complex, non-linear dependencies between pixels found in real, natural images. |

| **Wavelet Analysis (HOS)** | Analysis is often performed using **Higher-Order Statistics (HOS)** in the wavelet domain. A **real photograph**'s statistical distributions conform to known mathematical models for natural scenes. A **synthetic image** exhibits subtle, systematic statistical deviations or "over-regularity" that flags it as algorithmically generated. |



---



### 5. 3D Geometric Consistency



This method analyzes geometric properties within the image.



| Aspect Detected | Reasoning/Thought Process |

| :--- | :--- |

| **Symmetry and Smoothness** | Real-world objects often exhibit natural variations and imperfections. CGI, especially early or less sophisticated forms, can show unnaturally perfect symmetry, overly smooth surfaces, or repetitive patterns that betray their synthetic origin. |

| **Edge Regularity and Gradient Consistency** | The way edges transition and color gradients flow in an image can reveal manipulation. Inconsistent edge rendering or unnatural gradient changes across different parts of an object or scene can indicate that elements were digitally inserted or generated. |



---



### 6. Scene Lighting Consistency



This method focuses on the physics of light within a scene.



| Aspect Detected | Reasoning/Thought Process |

| :--- | :--- |

| **Lighting Direction Alignment** | All objects in a naturally lit scene should show shadows and highlights consistent with a common light source direction. If different objects or regions within an image appear to be lit from varying directions, it's a strong indicator of a composite image or CGI. |

| **Shadow Accuracy and Softness** | Shadows provide critical clues about light sources. Analysis includes checking if shadows are cast correctly relative to objects, if their length and angle are consistent, and if the softness or sharpness of shadow edges matches the expected light source properties within the scene. Inconsistencies suggest manipulation. |



---



### 7. Specialized CGI/AIGC Detection



This method employs advanced techniques to identify artifacts specific to different generation methods.



| Aspect Detected | Reasoning/Thought Process |

| :--- | :--- |

| **GAN/Diffusion Artifacts** | Generative Adversarial Networks (GANs) and Diffusion Models, while powerful, leave subtle statistical "fingerprints" in the images they produce. These can include characteristic noise patterns, frequency spectrum anomalies, or specific textural irregularities that are imperceptible to the human eye but detectable by specialized algorithms. |

| **Face Synthesis and 3D Rendering Artifacts** | Dedicated detectors can target known imperfections in AI-generated faces (e.g., distorted backgrounds, inconsistent accessories, repetitive textures) or patterns typical of 3D rendering engines (e.g., perfectly smooth surfaces, uncanny material properties, aliasing artifacts in specific contexts). |



#### Credits: Professor Hany Farid's research on digital image forensic - https://farid.berkeley.edu/
*   **TED Talk Video:** [How to spot fake AI photos](https://www.ted.com/talks/hany_farid_how_to_spot_fake_ai_photos)

---

### 8. RAMBiNo Statistical Analysis

This method utilizes advanced statistical modeling of image noise to detect manipulation.

| Aspect Detected | Reasoning/Thought Process |
| :--- | :--- |
| **Anomalous Noise Characteristics** | RAMBiNo (Region-based Analysis of Multi-channel Bidimensional Noise) examines the complex statistical properties of noise across various color channels within an image. Real images exhibit consistent and predictable noise characteristics inherent to the camera sensor.
| **Detection of Statistical Deviations** | Forged or generated images, however, often introduce anomalous noise patterns or alter existing ones in ways that deviate significantly from natural photographic noise. RAMBiNo excels at identifying these subtle statistical inconsistencies, providing strong indicators of manipulation or synthetic origin. |

---

## Training the Model

To ensure a robust and resumable training process, the `train_model.py` script implements a detailed progress tracking and chunking system.

1.  **Progress File (`training_progress.json`):** A central JSON file is used to track the entire training process. It is located at `cgi-detector-service/scripts/training_progress.json`.

2.  **Initialization:**
    *   On its first run, the script scans the entire dataset.
    *   It creates a sorted list of all image file paths.
    *   This list is then divided into "chunks" of 200 images each.
    *   This chunk division and the full list of files are saved into the `training_progress.json` file.

3.  **Detailed Tracking:** For each image, the script maintains a detailed record:
    *   A unique, clean key is generated from the filename (e.g., `"my image (1).jpg"` becomes `"my_image_1_jpg"`).
    *   **Before processing:** The image's status is updated to `"processing"`, a `started_timestamp` is recorded, and a top-level `currently_being_processed` field is set to the image's key.
    *   **After processing:** The image's record is updated with an `ended_timestamp`, a final `status` (`"completed"` or `"error"`), and any relevant error messages. The `currently_being_processed` field is then cleared.

4.  **Resumability:**
    *   If the script is stopped and restarted, it reads the `training_progress.json` file to determine the exact state of the process.
    *   It automatically skips any images that are already marked as `"completed"`.
    *   If an image was left in the `"processing"` state (indicating an unexpected stop), the script will re-attempt to process it to ensure no data is lost.

5.  **Execution Flow:** The script processes images sequentially through the defined chunks, updating the JSON file at the start and end of each image's processing cycle. Once all features for all images have been successfully extracted, it proceeds with the main model training phase.
