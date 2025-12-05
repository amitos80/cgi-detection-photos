
import cProfile
import pstats
import os
from reflection_consistency import detect_reflection_inconsistencies

def run_reflection_consistency_analysis():
    # Path to a sample image
    image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dummy_dataset', 'fake', 'fake_image_0.png')
    
    # Call the detect_reflection_inconsistencies function
    detect_reflection_inconsistencies(image_path)

if __name__ == "__main__":
    profile_output_path = "reflection_consistency_profile.prof"
    cProfile.run('run_reflection_consistency_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
