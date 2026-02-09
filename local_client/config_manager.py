"""
Configuration Manager for JARVIS Desktop Application

This module provides the ConfigurationManager class for loading, saving,
validating, and managing JARVIS configuration with backup/restore functionality.
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from urllib.parse import urlparse

from config_schema import (
    Configuration,
    DEFAULT_CONFIG,
    VALIDATION_RULES,
    ValidationRule,
    get_config_template,
)


class ConfigurationManager:
    """
    Manages JARVIS configuration with validation, backup, and persistence.
    
    Responsibilities:
    - Load configuration from file or create with defaults
    - Validate configuration against defined rules
    - Save configuration to disk
    - Create and restore backups
    - Detect first-run state
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigurationManager.
        
        Args:
            config_path: Path to configuration file. Defaults to local_client/config.py
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.py"
        
        self.config_path = Path(config_path)
        self.json_config_path = self.config_path.with_suffix('.json')
        self.backup_dir = self.config_path.parent / "config_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.config: Configuration = self._load_or_create()
    
    def _load_or_create(self) -> Configuration:
        """
        Load existing configuration or create from defaults.
        
        Returns:
            Configuration object
        """
        # Try to load from JSON first (new format)
        if self.json_config_path.exists():
            try:
                return self._load_from_json()
            except Exception as e:
                print(f"Warning: Failed to load JSON config: {e}")
        
        # Try to load from Python config file (legacy format)
        if self.config_path.exists():
            try:
                return self._load_from_python_config()
            except Exception as e:
                print(f"Warning: Failed to load Python config: {e}")
        
        # Create new configuration with defaults
        print("Creating new configuration with defaults")
        return Configuration.from_dict(DEFAULT_CONFIG)
    
    def _load_from_json(self) -> Configuration:
        """Load configuration from JSON file"""
        with open(self.json_config_path, 'r') as f:
            data = json.load(f)
        return Configuration.from_dict(data)
    
    def _load_from_python_config(self) -> Configuration:
        """
        Load configuration from existing Python config.py file.
        This provides backward compatibility with the existing config format.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", self.config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Map old config to new structure
        config_dict = DEFAULT_CONFIG.copy()
        
        # System
        if hasattr(config_module, 'SERVER_URL'):
            config_dict['system']['server_url'] = config_module.SERVER_URL
        if hasattr(config_module, 'WINDOWS_USERNAME'):
            config_dict['system']['windows_username'] = config_module.WINDOWS_USERNAME
        
        # LLM
        if hasattr(config_module, 'LLM_PROVIDER'):
            config_dict['llm']['provider'] = config_module.LLM_PROVIDER
        if hasattr(config_module, 'OPENAI_API_KEY'):
            config_dict['llm']['openai_api_key'] = config_module.OPENAI_API_KEY
        if hasattr(config_module, 'GEMINI_API_KEY'):
            config_dict['llm']['gemini_api_key'] = getattr(config_module, 'GEMINI_API_KEY', '')
        
        # Paths
        if hasattr(config_module, 'DESKTOP_PATH'):
            config_dict['paths']['desktop'] = config_module.DESKTOP_PATH
        if hasattr(config_module, 'DOCUMENTS_PATH'):
            config_dict['paths']['documents'] = config_module.DOCUMENTS_PATH
        if hasattr(config_module, 'DOWNLOADS_PATH'):
            config_dict['paths']['downloads'] = config_module.DOWNLOADS_PATH
        if hasattr(config_module, 'STICKERS_PATH'):
            config_dict['paths']['stickers'] = getattr(config_module, 'STICKERS_PATH', '')
        
        # Timing
        if hasattr(config_module, 'ACTION_DELAY'):
            config_dict['timing']['action_delay'] = config_module.ACTION_DELAY
        if hasattr(config_module, 'APP_LAUNCH_WAIT'):
            config_dict['timing']['app_launch_wait'] = config_module.APP_LAUNCH_WAIT
        if hasattr(config_module, 'HOTKEY_DELAY'):
            config_dict['timing']['hotkey_delay'] = getattr(config_module, 'HOTKEY_DELAY', 0.5)
        if hasattr(config_module, 'PRE_TYPE_DELAY'):
            config_dict['timing']['pre_type_delay'] = getattr(config_module, 'PRE_TYPE_DELAY', 0.2)
        if hasattr(config_module, 'SCREENSHOT_DELAY'):
            config_dict['timing']['screenshot_delay'] = getattr(config_module, 'SCREENSHOT_DELAY', 0.5)
        if hasattr(config_module, 'WINDOW_ACTIVATION_TIMEOUT'):
            config_dict['timing']['window_activation_timeout'] = getattr(config_module, 'WINDOW_ACTIVATION_TIMEOUT', 10)
        if hasattr(config_module, 'WINDOW_POLL_INTERVAL'):
            config_dict['timing']['window_poll_interval'] = getattr(config_module, 'WINDOW_POLL_INTERVAL', 0.5)
        if hasattr(config_module, 'RETRY_DELAY'):
            config_dict['timing']['retry_delay'] = getattr(config_module, 'RETRY_DELAY', 2)
        if hasattr(config_module, 'VERIFICATION_DELAY'):
            config_dict['timing']['verification_delay'] = getattr(config_module, 'VERIFICATION_DELAY', 1)
        
        # Verification
        if hasattr(config_module, 'VERIFICATION_ENABLED'):
            config_dict['verification']['enabled'] = config_module.VERIFICATION_ENABLED
        if hasattr(config_module, 'MAX_RETRIES'):
            config_dict['verification']['max_retries'] = config_module.MAX_RETRIES
        if hasattr(config_module, 'CONFIDENCE_THRESHOLD'):
            config_dict['verification']['confidence_threshold'] = getattr(config_module, 'CONFIDENCE_THRESHOLD', 0.7)
        
        # Window Manager
        if hasattr(config_module, 'WINDOW_ACTIVATION_ATTEMPTS'):
            config_dict['window_manager']['activation_attempts'] = getattr(config_module, 'WINDOW_ACTIVATION_ATTEMPTS', 3)
        if hasattr(config_module, 'WINDOW_MANAGER_VERBOSE'):
            config_dict['window_manager']['verbose'] = getattr(config_module, 'WINDOW_MANAGER_VERBOSE', True)
        
        # FlexiSign
        if hasattr(config_module, 'FLEXISIGN_PROCESS_NAME'):
            config_dict['flexisign']['process_name'] = getattr(config_module, 'FLEXISIGN_PROCESS_NAME', '')
        if hasattr(config_module, 'FLEXISIGN_EXE_PATH'):
            config_dict['flexisign']['exe_path'] = getattr(config_module, 'FLEXISIGN_EXE_PATH', '')
        if hasattr(config_module, 'FLEXISIGN_WINDOW_TITLE'):
            config_dict['flexisign']['window_title'] = getattr(config_module, 'FLEXISIGN_WINDOW_TITLE', '')
        if hasattr(config_module, 'STARTUP_MODAL_ENABLED'):
            config_dict['flexisign']['startup_modal_enabled'] = getattr(config_module, 'STARTUP_MODAL_ENABLED', True)
        if hasattr(config_module, 'STARTUP_MODAL_TITLE'):
            config_dict['flexisign']['startup_modal_title'] = getattr(config_module, 'STARTUP_MODAL_TITLE', '')
        if hasattr(config_module, 'STARTUP_MODAL_BUTTON'):
            config_dict['flexisign']['startup_modal_button'] = getattr(config_module, 'STARTUP_MODAL_BUTTON', '')
        if hasattr(config_module, 'STARTUP_MODAL_TIMEOUT'):
            config_dict['flexisign']['startup_modal_timeout'] = getattr(config_module, 'STARTUP_MODAL_TIMEOUT', 30)
        
        return Configuration.from_dict(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'llm.provider')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'llm.provider')
            value: Value to set
        """
        parts = key.split('.')
        obj = self.config
        
        # Navigate to the parent object
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise KeyError(f"Invalid configuration key: {key}")
        
        # Set the final value
        if hasattr(obj, parts[-1]):
            setattr(obj, parts[-1], value)
        else:
            raise KeyError(f"Invalid configuration key: {key}")
    
    def save(self) -> None:
        """
        Save configuration to disk in both JSON and Python formats.
        Creates a backup before saving.
        """
        # Create backup before saving
        if self.json_config_path.exists():
            self.backup()
        
        # Save as JSON (primary format)
        config_dict = self.config.to_dict()
        with open(self.json_config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        # Save as Python config file (for backward compatibility)
        config_content = get_config_template(self.config)
        with open(self.config_path, 'w') as f:
            f.write(config_content)
    
    def validate(self) -> List[str]:
        """
        Validate configuration against defined rules.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        config_dict = self.config.to_dict()
        
        for rule in VALIDATION_RULES:
            error = self._validate_rule(config_dict, rule)
            if error:
                errors.append(error)
        
        return errors
    
    def _validate_rule(self, config_dict: Dict[str, Any], rule: ValidationRule) -> Optional[str]:
        """
        Validate a single rule against configuration.
        
        Args:
            config_dict: Configuration as dictionary
            rule: Validation rule to check
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Get value from config using dot notation
        value = self._get_nested_value(config_dict, rule.field_path)
        
        if rule.rule_type == "required":
            if value is None or value == "":
                return rule.error_message
        
        elif rule.rule_type == "type":
            expected_type = rule.params.get("expected_type")
            if value is not None and not isinstance(value, expected_type):
                return rule.error_message
        
        elif rule.rule_type == "choice":
            choices = rule.params.get("choices", [])
            if value not in choices:
                return rule.error_message
        
        elif rule.rule_type == "range":
            min_val = rule.params.get("min")
            max_val = rule.params.get("max")
            if value is not None:
                if min_val is not None and value < min_val:
                    return rule.error_message
                if max_val is not None and value > max_val:
                    return rule.error_message
        
        elif rule.rule_type == "path_exists":
            if value and not Path(value).exists():
                return rule.error_message
        
        elif rule.rule_type == "url":
            if value:
                try:
                    result = urlparse(value)
                    if not all([result.scheme, result.netloc]):
                        return rule.error_message
                except Exception:
                    return rule.error_message
        
        elif rule.rule_type == "api_key":
            # Basic API key validation (non-empty, reasonable length)
            if value and (len(value) < 10 or len(value) > 200):
                return rule.error_message
        
        return None
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested dictionary value using dot notation"""
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def backup(self) -> Path:
        """
        Create a backup of the current configuration.
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"config_backup_{timestamp}.json"
        
        if self.json_config_path.exists():
            shutil.copy2(self.json_config_path, backup_path)
        
        return backup_path
    
    def restore(self, backup_path: Path) -> None:
        """
        Restore configuration from a backup file.
        
        Args:
            backup_path: Path to backup file
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Load backup
        with open(backup_path, 'r') as f:
            data = json.load(f)
        
        # Update current configuration
        self.config = Configuration.from_dict(data)
        
        # Save restored configuration
        self.save()
    
    def list_backups(self) -> List[Path]:
        """
        List all available backup files.
        
        Returns:
            List of backup file paths, sorted by date (newest first)
        """
        backups = list(self.backup_dir.glob("config_backup_*.json"))
        return sorted(backups, reverse=True)
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the application.
        
        Returns:
            True if first run, False otherwise
        """
        return not self.config.first_run_complete
    
    def mark_configured(self) -> None:
        """Mark first-run setup as complete"""
        self.config.first_run_complete = True
        self.save()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = Configuration.from_dict(DEFAULT_CONFIG)
        self.save()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.config.to_dict()
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            updates: Dictionary with configuration updates
        """
        current_dict = self.config.to_dict()
        self._deep_update(current_dict, updates)
        self.config = Configuration.from_dict(current_dict)
    
    def _deep_update(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Recursively update nested dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_config_manager(config_path: Optional[Path] = None) -> ConfigurationManager:
    """
    Get or create a ConfigurationManager instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ConfigurationManager instance
    """
    return ConfigurationManager(config_path)


def load_config(config_path: Optional[Path] = None) -> Configuration:
    """
    Load configuration from file.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration object
    """
    manager = ConfigurationManager(config_path)
    return manager.config


def save_config(config: Configuration, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration object to save
        config_path: Optional path to configuration file
    """
    manager = ConfigurationManager(config_path)
    manager.config = config
    manager.save()
