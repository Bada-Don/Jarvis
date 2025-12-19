"""
Debug script to add logging to settings_app.py
Run this before launching PyWebView to see what's happening
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Monkey-patch the SettingsAPI to add debug logging
from settings_app import SettingsAPI
original_get_settings = SettingsAPI.get_settings

def debug_get_settings(self):
    print("\n" + "=" * 70)
    print("DEBUG: get_settings() called")
    print("=" * 70)
    
    result = original_get_settings(self)
    
    if result['success']:
        settings = result['data']
        print(f"✓ Settings loaded successfully")
        print(f"  Categories: {list(settings.keys())}")
        
        if 'prompts' in settings:
            print(f"  ✓ Prompts present")
            prompts = settings['prompts']
            
            if 'planner' in prompts:
                planner = prompts['planner']
                print(f"    Planner prompts: {list(planner.keys())}")
                
                for key, value in planner.items():
                    print(f"      {key}: {len(value)} chars")
            else:
                print("    ✗ No planner prompts!")
        else:
            print("  ✗ No prompts in settings!")
    else:
        print(f"✗ Failed: {result.get('error', {}).get('message')}")
    
    print("=" * 70 + "\n")
    return result

SettingsAPI.get_settings = debug_get_settings

print("Debug logging enabled for SettingsAPI.get_settings()")
print("Now import and run your settings app...")
