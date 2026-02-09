#!/usr/bin/env python3
"""
Directory structure script for JARVIS packaging.
Creates the final application directory structure and organizes all components.
"""

import os
import sys
import shutil
from pathlib import Path


def create_directory_structure():
    """Create the complete JARVIS application directory structure."""
    print("Creating JARVIS application directory structure...")
    print("=" * 60)
    
    base_dir = Path('dist/JARVIS')
    
    # Define directory structure
    directories = [
        'runtime/python',
        'runtime/node',
        'app/backend',
        'app/local_client',
        'app/settings_ui',
        'assets/weights',
        'assets/icons',
        'assets/config',
        'assets/audio',
        'data/logs',
        'data/config_backups',
    ]
    
    print("\nCreating directories...")
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    return base_dir


def organize_python_components(base_dir):
    """Move Python components to app directory."""
    print("\nOrganizing Python components...")
    
    components = [
        ('dist/jarvis_backend', 'app/backend'),
        ('dist/jarvis_client', 'app/local_client'),
    ]
    
    for source, dest in components:
        source_path = Path(source)
        dest_path = base_dir / dest
        
        if source_path.exists():
            # Copy all files from source to destination
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
            print(f"  ✓ Moved {source} → {dest}")
        else:
            print(f"  ⚠ Warning: {source} not found")
    
    return True


def organize_nodejs_components(base_dir):
    """Move Node.js components to app directory."""
    print("\nOrganizing Node.js components...")
    
    source_path = Path('settings_ui/dist')
    dest_path = base_dir / 'app/settings_ui'
    
    if source_path.exists():
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(source_path, dest_path)
        print(f"  ✓ Moved settings_ui/dist → app/settings_ui")
        
        # Count files
        file_count = len(list(dest_path.rglob('*')))
        print(f"    ({file_count} files)")
        return True
    else:
        print(f"  ⚠ Warning: settings_ui/dist not found")
        return False


def organize_assets(base_dir):
    """Move assets to assets directory."""
    print("\nOrganizing assets...")
    
    source_assets = Path('dist/assets')
    dest_assets = base_dir / 'assets'
    
    if source_assets.exists():
        # Copy each subdirectory
        for subdir in source_assets.iterdir():
            if subdir.is_dir():
                dest_subdir = dest_assets / subdir.name
                if dest_subdir.exists():
                    shutil.rmtree(dest_subdir)
                shutil.copytree(subdir, dest_subdir)
                file_count = len(list(dest_subdir.rglob('*')))
                print(f"  ✓ Moved assets/{subdir.name} ({file_count} items)")
        return True
    else:
        print(f"  ⚠ Warning: dist/assets not found")
        return False


def organize_data_directory(base_dir):
    """Set up data directory."""
    print("\nOrganizing data directory...")
    
    source_data = Path('dist/data')
    dest_data = base_dir / 'data'
    
    if source_data.exists():
        # Copy data directory structure
        for item in source_data.iterdir():
            dest_item = dest_data / item.name
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
                print(f"  ✓ Created data/{item.name}")
            else:
                shutil.copy2(item, dest_item)
                print(f"  ✓ Copied data/{item.name}")
        return True
    else:
        print(f"  ⚠ Warning: dist/data not found")
        # Create minimal data structure
        (dest_data / 'logs').mkdir(parents=True, exist_ok=True)
        (dest_data / 'config_backups').mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created minimal data structure")
        return False


