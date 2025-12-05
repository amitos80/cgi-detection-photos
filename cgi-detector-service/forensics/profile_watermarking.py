import cProfile
import pstats
import io
import os
import numpy as np
import cv2
from cgi_detector_service.forensics import watermarking

def create_dummy_image_bytes(width=512, height=512, format='png') -> bytes:
    """Helper to create a dummy image for profiling."""
    img = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    _, encoded_image = cv2.imencode(f'.{format}', img)
    return encoded_image.tobytes()

def profile_watermarking_analysis():
    """
    Profiles the watermarking analysis function with a dummy image.
    """
    print("Starting profiling for watermarking.analyze_watermark...")
    image_bytes = create_dummy_image_bytes()

    pr = cProfile.Profile()
    pr.enable()

    # Run the function to be profiled
    _ = watermarking.analyze_watermark(image_bytes)

    pr.disable()

    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()

    print(s.getvalue())
    print("Profiling complete.")

    # Optionally save to a file
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..") # Go up to project root
    output_file = os.path.join(output_dir, "watermarking_profile.prof")
    pr.dump_stats(output_file)
    print(f"Profiling data saved to {output_file}")

if __name__ == '__main__':
    profile_watermarking_analysis()