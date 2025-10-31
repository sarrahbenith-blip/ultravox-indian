#!/usr/bin/env python3
"""Test runner for all unit tests."""

import sys
import subprocess

# Test files to run
TEST_FILES = [
    "tests/unit/test_validator.py",
    "tests/unit/test_agent_storage.py",
    "tests/unit/test_cost_calculator.py",
]


def run_tests():
    """Run all unit tests."""
    print("=" * 80)
    print("Running Unit Tests for Ultravox Indian Platform")
    print("=" * 80)

    failed = []
    passed = []

    for test_file in TEST_FILES:
        print(f"\n{'=' * 80}")
        print(f"Running: {test_file}")
        print("=" * 80)

        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
            cwd="/workspace/cmhd1n92h004kr7im2isekfrs/ultravox-indian",
        )

        if result.returncode == 0:
            passed.append(test_file)
        else:
            failed.append(test_file)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {len(passed)}/{len(TEST_FILES)}")
    if passed:
        for test_file in passed:
            print(f"  ✓ {test_file}")

    if failed:
        print(f"\nFailed: {len(failed)}/{len(TEST_FILES)}")
        for test_file in failed:
            print(f"  ✗ {test_file}")
        return 1

    print("\n✓ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
