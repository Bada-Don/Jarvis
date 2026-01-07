#!/usr/bin/env python3
"""
Launcher script for JARVIS Settings Interface

This script provides a convenient way to launch the settings interface
with optional development mode support.
"""

import sys
import argparse
from pathlib import Path

# Add the local_client directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import main


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Launch JARVIS Settings Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_settings.py              # Launch in production mode
  python run_settings.py --dev        # Launch in development mode with debug output
  python run_settings.py --check      # Check dependencies without launching
  python run_settings.py --help       # Show this help message

Development Mode:
  In development mode (--dev), the application will:
  - Enable debug output in PyWebView
  - Attempt to connect to Vite dev server (http://localhost:5173)
  - Fall back to production build if dev server is not running
  
  To use hot reload:
  1. In a separate terminal, run: cd settings_ui && npm run dev
  2. Then run: python run_settings.py --dev
        """
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode with debug output and hot reload support'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if all dependencies are installed without launching the app'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='JARVIS Settings Interface v1.0.0',
        help='Show version information'
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking dependencies...")
    
    missing_deps = []
    
    # Check Python modules
    required_modules = [
        ('webview', 'pywebview'),
        ('config_manager', None),
        ('prompt_manager', None),
        ('validation_service', None),
    ]
    
    for module_name, pip_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except ImportError:
            print(f"  ✗ {module_name}")
            missing_deps.append(pip_name or module_name)
    
    # Check required files
    project_root = Path(__file__).parent.parent
    required_files = [
        'local_client/config.py',
        'local_client/config_manager.py',
        'local_client/prompt_manager.py',
        'local_client/validation_service.py',
        'backend/planner_service.py',
        'local_client/vision_service.py',
    ]
    
    print("\nChecking required files...")
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path}")
            missing_files.append(file_path)
    
    # Check frontend build
    print("\nChecking frontend build...")
    frontend_path = project_root / "settings_ui" / "dist"
    if frontend_path.exists():
        print(f"  ✓ Frontend built at {frontend_path}")
    else:
        print(f"  ✗ Frontend not built")
        print("\n  To build the frontend:")
        print("    cd settings_ui")
        print("    npm install")
        print("    npm run build")
    
    # Summary
    print("\n" + "=" * 60)
    if missing_deps or missing_files or not frontend_path.exists():
        print("DEPENDENCY CHECK FAILED")
        print("=" * 60)
        
        if missing_deps:
            print("\nMissing Python packages:")
            for dep in missing_deps:
                print(f"  - {dep}")
            print("\nInstall with: pip install " + " ".join(missing_deps))
        
        if missing_files:
            print("\nMissing required files:")
            for file in missing_files:
                print(f"  - {file}")
        
        if not frontend_path.exists():
            print("\nFrontend needs to be built (see instructions above)")
        
        return False
    else:
        print("ALL DEPENDENCIES OK")
        print("=" * 60)
        return True


if __name__ == "__main__":
    args = parse_args()
    
    # Handle check mode
    if args.check:
        success = check_dependencies()
        sys.exit(0 if success else 1)
    
    # Launch the application with dev mode flag
    try:
        main(dev_mode=args.dev)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except ImportError as e:
        print(f"\nMissing dependency: {e}")
        print("\nRun with --check to see all missing dependencies:")
        print("  python run_settings.py --check")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nRequired file not found: {e}")
        print("\nRun with --check to verify all required files:")
        print("  python run_settings.py --check")
        sys.exit(1)
    except Exception as e:
        print(f"\nFailed to launch settings interface: {e}")
        print("\nTroubleshooting steps:")
        print("  1. Check dependencies: python run_settings.py --check")
        print("  2. Ensure frontend is built: cd settings_ui && npm run build")
        print("  3. Check that config files are not corrupted")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        sys.exit(1)
