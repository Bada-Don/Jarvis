#!/usr/bin/env python3
"""
Build script for Python components using PyInstaller.
Bundles backend and local_client with all dependencies.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """Remove previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}...")
        spec_file.unlink()


def create_backend_spec():
    """Create PyInstaller spec file for backend server."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/weights', 'weights'),
        ('backend/.env.example', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'flask_socketio',
        'eventlet',
        'eventlet.wsgi',
        'eventlet.green',
        'dns',
        'dns.resolver',
        'google.genai',
        'openai',
        'firebase_admin',
        'ultralytics',
        'cv2',
        'PIL',
        'torch',
        'torchvision',
        'pyautogui',
        'pytesseract',
        'pygetwindow',
        'pygame',
        'easyocr',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='jarvis_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='jarvis_backend',
)
"""
    
    with open('backend.spec', 'w') as f:
        f.write(spec_content)
    print("Created backend.spec")


def create_local_client_spec():
    """Create PyInstaller spec file for local client."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['local_client/client.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('local_client/config.json.example', '.'),
        ('local_client/flexisign_config.json.example', '.'),
        ('local_client/assets', 'assets'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'pyautogui',
        'PIL',
        'pygame',
        'socketio',
        'websocket',
        'flask_socketio',
        'easyocr',
        'win32api',
        'win32con',
        'win32gui',
        'comtypes',
        'comtypes.client',
        'uiautomation',
        'watchdog',
        'psutil',
        'google.genai',
        'pywebview',
        'hypothesis',
        'firebase_admin',
        'qrcode',
        'pystray',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='jarvis_client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='jarvis_client',
)
"""
    
    with open('local_client.spec', 'w') as f:
        f.write(spec_content)
    print("Created local_client.spec")


def build_component(spec_file, component_name):
    """Build a component using PyInstaller."""
    print(f"\n{'='*60}")
    print(f"Building {component_name}...")
    print(f"{'='*60}\n")
    
    try:
        subprocess.run(
            ['pyinstaller', '--clean', spec_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✓ {component_name} built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build {component_name}")
        print(f"Error: {e.stderr}")
        return False


def verify_build():
    """Verify that build artifacts were created."""
    required_dirs = [
        'dist/jarvis_backend',
        'dist/jarvis_client',
    ]
    
    required_files = [
        'dist/jarvis_backend/jarvis_backend.exe',
        'dist/jarvis_client/jarvis_client.exe',
    ]
    
    print("\nVerifying build artifacts...")
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} exists")
        else:
            print(f"✗ {dir_path} missing")
            all_good = False
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"✓ {file_path} exists ({size_mb:.1f} MB)")
        else:
            print(f"✗ {file_path} missing")
            all_good = False
    
    return all_good


def main():
    """Main build process."""
    print("JARVIS Python Components Build Script")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(['pyinstaller', '--version'], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create spec files
    create_backend_spec()
    create_local_client_spec()
    
    # Build components
    backend_success = build_component('backend.spec', 'Backend Server')
    client_success = build_component('local_client.spec', 'Local Client')
    
    # Verify builds
    if backend_success and client_success:
        if verify_build():
            print("\n" + "=" * 60)
            print("✓ All Python components built successfully!")
            print("=" * 60)
            print("\nBuild artifacts located in:")
            print("  - dist/jarvis_backend/")
            print("  - dist/jarvis_client/")
            return 0
        else:
            print("\n✗ Build verification failed")
            return 1
    else:
        print("\n✗ Build failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
