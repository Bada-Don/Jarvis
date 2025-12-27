#!/usr/bin/env python3
"""
Install Dependencies Script

This script installs all required dependencies for the FunctionGemma integration.
It checks for existing installations and provides detailed progress feedback.

Usage:
    python install_dependencies.py [--upgrade] [--dev]

Options:
    --upgrade    Upgrade existing packages to latest versions
    --dev        Install development dependencies (testing, linting)
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


# Core dependencies
CORE_DEPENDENCIES = [
    "transformers>=4.35.0",
    "torch>=2.0.0",
    "flask>=2.3.0",
    "flask-cors>=4.0.0",
    "flask-socketio>=5.3.0",
    "python-socketio>=5.10.0",
    "eventlet>=0.33.0",
    "pyautogui>=0.9.54",
    "pillow>=10.0.0",
    "opencv-python>=4.8.0",
    "ultralytics>=8.0.0",
    "python-dotenv>=1.0.0",
    "psutil>=5.9.0",
]

# Development dependencies
DEV_DEPENDENCIES = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "hypothesis>=6.90.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
]


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error(
            f"✗ Python 3.8+ required (found {version.major}.{version.minor})"
        )
        return False
    
    logger.info(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_pip():
    """Check if pip is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ pip available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        logger.error("✗ pip not found")
        return False


def install_package(package: str, upgrade: bool = False):
    """
    Install a single package.
    
    Args:
        package: Package specification (e.g., "torch>=2.0.0")
        upgrade: Whether to upgrade if already installed
    """
    cmd = [sys.executable, "-m", "pip", "install"]
    
    if upgrade:
        cmd.append("--upgrade")
    
    cmd.append(package)
    
    try:
        logger.info(f"Installing {package}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ {package} installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to install {package}")
        logger.error(f"  Error: {e.stderr}")
        return False


def install_dependencies(packages: list, upgrade: bool = False):
    """
    Install a list of packages.
    
    Args:
        packages: List of package specifications
        upgrade: Whether to upgrade existing packages
    """
    success_count = 0
    fail_count = 0
    
    for package in packages:
        if install_package(package, upgrade):
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count


def verify_installation():
    """Verify that key packages are importable."""
    logger.info("")
    logger.info("Verifying installation...")
    
    packages_to_verify = [
        ("transformers", "Transformers"),
        ("torch", "PyTorch"),
        ("flask", "Flask"),
        ("pyautogui", "PyAutoGUI"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("dotenv", "python-dotenv"),
        ("psutil", "psutil"),
    ]
    
    all_ok = True
    for module_name, display_name in packages_to_verify:
        try:
            __import__(module_name)
            logger.info(f"✓ {display_name} importable")
        except ImportError:
            logger.error(f"✗ {display_name} not importable")
            all_ok = False
    
    return all_ok


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Install dependencies for FunctionGemma integration"
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade existing packages to latest versions"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("FunctionGemma Integration - Dependency Installation")
    logger.info("=" * 60)
    logger.info("")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    logger.info("")
    logger.info("Installing core dependencies...")
    logger.info("-" * 60)
    
    # Install core dependencies
    core_success, core_fail = install_dependencies(CORE_DEPENDENCIES, args.upgrade)
    
    # Install dev dependencies if requested
    dev_success, dev_fail = 0, 0
    if args.dev:
        logger.info("")
        logger.info("Installing development dependencies...")
        logger.info("-" * 60)
        dev_success, dev_fail = install_dependencies(DEV_DEPENDENCIES, args.upgrade)
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Installation Summary")
    logger.info("=" * 60)
    logger.info(f"Core packages: {core_success} succeeded, {core_fail} failed")
    if args.dev:
        logger.info(f"Dev packages: {dev_success} succeeded, {dev_fail} failed")
    
    # Verify installation
    if core_fail == 0 and (not args.dev or dev_fail == 0):
        if verify_installation():
            logger.info("")
            logger.info("✓ All dependencies installed successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Download model: python scripts/download_model.py")
            logger.info("  2. Run tests: python scripts/run_tests.py")
            logger.info("  3. Start service: python scripts/start_service.py")
            sys.exit(0)
        else:
            logger.error("")
            logger.error("✗ Some packages failed verification")
            sys.exit(1)
    else:
        logger.error("")
        logger.error("✗ Some packages failed to install")
        logger.error("Please check the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
