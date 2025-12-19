"""
Quick fix script to clear all caches and rebuild settings UI
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("JARVIS Settings UI - Cache Clear & Rebuild")
print("=" * 70)

project_root = Path(__file__).parent.parent

# Step 1: Clear Python cache
print("\n1. Clearing Python cache...")
cache_dirs = []
for root, dirs, files in os.walk(project_root):
    if '__pycache__' in dirs:
        cache_path = Path(root) / '__pycache__'
        cache_dirs.append(cache_path)

if cache_dirs:
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✓ Removed: {cache_dir.relative_to(project_root)}")
        except Exception as e:
            print(f"   ✗ Failed to remove {cache_dir}: {e}")
    print(f"   ✓ Cleared {len(cache_dirs)} cache directories")
else:
    print("   ✓ No cache directories found")

# Step 2: Clear .pyc files
print("\n2. Clearing .pyc files...")
pyc_files = list(project_root.rglob('*.pyc'))
if pyc_files:
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
        except Exception as e:
            print(f"   ✗ Failed to remove {pyc_file}: {e}")
    print(f"   ✓ Removed {len(pyc_files)} .pyc files")
else:
    print("   ✓ No .pyc files found")

# Step 3: Rebuild frontend
print("\n3. Rebuilding frontend...")
settings_ui_dir = project_root / "settings_ui"

if settings_ui_dir.exists():
    try:
        # Change to settings_ui directory and run build
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=settings_ui_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            print("   ✓ Frontend rebuilt successfully")
            
            # Check dist directory
            dist_dir = settings_ui_dir / "dist"
            if dist_dir.exists():
                js_files = list(dist_dir.glob("assets/*.js"))
                css_files = list(dist_dir.glob("assets/*.css"))
                print(f"   ✓ Build output: {len(js_files)} JS files, {len(css_files)} CSS files")
            else:
                print("   ✗ dist directory not found after build")
        else:
            print("   ✗ Build failed:")
            print(result.stderr)
    except Exception as e:
        print(f"   ✗ Build error: {e}")
else:
    print("   ✗ settings_ui directory not found")

# Step 4: Verify backend
print("\n4. Verifying backend...")
try:
    sys.path.insert(0, str(project_root / "local_client"))
    from settings_app import SettingsAPI
    
    api = SettingsAPI()
    result = api.get_settings()
    
    if result['success']:
        settings = result['data']
        if 'prompts' in settings:
            planner = settings['prompts'].get('planner', {})
            general_len = len(planner.get('GENERAL_SYSTEM_PROMPT', ''))
            flexisign_len = len(planner.get('FLEXISIGN_SYSTEM_PROMPT', ''))
            
            if general_len > 0 and flexisign_len > 0:
                print(f"   ✓ Backend working correctly")
                print(f"     GENERAL_SYSTEM_PROMPT: {general_len} chars")
                print(f"     FLEXISIGN_SYSTEM_PROMPT: {flexisign_len} chars")
            else:
                print("   ✗ Prompts are empty in backend")
        else:
            print("   ✗ No prompts in backend response")
    else:
        print(f"   ✗ Backend error: {result.get('error', {}).get('message')}")
except Exception as e:
    print(f"   ✗ Backend verification failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DONE!")
print("=" * 70)
print("\nNext steps:")
print("  1. Close any running PyWebView instances")
print("  2. Run: python local_client/run_settings.py")
print("  3. Check if prompts now load correctly")
print("\nIf still not working, check: SETTINGS_UI_TROUBLESHOOTING.md")
print("=" * 70)
