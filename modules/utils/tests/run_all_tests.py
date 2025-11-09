#!/usr/bin/env python3
"""
Unified test runner for all LF Nodes tests.
Discovers and runs tests from hierarchical directory structure.
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all tests using unittest discovery."""
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the modules directory to the path
    modules_dir = os.path.join(test_dir, '..', '..')
    sys.path.insert(0, modules_dir)

    # Apply selective mocking - enable torch for tests that need it
    # Individual test files can override this with their own mocking setup
    try:
        from modules.tests.common_mocks import setup_common_mocks
        # Don't apply global mocking - let individual tests manage their own mocking needs
        # setup_common_mocks(torch_enabled=True)  # Allow real torch usage by default
    except ImportError:
        # If common_mocks is not available, continue without mocking
        pass

    # Use unittest discovery to find all tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')

    # Count total tests before running
    total_tests = suite.countTestCases()
    print(f"Discovered {total_tests} tests in hierarchical structure")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*60)
    print("LF NODES TEST SUMMARY")
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
    success = run_all_tests()
    sys.exit(0 if success else 1)