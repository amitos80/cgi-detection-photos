# Scene Lighting and Text Consistency Analysis Feature

## Overview

The Scene Lighting Consistency Analysis is a forensic feature that detects CGI and composite images by analyzing lighting inconsistencies across different regions. This technique is based on Prof. Hany Farid's research on detecting image forgeries through lighting analysis.

## Implementation Date
2025-01-17

## Location
- **Module:** `cgi-detector-service/forensics/lighting_text.py`
- **Integration:** `cgi-detector-service/forensics/engine.py`
- **Weight in Analysis:** 10% of final score

## Background & Motivation

When objects or text are digitally inserted into an image, or when CGI elements are combined with real photographs, one of the most telltale signs is **inconsistent lighting**. Different parts of the image may show:
- Different light source directions
- Inconsistent shadow orientations
- Mismatched lighting between foreground and background
- Unnatural lighting on text or overlaid elements

These inconsistencies are difficult to achieve perfectly even with sophisticated CGI tools, making lighting analysis a powerful forensic technique.

## Technical Approach

Rather than relying on heavyweight OCR libraries or deep learning models, this implementation uses **gradient-based lighting estimation** - a lightweight, efficient approach based on fundamental image analysis.

### Core Principle

Lighting direction can be estimated from image gradients because:
- Surfaces facing the light source have steeper intensity gradients
- Gradient direction indicates the direction of maximum intensity change
- Consistent lighting produces consistent gradient patterns across regions

## Analysis Components

### 1. Lighting Direction Consistency
**Purpose:** Detect inconsistent lighting directions across the image

**Method:**
- Divides image into 64×64 pixel blocks
- Calculates Sobel gradients (∂I/∂x, ∂I/∂y)
- Computes gradient magnitude and direction for each pixel
- Estimates dominant lighting direction per block using circular statistics
- Calculates circular standard deviation across all blocks

**Scoring:**
- Consistent lighting (std < 0.8 rad) → low suspicion
- Moderate variation (0.8-1.2 rad) → medium score
- Highly inconsistent (std > 1.2 rad) → high suspicion

**Weight:** 30% of lighting score

### 2. Regional Lighting Consistency
**Purpose:** Compare lighting between bright and dark regions

**Method:**
- Applies Gaussian blur to reduce noise
- Uses Otsu's threshold to segment bright/dark regions
- Calculates dominant gradient directions in each region
- Compares angular difference between region lighting

**Physical Intuition:**
In a real scene, bright and dark regions should show related lighting patterns from the same light source. Large angular differences (>90°) suggest composite images with inconsistent lighting.

**Scoring:**
- Angular difference < 60° → low suspicion
- Angular difference 60-90° → medium score
- Angular difference > 90° → high suspicion

**Weight:** 30% of lighting score

### 3. Shadow Consistency
**Purpose:** Analyze shadow orientation consistency

**Method:**
- Uses adaptive thresholding to detect dark regions (potential shadows)
- Removes noise with morphological operations
- Labels connected components as shadow candidates
- Analyzes orientation using region properties
- Calculates circular standard deviation of shadow orientations

**Physical Basis:**
Shadows cast by a single light source should be aligned. Multiple inconsistent shadow directions indicate:
- Multiple light sources (suspicious in outdoor scenes)
- Composite images
- CGI with incorrect shadow rendering

**Scoring:**
- Aligned shadows (std < 0.5 rad) → low suspicion
- Moderate variation (0.5-1.0 rad) → medium score
- Inconsistent shadows (std > 1.0 rad) → high suspicion

**Weight:** 25% of lighting score

### 4. High-Contrast Region Detection
**Purpose:** Analyze lighting on text-like patterns without OCR

**Method:**
- Uses Canny edge detection to find high-contrast regions
- Calculates local edge density using convolution
- Identifies text-like regions (high edge density areas)
- Compares gradient directions in text vs non-text regions
- Measures angular difference

**Rationale:**
Text or patterns overlaid on an image often have lighting that doesn't match the scene. This is particularly evident in:
- License plates on vehicles
- Signs in photographs
- Watermarks or added text
- CGI interface elements

**Scoring:**
- Consistent lighting (diff < 45°) → low suspicion
- Moderate difference (45-90°) → medium score
- Large difference (> 90°) → high suspicion

