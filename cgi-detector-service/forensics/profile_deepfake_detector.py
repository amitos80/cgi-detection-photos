
import cProfile
import pstats
import os
from deepfake_detector import detect_deepfake

def run_deepfake_analysis():
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dummy_dataset', 'fake', 'fake_image_0.png')
    
    # Call the detect_deepfake function
    detect_deepfake(image_path)

if __name__ == "__main__":
    profile_output_path = "deepfake_detector_profile.prof"
    cProfile.run('run_deepfake_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
