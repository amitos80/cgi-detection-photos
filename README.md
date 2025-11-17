# AI? CGI? DEEPFAKE? Digital Forensics in Images: Detection of CGIs and Deepfakes in digital images 🕵️

![Deepfake Detection Cover](./.github/cover.png)

This project is a web-based application for detecting digital forgeries in images, with a focus on identifying Computer-Generated Imagery (CGI). It uses a sophisticated backend engine based on the digital image forensics research of Professor Hany Farid.

When an image is uploaded, the application performs a series of forensic tests and presents a detailed report, including a final prediction, a confidence score, and a breakdown of each test's results. The report includes a table with insights and a simple infographic to help visualize the findings.

## Project Architecture

This project utilizes a two-service architecture for robust CGI detection, based on the principles of digital image forensics research by Professor Hany Farid.

1.  **Node.js Webservice (Frontend & API Gateway):** This service handles user requests, serves the static frontend, and acts as an API gateway. It forwards uploaded images to the Python AI microservice for processing and relays the results back to the client.
2.  **Python AI Microservice (CGI Detector):** This service is responsible for the core forensic analysis. Instead of a generic ML model, it uses a custom-built engine that combines several forensic techniques:
    *   **Error Level Analysis (ELA):** Detects inconsistencies in JPEG compression artifacts.
    *   **Color Filter Array (CFA) Analysis:** Identifies disruptions in the camera's sensor pattern.
    *   **Higher-Order Wavelet Statistics (HOS):** Analyzes the statistical properties of the image to distinguish between natural and synthetic sources.
    
    The engine combines the scores from these methods to produce a unified, more reliable prediction.

## How to Run

To run the entire application, ensure you have Docker and Docker Compose installed. Then, navigate to the project root directory and execute the following command:

```bash
docker-compose up --build
```

This command will:
*   Build the Docker images for both the Node.js webservice and the Python AI microservice.
*   Start both services, allowing them to communicate over a shared Docker network.
*   Expose the Node.js webservice on port `8000`.

Once the services are up, open your web browser and navigate to `http://localhost:8000` to access the application.

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
        "insight": "Detects inconsistencies in JPEG compression artifacts. High scores suggest manipulation."
      },
      {
        "feature": "Color Filter Array (CFA)",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.3],
        "insight": "Analyzes low-level sensor patterns. High scores indicate a disruption of natural camera patterns."
      },
      {
        "feature": "Wavelet Statistics (HOS)",
        "score": 0.0 - 1.0,
        "normal_range": [0.0, 0.4],
        "insight": "Measures statistical properties of the image. High scores suggest the image is synthetic."
      }
    ]
  }
}
```

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
| **JPEG Quantization Discrepancies** | Every time an image is saved in a lossy format like JPEG, a specific compression pattern (**quantization**) is applied. A pasted element often comes from a source that was compressed differently, resulting in an area that exhibits **double-quantization** (two compression grids) which is statistically inconsistent with the rest of the image. |

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



#### Credits: Professor Hany Farid's research on digital image forensic - https://farid.berkeley.edu/
*   **TED Talk Video:** [How to spot fake AI photos](https://www.ted.com/talks/hany_farid_how_to_spot_fake_ai_photos)
