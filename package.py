#!/usr/bin/env python3
"""
Main packaging script for JARVIS Desktop Application.
Orchestrates all build steps, generates version information, creates ZIP archive,
and validates package contents.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from pathlib import Path
from datetime import datetime


VERSION = "1.0.0"
BUILD_DATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_step(step_num, total_steps, description):
    """Print a step indicator."""
    print(f"\n[Step {step_num}/{total_steps}] {description}")
    print("-" * 70)


def check_prerequisites():
    """Check that all required tools are installed."""
    print_header("Checking Prerequisites")
    
    required_tools = [
        ('python', '--version', 'Python'),
        ('pyinstaller', '--version', 'PyInstaller'),
        ('node', '--version', 'Node.js'),
        ('npm', '--version', 'npm'),
    ]
    
    all_good = True
    for tool, version_arg, name in required_tools:
        try:
            result = subprocess.run(
                [tool, version_arg],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            version = result.stdout.strip().split('\n')[0]
            print(f"  ✓ {name}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ✗ {name} not found")
            all_good = False
    
    if not all_good:
        print("\n✗ Missing required tools. Please install them and try again.")
        return False
    
    print("\n✓ All prerequisites satisfied")
    return True


def clean_previous_builds():
    """Remove previous build artifacts."""
    print_header("Cleaning Previous Builds")
    
    dirs_to_clean = [
        'build',
        'dist',
        '__pycache__',
        'settings_ui/dist',
        'settings_ui/node_modules/.vite',
    ]
    
    files_to_clean = [
        '*.spec',
        'JARVIS-*.zip',
    ]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  Removing {dir_name}...")
            shutil.rmtree(dir_path)
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            print(f"  Removing {file_path}...")
            file_path.unlink()
    
    print("\n✓ Cleanup complete")
    return True


def run_build_script(script_name, description):
    """Run a build script and return success status."""
    print(f"\nRunning {script_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Print output
        print(result.stdout)
        
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            print(f"✗ {description} failed")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"✗ {script_name} not found")
        return False


def generate_version_info():
    """Generate version information file."""
    print_header("Generating Version Information")
    
    version_info = {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'build_timestamp': datetime.now().isoformat(),
        'python_version': sys.version.split()[0],
        'platform': sys.platform,
        'components': {
            'backend': 'jarvis_backend',
            'local_client': 'jarvis_client',
            'settings_ui': 'React + Vite',
        },
        'requirements': {
            'os': 'Windows 10 or later (64-bit)',
            'ram': '4 GB minimum (8 GB recommended)',
            'disk': '2 GB free space',
            'network': 'Internet connection required',
        }
    }
    
    version_file = Path('dist/JARVIS/version.json')
    version_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print(f"  ✓ Created version.json")
    print(f"    Version: {VERSION}")
    print(f"    Build Date: {BUILD_DATE}")
    
    return True


def create_zip_archive():
    """Create ZIP archive of the application."""
    print_header("Creating ZIP Archive")
    
    source_dir = Path('dist/JARVIS')
    if not source_dir.exists():
        print(f"  ✗ Source directory not found: {source_dir}")
        return False
    
    # Create archive name with version and date
    date_str = datetime.now().strftime('%Y%m%d')
    archive_name = f'JARVIS-{VERSION}-{date_str}.zip'
    archive_path = Path(archive_name)
    
    print(f"  Creating {archive_name}...")
    print(f"  This may take a few minutes...")
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            file_count = 0
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir.parent)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    
                    # Print progress every 100 files
                    if file_count % 100 == 0:
                        print(f"    Compressed {file_count} files...")
        
        # Get archive size
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        
        print(f"\n  ✓ Archive created successfully")
        print(f"    Files: {file_count}")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Location: {archive_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to create archive: {e}")
        return False


def validate_package():
    """Validate the package contents."""
    print_header("Validating Package")
    
    base_dir = Path('dist/JARVIS')
    
    # Define required files and directories
    required_items = [
        ('app/backend/jarvis_backend.exe', 'file', 'Backend executable'),
        ('app/local_client/jarvis_client.exe', 'file', 'Client executable'),
        ('app/settings_ui/index.html', 'file', 'Settings UI'),
        ('assets/config', 'dir', 'Configuration templates'),
        ('data/logs', 'dir', 'Logs directory'),
        ('JARVIS.py', 'file', 'Launcher script'),
        ('start_jarvis.bat', 'file', 'Windows launcher'),
        ('README.txt', 'file', 'README'),
        ('LICENSE.txt', 'file', 'License'),
        ('version.json', 'file', 'Version info'),
    ]
    
    print("Checking required files and directories...")
    all_good = True
    
    for item_path, item_type, description in required_items:
        full_path = base_dir / item_path
        
        if item_type == 'file':
            if full_path.exists() and full_path.is_file():
                size_kb = full_path.stat().st_size / 1024
                print(f"  ✓ {description}: {item_path} ({size_kb:.1f} KB)")
            else:
                print(f"  ✗ {description}: {item_path} MISSING")
                all_good = False
        
        elif item_type == 'dir':
            if full_path.exists() and full_path.is_dir():
                file_count = len(list(full_path.rglob('*')))
                print(f"  ✓ {description}: {item_path} ({file_count} items)")
            else:
                print(f"  ✗ {description}: {item_path} MISSING")
                all_good = False
    
    # Check for ZIP archive
    date_str = datetime.now().strftime('%Y%m%d')
    archive_name = f'JARVIS-{VERSION}-{date_str}.zip'
    archive_path = Path(archive_name)
    
    if archive_path.exists():
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print(f"\n  ✓ ZIP archive: {archive_name} ({size_mb:.2f} MB)")
    else:
        print(f"\n  ✗ ZIP archive: {archive_name} MISSING")
        all_good = False
    
    return all_good


def print_summary():
    """Print build summary."""
    print_header("Build Summary")
    
    base_dir = Path('dist/JARVIS')
    
    # Calculate statistics
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
    
    # Get archive info
    date_str = datetime.now().strftime('%Y%m%d')
    archive_name = f'JARVIS-{VERSION}-{date_str}.zip'
    archive_path = Path(archive_name)
    archive_size_mb = archive_path.stat().st_size / (1024 * 1024) if archive_path.exists() else 0
    
    print(f"Version: {VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"\nPackage Statistics:")
    print(f"  Files: {file_count}")
    print(f"  Directories: {dir_count}")
    if size_gb >= 1:
        print(f"  Total Size: {size_gb:.2f} GB")
    else:
        print(f"  Total Size: {size_mb:.2f} MB")
    print(f"\nArchive:")
    print(f"  Name: {archive_name}")
    print(f"  Size: {archive_size_mb:.2f} MB")
    print(f"  Compression: {(1 - archive_size_mb/size_mb)*100:.1f}%")
    
    print(f"\nOutput Locations:")
    print(f"  Application: {base_dir.absolute()}")
    print(f"  Archive: {archive_path.absolute()}")
    
    print(f"\nNext Steps:")
    print(f"  1. Test the application by running: dist/JARVIS/start_jarvis.bat")
    print(f"  2. Distribute the ZIP archive: {archive_name}")
    print(f"  3. Users should extract and run start_jarvis.bat")


def main():
    """Main packaging process."""
    print_header("JARVIS Desktop Application Packaging")
    print(f"Version: {VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    
    total_steps = 7
    
    # Step 1: Check prerequisites
    print_step(1, total_steps, "Checking Prerequisites")
    if not check_prerequisites():
        return 1
    
    # Step 2: Clean previous builds
    print_step(2, total_steps, "Cleaning Previous Builds")
    if not clean_previous_builds():
        return 1
    
    # Step 3: Build Python components
    print_step(3, total_steps, "Building Python Components")
    if not run_build_script('build_python.py', 'Python components build'):
        return 1
    
    # Step 4: Build Node.js components
    print_step(4, total_steps, "Building Node.js Components")
    if not run_build_script('build_nodejs.py', 'Node.js components build'):
        return 1
    
    # Step 5: Package assets
    print_step(5, total_steps, "Packaging Assets")
    if not run_build_script('build_assets.py', 'Asset packaging'):
        return 1
    
    # Step 6: Create directory structure
    print_step(6, total_steps, "Creating Directory Structure")
    if not run_build_script('build_structure.py', 'Directory structure creation'):
        return 1
    
    # Generate version info
    if not generate_version_info():
        return 1
    
    # Step 7: Create ZIP archive
    print_step(7, total_steps, "Creating ZIP Archive")
    if not create_zip_archive():
        return 1
    
    # Validate package
    if not validate_package():
        print("\n✗ Package validation failed")
        return 1
    
    # Print summary
    print_summary()
    
    print_header("✓ Packaging Complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
