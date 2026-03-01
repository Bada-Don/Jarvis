"""Print the fully interpolated system prompts."""

import sys
import codecs
from pathlib import Path

# Force UTF-8 for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add local_client to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent / "local_client"))

from newPlanner_service import PlannerService

# 1. Dynamically load paths from config (Best of previous version)
try:
    import config as user_config
    cfg = {
        'WINDOWS_USERNAME': getattr(user_config, 'WINDOWS_USERNAME', 'user'),
        'DESKTOP_PATH': getattr(user_config, 'DESKTOP_PATH', r'C:\Users\user\Desktop'),
        'DOCUMENTS_PATH': getattr(user_config, 'DOCUMENTS_PATH', r'C:\Users\user\Documents'),
        'DOWNLOADS_PATH': getattr(user_config, 'DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
        'STICKERS_PATH': getattr(user_config, 'STICKERS_PATH', r'D:\Stickers\New Briefcase'),
    }
except ImportError as e:
    print(f"Warning: Could not load config.py ({e}). Using dummy fallback paths.\n")
    cfg = {
        'WINDOWS_USERNAME': 'user',
        'DESKTOP_PATH': r'C:\Users\user\Desktop',
        'DOCUMENTS_PATH': r'C:\Users\user\Documents',
        'DOWNLOADS_PATH': r'C:\Users\user\Downloads',
        'STICKERS_PATH': r'D:\Stickers\New Briefcase',
    }

# 2. Initialize Planner with the dynamic config (Best of new version)
planner = PlannerService(config=cfg)

print("=" * 80)
print("GENERAL SYSTEM PROMPT")
print("=" * 80)
# Assemble a prompt with all general modules
general_route = {"mode": "general", "modules":["ui_os", "email", "shell", "file_editing", "file_navigation"]}
print(planner.build_prompt(general_route))

print("\n" + "=" * 80)
print("FLEXISIGN SYSTEM PROMPT")
print("=" * 80)
# Assemble FlexiSIGN prompt
flexi_route = {"mode": "flexisign", "modules": ["flexisign"]}
print(planner.build_prompt(flexi_route))