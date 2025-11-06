#!/usr/bin/env python3
"""
Comprehensive test runner for all helper function test suites.
Run this to verify all helper functions work correctly.
"""

import unittest
import sys
import os

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def run_all_helper_tests():
    """Run all helper test suites."""
    # Import test classes
    from test_logic_helpers import TestLogicHelpers
    from test_conversion_helpers import TestConversionHelpers
    from test_torch_helpers import TestTorchHelpers
    from test_detection_helpers import TestDetectionHelpers

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLogicHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestConversionHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestTorchHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestDetectionHelpers))

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

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"Success rate: {success_rate:.1f}%")
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_helper_tests()
    sys.exit(0 if success else 1)