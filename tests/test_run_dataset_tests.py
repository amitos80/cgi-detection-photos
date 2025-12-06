import unittest
import os
import shutil

# Assume run_dataset_tests.py is in the same directory or accessible via PYTHONPATH
# For testing, we might need to mock file system operations and module imports.
# For simplicity here, we'll focus on testing the core logic functions directly if possible,
# or mock their dependencies.

# Mocking dependencies: sys.path, glob, importlib, random, json, argparse
# We will need to mock these to isolate the function being tested.

# For the sake of this example, let's assume we are testing the helper functions.
# A full test suite would mock the entire script execution or its main components.

# Import the script to be tested (assuming it's in a location accessible by the test runner)
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cgi-detector-service', 'scripts')))
# from run_dataset_tests import sample_images, load_forensic_modules, analyze_image_with_module, classify_image, check_assertions, save_test_results # This import might need adjustment


class TestRunDatasetTestsScript(unittest.TestCase):

    def setUp(self):
        # Create dummy dataset directories and files for testing purposes
        self.test_dir = "./test_data_for_unit_tests"
        self.real_dir = os.path.join(self.test_dir, "real")
        self.fake_dir = os.path.join(self.test_dir, "fake")
        os.makedirs(self.real_dir, exist_ok=True)
        os.makedirs(self.fake_dir, exist_ok=True)

        # Create dummy image files
        with open(os.path.join(self.real_dir, "real_img_01.jpg"), "w") as f: f.write("dummy_real_content")
        with open(os.path.join(self.real_dir, "real_img_02.png"), "w") as f: f.write("dummy_real_content")
        with open(os.path.join(self.fake_dir, "fake_img_01.jpg"), "w") as f: f.write("dummy_fake_content")
        with open(os.path.join(self.fake_dir, "fake_img_02.png"), "w") as f: f.write("dummy_fake_content")
        with open(os.path.join(self.fake_dir, "fake_img_03.jpeg"), "w") as f: f.write("dummy_fake_content")

        # Mock the forensics directory and modules
        self.mock_forensics_dir = os.path.join(self.test_dir, "mock_forensics")
        os.makedirs(self.mock_forensics_dir, exist_ok=True)
        with open(os.path.join(self.mock_forensics_dir, "ela.py"), "w") as f: f.write("def analyze_ela(image_bytes): return 0.2") # Mock ELA, returns low score
        with open(os.path.join(self.mock_forensics_dir, "hos.py"), "w") as f: f.write("def analyze_hos(image_bytes): return 0.8") # Mock HOS, returns high score
        with open(os.path.join(self.mock_forensics_dir, "__init__.py"), "w") as f: f.write("")
        with open(os.path.join(self.mock_forensics_dir, "test_dummy.py"), "w") as f: f.write("def analyze_test_dummy(image_bytes): return 0.5") # Should be ignored

        # Adjust sys.path to include mock forensics for importlib
        # Note: Actual tests would use unittest.mock.patch for sys.path
        # For simplicity here, we are setting it directly, which might have side effects if not properly managed.
        self.original_sys_path = list(sys.path)
        sys.path.insert(0, self.mock_forensics_dir)

        # Mock the run_dataset_tests module itself to test its functions
        # This is complex. For now, we'll focus on testing standalone functions if possible.
        # A better approach is to import the script and test its functions, but we need to handle imports correctly.
        # For this example, we'll import the functions directly if they are exposed, or simulate them.

    def tearDown(self):
        # Clean up dummy directories and files
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # Restore original sys.path
        sys.path = self.original_sys_path

    # --- Test Cases for Helper Functions ---

    def test_load_forensic_modules(self):
        # This test requires direct access to the script's load_forensic_modules function
        # We'll need to import it or mock it. Let's assume it's importable for now.
        from run_dataset_tests import load_forensic_modules
        
        modules = load_forensic_modules(self.mock_forensics_dir)
        self.assertEqual(modules, ['ela', 'hos']) # Expecting ela and hos, excluding others

    def test_analyze_image_with_module(self):
        from run_dataset_tests import analyze_image_with_module

        # Test with a real image and ELA (mocked to return 0.2)
        score, error = analyze_image_with_module(os.path.join(self.real_dir, "real_img_01.jpg"), "ela")
        self.assertAlmostEqual(score, 0.2)
        self.assertIsNone(error)

        # Test with a fake image and HOS (mocked to return 0.8)
        score, error = analyze_image_with_module(os.path.join(self.fake_dir, "fake_img_01.jpg"), "hos")
        self.assertAlmostEqual(score, 0.8)
        self.assertIsNone(error)

        # Test with non-existent module
        score, error = analyze_image_with_module(os.path.join(self.real_dir, "real_img_01.jpg"), "non_existent_module")
        self.assertIsNone(score)
        self.assertIsNotNone(error)

        # Test with non-existent image
        score, error = analyze_image_with_module("non_existent_image.jpg", "ela")
        self.assertIsNone(score)
        self.assertIsNotNone(error)

    def test_check_assertions(self):
        from run_dataset_tests import check_assertions

        # Mock scores for a real image
        scores_real_good = {'ela': 0.1, 'hos': 0.3}
        modules_run = ['ela', 'hos']
        assertions_met, failed_assertions = check_assertions(scores_real_good, 'real', modules_run)
        self.assertTrue(assertions_met)
        self.assertEqual(len(failed_assertions), 0)

        # Mock scores for a fake image (failing assertions)
        scores_fake_bad = {'ela': 0.6, 'hos': 0.2}
        assertions_met, failed_assertions = check_assertions(scores_fake_bad, 'fake', modules_run)
        self.assertFalse(assertions_met)
        self.assertGreater(len(failed_assertions), 0)
        # Check for specific assertion failure message
        self.assertTrue(any("assertion failed for fake image" in msg for msg in failed_assertions))

        # Mock scores with a module failure
        scores_with_module_failure = {'ela': 0.1, 'hos': None}
        assertions_met, failed_assertions = check_assertions(scores_with_module_failure, 'real', modules_run)
        self.assertFalse(assertions_met)
        self.assertTrue(any("failed to produce a score" in msg for msg in failed_assertions))

    def test_classify_image(self):
        from run_dataset_tests import classify_image

        # Test a real image scenario
        scores_real_all_low = {'ela': 0.1, 'hos': 0.3}
        classification, is_correct = classify_image(scores_real_all_low, 'real', ['ela', 'hos'])
        self.assertEqual(classification, 'real')
        self.assertTrue(is_correct)

        # Test a fake image scenario (one score high)
        scores_fake_one_high = {'ela': 0.1, 'hos': 0.8}
        classification, is_correct = classify_image(scores_fake_one_high, 'fake', ['ela', 'hos'])
        self.assertEqual(classification, 'fake')
        self.assertTrue(is_correct)

        # Test misclassification scenario (real image classified as fake)
        scores_real_misclassified = {'ela': 0.6, 'hos': 0.7}
        classification, is_correct = classify_image(scores_real_misclassified, 'real', ['ela', 'hos'])
        self.assertEqual(classification, 'fake')
        self.assertFalse(is_correct)

        # Test misclassification scenario (fake image classified as real)
        scores_fake_misclassified = {'ela': 0.1, 'hos': 0.3}
        classification, is_correct = classify_image(scores_fake_misclassified, 'fake', ['ela', 'hos'])
        self.assertEqual(classification, 'real')
        self.assertFalse(is_correct)

        # Test with unknown classification (no valid scores)
        scores_unknown = {'ela': None, 'hos': None}
        classification, is_correct = classify_image(scores_unknown, 'real', ['ela', 'hos'])
        self.assertEqual(classification, 'unknown')
        self.assertFalse(is_correct)

    def test_sample_images(self):
        from run_dataset_tests import sample_images
        
        all_paths = [os.path.join(self.real_dir, f) for f in os.listdir(self.real_dir)] + \
                      [os.path.join(self.fake_dir, f) for f in os.listdir(self.fake_dir)]

        # Test sampling with None size (should return all)
        sampled_all = sample_images(all_paths, sample_size=None, strategy='stratified', is_real=None)
        self.assertEqual(len(sampled_all), len(all_paths))

        # Test sampling with size larger than available
        sampled_over = sample_images(all_paths, sample_size=100, strategy='stratified', is_real=None)
        self.assertEqual(len(sampled_over), len(all_paths))

        # Test random sampling
        sampled_random = sample_images(all_paths, sample_size=2, strategy='random', is_real=None)
        self.assertEqual(len(sampled_random), 2)
        # Ensure sampled items are from the original list
        for path in sampled_random:
            self.assertIn(path, all_paths)

        # Test stratified sampling (requires proper list separation)
        real_paths_only = [os.path.join(self.real_dir, f) for f in os.listdir(self.real_dir)]
        fake_paths_only = [os.path.join(self.fake_dir, f) for f in os.listdir(self.fake_dir)]

        sampled_stratified_real = sample_images(real_paths_only, sample_size=1, strategy='stratified', is_real=True)
        self.assertEqual(len(sampled_stratified_real), 1)
        self.assertTrue(sampled_stratified_real[0].startswith(self.real_dir))

        sampled_stratified_fake = sample_images(fake_paths_only, sample_size=1, strategy='stratified', is_real=False)
        self.assertEqual(len(sampled_stratified_fake), 1)
        self.assertTrue(sampled_stratified_fake[0].startswith(self.fake_dir))

        # Test fallback to random when is_real is None for stratified strategy
        sampled_stratified_fallback = sample_images(all_paths, sample_size=2, strategy='stratified', is_real=None)
        self.assertEqual(len(sampled_stratified_fallback), 2)
        for path in sampled_stratified_fallback:
            self.assertIn(path, all_paths)

    # NOTE: Testing save_test_results requires mocking file I/O operations.
    # Testing the main run_tests function would be more involved, requiring
    # mocking of file system access, module imports, and potentially subprocess calls.


if __name__ == '__main__':
    unittest.main()
