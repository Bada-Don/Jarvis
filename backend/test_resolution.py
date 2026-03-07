
import os
import sys
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock the providers before they are imported by newPlanner_service
mock_llm = MagicMock()
sys.modules['llm_provider'] = mock_llm
mock_llm.GeminiProvider = MagicMock()
mock_llm.OpenAIProvider = MagicMock()
mock_llm.AWSBedrockProvider = MagicMock()

# Add backend to path
backend_path = Path(r"d:\Documents\Codes\Jarvis\backend")
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from newPlanner_service import PlannerService

class MockProvider:
    def __init__(self):
        self.last_system_prompt = None
        self.last_user_prompt = None
    
    def generate_content(self, system_prompt, user_prompt):
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        # Return a plan that includes a placeholder
        return json.dumps({
            "mode": "general",
            "sequence": [
                {
                    "order": 1,
                    "type": "shell_command",
                    "command": 'mkdir "{DESKTOP_PATH}\\TestFolder"',
                    "desc": "Create a folder on desktop"
                }
            ],
            "expected_final_state": "Folder created on {DESKTOP_PATH}"
        })

def test_late_resolution():
    config = {
        'WINDOWS_USERNAME': 'harsh',
        'DESKTOP_PATH': r'C:\Users\harsh\Desktop',
        'DOCUMENTS_PATH': r'C:\Users\harsh\Documents',
        'DOWNLOADS_PATH': r'C:\Users\harsh\Downloads',
        'STICKERS_PATH': r'D:\Stickers\New Briefcase',
    }
    
    service = PlannerService(config=config)
    mock_provider = MockProvider()
    service.provider = mock_provider
    service.llm_provider = 'mock'
    
    print("Testing generate_plan...")
    plan = service.generate_plan("create folder test on desktop")
    
    # Check what was sent to LLM
    print("\nChecking System Prompt sent to LLM:")
    if "C:\\Users\\harsh\\Desktop" in mock_provider.last_system_prompt:
        print("FAIL: Real path leaked to LLM!")
    elif "{DESKTOP_PATH}" in mock_provider.last_system_prompt:
        print("SUCCESS: Abstract placeholder sent to LLM.")
    else:
        print("WARNING: Placeholder not found in prompt (check build_prompt logic).")
        
    # Check the resolved plan
    print("\nChecking Resolved Plan:")
    command = plan['sequence'][0]['command']
    expected_path = r'C:\Users\harsh\Desktop\TestFolder'
    if expected_path in command:
        print(f"SUCCESS: Resolved path found: {command}")
    else:
        print(f"FAIL: Path not resolved. Found: {command}")
        
    final_state = plan['expected_final_state']
    if "C:\\Users\\harsh\\Desktop" in final_state:
        print(f"SUCCESS: Final state resolved: {final_state}")
    else:
        print(f"FAIL: Final state not resolved: {final_state}")

if __name__ == "__main__":
    test_late_resolution()
