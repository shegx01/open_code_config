#!/usr/bin/env python3
"""
Test runner for debugger agent generator tests.

This script runs all unit and integration tests for the debugger agent generator.
"""

import sys
import unittest
from pathlib import Path

# Add the parent directory to the path to import test modules
sys.path.insert(0, str(Path(__file__).parent))

def run_all_tests():
    """Run all unit and integration tests."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print(f"SKIPPED: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.splitlines()[-1] if traceback else 'Unknown failure'}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.splitlines()[-1] if traceback else 'Unknown error'}")
    
    print(f"{'='*60}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

def run_unit_tests():
    """Run only unit tests."""
    loader = unittest.TestLoader()
    suite = loader.discover(Path(__file__).parent / 'unit', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def run_integration_tests():
    """Run only integration tests."""
    loader = unittest.TestLoader()
    suite = loader.discover(Path(__file__).parent / 'integration', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'unit':
            success = run_unit_tests()
        elif sys.argv[1] == 'integration':
            success = run_integration_tests()
        else:
            print(f"Unknown test type: {sys.argv[1]}")
            print("Usage: python run_tests.py [unit|integration]")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
