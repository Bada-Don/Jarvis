"""
Verification script for JARVIS Settings Interface setup

This script checks that all required dependencies and files are in place.
"""

import sys
import os
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and report the result."""
    if Path(path).exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {path}")
        return False

def check_directory_exists(path, description):
    """Check if a directory exists and report the result."""
    if Path(path).is_dir():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {path}")
        return False

def check_python_module(module_name):
    """Check if a Python module can be imported."""
    try:
        __import__(module_name)
        print(f"✓ Python module '{module_name}' is installed")
        return True
    except ImportError:
        print(f"✗ Python module '{module_name}' is NOT installed")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("JARVIS Settings Interface - Setup Verification")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check frontend structure
    print("Checking Frontend Structure...")
    print("-" * 60)
    all_checks_passed &= check_directory_exists("settings_ui", "Frontend directory")
    all_checks_passed &= check_file_exists("settings_ui/package.json", "Package.json")
    all_checks_passed &= check_file_exists("settings_ui/vite.config.ts", "Vite config")
    all_checks_passed &= check_file_exists("settings_ui/tailwind.config.js", "Tailwind config")
    all_checks_passed &= check_file_exists("settings_ui/postcss.config.js", "PostCSS config")
    all_checks_passed &= check_directory_exists("settings_ui/src", "Source directory")
    all_checks_passed &= check_file_exists("settings_ui/src/App.tsx", "App component")
    all_checks_passed &= check_file_exists("settings_ui/src/main.tsx", "Main entry point")
    all_checks_passed &= check_file_exists("settings_ui/src/index.css", "Global styles")
    print()
    
    # Check if frontend is built
    print("Checking Frontend Build...")
    print("-" * 60)
    if check_directory_exists("settings_ui/dist", "Build output directory"):
        check_file_exists("settings_ui/dist/index.html", "Built index.html")
    else:
        print("  ℹ Run 'npm run build' in settings_ui to create the build")
    print()
    
    # Check backend structure
    print("Checking Backend Structure...")
    print("-" * 60)
    all_checks_passed &= check_file_exists("local_client/settings_app.py", "Settings app backend")
    all_checks_passed &= check_file_exists("local_client/run_settings.py", "Launcher script")
    all_checks_passed &= check_file_exists("local_client/requirements.txt", "Requirements file")
    print()
    
    # Check Python dependencies
    print("Checking Python Dependencies...")
    print("-" * 60)
    all_checks_passed &= check_python_module("webview")
    all_checks_passed &= check_python_module("hypothesis")
    print()
    
    # Check Node modules
    print("Checking Node Dependencies...")
    print("-" * 60)
    if check_directory_exists("settings_ui/node_modules", "Node modules directory"):
        print("  ℹ Frontend dependencies are installed")
    else:
        print("  ℹ Run 'npm install' in settings_ui to install dependencies")
        all_checks_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_checks_passed:
        print("✓ All checks passed! Setup is complete.")
        print()
        print("Next steps:")
        print("  1. Build the frontend: cd settings_ui && npm run build")
        print("  2. Run the settings interface: python local_client/run_settings.py")
    else:
        print("✗ Some checks failed. Please review the output above.")
        print()
        print("Common fixes:")
        print("  - Install frontend dependencies: cd settings_ui && npm install")
        print("  - Install Python dependencies: pip install -r local_client/requirements.txt")
        print("  - Build the frontend: cd settings_ui && npm run build")
    print("=" * 60)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
