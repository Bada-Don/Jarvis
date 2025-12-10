"""
Path Configuration Module for Direct Path Automation

This module provides configuration management for direct path automation,
including default directories, overwrite policies, and path construction helpers.

Requirements: 6.1, 6.4, 1.4
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# Default configuration file path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "direct_path_config.json"


@dataclass
class PathConfig:
    """
    Configuration for direct path automation.
    
    Manages default paths and automation policies for file operations.
    
    Attributes:
        default_save_directory: Default directory for save operations (e.g., Desktop)
        default_open_directory: Default directory for open operations (e.g., Documents)
        overwrite_policy: Policy for file conflicts ("overwrite", "rename", "abort", "prompt")
        dialog_wait_timeout: Timeout in seconds for waiting for dialogs to appear
    """
    default_save_directory: str = ""
    default_open_directory: str = ""
    overwrite_policy: str = "prompt"
    dialog_wait_timeout: float = 2.0
    
    def __post_init__(self):
        """Initialize default directories if not provided."""
        if not self.default_save_directory:
            self.default_save_directory = self._get_desktop_path()
        if not self.default_open_directory:
            self.default_open_directory = self._get_documents_path()
        
        # Validate overwrite_policy
        valid_policies = {"overwrite", "rename", "abort", "prompt"}
        if self.overwrite_policy not in valid_policies:
            raise ValueError(
                f"Invalid overwrite_policy '{self.overwrite_policy}'. "
                f"Must be one of: {valid_policies}"
            )
        
        # Validate dialog_wait_timeout
        if self.dialog_wait_timeout <= 0:
            raise ValueError("dialog_wait_timeout must be positive")
    
    @staticmethod
    def _get_desktop_path() -> str:
        """Get the user's Desktop path."""
        # Try Windows-specific path first
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return str(desktop)
        
        # Try OneDrive Desktop
        onedrive_desktop = Path.home() / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return str(onedrive_desktop)
        
        # Fallback to home directory
        return str(Path.home())
    
    @staticmethod
    def _get_documents_path() -> str:
        """Get the user's Documents path."""
        # Try Windows-specific path first
        documents = Path.home() / "Documents"
        if documents.exists():
            return str(documents)
        
        # Try OneDrive Documents
        onedrive_docs = Path.home() / "OneDrive" / "Documents"
        if onedrive_docs.exists():
            return str(onedrive_docs)
        
        # Fallback to home directory
        return str(Path.home())
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'PathConfig':
        """
        Load configuration from a JSON file or use defaults.
        
        Args:
            config_path: Path to the JSON configuration file. 
                        If None, uses the default config path.
        
        Returns:
            PathConfig instance with loaded or default values.
        
        Requirements: 6.1, 6.4
        """
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle nested structure (direct_path_config key)
                if 'direct_path_config' in data:
                    data = data['direct_path_config']
                
                # Extract only the fields we care about
                return cls(
                    default_save_directory=data.get('default_save_directory', ''),
                    default_open_directory=data.get('default_open_directory', ''),
                    overwrite_policy=data.get('overwrite_policy', 'prompt'),
                    dialog_wait_timeout=float(data.get('dialog_wait_timeout', 2.0))
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                # If config file is invalid, use defaults
                print(f"Warning: Could not load config from {path}: {e}. Using defaults.")
                return cls()
        
        # Config file doesn't exist, use defaults (Requirement 6.4)
        return cls()
    
    def save(self, config_path: Optional[str] = None) -> None:
        """
        Save current configuration to a JSON file.
        
        Args:
            config_path: Path to save the configuration. 
                        If None, uses the default config path.
        """
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "direct_path_config": {
                "default_save_directory": self.default_save_directory,
                "default_open_directory": self.default_open_directory,
                "overwrite_policy": self.overwrite_policy,
                "dialog_wait_timeout": self.dialog_wait_timeout
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    
    def get_full_save_path(self, filename: str, directory: Optional[str] = None) -> str:
        """
        Construct a full save path with defaults.
        
        Args:
            filename: The filename (with or without extension)
            directory: Optional directory path. If None, uses default_save_directory.
        
        Returns:
            Full absolute path for the save operation.
        
        Requirements: 1.4
        """
        # Use provided directory or default
        dir_path = directory if directory else self.default_save_directory
        
        # Normalize the directory path
        dir_path = os.path.normpath(dir_path)
        
        # Combine directory and filename
        full_path = os.path.join(dir_path, filename)
        
        # Return normalized absolute path
        return os.path.normpath(os.path.abspath(full_path))
    
    def get_full_open_path(self, filename: str, directory: Optional[str] = None) -> str:
        """
        Construct a full open path.
        
        Args:
            filename: The filename (with extension)
            directory: Optional directory path. If None, uses default_open_directory.
        
        Returns:
            Full absolute path for the open operation.
        """
        # Use provided directory or default
        dir_path = directory if directory else self.default_open_directory
        
        # Normalize the directory path
        dir_path = os.path.normpath(dir_path)
        
        # Combine directory and filename
        full_path = os.path.join(dir_path, filename)
        
        # Return normalized absolute path
        return os.path.normpath(os.path.abspath(full_path))
    
    def to_dict(self) -> dict:
        """Convert configuration to a dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PathConfig':
        """Create a PathConfig from a dictionary."""
        return cls(
            default_save_directory=data.get('default_save_directory', ''),
            default_open_directory=data.get('default_open_directory', ''),
            overwrite_policy=data.get('overwrite_policy', 'prompt'),
            dialog_wait_timeout=float(data.get('dialog_wait_timeout', 2.0))
        )