**Weight:** 15% of lighting score

## Mathematical Foundation

### Circular Statistics
Since lighting directions are angular quantities (0-2π), we use circular statistics:

**Circular Mean:**
```
θ̄ = atan2(Σ sin(θᵢ), Σ cos(θᵢ))
```

**Circular Standard Deviation:**
```
R = √[(Σ cos(θᵢ))² + (Σ sin(θᵢ))²] / n
σ_circ = √(-2 ln(R))
```

### Gradient-Based Lighting Estimation

**Gradient Calculation:**
```
∂I/∂x = Sobel_x(I)
∂I/∂y = Sobel_y(I)
```

**Magnitude and Direction:**
```
magnitude = √[(∂I/∂x)² + (∂I/∂y)²]
direction = atan2(∂I/∂y, ∂I/∂x)
```

## Integration

The feature is integrated as one of seven forensic techniques:

| Feature | Weight |
|---------|--------|
| Error Level Analysis (ELA) | 16% |
| Color Filter Array (CFA) | 16% |
| Wavelet Statistics (HOS) | 16% |
| JPEG Ghost Analysis | 16% |
| RAMBiNo Statistical Analysis | 16% |
| 3D Geometric Consistency | 10% |
| **Scene Lighting Consistency** | **10%** |

## API Response

The feature appears in the `analysis_breakdown` array:

```json
{
  "feature": "Scene Lighting Consistency",
  "score": 0.0-1.0,
  "normal_range": [0.0, 0.3],
  "insight": "Analyzes lighting direction consistency across regions, shadow alignment, and lighting in high-contrast areas. High scores indicate inconsistent lighting typical of composite or CGI images.",
  "url": "https://farid.berkeley.edu/research/digital-forensics/"
}
```

## Dependencies

Uses existing dependencies:
- `numpy` - numerical operations and array processing
- `scipy` - signal processing (Sobel filters) and circular statistics
- `scikit-image` - edge detection (Canny), thresholding, morphology, region analysis
- `PIL` - image loading

No additional dependencies required.

## Performance Characteristics

- **Computational Complexity:** O(n) where n = number of pixels
- **Memory Usage:** Moderate (stores gradient arrays)
- **Processing Time:** ~0.5-1.5 seconds for typical images
- **Parallelizable:** Block-based analysis can be parallelized

## Advantages of This Approach

1. **No Heavy Dependencies:** No OCR or deep learning models required
2. **Physically Motivated:** Based on fundamental physics of light
3. **Robust:** Works on various image types and resolutions
4. **Interpretable:** Results can be explained in physical terms
5. **Lightweight:** Efficient enough for real-time web applications

## Limitations & Future Work

### Current Limitations
1. **Multiple Light Sources:** Natural scenes with multiple lights may score higher
2. **HDR Images:** High dynamic range processing can affect gradient analysis
3. **No 3D Reconstruction:** Doesn't model 3D scene geometry
4. **Text Detection:** Indirect detection via edge density (not true OCR)

### Future Enhancements
1. **Scene Classification:** Adapt thresholds based on scene type (indoor/outdoor)
2. **3D Lighting Models:** Incorporate 3D surface normal estimation
3. **Color Analysis:** Extend to analyze color temperature consistency
4. **Specular Highlights:** Add detection of inconsistent reflections
5. **Machine Learning:** Train adaptive thresholds from labeled datasets

## Research References

Based on Prof. Hany Farid's publications:
- "Exposing Digital Forgeries by Detecting Inconsistencies in Lighting"
- "Exposing Photo Manipulation from Shading and Shadows"
- "Exposing Photo Manipulation with Inconsistent Shadows"

Inspired by:
- `btlorch/license-plates` project on forensic analysis
- Research on lighting consistency in composite images

## Testing & Validation

Successfully tested with:
1. ✅ Module import and function validation
2. ✅ Integration with full analysis engine
3. ✅ Various synthetic test images
4. ✅ Score range validation (0.0-1.0)
5. ✅ Docker container deployment

## Maintainer Notes

- Thresholds (0.8 rad, 1.2 rad, etc.) are based on empirical observation
- Should be validated against datasets of real CGI vs natural images
- Consider adjusting weights if certain components prove more discriminative
- Monitor for edge cases: night scenes, silhouettes, very uniform images
