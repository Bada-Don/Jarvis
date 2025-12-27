#!/usr/bin/env python3
"""
Download FunctionGemma Model Script

This script downloads the FunctionGemma-270M model from Hugging Face
and saves it to the local models directory for offline use.

Usage:
    python download_model.py [--model-path PATH] [--force]

Options:
    --model-path PATH   Custom path to save model (default: ./local_models/functiongemma-270m-it)
    --force            Force re-download even if model exists
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import transformers
        import torch
        logger.info("✓ Dependencies found: transformers, torch")
        return True
    except ImportError as e:
        logger.error(
            f"✗ Missing dependencies: {e}\n"
            f"Please install with: pip install transformers torch"
        )
        return False


def download_model(model_path: str, force: bool = False):
    """
    Download FunctionGemma model from Hugging Face.
    
    Args:
        model_path: Path to save the model
        force: Force re-download even if model exists
    """
    # Check if model already exists
    model_dir = Path(model_path)
    if model_dir.exists() and not force:
        logger.info(f"Model already exists at: {model_path}")
        logger.info("Use --force to re-download")
        return True
    
    # Create directory if it doesn't exist
    model_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        
        logger.info("=" * 60)
        logger.info("Downloading FunctionGemma-270M Model")
        logger.info("=" * 60)
        logger.info(f"Model: google/functiongemma-270m-it")
        logger.info(f"Destination: {model_path}")
        logger.info("")
        
        # Download processor
        logger.info("Step 1/2: Downloading AutoProcessor...")
        processor = AutoProcessor.from_pretrained(
            "google/functiongemma-270m-it",
            cache_dir=model_path
        )
        logger.info("✓ AutoProcessor downloaded")
        
        # Download model
        logger.info("Step 2/2: Downloading model (this may take a few minutes)...")
        model = AutoModelForCausalLM.from_pretrained(
            "google/functiongemma-270m-it",
            cache_dir=model_path
        )
        logger.info("✓ Model downloaded")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ Download Complete!")
        logger.info("=" * 60)
        logger.info(f"Model saved to: {model_path}")
        logger.info("")
        logger.info("You can now use the model offline by setting:")
        logger.info(f"  model_path='{model_path}'")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Download failed: {e}")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Check internet connection")
        logger.error("  2. Verify Hugging Face access")
        logger.error("  3. Check disk space (model is ~500MB)")
        logger.error("  4. Try again with --force flag")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download FunctionGemma-270M model for offline use"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default="./local_models/functiongemma-270m-it",
        help="Path to save model (default: ./local_models/functiongemma-270m-it)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if model exists"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Download model
    success = download_model(args.model_path, args.force)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
