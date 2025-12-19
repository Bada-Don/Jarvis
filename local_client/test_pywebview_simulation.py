"""
Simulate PyWebView API calls to verify the settings UI will work correctly
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI

print("=" * 70)
print("SIMULATING PYWEBVIEW API CALLS")
print("=" * 70)

# Create API instance (same as PyWebView does)
api = SettingsAPI()

# Test 1: Get Settings (what the UI calls on load)
print("\n1. Testing window.pywebview.api.get_settings()...")
result = api.get_settings()

if result['success']:
    print("   ✓ API call successful")
    settings = result['data']
    
    # Check prompts
    if 'prompts' in settings:
        print("   ✓ Prompts included in response")
        
        if 'planner' in settings['prompts']:
            planner = settings['prompts']['planner']
            
            if 'GENERAL_SYSTEM_PROMPT' in planner:
                prompt_len = len(planner['GENERAL_SYSTEM_PROMPT'])
                if prompt_len > 0:
                    print(f"   ✓ GENERAL_SYSTEM_PROMPT: {prompt_len} chars")
                    print(f"     Preview: {planner['GENERAL_SYSTEM_PROMPT'][:80]}...")
                else:
                    print("   ✗ GENERAL_SYSTEM_PROMPT is EMPTY!")
            else:
                print("   ✗ GENERAL_SYSTEM_PROMPT not found!")
            
            if 'FLEXISIGN_SYSTEM_PROMPT' in planner:
                prompt_len = len(planner['FLEXISIGN_SYSTEM_PROMPT'])
                if prompt_len > 0:
                    print(f"   ✓ FLEXISIGN_SYSTEM_PROMPT: {prompt_len} chars")
                else:
                    print("   ✗ FLEXISIGN_SYSTEM_PROMPT is EMPTY!")
            else:
                print("   ✗ FLEXISIGN_SYSTEM_PROMPT not found!")
        else:
            print("   ✗ No planner prompts!")
    else:
        print("   ✗ No prompts in settings!")
else:
    print(f"   ✗ API call failed: {result.get('error', {}).get('message')}")

# Test 2: Verify JSON serialization (what PyWebView does)
print("\n2. Testing JSON serialization (PyWebView bridge)...")
try:
    json_str = json.dumps(result)
    print(f"   ✓ Response serializes to JSON: {len(json_str)} bytes")
    
    # Verify it can be parsed back
    parsed = json.loads(json_str)
    if 'data' in parsed and 'prompts' in parsed['data']:
        print("   ✓ JSON round-trip successful")
        
        # Check if prompts survived serialization
        if parsed['data']['prompts']['planner']['GENERAL_SYSTEM_PROMPT']:
            print("   ✓ Prompts preserved after JSON round-trip")
        else:
            print("   ✗ Prompts lost after JSON round-trip!")
    else:
        print("   ✗ JSON structure corrupted after round-trip")
except Exception as e:
    print(f"   ✗ JSON serialization failed: {e}")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)

if result['success'] and 'prompts' in result['data']:
    planner = result['data']['prompts'].get('planner', {})
    if planner.get('GENERAL_SYSTEM_PROMPT') and planner.get('FLEXISIGN_SYSTEM_PROMPT'):
        print("✓ PyWebView should receive prompts correctly!")
        print("\nIf you still see empty fields in PyWebView:")
        print("  1. Make sure you rebuilt the frontend: cd settings_ui && npm run build")
        print("  2. Close and restart the PyWebView app completely")
        print("  3. Check browser console for JavaScript errors (F12 in PyWebView)")
    else:
        print("✗ Prompts are empty - backend issue")
else:
    print("✗ API not returning prompts - backend issue")

print("=" * 70)
