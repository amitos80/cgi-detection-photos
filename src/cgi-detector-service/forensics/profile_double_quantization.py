
import cProfile
import pstats
import os
from double_quantization import detect_double_quantization

def run_double_quantization_analysis():
    # Path to a dummy video file in the temporary directory
    video_path = os.path.join('/Users/amit/.gemini/tmp/0cd18e5e14641d89d20a12aa4017baa1a5e49a8ccab9e881d7f88a1ac9adb1ee', 'dummy_video.mp4')
    
    # Call the detect_double_quantization function
    detect_double_quantization(video_path)

if __name__ == "__main__":
    profile_output_path = "double_quantization_profile.prof"
    cProfile.run('run_double_quantization_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
