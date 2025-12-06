#!/usr/bin/env python3

import os
import glob
import importlib
import sys
import argparse
import random
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple

# Ensure the cgi_detector_service package is importable
# Add the parent directory of 'forensics' to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
forensics_path_relative = os.path.join(script_dir, '..', 'forensics')
forensics_dir = os.path.abspath(forensics_path_relative)

if forensics_dir not in sys.path:
    sys.path.insert(0, forensics_dir)
print(f"DEBUG: forensics_dir added to sys.path: {forensics_dir}")

# --- Configuration and Thresholds ---

GENERAL_THRESHOLDS = {
    'real_max_score': 0.5,  # For real images, most module scores should be below this.
    'fake_min_score': 0.4,  # For fake images, at least one module score should be above this.
}

MODULE_ASSERTIONS = {
    'ela': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'hos': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'jpeg_ghost': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'lighting_text': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'statistical_anomaly': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'deepfake_detector': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'ml_predictor': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'reflection_consistency': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'double_quantization': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'jpeg_dimples': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
    'watermarking': {
        'real': lambda score: score is not None and score < GENERAL_THRESHOLDS['real_max_score'],
        'fake': lambda score: score is not None and score > GENERAL_THRESHOLDS['fake_min_score'],
    },
}

ANALYSIS_FUNCTION_MAP = {
    'cfa': 'analyze_cfa',
    'deepfake_detector': 'detect_deepfake',
    'double_quantization': 'detect_double_quantization',
    'ela': 'analyze_ela',
    'geometric_3d': 'analyze_geometric_consistency',
    'hos': 'analyze_hos',
    'jpeg_dimples': 'detect_jpeg_dimples',
    'jpeg_ghost': 'analyze_jpeg_ghost',
    'lighting_text': 'analyze_lighting_consistency',
    'rambino': 'analyze_rambino_features',
    'reflection_consistency': 'detect_reflection_inconsistencies',
    'specialized_detectors': 'analyze_specialized_cgi_types',
    'statistical_anomaly': 'analyze_statistical_anomaly',
    'watermarking': 'analyze_watermark',
}


def load_forensic_modules(forensics_path: str) -> List[str]:
    module_names = []
    print(f"DEBUG: Searching for modules in: {forensics_path}") 
    for module_file in glob.glob(os.path.join(forensics_path, '*.py')):
        module_name = os.path.splitext(os.path.basename(module_file))[0]
        # Exclude __init__.py, test files, profile files, and execute_tests.py
        if not module_name.startswith('_') and \
           module_name != '__init__' and \
           not module_name.startswith('test_') and \
           not module_name.startswith('profile_') and \
           module_name != 'execute_tests': # Exclude execute_tests.py
            try:
                importlib.import_module(module_name)
                module_names.append(module_name)
            except ImportError as e:
                print(f"Warning: Module '{module_name}' failed to import. Ensure it's a valid Python module and has no import errors within itself. Details: {e}") 
            except Exception as e:
                print(f"Warning: An unexpected error occurred while checking module '{module_name}': {e}")
    print(f"DEBUG: Found modules: {module_names}") 
    return sorted(module_names)

def analyze_image_with_module(image_path: str, module_name: str) -> Tuple[float | None, str | None]:
    try:
        module = importlib.import_module(module_name)
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        analysis_func_name = ANALYSIS_FUNCTION_MAP.get(module_name)
        if analysis_func_name and hasattr(module, analysis_func_name):
            analysis_func = getattr(module, analysis_func_name)
            result = analysis_func(image_bytes)
            
            # Handle dictionary and direct score returns
            if isinstance(result, dict):
                score = result.get('confidence', result.get('score', 0.0))
            else:
                score = result

            if isinstance(score, (int, float)):
                return float(score), None
            else:
                try:
                    return float(str(score)), None
                except (ValueError, TypeError):
                    return None, f"Module '{module_name}' returned a non-numeric score type: {type(score).__name__} ({score})"
        else:
            return None, f"Analysis function for module '{module_name}' not found."

    except FileNotFoundError:
        return None, f"Image file not found at {image_path}"
    except ImportError:
        return None, f"Could not import module '{module_name}'. Ensure it's in the PYTHONPATH."
    except Exception as e:
        return None, f"An error occurred during analysis of {image_path} with {module_name}: {e}"


