#!/usr/bin/env python3
"""
Deployment Script

This script orchestrates the complete deployment process for the
FunctionGemma integration. It runs all necessary steps in sequence
and provides detailed feedback.

Usage:
    python deploy.py [--skip-tests] [--skip-model] [--production]

Options:
    --skip-tests     Skip running tests before deployment
    --skip-model     Skip model download (use existing model)
    --production     Deploy in production mode (default: development)
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


def run_script(script_name: str, args: list = None):
    """
    Run a deployment script.
    
    Args:
        script_name: Name of the script to run
        args: Additional arguments for the script
    """
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        logger.error(f"✗ Script not found: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Script failed: {script_name}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy FunctionGemma integration"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before deployment"
    )
    parser.add_argument(
        "--skip-model",
        action="store_true",
        help="Skip model download (use existing model)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Deploy in production mode"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("FunctionGemma Integration - Deployment")
    logger.info("=" * 60)
    logger.info("")
    
    # Step 1: Install dependencies
    logger.info("Step 1/4: Installing dependencies...")
    logger.info("-" * 60)
    if not run_script("install_dependencies.py"):
        logger.error("✗ Dependency installation failed")
        sys.exit(1)
    logger.info("✓ Dependencies installed")
    logger.info("")
    
    # Step 2: Download model (if not skipped)
    if not args.skip_model:
        logger.info("Step 2/4: Downloading model...")
        logger.info("-" * 60)
        if not run_script("download_model.py"):
            logger.warning("⚠ Model download failed (continuing anyway)")
        else:
            logger.info("✓ Model downloaded")
        logger.info("")
    else:
        logger.info("Step 2/4: Skipping model download")
        logger.info("")
    
    # Step 3: Run tests (if not skipped)
    if not args.skip_tests:
        logger.info("Step 3/4: Running tests...")
        logger.info("-" * 60)
        if not run_script("run_tests.py", ["--type", "unit"]):
            logger.error("✗ Tests failed")
            logger.error("")
            logger.error("Deployment aborted due to test failures")
            logger.error("Fix the issues and try again, or use --skip-tests")
            sys.exit(1)
        logger.info("✓ Tests passed")
        logger.info("")
    else:
        logger.info("Step 3/4: Skipping tests")
        logger.info("")
    
    # Step 4: Start service
    mode = "prod" if args.production else "dev"
    logger.info(f"Step 4/4: Starting service ({mode} mode)...")
    logger.info("-" * 60)
    logger.info("")
    
    # Note: This will block until service is stopped
    if not run_script("start_service.py", ["--mode", mode]):
        logger.error("✗ Service startup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
