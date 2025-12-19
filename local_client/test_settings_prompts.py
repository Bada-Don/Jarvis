"""Test script to verify settings API returns prompts correctly"""
import sys
from pathlib import Path

# Add local_client to path
sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI

# Create API instance
api = SettingsAPI()

# Get settings
result = api.get_settings()

if result['success']:
    settings = result['data']
    print("✓ Settings loaded successfully")
    print(f"  Categories: {list(settings.keys())}")
    
    if 'prompts' in settings:
        print(f"  Prompt categories: {list(settings['prompts'].keys())}")
        
        if 'planner' in settings['prompts']:
            planner_prompts = settings['prompts']['planner']
            print(f"  Planner prompts: {list(planner_prompts.keys())}")
            
            if 'GENERAL_SYSTEM_PROMPT' in planner_prompts:
                prompt_len = len(planner_prompts['GENERAL_SYSTEM_PROMPT'])
                print(f"  GENERAL_SYSTEM_PROMPT length: {prompt_len} chars")
                print(f"  First 100 chars: {planner_prompts['GENERAL_SYSTEM_PROMPT'][:100]}")
            else:
                print("  ✗ GENERAL_SYSTEM_PROMPT not found!")
        else:
            print("  ✗ Planner prompts not found!")
    else:
        print("  ✗ Prompts not found in settings!")
else:
    print(f"✗ Failed to load settings: {result.get('error', {}).get('message', 'Unknown error')}")
