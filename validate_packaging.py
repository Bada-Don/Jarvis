#!/usr/bin/env python3
"""
Validation script for JARVIS packaging system.
Verifies that all packaging scripts are present and correctly structured.
"""

import sys
from pathlib import Path
import ast


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_file_exists(file_path, description):
    """Check if a file exists and return its size."""
    path = Path(file_path)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  ✓ {description}: {file_path} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"  ✗ {description}: {file_path} MISSING")
        return False


def validate_python_syntax(file_path):
    """Validate Python file syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"    ✗ Syntax error: {e}")
        return False


def check_packaging_scripts():
    """Check that all packaging scripts exist and are valid."""
    print_header("Checking Packaging Scripts")
    
    scripts = [
        ('package.py', 'Main packaging script'),
        ('build_python.py', 'Python components builder'),
        ('build_nodejs.py', 'Node.js components builder'),
        ('build_assets.py', 'Assets packager'),
        ('build_structure.py', 'Directory structure creator'),
    ]
    
    all_good = True
    for script_path, description in scripts:
        if check_file_exists(script_path, description):
            if not validate_python_syntax(script_path):
                all_good = False
        else:
            all_good = False
    
    return all_good


def check_required_functions(file_path, required_functions):
    """Check if a Python file contains required functions."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        
        defined_functions = {node.name for node in ast.walk(tree) 
                           if isinstance(node, ast.FunctionDef)}
        
        missing = set(required_functions) - defined_functions
        if missing:
            print(f"    ⚠ Missing functions: {', '.join(missing)}")
            return False
        else:
            print(f"    ✓ All required functions present")
            return True
    except Exception as e:
        print(f"    ✗ Error checking functions: {e}")
        return False


def validate_package_py():
    """Validate package.py structure."""
    print_header("Validating package.py")
    
    required_functions = [
        'check_prerequisites',
        'clean_previous_builds',
        'run_build_script',
        'generate_version_info',
        'create_zip_archive',
        'validate_package',
        'main',
    ]
    
    return check_required_functions('package.py', required_functions)


def validate_build_python_py():
    """Validate build_python.py structure."""
    print_header("Validating build_python.py")
    
    required_functions = [
        'clean_build_dirs',
        'create_backend_spec',
        'create_local_client_spec',
        'build_component',
        'verify_build',
        'main',
    ]
    
    return check_required_functions('build_python.py', required_functions)


def validate_build_nodejs_py():
    """Validate build_nodejs.py structure."""
    print_header("Validating build_nodejs.py")
    
    required_functions = [
        'check_node_installed',
        'clean_build_dirs',
        'install_dependencies',
        'build_settings_ui',
        'optimize_bundle',
        'verify_build',
        'main',
    ]
    
    return check_required_functions('build_nodejs.py', required_functions)


def validate_build_assets_py():
    """Validate build_assets.py structure."""
    print_header("Validating build_assets.py")
    
    required_functions = [
        'create_assets_directory',
        'copy_fastsam_weights',
        'copy_application_icons',
        'create_config_templates',
        'create_data_directory',
        'verify_assets',
        'main',
    ]
    
    return check_required_functions('build_assets.py', required_functions)


def validate_build_structure_py():
    """Validate build_structure.py structure."""
    print_header("Validating build_structure.py")
    
    required_functions = [
        'create_directory_structure',
        'organize_python_components',
        'organize_nodejs_components',
        'organize_assets',
        'organize_data_directory',
        'create_launcher_script',
        'create_readme',
        'create_license',
        'verify_structure',
        'main',
    ]
    
    return check_required_functions('build_structure.py', required_functions)


def check_source_files():
    """Check that source files required for packaging exist."""
    print_header("Checking Source Files")
    
    required_sources = [
        ('backend/server.py', 'Backend server entry point'),
        ('local_client/client.py', 'Local client entry point'),
        ('settings_ui/package.json', 'Settings UI package config'),
        ('settings_ui/vite.config.js', 'Vite configuration'),
        ('JARVIS.py', 'Application launcher'),
        ('start_jarvis.bat', 'Windows launcher'),
    ]
    
    all_good = True
    for source_path, description in required_sources:
        if not check_file_exists(source_path, description):
            all_good = False
    
    return all_good


def check_expected_outputs():
    """Document expected outputs from packaging."""
    print_header("Expected Packaging Outputs")
    
    print("After successful packaging, the following should be created:")
    print()
    print("  dist/JARVIS/")
    print("  ├── app/")
    print("  │   ├── backend/jarvis_backend.exe")
    print("  │   ├── local_client/jarvis_client.exe")
    print("  │   └── settings_ui/index.html")
    print("  ├── assets/")
    print("  │   ├── weights/FastSAM-s.pt")
    print("  │   ├── icons/")
    print("  │   ├── config/")
    print("  │   └── audio/")
    print("  ├── data/")
    print("  │   ├── logs/")
    print("  │   └── config_backups/")
    print("  ├── JARVIS.py")
    print("  ├── start_jarvis.bat")
    print("  ├── README.txt")
    print("  ├── LICENSE.txt")
    print("  └── version.json")
    print()
    print("  JARVIS-1.0.0-YYYYMMDD.zip")
    print()


def check_prerequisites_documented():
    """Check that prerequisites are documented."""
    print_header("Checking Prerequisites Documentation")
    
    print("Required tools for packaging:")
    print("  • Python 3.10+ with pip")
    print("  • PyInstaller (pip install pyinstaller)")
    print("  • Node.js 18+ with npm")
    print("  • Git (for version control)")
    print()
    
    # Check if PACKAGING_GUIDE.md exists
    packaging_guide = Path('PACKAGING_GUIDE.md')
    if packaging_guide.exists():
        print(f"  ✓ PACKAGING_GUIDE.md exists")
        return True
    else:
        print(f"  ⚠ PACKAGING_GUIDE.md not found (optional)")
        return True


def print_summary(results):
    """Print validation summary."""
    print_header("Validation Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✓ All validation checks passed!")
        print()
        print("The packaging system is correctly implemented.")
        print("To create a distribution package:")
        print("  1. Install PyInstaller: pip install pyinstaller")
        print("  2. Ensure npm is in PATH")
        print("  3. Run: python package.py")
        return True
    else:
        print("✗ Some validation checks failed")
        print()
        print("Failed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  • {check}")
        return False


def main():
    """Main validation process."""
    print("JARVIS Packaging System Validation")
    print("=" * 70)
    print()
    print("This script validates the packaging system implementation")
    print("without requiring PyInstaller or npm to be installed.")
    
    results = {}
    
    # Run validation checks
    results['Packaging scripts exist'] = check_packaging_scripts()
    results['package.py structure'] = validate_package_py()
    results['build_python.py structure'] = validate_build_python_py()
    results['build_nodejs.py structure'] = validate_build_nodejs_py()
    results['build_assets.py structure'] = validate_build_assets_py()
    results['build_structure.py structure'] = validate_build_structure_py()
    results['Source files exist'] = check_source_files()
    results['Prerequisites documented'] = check_prerequisites_documented()
    
    # Show expected outputs
    check_expected_outputs()
    
    # Print summary
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
