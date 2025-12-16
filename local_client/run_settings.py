"""
Launcher script for JARVIS Settings Interface

This script launches the settings interface application.
It can be run in development mode or production mode.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from local_client.settings_app import main
except ImportError as e:
    print(f"Error: Failed to import settings_app module: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r local_client/requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting JARVIS Settings Interface...")
    main()
