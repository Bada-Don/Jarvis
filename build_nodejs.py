#!/usr/bin/env python3
"""
Build script for Node.js components using Vite.
Builds settings_ui and optimizes bundle size.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_node_installed():
    """Check if Node.js and npm are installed."""
    try:
        node_result = subprocess.run(
            ['node', '--version'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        npm_result = subprocess.run(
            ['npm', '--version'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✓ Node.js {node_result.stdout.strip()} detected")
        print(f"✓ npm {npm_result.stdout.strip()} detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Node.js or npm not found")
        print("Please install Node.js from https://nodejs.org/")
        return False


def clean_build_dirs():
    """Remove previous build artifacts."""
    settings_ui_dist = Path('settings_ui/dist')
    if settings_ui_dist.exists():
        print(f"Cleaning {settings_ui_dist}...")
        shutil.rmtree(settings_ui_dist)
    
    # Clean node_modules/.vite cache
    vite_cache = Path('settings_ui/node_modules/.vite')
    if vite_cache.exists():
        print(f"Cleaning Vite cache...")
        shutil.rmtree(vite_cache)


def install_dependencies():
    """Install npm dependencies if needed."""
    settings_ui_path = Path('settings_ui')
    node_modules = settings_ui_path / 'node_modules'
    
    if not node_modules.exists():
        print("\nInstalling npm dependencies...")
        print("This may take a few minutes...")
        
        try:
            subprocess.run(
                ['npm', 'install'],
                cwd=settings_ui_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install dependencies")
            print(f"Error: {e.stderr}")
            return False
    else:
        print("✓ Dependencies already installed")
        return True


def build_settings_ui():
    """Build settings_ui with Vite."""
    print("\n" + "=" * 60)
    print("Building Settings UI...")
    print("=" * 60 + "\n")
    
    settings_ui_path = Path('settings_ui')
    
    try:
        # Run production build
        result = subprocess.run(
            ['npm', 'run', 'build:prod'],
            cwd=settings_ui_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✓ Settings UI built successfully")
        
        # Show build output summary
        if 'dist' in result.stdout:
            print("\nBuild output:")
            for line in result.stdout.split('\n'):
                if 'dist' in line or 'kB' in line or 'MB' in line:
                    print(f"  {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build Settings UI")
        print(f"Error output:")
        print(e.stderr)
        return False


def optimize_bundle():
    """Optimize the built bundle."""
    print("\nOptimizing bundle...")
    
    dist_path = Path('settings_ui/dist')
    
    # Remove source maps in production
    for source_map in dist_path.rglob('*.map'):
        print(f"  Removing {source_map.name}")
        source_map.unlink()
    
    # Calculate bundle size
    total_size = 0
    file_count = 0
    
    for file_path in dist_path.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
            file_count += 1
    
    size_mb = total_size / (1024 * 1024)
    print(f"✓ Bundle optimized: {file_count} files, {size_mb:.2f} MB total")
    
    return True


def verify_build():
    """Verify that build artifacts were created."""
    dist_path = Path('settings_ui/dist')
    
    required_files = [
        dist_path / 'index.html',
    ]
    
    print("\nVerifying build artifacts...")
    all_good = True
    
    if dist_path.exists():
        print(f"✓ {dist_path} exists")
        
        # Check for index.html
        index_html = dist_path / 'index.html'
        if index_html.exists():
            print(f"✓ index.html exists")
        else:
            print(f"✗ index.html missing")
            all_good = False
        
        # Check for assets directory
        assets_dir = dist_path / 'assets'
        if assets_dir.exists():
            js_files = list(assets_dir.glob('*.js'))
            css_files = list(assets_dir.glob('*.css'))
            print(f"✓ assets/ exists ({len(js_files)} JS, {len(css_files)} CSS)")
        else:
            print(f"✗ assets/ directory missing")
            all_good = False
    else:
        print(f"✗ {dist_path} missing")
        all_good = False
    
    return all_good


def create_build_info():
    """Create a build info file with metadata."""
    from datetime import datetime
    
    build_info = {
        'build_date': datetime.now().isoformat(),
        'node_version': subprocess.run(
            ['node', '--version'],
            stdout=subprocess.PIPE,
            text=True
        ).stdout.strip(),
        'npm_version': subprocess.run(
            ['npm', '--version'],
            stdout=subprocess.PIPE,
            text=True
        ).stdout.strip(),
    }
    
    info_file = Path('settings_ui/dist/build-info.json')
    import json
    with open(info_file, 'w') as f:
        json.dump(build_info, f, indent=2)
    
    print(f"✓ Build info saved to {info_file}")


def main():
    """Main build process."""
    print("JARVIS Node.js Components Build Script")
    print("=" * 60)
    
    # Check Node.js installation
    if not check_node_installed():
        return 1
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Build settings UI
    if not build_settings_ui():
        return 1
    
    # Optimize bundle
    if not optimize_bundle():
        return 1
    
    # Create build info
    create_build_info()
    
    # Verify build
    if verify_build():
        print("\n" + "=" * 60)
        print("✓ Node.js components built successfully!")
        print("=" * 60)
        print("\nBuild artifacts located in:")
        print("  - settings_ui/dist/")
        return 0
    else:
        print("\n✗ Build verification failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
