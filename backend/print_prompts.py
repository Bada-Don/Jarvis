"""Print the fully interpolated system prompts."""

import sys
import codecs
from pathlib import Path

# Force UTF-8 for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add local_client to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent / "local_client"))

from planner_service import GENERAL_SYSTEM_PROMPT, FLEXISIGN_SYSTEM_PROMPT

try:
    import config as user_config
    cfg = {
        'WINDOWS_USERNAME': getattr(user_config, 'WINDOWS_USERNAME', 'user'),
        'DESKTOP_PATH': getattr(user_config, 'DESKTOP_PATH', r'C:\Users\user\Desktop'),
        'DOCUMENTS_PATH': getattr(user_config, 'DOCUMENTS_PATH', r'C:\Users\user\Documents'),
        'DOWNLOADS_PATH': getattr(user_config, 'DOWNLOADS_PATH', r'C:\Users\user\Downloads'),
        'STICKERS_PATH': getattr(user_config, 'STICKERS_PATH', r'D:\Stickers\New Briefcase'),
    }
except Exception as e:
    print(f"Could not load config: {e}")
    sys.exit(1)

print("=" * 80)
print("GENERAL SYSTEM PROMPT")
print("=" * 80)
print(GENERAL_SYSTEM_PROMPT.format(**cfg))

print("\n" + "=" * 80)
print("FLEXISIGN SYSTEM PROMPT")
print("=" * 80)
print(FLEXISIGN_SYSTEM_PROMPT.format(**cfg))
