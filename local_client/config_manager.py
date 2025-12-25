"""
Configuration Manager for JARVIS Settings Interface

This module provides the ConfigManager class for reading and writing
configuration settings to config.py while preserving file structure.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


# Settings schema with default values and metadata
SETTINGS_SCHEMA = {
    "system": {
        "SERVER_URL": {
            "type": "string",
            "default": "http://localhost:5000",
            "validation": "url",
            "description": "Backend server URL"
        },
        "WINDOWS_USERNAME": {
            "type": "string",
            "default": "",
            "required": True,
            "description": "Windows username for path generation"
        }
    },
    "paths": {
        "DESKTOP_PATH": {
            "type": "string",
            "default": "",
            "description": "Path to Desktop folder (used in AI prompts)"
        },
        "DOCUMENTS_PATH": {
            "type": "string",
            "default": "",
            "description": "Path to Documents folder (used in AI prompts)"
        },
        "DOWNLOADS_PATH": {
            "type": "string",
            "default": "",
            "description": "Path to Downloads folder (used in AI prompts)"
        },
        "STICKERS_PATH": {
            "type": "string",
            "default": "",
            "description": "Path to Stickers/New Briefcase folder (used in AI prompts)"
        }
    },
    "timing": {
        "ACTION_DELAY": {
            "type": "float",
            "default": 0.3,
            "min": 0.0,
            "max": 10.0,
            "unit": "seconds",
            "description": "Default delay after each step"
        },
        "APP_LAUNCH_WAIT": {
            "type": "float",
            "default": 3.0,
            "min": 0.5,
            "max": 30.0,
            "unit": "seconds",
            "description": "Extended delay after launching an application"
        },
        "HOTKEY_DELAY": {
            "type": "float",
            "default": 0.5,
            "min": 0.0,
            "max": 5.0,
            "unit": "seconds",
            "description": "Delay after hotkey combinations"
        },
        "PRE_TYPE_DELAY": {
            "type": "float",
            "default": 0.2,
            "min": 0.0,
            "max": 2.0,
            "unit": "seconds",
            "description": "Small delay before typing text"
        },
        "SCREENSHOT_DELAY": {
            "type": "float",
            "default": 0.5,
            "min": 0.0,
            "max": 5.0,
            "unit": "seconds",
            "description": "Screenshot delay before vision analysis"
        },
        "WINDOW_ACTIVATION_TIMEOUT": {
            "type": "float",
            "default": 10.0,
            "min": 1.0,
            "max": 60.0,
            "unit": "seconds",
            "description": "Maximum time to wait for window appearance"
        },
        "WINDOW_POLL_INTERVAL": {
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 5.0,
            "unit": "seconds",
            "description": "How often to poll for window appearance"
        }
    },
    "window_manager": {
        "WINDOW_ACTIVATION_ATTEMPTS": {
            "type": "int",
            "default": 3,
            "min": 1,
            "max": 10,
            "description": "Maximum attempts to activate a window"
        },
        "WINDOW_MANAGER_VERBOSE": {
            "type": "bool",
            "default": True,
            "description": "Verbose logging for window operations"
        }
    },
    "flexisign": {
        "FLEXISIGN_PROCESS_NAME": {
            "type": "string",
            "default": "Production Suite Scanner 10.5.1 Build 1806 Protected",
            "description": "FlexiSIGN process name"
        },
        "FLEXISIGN_EXE_PATH": {
            "type": "path",
            "default": "",
            "file_type": "executable",
            "description": "Path to FlexiSIGN executable"
        },
        "FLEXISIGN_WINDOW_TITLE": {
            "type": "string",
            "default": "FlexiSIGN-PRO",
            "description": "FlexiSIGN window title"
        },
        "STARTUP_MODAL_ENABLED": {
            "type": "bool",
            "default": True,
            "description": "Enable startup modal handling"
        },
        "STARTUP_MODAL_TITLE": {
            "type": "string",
            "default": "FlexiSIGN",
            "description": "Startup modal window title"
        },
        "STARTUP_MODAL_BUTTON": {
            "type": "string",
            "default": "OK",
            "description": "Startup modal button text"
        },
        "STARTUP_MODAL_TIMEOUT": {
            "type": "int",
            "default": 30,
            "min": 5,
            "max": 120,
            "unit": "seconds",
            "description": "Startup modal timeout"
        }
    },
    "verification": {
        "VERIFICATION_ENABLED": {
            "type": "bool",
            "default": False,
            "description": "Enable task verification after execution"
        },
        "MAX_RETRIES": {
            "type": "int",
            "default": 0,
            "min": 0,
            "max": 10,
            "description": "Maximum retry attempts if verification fails"
        },
        "RETRY_DELAY": {
            "type": "float",
            "default": 2.0,
            "min": 0.5,
            "max": 30.0,
            "unit": "seconds",
            "description": "Delay before retrying after verification failure"
        },
        "VERIFICATION_DELAY": {
            "type": "float",
            "default": 1.0,
            "min": 0.0,
            "max": 10.0,
            "unit": "seconds",
            "description": "Delay before starting verification"
        },
        "CONFIDENCE_THRESHOLD": {
            "type": "float",
            "default": 0.7,
            "min": 0.0,
            "max": 1.0,
            "description": "Minimum confidence score for successful verification"
        }
    },
    "legacy": {
        "PROCESS_START_WAIT": {
            "type": "int",
            "default": 5,
            "description": "Legacy process start wait time"
        },
        "WINDOW_SWITCH_WAIT": {
            "type": "int",
            "default": 1,
            "description": "Legacy window switch wait time"
        },
        "MODAL_CHECK_INTERVAL": {
            "type": "int",
            "default": 1,
            "description": "Legacy modal check interval"
        }
    }
}


class ConfigManager:
    """
    Manages reading and writing configuration settings to config.py
    while preserving file structure and comments.
    
    Note: All paths are stored as strings to avoid pywebview serialization issues.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize ConfigManager with path to config.py
        
        Args:
            config_path: Path to the config.py file
        """
        # Store as strings only - no Path objects to avoid pywebview serialization issues
        self.config_path_str = str(config_path)
        self.backup_path_str = str(config_path) + '.backup'
        
        if not Path(self.config_path_str).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
    
    def read_config(self) -> Dict[str, Any]:
        """
        Read current configuration from config.py
        
        Returns:
            dict: Configuration settings organized by category
        """
        config_dict = {}
        
        # Read the config file
        with open(self.config_path_str, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all variable assignments
        # Pattern matches: VARIABLE_NAME = value
        pattern = r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)(?:\s*#.*)?$'
        
        for line in content.split('\n'):
            line = line.strip()
            match = re.match(pattern, line)
            
            if match:
                var_name = match.group(1)
                var_value_str = match.group(2).strip()
                
                # Parse the value
                value = self._parse_value(var_value_str)
                
                # Find which category this setting belongs to
                category = self._find_category(var_name)
                
                if category:
                    if category not in config_dict:
                        config_dict[category] = {}
                    config_dict[category][var_name] = value
        
        return config_dict
    
    def write_config(self, settings: Dict[str, Dict[str, Any]]) -> bool:
        """
        Write settings back to config.py while preserving structure
        
        Args:
            settings: Dictionary of settings organized by category
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup before modifying
            self.create_backup()
            
            # Read current file content
            with open(self.config_path_str, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update each setting in the content
            for category, category_settings in settings.items():
                for key, value in category_settings.items():
                    content = self._update_setting_in_content(content, key, value)
            
            # Write back to file
            with open(self.config_path_str, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error writing config: {e}")
            # Attempt to restore backup
            if Path(self.backup_path_str).exists():
                self.restore_backup()
            return False
    
    def create_backup(self) -> None:
        """Create backup of current config before modifications"""
        if Path(self.config_path_str).exists():
            shutil.copy2(self.config_path_str, self.backup_path_str)
    
    def restore_backup(self) -> bool:
        """
        Restore config from backup
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if Path(self.backup_path_str).exists():
                shutil.copy2(self.backup_path_str, self.config_path_str)
                return True
            return False
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def get_default_value(self, key: str) -> Optional[Any]:
        """
        Get default value for a setting from schema
        
        Args:
            key: Setting key name
            
        Returns:
            Default value or None if not found
        """
        for category, settings in SETTINGS_SCHEMA.items():
            if key in settings:
                return settings[key].get("default")
        return None
    
    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a string value from config.py into appropriate Python type
        
        Args:
            value_str: String representation of the value
            
        Returns:
            Parsed value
        """
        value_str = value_str.strip()
        
        # Handle string values (single or double quotes)
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]
        
        # Handle raw strings (r"..." or r'...')
        if value_str.startswith('r"') and value_str.endswith('"'):
            return value_str[2:-1]
        if value_str.startswith("r'") and value_str.endswith("'"):
            return value_str[2:-1]
        
        # Handle boolean values
        if value_str == 'True':
            return True
        if value_str == 'False':
            return False
        
        # Handle numeric values
        try:
            # Try integer first
            if '.' not in value_str:
                return int(value_str)
            # Then float
            return float(value_str)
        except ValueError:
            pass
        
        # Return as string if can't parse
        return value_str
    
    def _format_value(self, value: Any) -> str:
        """
        Format a Python value for writing to config.py
        
        Args:
            value: Value to format
            
        Returns:
            String representation suitable for config.py
        """
        if isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            # Check if it's a path (contains backslashes or forward slashes)
            if '\\' in value or '/' in value:
                # Use raw string for paths
                return f'r"{value}"'
            else:
                # Use regular string
                return f"'{value}'"
        else:
            return str(value)
    
    def _update_setting_in_content(self, content: str, key: str, value: Any) -> str:
        """
        Update a single setting in the file content
        
        Args:
            content: Current file content
            key: Setting key to update
            value: New value
            
        Returns:
            Updated content
        """
        # Pattern to match the variable assignment line
        # Matches: KEY = value (with optional comment)
        pattern = rf'^({key}\s*=\s*)(.+?)(\s*#.*)?$'
        
        formatted_value = self._format_value(value)
        
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                # Preserve the assignment operator and any comment
                prefix = match.group(1)
                comment = match.group(3) if match.group(3) else ''
                updated_line = f"{prefix}{formatted_value}{comment}"
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def _find_category(self, key: str) -> Optional[str]:
        """
        Find which category a setting belongs to
        
        Args:
            key: Setting key name
            
        Returns:
            Category name or None if not found
        """
        for category, settings in SETTINGS_SCHEMA.items():
            if key in settings:
                return category
        return None
