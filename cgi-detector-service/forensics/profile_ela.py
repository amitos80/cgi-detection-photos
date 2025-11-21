
import cProfile
import pstats
import os
from ela import analyze_ela

def run_ela_analysis():
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dummy_dataset', 'fake', 'fake_image_0.png')
    
    # Read the image as bytes
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Call the analyze_ela function
    analyze_ela(image_bytes)

if __name__ == "__main__":
    profile_output_path = "ela_profile.prof"
    cProfile.run('run_ela_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