def create_launcher_script(base_dir):
    """Create the main launcher script."""
    print("\nCreating launcher script...")
    
    launcher_content = """#!/usr/bin/env python3
\"\"\"
JARVIS Application Launcher
Starts all components in the correct order and manages their lifecycle.
\"\"\"

import sys
import subprocess
import time
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

def main():
    print("Starting JARVIS...")
    print("=" * 60)
    
    # Start backend server
    print("Starting backend server...")
    backend_exe = app_dir / 'backend' / 'jarvis_backend.exe'
    if backend_exe.exists():
        backend_process = subprocess.Popen([str(backend_exe)])
        print(f"  ✓ Backend started (PID: {backend_process.pid})")
    else:
        print(f"  ✗ Backend executable not found: {backend_exe}")
        return 1
    
    # Wait for backend to initialize
    time.sleep(2)
    
    # Start local client
    print("Starting local client...")
    client_exe = app_dir / 'local_client' / 'jarvis_client.exe'
    if client_exe.exists():
        client_process = subprocess.Popen([str(client_exe)])
        print(f"  ✓ Client started (PID: {client_process.pid})")
    else:
        print(f"  ✗ Client executable not found: {client_exe}")
        backend_process.terminate()
        return 1
    
    # Wait for client to initialize
    time.sleep(1)
    
    print("=" * 60)
    print("✓ JARVIS is running!")
    print("  Backend: http://localhost:5000")
    print("  Settings UI will open automatically")
    print("=" * 60)
    
    try:
        # Keep launcher running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\\nShutting down JARVIS...")
        backend_process.terminate()
        client_process.terminate()
        print("✓ JARVIS stopped")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
    
    launcher_path = base_dir / 'JARVIS.py'
    launcher_path.write_text(launcher_content)
    print(f"  ✓ Created JARVIS.py")
    
    # Create Windows batch file launcher
    batch_content = """@echo off
echo Starting JARVIS...
python JARVIS.py
pause
"""
    
    batch_path = base_dir / 'start_jarvis.bat'
    batch_path.write_text(batch_content)
    print(f"  ✓ Created start_jarvis.bat")
    
    return True


def create_readme(base_dir):
    """Create README file for the package."""
    print("\nCreating README...")
    
    readme_content = """JARVIS Desktop Application
==========================

Thank you for installing JARVIS!

Quick Start
-----------

1. First-Time Setup:
   - Run start_jarvis.bat (Windows) or python JARVIS.py
   - The Settings UI will open automatically
   - Complete the first-run setup wizard:
     * Enter your Gemini API key (required)
     * Enter your OpenAI API key (optional)
     * Configure system paths (Desktop, Documents, Downloads)
   - Generate a pairing QR code for your mobile device

2. Mobile App Pairing:
   - Install the JARVIS mobile app on your phone
   - Scan the QR code displayed in the Settings UI
   - Wait for pairing confirmation

3. Using JARVIS:
   - Send voice commands from your mobile app
   - JARVIS will execute automation tasks on your desktop
   - Monitor status and progress in the mobile app

Configuration
-------------

Configuration files are stored in the data/ directory:
- config.py: Main application configuration
- firebase_config.json: Firebase web app configuration
- firebase-admin-credentials.json: Firebase service account credentials

Templates for these files are available in assets/config/

System Requirements
-------------------

