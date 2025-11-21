
import cProfile
import pstats
import os
import numpy as np
from ml_predictor import load_model, predict

def run_ml_predictor_analysis():
    # Load a dummy model (or train one if it doesn't exist)
    model = load_model()
    
    # Create dummy features for prediction
    sample_features = np.random.rand(10) # 10 features, matching the dummy training data
    
    # Call the predict function
    predict(model, sample_features)

if __name__ == "__main__":
    profile_output_path = "ml_predictor_profile.prof"
    cProfile.run('run_ml_predictor_analysis()', profile_output_path)
    
    # Print a summary of the profiling results
    stats = pstats.Stats(profile_output_path)
    stats.sort_stats('cumulative').print_stats(10) # Print top 10 functions by cumulative time
