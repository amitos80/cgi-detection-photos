# Performance Profiling Script for Statistical Anomaly Detection

import cProfile
import pstats
import os
import numpy as np
from PIL import Image
from io import BytesIO

# Assuming statistical_anomaly.py is in the same directory or accessible via path
# Adjust import path if necessary.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cgi_detector_service.forensics.statistical_anomaly import analyze_statistical_anomaly

def run_profiler():
    """
    Runs the profiler on the analyze_statistical_anomaly function.
    """
    # Create a dummy image for profiling
    img_size = (1024, 1024) # Use a reasonable size for profiling
    img = Image.new('RGB', img_size, color = 'red')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()

    # Setup profiler
    profiler = cProfile.Profile()
    profiler.enable()

    # Run the function to be profiled
    try:
        analyze_statistical_anomaly(image_bytes)
    except Exception as e:
        print(f"Error during profiling: {e}")

    profiler.disable()

    # Print stats
    s = pstats.Stats(profiler).sort_stats('cumulative')
    s.print_stats(20) # Print top 20 cumulative time stats

if __name__ == "__main__":
    print("Starting performance profiling for analyze_statistical_anomaly...")
    run_profiler()
    print("Profiling finished.")