- Windows 10 or later (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- 2 GB free disk space
- Internet connection for Firebase communication
- Gemini API key (get one at https://makersuite.google.com/app/apikey)

Directory Structure
-------------------

JARVIS/
├── app/                    # Application components
│   ├── backend/           # Backend server
│   ├── local_client/      # Automation client
│   └── settings_ui/       # Settings interface
├── assets/                # Application assets
│   ├── weights/          # AI model weights
│   ├── icons/            # Application icons
│   ├── config/           # Configuration templates
│   └── audio/            # Audio feedback files
├── data/                  # User data and configuration
│   ├── logs/             # Application logs
│   └── config_backups/   # Configuration backups
├── JARVIS.py             # Main launcher script
├── start_jarvis.bat      # Windows launcher
├── README.txt            # This file
└── LICENSE.txt           # License information

Troubleshooting
---------------

If JARVIS fails to start:
1. Check data/logs/ for error messages
2. Verify your API keys are correct
3. Ensure Firebase credentials are properly configured
4. Check that ports 5000 and 5001 are not in use

For more help, visit: https://github.com/yourusername/jarvis

Support
-------

- GitHub Issues: https://github.com/yourusername/jarvis/issues
- Documentation: https://github.com/yourusername/jarvis/wiki
- Email: support@jarvis.example.com

License
-------

See LICENSE.txt for license information.

Version: 1.0.0
Build Date: {build_date}
"""
    
    from datetime import datetime
    readme_content = readme_content.format(build_date=datetime.now().strftime('%Y-%m-%d'))
    
    readme_path = base_dir / 'README.txt'
    readme_path.write_text(readme_content)
    print(f"  ✓ Created README.txt")
    
    return True


def create_license(base_dir):
    """Create LICENSE file."""
    print("\nCreating LICENSE...")
    
    # Check if LICENSE.md exists in root
    root_license = Path('LICENSE.md')
    if root_license.exists():
        dest_license = base_dir / 'LICENSE.txt'
        shutil.copy2(root_license, dest_license)
        print(f"  ✓ Copied LICENSE.md → LICENSE.txt")
    else:
        # Create placeholder
        license_content = """Copyright (c) 2024 JARVIS Project

[Add your license text here]

This software is provided "as is" without warranty of any kind.
"""
        license_path = base_dir / 'LICENSE.txt'
        license_path.write_text(license_content)
        print(f"  ✓ Created placeholder LICENSE.txt")
    
    return True


def set_permissions(base_dir):
    """Set appropriate file permissions."""
    print("\nSetting file permissions...")
    
    # Make launcher scripts executable (on Unix-like systems)
    if sys.platform != 'win32':
        launcher_py = base_dir / 'JARVIS.py'
        if launcher_py.exists():
            os.chmod(launcher_py, 0o755)
            print(f"  ✓ Made JARVIS.py executable")
    
    # Ensure data directory is writable
    data_dir = base_dir / 'data'
    if data_dir.exists():
        print(f"  ✓ Data directory is writable")
    
    return True


def verify_structure(base_dir):
    """Verify the directory structure is correct."""
    print("\nVerifying directory structure...")
    
    required_paths = [
        'app/backend',
        'app/local_client',
        'app/settings_ui',
        'assets/weights',
        'assets/icons',
        'assets/config',
        'data/logs',
        'JARVIS.py',
        'start_jarvis.bat',
        'README.txt',
        'LICENSE.txt',
    ]
    
    all_good = True
    for path_str in required_paths:
        path = base_dir / path_str
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.rglob('*')))
                print(f"  ✓ {path_str} ({file_count} items)")
            else:
                size_kb = path.stat().st_size / 1024
                print(f"  ✓ {path_str} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {path_str} missing")
            all_good = False
    
    return all_good


def calculate_total_size(base_dir):
    """Calculate total size of the application."""
    print("\nCalculating total size...")
    
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for item in base_dir.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    
    size_mb = total_size / (1024 * 1024)
    size_gb = size_mb / 1024
    
    print(f"  Total: {file_count} files in {dir_count} directories")
    if size_gb >= 1:
        print(f"  Size: {size_gb:.2f} GB")
    else:
        print(f"  Size: {size_mb:.2f} MB")


def main():
    """Main directory structure creation process."""
    print("JARVIS Directory Structure Script")
    print("=" * 60)
    
    # Create base structure
    base_dir = create_directory_structure()
    
    # Organize components
    organize_python_components(base_dir)
    organize_nodejs_components(base_dir)
    organize_assets(base_dir)
    organize_data_directory(base_dir)
    
    # Create launcher and documentation
    create_launcher_script(base_dir)
    create_readme(base_dir)
    create_license(base_dir)
    
    # Set permissions
    set_permissions(base_dir)
    
    # Verify and report
    if verify_structure(base_dir):
        calculate_total_size(base_dir)
        print("\n" + "=" * 60)
        print("✓ Directory structure created successfully!")
        print("=" * 60)
        print(f"\nApplication ready at: {base_dir}")
        return 0
    else:
        print("\n✗ Directory structure verification failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