def analyze_image_with_service(image_path: str, service_url: str) -> Tuple[Dict[str, float | None] | None, str | None]:
    """Sends an image to the service and gets the analysis scores."""
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(f"{service_url}/analyze", files=files, timeout=45)
            response.raise_for_status()
            
            analysis_data = response.json()
            scores = {item['feature'].lower().replace(' ', '_'): item['score'] for item in analysis_data.get('analysis_breakdown', [])}
            return scores, None

    except requests.exceptions.RequestException as e:
        return None, f"Service request failed: {e}"
    except (IOError, KeyError, json.JSONDecodeError) as e:
        return None, f"Error processing service response: {e}"



def analyze_image_with_ml_predictor(image_path: str) -> Tuple[Dict[str, float | None] | None, str | None]:
    """Analyzes an image using the full forensic engine and ML predictor."""
    try:
        # This requires importing the main analysis engine
        from forensics.engine import run_analysis
        
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        analysis_data = run_analysis(image_bytes)
        scores = {item['feature'].lower().replace(' ', '_'): item['score'] for item in analysis_data.get('analysis_breakdown', [])}
        scores['final_confidence'] = analysis_data.get('confidence', 0.0)
        
        return scores, None
    except Exception as e:
        return None, f"ML predictor analysis failed: {e}"


def check_assertions(scores: Dict[str, float | None], ground_truth: str, modules_run: List[str]) -> Tuple[bool, List[str]]:
    failed_assertions = []
    all_assertions_met = True


    for module_name in modules_run:
        score = scores.get(module_name)
        
        if score is None:
            failed_assertions.append(f"Module '{module_name}' failed to produce a score.")
            all_assertions_met = False
            continue

        if module_name in MODULE_ASSERTIONS:
            module_asserts = MODULE_ASSERTIONS[module_name]
            assertion_func = module_asserts.get(ground_truth)
            
            if assertion_func:
                if not assertion_func(score):
                    failed_assertions.append(f"Module '{module_name}' assertion failed for {ground_truth} image: score {score:.4f} did not meet criteria.")
                    all_assertions_met = False

    return all_assertions_met, failed_assertions

def sample_images(image_paths: List[str], sample_size: int | None, strategy: str = 'stratified', is_real: bool | None = None) -> List[str]:
    if sample_size is None or sample_size >= len(image_paths):
        return image_paths 

    if strategy == 'random':
        return random.sample(image_paths, k=sample_size)
    
    if strategy == 'stratified':
        if is_real is None: 
            print(f"Warning: Stratified sampling requires ground truth. Falling back to random sampling for {sample_size} images.")
            return random.sample(image_paths, k=sample_size)
        
        # The logic here assumes image_paths is already separated into real/fake lists.
        # So, we just need to sample from the provided list.
        return random.sample(image_paths, k=min(sample_size, len(image_paths)))

    else:
        print(f"Warning: Unknown sampling strategy '{strategy}'. Falling back to random sampling.")
        return random.sample(image_paths, k=min(sample_size, len(image_paths)))

def classify_image(scores: Dict[str, float | None], ground_truth: str, modules_run: List[str]) -> Tuple[str, bool]:
    """Classifies an image as 'real' or 'fake' based on module scores."""
    is_fake = False
    for module_name in modules_run:
        score = scores.get(module_name)
        if score is not None and score > GENERAL_THRESHOLDS['fake_min_score']:
            is_fake = True
            break
    
    classification = 'fake' if is_fake else 'real'
    is_correct = classification == ground_truth
    return classification, is_correct


def save_test_results(results: Dict[str, Any], output_format: str = 'json', filename_prefix: str = 'test_results'):
    """Saves the test results to a file.

    Args:
        results: The dictionary containing test results.
        output_format: The format to save the results in ('json' or 'csv').
        filename_prefix: A prefix for the output filename.
    """
    if output_format == 'json':
        filename = f"{filename_prefix}_results.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=4)
            print(f"Test results saved to {filename}")
        except IOError as e:
            print(f"Error saving JSON results to {filename}: {e}")
    elif output_format == 'csv':
        print("CSV output format not yet implemented.")
        # TODO: Implement CSV export logic. This would likely involve pandas.
    else:
        print(f"Error: Unsupported output format '{output_format}' for saving results.")


