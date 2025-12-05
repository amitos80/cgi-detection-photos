import numpy as np
from PIL import Image
from io import BytesIO
from scipy.stats import entropy
from skimage.feature import graycomatrix, graycoprops

def analyze_statistical_anomaly(image_bytes: bytes) -> float:
    """
    Analyzes an image for statistical anomalies indicative of AI generation.

    This function performs several statistical analyses on the input image:
    1.  **Local Entropy Analysis:** Calculates the entropy of small image blocks.
        AI-generated images may exhibit unnaturally uniform or heterogeneous
        entropy distributions compared to natural images.
    2.  **GLCM Texture Analysis:** Extracts Gray-Level Co-occurrence Matrix (GLCM)
        features like contrast, dissimilarity, homogeneity, and energy.
        AI models can produce textures that are statistically different from
        natural textures, often appearing too smooth, repetitive, or chaotic.
    3.  **Local Noise Variance:** Measures the variance of pixel values in local
        neighborhoods. Natural images typically have a more consistent noise
        profile than AI-generated images, which can sometimes have areas of
        unusually high or low noise.

    The final score is a composite of these metrics, normalized to be between 0.0 and 1.0.
    A higher score indicates a higher likelihood of statistical anomalies,
    suggesting AI generation.

    Args:
        image_bytes: The raw bytes of the image.

    Returns:
        A float score between 0.0 and 1.0, where higher values indicate a
        higher probability of statistical anomalies consistent with AI generation.
    """
    try:
        image = Image.open(BytesIO(image_bytes)).convert('L')  # Convert to grayscale
        img_array = np.array(image)
    except Exception:
        return 0.0

    if img_array.ndim != 2:
        return 0.0  # Ensure it's a 2D grayscale image

    # Normalize image to 0-255 for GLCM and entropy calculations
    img_array_norm = (img_array / img_array.max() * 255).astype(np.uint8)

    # --- 1. Local Entropy Analysis ---
    # Divide image into blocks and compute entropy for each
    block_size = 16
    h, w = img_array_norm.shape
    entropies = []
    for r in range(0, h - block_size + 1, block_size):
        for c in range(0, w - block_size + 1, block_size):
            block = img_array_norm[r:r + block_size, c:c + block_size]
            hist, _ = np.histogram(block.flatten(), bins=256, range=(0, 256))
            hist = hist / hist.sum()  # Normalize to get probabilities
            entropies.append(entropy(hist + 1e-10))  # Add small epsilon to prevent log(0)

    entropy_std_dev = np.std(entropies) if entropies else 0.0

    # --- 2. GLCM Texture Analysis ---
    # Ensure a proper range for GLCM; if image is too uniform, it can cause issues
    if np.max(img_array_norm) == np.min(img_array_norm):
        glcm_contrast = 0.0
        glcm_dissimilarity = 0.0
        glcm_homogeneity = 1.0
        glcm_energy = 1.0
    else:
        # Increase n_levels to better capture variations in images with many shades of gray
        # But limit to 256 as np.uint8 range
        levels = 256
        if img_array_norm.max() < levels:
            levels = img_array_norm.max() + 1
        
        distances = [1]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]

        # Use symmetric and normed properties for better feature stability
        glcm = graycomatrix(img_array_norm, distances=distances, angles=angles, levels=levels,
                            symmetric=True, normed=True)
        
        contrast = graycoprops(glcm, 'contrast').mean()
        dissimilarity = graycoprops(glcm, 'dissimilarity').mean()
        homogeneity = graycoprops(glcm, 'homogeneity').mean()
        energy = graycoprops(glcm, 'energy').mean()

        glcm_contrast = contrast
        glcm_dissimilarity = dissimilarity
        glcm_homogeneity = homogeneity
        glcm_energy = energy

    # --- 3. Local Noise Variance ---
    kernel_size = 3
    noise_variances = []
    for r in range(0, h - kernel_size + 1):
        for c in range(0, w - kernel_size + 1):
            block = img_array[r:r + kernel_size, c:c + kernel_size]
            noise_variances.append(np.var(block))

    noise_variance_std_dev = np.std(noise_variances) if noise_variances else 0.0

    # --- Combine Scores (Heuristic) ---
    # These weights and normalization factors are heuristic and can be tuned
    # based on dataset and observed behavior.
    
    # Entropy: Higher std dev of entropy might indicate anomalies
    entropy_score = np.clip(entropy_std_dev * 10, 0.0, 1.0) 

    # GLCM: High contrast/dissimilarity or low homogeneity/energy can be anomalous
    glcm_score = np.clip((glcm_contrast + glcm_dissimilarity - glcm_homogeneity - glcm_energy + 2) / 4, 0.0, 1.0)
    
    # Noise Variance: High std dev of noise variance might indicate anomalies
    noise_score = np.clip(noise_variance_std_dev / 1000, 0.0, 1.0) # Scale appropriately

    # Simple average for now, can be improved with ML or more complex weighting
    final_score = (entropy_score + glcm_score + noise_score) / 3.0

    return float(final_score)

