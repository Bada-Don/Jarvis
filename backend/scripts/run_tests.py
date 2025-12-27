#!/usr/bin/env python3
"""
Run Tests Script

This script runs the test suite for the FunctionGemma integration.
It supports different test types and provides detailed reporting.

Usage:
    python run_tests.py [--type TYPE] [--coverage] [--verbose]

Options:
    --type TYPE      Test type: all, unit, property, integration (default: all)
    --coverage       Generate coverage report
    --verbose        Verbose output
    --fast           Skip slow tests (property tests with many iterations)
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_pytest():
    """Check if pytest is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ pytest available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        logger.error("✗ pytest not found")
        logger.error("Install with: pip install pytest pytest-cov hypothesis")
        return False


def run_tests(test_type: str, coverage: bool, verbose: bool, fast: bool):
    """
    Run tests based on type.
    
    Args:
        test_type: Type of tests to run (all, unit, property, integration)
        coverage: Whether to generate coverage report
        verbose: Whether to use verbose output
        fast: Whether to skip slow tests
    """
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test selection based on type
    if test_type == "unit":
        cmd.extend(["-m", "not property_test and not integration_test"])
    elif test_type == "property":
        cmd.extend(["-m", "property_test"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration_test"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        logger.error(f"Unknown test type: {test_type}")
        return False
    
    # Add fast mode (skip slow tests)
    if fast:
        cmd.extend(["-m", "not slow"])
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add test directory
    cmd.append(".")
    
    logger.info("")
    logger.info("Running tests...")
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info("-" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,  # Run from backend directory
            check=False
        )
        
        logger.info("-" * 60)
        
        if result.returncode == 0:
            logger.info("✓ All tests passed!")
            if coverage:
                logger.info("")
                logger.info("Coverage report generated:")
                logger.info("  HTML: backend/htmlcov/index.html")
            return True
        else:
            logger.error("✗ Some tests failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Test execution failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run tests for FunctionGemma integration"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["all", "unit", "property", "integration"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (property tests with many iterations)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("FunctionGemma Integration - Test Suite")
    logger.info("=" * 60)
    logger.info(f"Test type: {args.type}")
    logger.info(f"Coverage: {args.coverage}")
    logger.info(f"Verbose: {args.verbose}")
    logger.info(f"Fast mode: {args.fast}")
    
    # Check pytest
    if not check_pytest():
        sys.exit(1)
    
    # Run tests
    success = run_tests(args.type, args.coverage, args.verbose, args.fast)
    
    if success:
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Test Suite Complete")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("")
        logger.error("=" * 60)
        logger.error("✗ Test Suite Failed")
        logger.error("=" * 60)
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Check test output above for specific failures")
        logger.error("  2. Run with --verbose for more details")
        logger.error("  3. Run specific test type (--type unit/property/integration)")
        logger.error("  4. Check TROUBLESHOOTING.md for common issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