def run_tests(dataset_root_dir: str, strategy: str = 'module', modules_to_test: List[str] | None = None, sample_size: int | None = None, sampling_strategy: str = 'stratified', service_url: str = 'http://localhost:8000'):
    """Runs tests against the dataset using the specified strategy and sampling.

    Args:
        dataset_root_dir: The root directory of the dataset (e.g., 'my_dataset').
        strategy: The testing strategy to use ('module' or 'service' or 'ml_predictor').
        modules_to_test: Optional list of specific forensic module names to test.
        sample_size: Number of images to sample from each class (real/fake).
        sampling_strategy: Strategy for sampling images ('stratified' or 'random').
    """
    print(f"Starting tests with strategy: {strategy}")
    print(f"Using dataset from: {dataset_root_dir}")

    real_images_dir = os.path.join(dataset_root_dir, 'real')
    fake_images_dir = os.path.join(dataset_root_dir, 'fake')

    if not os.path.isdir(real_images_dir):
        print(f"Error: Real images directory not found at {real_images_dir}")
        return
    if not os.path.isdir(fake_images_dir):
        print(f"Error: Fake images directory not found at {fake_images_dir}")
        return

    all_real_image_paths = sorted(glob.glob(os.path.join(real_images_dir, '*.*')))
    all_fake_image_paths = sorted(glob.glob(os.path.join(fake_images_dir, '*.*')))

    # Apply sampling
    real_image_paths = sample_images(all_real_image_paths, sample_size, strategy=sampling_strategy, is_real=True)
    fake_image_paths = sample_images(all_fake_image_paths, sample_size, strategy=sampling_strategy, is_real=False)

    print(f"Sampled {len(real_image_paths)} real images and {len(fake_image_paths)} fake images.")

    if not real_image_paths or not fake_image_paths:
        print("Warning: No images selected after sampling. Skipping analysis.")
        return

    modules_to_run: List[str] = []
    available_modules: List[str] = []
    if strategy in ['module', 'ml_predictor']:
        forensics_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'forensics')) # Corrected path construction
        available_modules = load_forensic_modules(forensics_path)
        
        if modules_to_test:
            modules_to_test_set = set(modules_to_test)
            selected_modules = [m for m in available_modules if m in modules_to_test_set]
            if not selected_modules:
                print(f"Error: None of the specified modules {modules_to_test} were found or are available.")
                return
            modules_to_run = selected_modules
        else:
            modules_to_run = available_modules
        
        if not modules_to_run:
            print("Error: No forensic modules found or selected for testing.")
            return
        print(f"Modules selected for testing: {', '.join(modules_to_run)}")
    
    test_results: Dict[str, Any] = {
        'dataset_root': dataset_root_dir,
        'strategy': strategy,
        'modules_tested': modules_to_run,
        'sample_size_per_class': sample_size,
        'sampling_strategy': sampling_strategy,
        'real_images': {
            'total': len(real_image_paths),
            'correctly_classified': 0,
            'details': []
        },
        'fake_images': {
            'total': len(fake_image_paths),
            'correctly_classified': 0,
            'details': []
        },
        'overall_metrics': {},
        'test_assertions': {'passed': 0, 'failed': 0, 'details': []},
        'errors': []
    }

    if strategy == 'module':
        print("\n--- Running Module-Level Tests ---")
        
        print(f"Processing {len(real_image_paths)} real images...")
        for img_path in real_image_paths:
            image_name = os.path.basename(img_path)
            image_analysis_scores: Dict[str, float | None] = {}
            module_errors_for_image: List[str] = []
            
            for module_name in modules_to_run:
                score, error = analyze_image_with_module(img_path, module_name)
                image_analysis_scores[module_name] = score
                if error:
                    module_errors_for_image.append(f"Module '{module_name}': {error}")
            
            classification, is_correct_classification = classify_image(image_analysis_scores, 'real', modules_to_run)
            test_results['real_images']['correctly_classified'] += int(is_correct_classification)

            assertions_met, failed_assertions = check_assertions(image_analysis_scores, 'real', modules_to_run)
            if not assertions_met:
                test_results['test_assertions']['failed'] += 1
                test_results['test_assertions']['details'].append({
                    'image': image_name,
                    'ground_truth': 'real',
                    'classification': classification,
                    'scores': image_analysis_scores,
                    'failed_assertions': failed_assertions
                })
            else:
                test_results['test_assertions']['passed'] += 1

            if module_errors_for_image:
                test_results['errors'].append({
                    'image': image_name,
                    'ground_truth': 'real',
                    'type': 'module_analysis',
                    'details': module_errors_for_image
                })

            test_results['real_images']['details'].append({
                'filename': image_name,
                'scores': image_analysis_scores,
                'classification': classification,
                'is_correct': is_correct_classification,
                'assertions_met': assertions_met,
                'failed_assertions_count': len(failed_assertions),
            })

        print(f"Processing {len(fake_image_paths)} fake images...")
        for img_path in fake_image_paths:
            image_name = os.path.basename(img_path)
            image_analysis_scores: Dict[str, float | None] = {}
            module_errors_for_image: List[str] = []

            for module_name in modules_to_run:
                score, error = analyze_image_with_module(img_path, module_name)
                image_analysis_scores[module_name] = score
                if error:
                    module_errors_for_image.append(f"Module '{module_name}': {error}")

            classification, is_correct_classification = classify_image(image_analysis_scores, 'fake', modules_to_run)
            test_results['fake_images']['correctly_classified'] += int(is_correct_classification)

            assertions_met, failed_assertions = check_assertions(image_analysis_scores, 'fake', modules_to_run)
            if not assertions_met:
                test_results['test_assertions']['failed'] += 1
                test_results['test_assertions']['details'].append({
                    'image': image_name,
                    'ground_truth': 'fake',
                    'classification': classification,
                    'scores': image_analysis_scores,
                    'failed_assertions': failed_assertions
                })
            else:
                test_results['test_assertions']['passed'] += 1

            if module_errors_for_image:
                test_results['errors'].append({
                    'image': image_name,
                    'ground_truth': 'fake',
                    'type': 'module_analysis',
                    'details': module_errors_for_image
                })

            test_results['fake_images']['details'].append({
                'filename': image_name,
                'scores': image_analysis_scores,
                'classification': classification,
                'is_correct': is_correct_classification,
                'assertions_met': assertions_met,
                'failed_assertions_count': len(failed_assertions),
            })

    elif strategy == 'service':
        print("\n--- Running Service-Level Tests ---")
        
        # Helper function to process a single image and record results
        def process_image(img_path, ground_truth):
            image_name = os.path.basename(img_path)
            scores, error = analyze_image_with_service(img_path, service_url)
            
            if error:
                return {
                    'image': image_name,
                    'ground_truth': ground_truth,
                    'type': 'service_analysis',
                    'details': [error]
                }, None

            classification, is_correct = classify_image(scores, ground_truth, list(scores.keys()))
            
            result_details = {
                'filename': image_name,
                'scores': scores,
                'classification': classification,
                'is_correct': is_correct,
            }
            return None, (result_details, is_correct, ground_truth)

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submitting all images to the executor
            futures = {executor.submit(process_image, img_path, 'real'): img_path for img_path in real_image_paths}
            futures.update({executor.submit(process_image, img_path, 'fake'): img_path for img_path in fake_image_paths})

            for future in as_completed(futures):
                error, result = future.result()
                if error:
                    test_results['errors'].append(error)
                elif result:
                    result_details, is_correct, ground_truth = result
                    if ground_truth == 'real':
                        test_results['real_images']['details'].append(result_details)
                        test_results['real_images']['correctly_classified'] += int(is_correct)
                    else:
                        test_results['fake_images']['details'].append(result_details)
                        test_results['fake_images']['correctly_classified'] += int(is_correct)


    elif strategy == 'ml_predictor':
        print("\n--- Running ML Predictor Tests ---")
        
        def process_image_ml(img_path, ground_truth):
            image_name = os.path.basename(img_path)
            scores, error = analyze_image_with_ml_predictor(img_path)

            if error:
                return {
                    'image': image_name,
                    'ground_truth': ground_truth,
                    'type': 'ml_predictor_analysis',
                    'details': [error]
                }, None

            # For ML predictor, the primary classification is based on the final confidence score
            final_confidence = scores.get('final_confidence', 0.0)
            classification = 'fake' if final_confidence > 0.5 else 'real'
            is_correct = classification == ground_truth
            
            result_details = {
                'filename': image_name,
                'scores': scores,
                'classification': classification,
                'is_correct': is_correct,
            }
            return None, (result_details, is_correct, ground_truth)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_image_ml, img_path, 'real'): img_path for img_path in real_image_paths}
            futures.update({executor.submit(process_image_ml, img_path, 'fake'): img_path for img_path in fake_image_paths})

            for future in as_completed(futures):
                error, result = future.result()
                if error:
                    test_results['errors'].append(error)
                elif result:
                    result_details, is_correct, ground_truth = result
                    if ground_truth == 'real':
                        test_results['real_images']['details'].append(result_details)
                        test_results['real_images']['correctly_classified'] += int(is_correct)
                    else:
                        test_results['fake_images']['details'].append(result_details)
                        test_results['fake_images']['correctly_classified'] += int(is_correct)


    else:
        print(f"Error: Unknown strategy '{strategy}'")

    # --- Reporting ---
    print("\n--- Test Run Complete ---")
    print(f"Dataset: {test_results['dataset_root']}")
    print(f"Strategy: {test_results['strategy']}")
    if test_results['modules_tested']:
        print(f"Modules tested: {', '.join(test_results['modules_tested'])}")
    if sample_size is not None:
        print(f"Sample size per class: {sample_size}")
    if sampling_strategy:
        print(f"Sampling strategy: {sampling_strategy}")

    print("\nResults Summary:")
    print(f"  Real Images: {test_results['real_images']['correctly_classified']}/{test_results['real_images']['total']} correctly classified")
    print(f"  Fake Images: {test_results['fake_images']['correctly_classified']}/{test_results['fake_images']['total']} correctly classified")

    total_real = test_results['real_images']['total']
    correct_real = test_results['real_images']['correctly_classified']
    total_fake = test_results['fake_images']['total']
    correct_fake = test_results['fake_images']['correctly_classified']

    total_images = total_real + total_fake
    if total_images > 0:
        accuracy = (correct_real + correct_fake) / total_images
        test_results['overall_metrics']['accuracy'] = accuracy
    else:
        accuracy = 0

    true_positives_fake = correct_fake 
    false_positives_fake = total_real - correct_real 
    false_negatives_fake = total_fake - correct_fake 
    
    if (true_positives_fake + false_positives_fake) > 0:
        precision_fake = true_positives_fake / (true_positives_fake + false_positives_fake)
        test_results['overall_metrics']['precision_fake'] = precision_fake
    else:
        precision_fake = 0

    if total_fake > 0:
        recall_fake = true_positives_fake / total_fake
        test_results['overall_metrics']['recall_fake'] = recall_fake
    else:
        recall_fake = 0

    if (precision_fake + recall_fake) > 0:
        f1_score_fake = 2 * (precision_fake * recall_fake) / (precision_fake + recall_fake)
        test_results['overall_metrics']['f1_score_fake'] = f1_score_fake
    else:
        f1_score_fake = 0

    print(f"  Overall Accuracy: {accuracy:.4f}")
    print(f"  Precision (Fake): {precision_fake:.4f}")
    print(f"  Recall (Fake): {recall_fake:.4f}")
    print(f"  F1-Score (Fake): {f1_score_fake:.4f}")

    print(f"\nAssertions: {test_results['test_assertions']['passed']} passed, {test_results['test_assertions']['failed']} failed.")
    if test_results['test_assertions']['failed'] > 0:
        print("  Failed Assertion Details (showing first 3):")
        for i, assertion_detail in enumerate(test_results['test_assertions']['details'][:min(3, len(test_results['test_assertions']['details']))]):
            details_str = "; ".join(assertion_detail.get('failed_assertions', ['No details']))
            print(f"    - Image: {assertion_detail.get('image', 'N/A')}, GT: {assertion_detail.get('ground_truth', 'N/A')}, Class: {assertion_detail.get('classification', 'N/A')}, Assertions: {details_str}")
        if len(test_results['test_assertions']['details']) > 3:
            print("    ...")

    if test_results['errors']:
        print(f"\nEncountered {len(test_results['errors'])} errors during testing.")
        for i, error_info in enumerate(test_results['errors'][:min(3, len(test_results['errors']))]):
            details_str = "; ".join(error_info.get('details', ['No details']))
            print(f"  - Image: {error_info.get('image', 'N/A')}, GT: {error_info.get('ground_truth', 'N/A')}, Type: {error_info.get('type', 'N/A')}, Details: {details_str}")
        if len(test_results['errors']) > 3:
            print("  ...")
    else:
        print("\nNo errors encountered during testing.")

    # Save results to a file
    save_test_results(test_results, output_format='json', filename_prefix='test_run')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run comprehensive tests on CGI detection models using a dataset.')
    parser.add_argument('--dataset_dir', type=str, default='my_dataset', help="Directory containing the real and fake image datasets. Defaults to 'my_dataset'.")
    parser.add_argument('--strategy', type=str, default='module', choices=['module', 'service', 'ml_predictor'], help="Testing strategy to use. Defaults to 'module'.")
    parser.add_argument('--modules', type=str, nargs='*', help='Optional list of specific forensic module names to test (e.g., --modules ela hos). If not provided, all modules will be tested.')
    parser.add_argument('--sample_size', type=int, help='Number of images to sample from each class (real/fake) for testing. If not provided, all images are used.')
    parser.add_argument('--sampling_strategy', type=str, default='stratified', choices=['stratified', 'random'], help="Strategy for sampling images. Defaults to 'stratified'.")
    parser.add_argument('--service_url', type=str, default='http://localhost:8000', help="URL of the CGI detector service to test against. Defaults to 'http://localhost:8000'.")
    
    args = parser.parse_args()
    
    run_tests(args.dataset_dir, args.strategy, args.modules, args.sample_size, args.sampling_strategy, args.service_url)
