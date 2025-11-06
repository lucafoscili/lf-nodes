#!/usr/bin/env python3
"""
Unified test runner for all LF Nodes helper function tests.
Runs tests alphabetically by category.
"""

import unittest
import sys
import os

# Add the modules directory to the path so we can import test modules
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, '..', '..')
sys.path.insert(0, modules_dir)

def run_all_tests():
    """Run all helper function tests."""
    # Discover and run tests
    loader = unittest.TestLoader()

    # Test categories in alphabetical order
    test_modules = [
        'test_api_helpers',
        'test_comfy_helpers',
        # Add more as they are completed:
        # 'test_editing_helpers',
        # 'test_logic_helpers',
        # etc.
    ]

    suite = unittest.TestSuite()

    for module_name in test_modules:
        try:
            module = __import__(f'modules.utils.tests.{module_name}', fromlist=[module_name])
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
            print(f"✓ Loaded {module_suite.countTestCases()} tests from {module_name}")
        except ImportError as e:
            print(f"✗ Failed to load {module_name}: {e}")
            continue

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)

    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Total tests run: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success rate: {((total_tests - failures - errors) / total_tests * 100):.1f}%" if total_tests > 0 else "No tests run")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)