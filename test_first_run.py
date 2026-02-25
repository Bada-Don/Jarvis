#!/usr/bin/env python3
"""Test if first run detection is working"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "local_client"))

from settings_app import SettingsAPI

# Create API instance
api = SettingsAPI()

# Check first run
result = api.is_first_run()
print("=" * 60)
print("First Run Check Result:")
print("=" * 60)
print(f"Success: {result.get('success')}")
print(f"Data (is_first_run): {result.get('data')}")
if 'error' in result:
    print(f"Error: {result['error']}")
print("=" * 60)

# Also check the config directly
print("\nDirect Config Check:")
print(f"Config exists: {api.config_manager.config is not None}")
print(f"First run complete: {api.config_manager.config.first_run_complete}")
print(f"is_first_run(): {api.config_manager.is_first_run()}")
