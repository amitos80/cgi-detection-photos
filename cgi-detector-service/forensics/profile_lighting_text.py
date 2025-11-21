
import cProfile
import pstats
import os
from lighting_text import analyze_lighting_consistency

def run_lighting_text_analysis():
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dummy_dataset', 'fake', 'fake_image_0.png')
    
    # Read the image as bytes
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Call the analyze_lighting_consistency function
    analyze_lighting_consistency(image_bytes)

if __name__ == "__main__":
    profile_output_path = "lighting_text_profile.prof"
    cProfile.run('run_lighting_text_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
