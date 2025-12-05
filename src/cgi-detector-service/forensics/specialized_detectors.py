"""
Specialized CGI Type Detectors Module

This module contains specialized detectors for specific types of CGI and AI-generated imagery.
Each detector looks for unique fingerprints and artifacts characteristic of different
generation methods (GANs, Diffusion Models, 3D Rendering, Face Synthesis).

Based on research into generative model fingerprints and CGI rendering artifacts.
"""

import numpy as np
from PIL import Image
from io import BytesIO
from scipy import ndimage, fft, signal
from scipy.stats import kurtosis, skew
from skimage import filters, feature, color
from skimage.util import img_as_float
import warnings

warnings.filterwarnings('ignore')


def analyze_specialized_cgi_types(image_bytes: bytes) -> dict:
    """
    Runs all specialized CGI type detectors and returns detailed results.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Dictionary containing:
        - overall_score: Weighted average of all detectors (0-1)
        - detector_scores: Individual scores for each detector type
        - likely_type: Most likely CGI generation method
    """
    try:
        # Load image
        image = Image.open(BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array
        img_array = np.array(image)

        # Run all specialized detectors
        gan_score = _detect_gan_fingerprints(img_array)
        diffusion_score = _detect_diffusion_artifacts(img_array)
        face_synthesis_score = _detect_face_synthesis(img_array)
        render_3d_score = _detect_3d_rendering(img_array)

        # Weight the different detectors
        weights = {
            'gan': 0.30,
            'diffusion': 0.30,
            'face_synthesis': 0.20,
            '3d_render': 0.20
        }

        # Calculate weighted average
        overall_score = (
            gan_score * weights['gan'] +
            diffusion_score * weights['diffusion'] +
            face_synthesis_score * weights['face_synthesis'] +
            render_3d_score * weights['3d_render']
        )

        # Determine likely type based on highest score
        detector_scores = {
            'gan': gan_score,
            'diffusion': diffusion_score,
            'face_synthesis': face_synthesis_score,
            '3d_render': render_3d_score
        }

        likely_type = max(detector_scores, key=detector_scores.get)
        type_names = {
            'gan': 'GAN-Generated',
            'diffusion': 'Diffusion Model',
            'face_synthesis': 'Face Synthesis/Deepfake',
            '3d_render': '3D-Rendered CGI'
        }

        return {
            'overall_score': float(np.clip(overall_score, 0.0, 1.0)),
            'detector_scores': {k: float(v) for k, v in detector_scores.items()},
            'likely_type': type_names.get(likely_type, 'Unknown') if max(detector_scores.values()) > 0.4 else 'Unknown'
        }

    except Exception as e:
        print(f"Error in specialized CGI detection: {e}")
        return {
            'overall_score': 0.0,
            'detector_scores': {'gan': 0.0, 'diffusion': 0.0, 'face_synthesis': 0.0, '3d_render': 0.0},
            'likely_type': 'Unknown'
        }


def _detect_gan_fingerprints(img_array: np.ndarray) -> float:
    """
    Detects fingerprints specific to GAN-generated images (StyleGAN, ProGAN, etc.).

    GANs often leave characteristic artifacts:
    - Checkerboard patterns from upsampling
    - Spectral irregularities in frequency domain
    - Over-regularity in high-frequency components
    - Unnatural spectral peaks

    Args:
        img_array: RGB image as numpy array

    Returns:
        Score (0-1) indicating likelihood of GAN generation
    """
    try:
        # Convert to grayscale for frequency analysis
        gray = np.mean(img_array, axis=2).astype(float)

        # 1. Check for checkerboard artifacts (common in GANs with upsampling)
        checkerboard_score = _detect_checkerboard_pattern(gray)

        # 2. Analyze frequency spectrum for GAN signatures
        spectral_score = _analyze_gan_spectral_signature(gray)

        # 3. Check for over-regularity in high frequencies
        regularity_score = _detect_spectral_regularity(gray)

        # Combine scores
        weights = {'checkerboard': 0.30, 'spectral': 0.40, 'regularity': 0.30}
        final_score = (
            checkerboard_score * weights['checkerboard'] +
            spectral_score * weights['spectral'] +
            regularity_score * weights['regularity']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in GAN fingerprint detection: {e}")
        return 0.0


def _detect_checkerboard_pattern(gray_image: np.ndarray) -> float:
    """Detects checkerboard artifacts from upsampling in GANs."""
    try:
        # Create checkerboard detection kernels
        kernel_size = 4
        checkerboard_kernel = np.array([[1, -1], [-1, 1]])

        # Convolve with checkerboard kernel
        response = signal.correlate2d(gray_image, checkerboard_kernel, mode='valid')

        # Calculate strength of checkerboard pattern
        pattern_strength = np.abs(response).mean()

        # Normalize (empirical threshold)
        threshold = 50.0
        score = min(pattern_strength / threshold, 1.0)

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _analyze_gan_spectral_signature(gray_image: np.ndarray) -> float:
    """Analyzes frequency spectrum for GAN-specific patterns."""
    try:
        # Compute 2D FFT
        f_transform = fft.fft2(gray_image)
        f_shift = fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)

        # Analyze radial frequency distribution
        center = np.array(magnitude_spectrum.shape) // 2
        y, x = np.ogrid[:magnitude_spectrum.shape[0], :magnitude_spectrum.shape[1]]
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)

        # Compute radial average
        r_int = r.astype(int)
        max_r = min(center)
        radial_profile = np.zeros(max_r)

        for radius in range(max_r):
            mask = (r_int == radius)
            if mask.any():
                radial_profile[radius] = magnitude_spectrum[mask].mean()

        # GANs often show unnatural peaks in mid-frequencies
        # Analyze kurtosis of radial profile (GAN = high kurtosis)
        profile_kurtosis = kurtosis(radial_profile[1:])  # Skip DC component

        # High kurtosis indicates sharp peaks (GAN artifact)
        if profile_kurtosis > 3.0:
            score = min((profile_kurtosis - 2.0) / 5.0, 1.0)
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_spectral_regularity(gray_image: np.ndarray) -> float:
    """Detects over-regularity in high-frequency components (GAN artifact)."""
    try:
        # Extract high-frequency components
        high_pass = gray_image - ndimage.gaussian_filter(gray_image, sigma=5)

        # Calculate local standard deviation
        local_std = ndimage.generic_filter(high_pass, np.std, size=16)

        # GANs often produce overly regular high-frequency content
        # Measure variance of the local standard deviations
        regularity = np.std(local_std)

        # Low variance = high regularity = suspicious
        if regularity < 5.0:
            score = (5.0 - regularity) / 5.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_diffusion_artifacts(img_array: np.ndarray) -> float:
    """
    Detects artifacts specific to diffusion models (Stable Diffusion, DALL-E, Midjourney).

    Diffusion models have characteristic signatures:
    - Specific noise residuals from denoising process
    - Unusual texture patterns
    - Color saturation artifacts
    - Over-smoothness in certain frequency bands

    Args:
        img_array: RGB image as numpy array

    Returns:
        Score (0-1) indicating likelihood of diffusion model generation
    """
    try:
        gray = np.mean(img_array, axis=2).astype(float)

        # 1. Detect diffusion noise residuals
        noise_score = _detect_diffusion_noise_pattern(gray)

        # 2. Analyze color saturation (diffusion models often oversaturate)
        saturation_score = _analyze_color_saturation(img_array)

        # 3. Check for over-smoothness in mid-frequencies
        smoothness_score = _detect_diffusion_smoothness(gray)

        # Combine scores
        weights = {'noise': 0.35, 'saturation': 0.30, 'smoothness': 0.35}
        final_score = (
            noise_score * weights['noise'] +
            saturation_score * weights['saturation'] +
            smoothness_score * weights['smoothness']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in diffusion artifact detection: {e}")
        return 0.0


def _detect_diffusion_noise_pattern(gray_image: np.ndarray) -> float:
    """Detects noise patterns characteristic of diffusion models."""
    try:
        # Apply multi-scale Laplacian to extract noise
        noise_bands = []
        for sigma in [1, 2, 4]:
            laplacian = ndimage.gaussian_laplace(gray_image, sigma=sigma)
            noise_bands.append(laplacian)

        # Diffusion models leave specific cross-scale correlations
        # Calculate correlation between different scales
        correlations = []
        for i in range(len(noise_bands) - 1):
            # Downsample larger scale to match
            corr = np.corrcoef(
                noise_bands[i].flatten()[:10000],
                noise_bands[i+1].flatten()[:10000]
            )[0, 1]
            correlations.append(abs(corr))

        # Diffusion models show higher cross-scale correlation
        avg_correlation = np.mean(correlations)

        if avg_correlation > 0.3:
            score = (avg_correlation - 0.2) / 0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _analyze_color_saturation(img_array: np.ndarray) -> float:
    """Analyzes color saturation patterns (diffusion models often oversaturate)."""
    try:
        # Convert to HSV
        img_float = img_as_float(img_array)
        hsv = color.rgb2hsv(img_float)
        saturation = hsv[:, :, 1]

        # Calculate saturation statistics
        mean_sat = np.mean(saturation)
        std_sat = np.std(saturation)

        # Diffusion models often produce:
        # 1. Higher mean saturation (> 0.5)
        # 2. Lower variance (more uniform saturation)

        over_saturation = 0.0
        if mean_sat > 0.5:
            over_saturation = (mean_sat - 0.5) / 0.5

        uniform_saturation = 0.0
        if std_sat < 0.15:
            uniform_saturation = (0.15 - std_sat) / 0.15

        score = (over_saturation + uniform_saturation) / 2.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_diffusion_smoothness(gray_image: np.ndarray) -> float:
    """Detects over-smoothness in mid-frequencies (diffusion artifact)."""
    try:
        # Apply bandpass filter to isolate mid-frequencies
        low_pass = ndimage.gaussian_filter(gray_image, sigma=8)
        high_pass = gray_image - ndimage.gaussian_filter(gray_image, sigma=2)
        mid_freq = gray_image - low_pass - high_pass

        # Calculate energy in mid-frequencies
        mid_energy = np.var(mid_freq)

        # Diffusion models often have reduced mid-frequency energy
        # due to the denoising process
        high_energy = np.var(high_pass)

        if high_energy > 0:
            ratio = mid_energy / high_energy
            # Natural images typically have ratio > 0.3
            # Diffusion images often have ratio < 0.2
            if ratio < 0.2:
                score = (0.2 - ratio) / 0.2
            else:
                score = 0.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_face_synthesis(img_array: np.ndarray) -> float:
    """
    Detects face synthesis and deepfakes.

    Face synthesis has specific characteristics:
    - Unnatural eye symmetry
    - Skin texture artifacts
    - Boundary inconsistencies around face region
    - Specific spectral signatures in facial regions

    Args:
        img_array: RGB image as numpy array

    Returns:
        Score (0-1) indicating likelihood of face synthesis
    """
    try:
        gray = np.mean(img_array, axis=2).astype(float)

        # 1. Detect unnatural symmetry (common in face synthesis)
        symmetry_score = _analyze_face_symmetry(gray)

        # 2. Analyze skin texture patterns
        texture_score = _analyze_skin_texture(img_array)

        # 3. Check for boundary artifacts
        boundary_score = _detect_face_boundary_artifacts(gray)

        # Combine scores
        weights = {'symmetry': 0.35, 'texture': 0.35, 'boundary': 0.30}
        final_score = (
            symmetry_score * weights['symmetry'] +
            texture_score * weights['texture'] +
            boundary_score * weights['boundary']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in face synthesis detection: {e}")
        return 0.0


def _analyze_face_symmetry(gray_image: np.ndarray) -> float:
    """Analyzes facial symmetry (synthesis often creates unnatural symmetry)."""
    try:
        height, width = gray_image.shape

        # Focus on center region (likely to contain face)
        center_h, center_w = height // 2, width // 2
        face_region = gray_image[
            center_h - height//4:center_h + height//4,
            center_w - width//4:center_w + width//4
        ]

        if face_region.size == 0:
            return 0.0

        # Compare left and right halves
        mid = face_region.shape[1] // 2
        left_half = face_region[:, :mid]
        right_half = face_region[:, mid:2*mid]
        right_half_flipped = np.fliplr(right_half)

        # Ensure same size
        min_w = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_w]
        right_half_flipped = right_half_flipped[:, :min_w]

        # Calculate correlation
        correlation = np.corrcoef(
            left_half.flatten(),
            right_half_flipped.flatten()
        )[0, 1]

        # Very high symmetry (>0.9) is suspicious for faces
        if correlation > 0.9:
            score = (correlation - 0.85) / 0.15
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _analyze_skin_texture(img_array: np.ndarray) -> float:
    """Analyzes skin texture patterns (synthetic skin looks different)."""
    try:
        # Convert to grayscale
        gray = np.mean(img_array, axis=2)

        # Extract texture using Gabor filters at multiple scales
        frequencies = [0.1, 0.2, 0.3]
        texture_responses = []

        for freq in frequencies:
            real, imag = filters.gabor(gray, frequency=freq)
            texture_responses.append(np.abs(real))

        # Calculate texture regularity
        regularity_scores = []
        for response in texture_responses:
            # Synthetic skin often has overly regular texture
            local_std = ndimage.generic_filter(response, np.std, size=20)
            regularity = np.std(local_std)
            regularity_scores.append(regularity)

        avg_regularity = np.mean(regularity_scores)

        # Low regularity variance = artificial texture
        if avg_regularity < 0.5:
            score = (0.5 - avg_regularity) / 0.5
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_face_boundary_artifacts(gray_image: np.ndarray) -> float:
    """Detects boundary artifacts around synthesized faces."""
    try:
        # Detect edges
        edges = feature.canny(gray_image, sigma=2)

        # Look for circular/elliptical boundaries (face boundaries)
        # Using edge density in annular regions
        height, width = gray_image.shape
        center_y, center_x = height // 2, width // 2

        y, x = np.ogrid[:height, :width]
        r = np.sqrt((x - center_x)**2 + (y - center_y)**2)

        # Check edge density in annular rings
        ring_densities = []
        for inner_r in range(50, min(height, width) // 2, 30):
            outer_r = inner_r + 30
            mask = (r >= inner_r) & (r < outer_r)
            if mask.any():
                density = edges[mask].sum() / mask.sum()
                ring_densities.append(density)

        if len(ring_densities) > 1:
            # Sharp transitions indicate face boundaries
            density_variance = np.var(ring_densities)
            if density_variance > 0.01:
                score = min(density_variance / 0.02, 1.0)
            else:
                score = 0.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_3d_rendering(img_array: np.ndarray) -> float:
    """
    Detects 3D-rendered CGI (Blender, Maya, game engines).

    3D rendering has characteristic features:
    - Perfect geometric precision
    - Specific shading patterns
    - Antialiasing artifacts
    - Unrealistic material properties

    Args:
        img_array: RGB image as numpy array

    Returns:
        Score (0-1) indicating likelihood of 3D rendering
    """
    try:
        gray = np.mean(img_array, axis=2).astype(float)

        # 1. Detect perfect edges (3D renders have precise geometry)
        precision_score = _detect_geometric_precision(gray)

        # 2. Analyze shading patterns
        shading_score = _analyze_render_shading(gray)

        # 3. Detect antialiasing patterns
        aa_score = _detect_antialiasing_artifacts(gray)

        # Combine scores
        weights = {'precision': 0.35, 'shading': 0.35, 'antialiasing': 0.30}
        final_score = (
            precision_score * weights['precision'] +
            shading_score * weights['shading'] +
            aa_score * weights['antialiasing']
        )

        return float(np.clip(final_score, 0.0, 1.0))

    except Exception as e:
        print(f"Error in 3D rendering detection: {e}")
        return 0.0


def _detect_geometric_precision(gray_image: np.ndarray) -> float:
    """Detects overly precise geometry typical of 3D rendering."""
    try:
        # Detect edges
        edges = feature.canny(gray_image, sigma=1.5)

        # Find lines using Hough transform
        from skimage.transform import probabilistic_hough_line
        lines = probabilistic_hough_line(edges, threshold=10, line_length=30, line_gap=3)

        if not lines or len(lines) < 5:
            return 0.0

        # Analyze line straightness (3D renders have very straight lines)
        straightness_scores = []
        for line in lines[:20]:  # Limit to first 20 lines
            p1, p2 = line
            length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            if length > 10:
                # Perfect lines in 3D renders
                straightness_scores.append(1.0)

        if straightness_scores:
            avg_straightness = np.mean(straightness_scores)
            # Very high average indicates 3D render
            if avg_straightness > 0.8:
                score = (avg_straightness - 0.7) / 0.3
            else:
                score = 0.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _analyze_render_shading(gray_image: np.ndarray) -> float:
    """Analyzes shading patterns typical of 3D rendering."""
    try:
        # Calculate gradients
        grad_x = ndimage.sobel(gray_image, axis=1)
        grad_y = ndimage.sobel(gray_image, axis=0)
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)

        # 3D renders often have very smooth gradients
        # Calculate second derivatives (curvature)
        grad_grad_x = ndimage.sobel(gradient_mag, axis=1)
        grad_grad_y = ndimage.sobel(gradient_mag, axis=0)
        curvature = np.sqrt(grad_grad_x**2 + grad_grad_y**2)

        # Low curvature variance = smooth shading = possible render
        curvature_std = np.std(curvature)

        if curvature_std < 5.0:
            score = (5.0 - curvature_std) / 5.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0


def _detect_antialiasing_artifacts(gray_image: np.ndarray) -> float:
    """Detects antialiasing patterns specific to 3D rendering."""
    try:
        # Detect edges
        edges = feature.canny(gray_image, sigma=1)

        # Dilate edges slightly
        from skimage.morphology import binary_dilation, disk
        dilated_edges = binary_dilation(edges, disk(2))

        # Extract regions around edges
        edge_regions = gray_image[dilated_edges]
        non_edge_regions = gray_image[~dilated_edges]

        if len(edge_regions) > 100 and len(non_edge_regions) > 100:
            # 3D renders often have specific intensity distributions around edges
            edge_std = np.std(edge_regions)
            non_edge_std = np.std(non_edge_regions)

            if non_edge_std > 0:
                ratio = edge_std / non_edge_std
                # 3D renders typically have higher edge variance due to AA
                if ratio > 1.5:
                    score = min((ratio - 1.2) / 1.0, 1.0)
                else:
                    score = 0.0
            else:
                score = 0.0
        else:
            score = 0.0

        return float(np.clip(score, 0.0, 1.0))

    except Exception:
        return 0.0
