#!/usr/bin/env python3
"""
Comprehensive test runner for all helper function test suites.
Run this to verify all helper functions work correctly.
Tests are run in alphabetical order by category.
"""

import unittest
import sys
import os

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def run_all_helper_tests():
    """Run all helper test suites in alphabetical order."""
    # Import test classes in alphabetical order
    test_classes = []

    # API helpers (completed)
    try:
        from test_api_helpers import TestAPIHelpers
        test_classes.append(TestAPIHelpers)
        print("✓ Loaded API helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load API helpers: {e}")

    # Comfy helpers (completed)
    try:
        from test_comfy_helpers import TestComfyHelpers
        test_classes.append(TestComfyHelpers)
        print("✓ Loaded Comfy helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Comfy helpers: {e}")

    # Conversion helpers (existing)
    try:
        from test_conversion_helpers import TestConversionHelpers
        test_classes.append(TestConversionHelpers)
        print("✓ Loaded Conversion helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Conversion helpers: {e}")

    # Detection helpers (existing)
    try:
        from test_detection_helpers import TestDetectionHelpers
        test_classes.append(TestDetectionHelpers)
        print("✓ Loaded Detection helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Detection helpers: {e}")

    # Editing helpers (completed)
    try:
        from test_editing_helpers import TestEditingHelpers
        test_classes.append(TestEditingHelpers)
        print("✓ Loaded Editing helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Editing helpers: {e}")

    # Logic helpers (existing)
    try:
        from test_logic_helpers import TestLogicHelpers
        test_classes.append(TestLogicHelpers)
        print("✓ Loaded Logic helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Logic helpers: {e}")

    # Torch helpers (existing)
    try:
        from test_torch_helpers import TestTorchHelpers
        test_classes.append(TestTorchHelpers)
        print("✓ Loaded Torch helpers tests")
    except ImportError as e:
        print(f"✗ Failed to load Torch helpers: {e}")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    print("HELPER FUNCTIONS TEST SUMMARY")
    print("="*60)
    print(f"Total tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_helper_tests()
    sys.exit(0 if success else 1)