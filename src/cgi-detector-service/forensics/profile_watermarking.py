import cProfile
import pstats
from io import BytesIO
from PIL import Image
import sys
import os
# Add the project root to sys.path to allow absolute imports from cgi_detector_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from cgi_detector_service.forensics.watermarking import analyze_watermark

# Helper function to create a dummy image
def create_dummy_image(width, height, color=(128, 128, 128)) -> bytes:
    img = Image.new("RGB", (width, height), color)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def profile_analyze_watermark():
    print("Starting profiling for analyze_watermark...")
    dummy_image_bytes = create_dummy_image(800, 600) # Create a medium-sized image

    # Profile the function call
    profiler = cProfile.Profile()
    profiler.enable()

    # Run the function multiple times for a more reliable profile
    for _ in range(50):
        analyze_watermark(dummy_image_bytes)

    profiler.disable()
    print("Profiling finished.")

    # Save and print the profiling results
    stats_path = "watermark_profiling_results.prof"
    with open(stats_path, "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats("cumulative")
        stats.print_stats()

    print(f"Profiling results saved to {stats_path}")

if __name__ == "__main__":
    profile_analyze_watermark()
