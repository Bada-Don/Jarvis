"""
JARVIS Settings Interface - PyWebView Backend

This module provides the backend for the JARVIS settings interface,
hosting a React frontend within a PyWebView window and providing
a bridge between the UI and the Python configuration system.
"""

import os
import sys
import json
import webview
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

# Import managers
from config_manager import ConfigManager, SETTINGS_SCHEMA
from prompt_manager import PromptManager, read_all_prompts, write_prompts_to_file, PROMPT_SCHEMA
from validation_service import ValidationService
from packaging_service import PackagingService


class SettingsAPI:
    """
    API bridge between React frontend and Python backend.
    Exposes methods for configuration management, validation, and packaging.
    
    Note: All paths are stored as strings to avoid pywebview serialization issues.
    pywebview tries to serialize all class attributes to JavaScript, and pathlib.Path
    objects cannot be serialized properly.
    """
    
    def __init__(self):
        """Initialize the Settings API with managers and services."""
        # Store as string to avoid pywebview serialization issues with Path objects
        self.project_root_str = str(Path(__file__).parent.parent)
        
        # Initialize ConfigManager
        config_path = Path(self.project_root_str) / "local_client" / "config.py"
        self.config_manager = ConfigManager(str(config_path))
        
        # Initialize ValidationService
        self.validation_service = ValidationService()
        
        # Initialize PackagingService
        self.packaging_service = PackagingService(self.project_root_str)
        
        # Prompt managers will be created on-demand for each file
    
    # Configuration Methods
    def get_settings(self):
        """
        Get all current settings from config.py and prompts from service files
        
        Returns:
            dict: Current settings organized by category, including prompts
        """
        try:
            # Read config settings
            settings = self.config_manager.read_config()
            
            # Read prompts from service files
            prompts = read_all_prompts(Path(self.project_root_str))
            
            # Merge prompts into settings
            settings['prompts'] = prompts
            
            return {
                "success": True,
                "data": settings
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "READ_ERROR",
                    "message": f"Failed to read settings: {str(e)}",
                    "details": {},
                    "suggestions": ["Check that config.py exists and is readable"]
                }
            }
    
    def save_settings(self, settings):
        """
        Save settings to config files and prompts to service files
        
        Args:
            settings (dict): Settings dictionary to save
            
        Returns:
            dict: Response with success status and any errors
        """
        try:
            # Separate prompts from regular settings
            prompts = settings.pop('prompts', None)
            
            # Save regular settings to config.py
            config_success = self.config_manager.write_config(settings)
            
            # Save prompts to service files if present
            prompts_success = True
            if prompts:
                # Group prompts by file
                files_to_update = {}
                
                for category, category_prompts in prompts.items():
                    for prompt_name, prompt_value in category_prompts.items():
                        # Find which file this prompt belongs to
                        if category in PROMPT_SCHEMA and prompt_name in PROMPT_SCHEMA[category]:
                            file_path = PROMPT_SCHEMA[category][prompt_name]["file"]
                            full_path = Path(self.project_root_str) / file_path
                            
                            if str(full_path) not in files_to_update:
                                files_to_update[str(full_path)] = {}
                            
                            files_to_update[str(full_path)][prompt_name] = prompt_value
                
                # Write to each file
                for file_path, file_prompts in files_to_update.items():
                    success = write_prompts_to_file(Path(file_path), file_prompts)
                    if not success:
                        prompts_success = False
            
            if config_success and prompts_success:
                return {
                    "success": True,
                    "message": "Settings saved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "WRITE_ERROR",
                        "message": "Failed to write some settings",
                        "details": {},
                        "suggestions": ["Check file permissions", "Verify files are not open in another program"]
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "WRITE_ERROR",
                    "message": f"Failed to save settings: {str(e)}",
                    "details": {},
                    "suggestions": ["Check file permissions", "Verify config files are not corrupted"]
                }
            }
    
    def reset_setting(self, key):
        """
        Reset a setting to its default value
        
        Args:
            key (str): Setting key to reset
            
        Returns:
            dict: Response with the default value
        """
        try:
            default_value = self.config_manager.get_default_value(key)
            
            if default_value is None:
                return {
                    "success": False,
                    "error": {
                        "code": "UNKNOWN_SETTING",
                        "message": f"Setting '{key}' not found in schema",
                        "details": {},
                        "suggestions": ["Check the setting name"]
                    }
                }
            
            return {
                "success": True,
                "data": {
                    "key": key,
                    "value": default_value
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "RESET_ERROR",
                    "message": f"Failed to reset setting: {str(e)}",
                    "details": {},
                    "suggestions": []
                }
            }
    
    def validate_setting(self, key, value):
        """
        Validate a single setting
        
        Args:
            key (str): Setting key
            value: Value to validate
            
        Returns:
            dict: Validation result
        """
        try:
            # Find the setting in the schema
            setting_schema = None
            category = None
            
            for cat, settings in SETTINGS_SCHEMA.items():
                if key in settings:
                    setting_schema = settings[key]
                    category = cat
                    break
            
            if not setting_schema:
                return {
                    "success": True,
                    "valid": False,
                    "error": f"Unknown setting: {key}"
                }
            
            # Validate based on type
            setting_type = setting_schema.get("type", "string")
            
            if setting_type == "string":
                # Check for URL validation
                if setting_schema.get("validation") == "url":
                    is_valid, error = self.validation_service.validate_url(value)
                else:
                    # Regular string validation
                    min_length = 1 if setting_schema.get("required", False) else 0
                    is_valid, error = self.validation_service.validate_string(value, min_length=min_length)
            
            elif setting_type == "int":
                min_val = setting_schema.get("min")
                max_val = setting_schema.get("max")
                is_valid, error = self.validation_service.validate_number(
                    value, min_val=min_val, max_val=max_val, allow_int_only=True
                )
            
            elif setting_type == "float":
                min_val = setting_schema.get("min")
                max_val = setting_schema.get("max")
                is_valid, error = self.validation_service.validate_number(
                    value, min_val=min_val, max_val=max_val, allow_int_only=False
                )
            
            elif setting_type == "bool":
                if not isinstance(value, bool):
                    is_valid = False
                    error = f"Value must be boolean, got {type(value).__name__}"
                else:
                    is_valid = True
                    error = ""
            
            elif setting_type == "path":
                file_type = setting_schema.get("file_type")
                is_executable = file_type == "executable"
                
                # Allow empty paths if not required
                if not value and not setting_schema.get("required", False):
                    is_valid = True
                    error = ""
                else:
                    is_valid, error = self.validation_service.validate_path(
                        value,
                        must_exist=True,
                        is_directory=False,
                        is_executable=is_executable
                    )
            else:
                is_valid = True
                error = ""
            
            return {
                "success": True,
                "valid": is_valid,
                "error": error if not is_valid else ""
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Failed to validate setting: {str(e)}",
                    "details": {},
                    "suggestions": []
                }
            }
    
    # Prompt Methods
    def get_prompts(self):
        """
        Get all AI prompts from source files
        
        Returns:
            dict: All prompts organized by category
        """
        try:
            prompts = read_all_prompts(Path(self.project_root_str))
            return {
                "success": True,
                "data": prompts
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "READ_ERROR",
                    "message": f"Failed to read prompts: {str(e)}",
                    "details": {},
                    "suggestions": ["Check that service files exist and are readable"]
                }
            }
    
    def save_prompts(self, prompts):
        """
        Save AI prompts to source files
        
        Args:
            prompts (dict): Prompts dictionary to save
                Format: {"planner": {...}, "vision": {...}}
            
        Returns:
            dict: Response with success status
        """
        try:
            # Group prompts by file
            files_to_update = {}
            
            for category, category_prompts in prompts.items():
                for prompt_name, prompt_value in category_prompts.items():
                    # Find which file this prompt belongs to
                    if category in PROMPT_SCHEMA and prompt_name in PROMPT_SCHEMA[category]:
                        file_path = PROMPT_SCHEMA[category][prompt_name]["file"]
                        full_path = Path(self.project_root_str) / file_path
                        
                        if str(full_path) not in files_to_update:
                            files_to_update[str(full_path)] = {}
                        
                        files_to_update[str(full_path)][prompt_name] = prompt_value
            
            # Write to each file
            all_success = True
            for file_path, file_prompts in files_to_update.items():
                success = write_prompts_to_file(Path(file_path), file_prompts)
                if not success:
                    all_success = False
            
            if all_success:
                return {
                    "success": True,
                    "message": "Prompts saved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "WRITE_ERROR",
                        "message": "Failed to write some prompts",
                        "details": {},
                        "suggestions": ["Check file permissions", "Verify files are not open in another program"]
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "WRITE_ERROR",
                    "message": f"Failed to save prompts: {str(e)}",
                    "details": {},
                    "suggestions": ["Check file permissions", "Verify service files are not corrupted"]
                }
            }
    
    def reset_prompt(self, prompt_name):
        """
        Reset a prompt to its default value
        
        Note: This would require storing default prompts separately.
        For now, this returns an error suggesting manual restoration.
        
        Args:
            prompt_name (str): Name of the prompt to reset
            
        Returns:
            dict: Response with the default prompt
        """
        return {
            "success": False,
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Prompt reset not yet implemented",
                "details": {},
                "suggestions": [
                    "Manually restore from version control",
                    "Re-install the application to restore defaults"
                ]
            }
        }
    
    # Path Methods
    def browse_file(self, title="Select File", file_types=(), save_mode=False):
        """
        Open native file browser dialog
        
        Args:
            title (str): Dialog title
            file_types (tuple): File type filters
            save_mode (bool): If True, opens save dialog instead of open dialog
            
        Returns:
            str: Selected file path or empty string if cancelled
        """
        dialog_type = webview.SAVE_DIALOG if save_mode else webview.OPEN_DIALOG
        result = webview.windows[0].create_file_dialog(
            dialog_type,
            directory='',
            file_types=file_types
        )
        return result[0] if result else ""
    
    def browse_folder(self, title="Select Folder"):
        """
        Open native folder browser dialog
        
        Args:
            title (str): Dialog title
            
        Returns:
            str: Selected folder path or empty string if cancelled
        """
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG,
            directory=''
        )
        return result[0] if result else ""
    
    def validate_path(self, path, is_directory=False):
        """
        Validate a file or folder path
        
        Args:
            path (str): Path to validate
            is_directory (bool): Whether path should be a directory
            
        Returns:
            dict: Validation result
        """
        try:
            is_valid, error = self.validation_service.validate_path(
                path,
                must_exist=True,
                is_directory=is_directory,
                is_executable=False
            )
            
            return {
                "success": True,
                "valid": is_valid,
                "error": error if not is_valid else ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Failed to validate path: {str(e)}",
                    "details": {},
                    "suggestions": []
                }
            }
    
    # Configuration Profile Methods
    def export_config(self, file_path):
        """
        Export configuration to JSON file
        
        Args:
            file_path (str): Path to save configuration
            
        Returns:
            dict: Response with success status
        """
        try:
            # Get current settings
            settings_result = self.get_settings()
            if not settings_result["success"]:
                return settings_result
            
            settings = settings_result["data"]
            
            # Get current prompts
            prompts_result = self.get_prompts()
            if not prompts_result["success"]:
                return prompts_result
            
            prompts = prompts_result["data"]
            
            # Create export data with metadata
            export_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "configuration_name": Path(file_path).stem
                },
                "settings": settings,
                "prompts": prompts
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return {
                "success": True,
                "message": f"Configuration exported to {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "EXPORT_ERROR",
                    "message": f"Failed to export configuration: {str(e)}",
                    "details": {},
                    "suggestions": ["Check file path and permissions"]
                }
            }
    
    def import_config(self, file_path):
        """
        Import configuration from JSON file
        
        Args:
            file_path (str): Path to configuration file
            
        Returns:
            dict: Response with import results
        """
        try:
            # Read the configuration file
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate structure
            if "settings" not in import_data and "prompts" not in import_data:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_FORMAT",
                        "message": "Invalid configuration file format",
                        "details": {},
                        "suggestions": ["Ensure the file was exported from JARVIS Settings"]
                    }
                }
            
            warnings = []
            
            # Import settings if present
            if "settings" in import_data:
                # Validate settings
                validation_result = self.validation_service.validate_settings_dict(
                    import_data["settings"],
                    SETTINGS_SCHEMA
                )
                
                # Collect warnings for invalid settings
                if validation_result["errors"]:
                    for key, error in validation_result["errors"].items():
                        warnings.append(f"Skipped invalid setting {key}: {error}")
                
                # Apply valid settings
                valid_settings = {}
                for category, category_settings in import_data["settings"].items():
                    valid_settings[category] = {}
                    for key, value in category_settings.items():
                        full_key = f"{category}.{key}"
                        if full_key not in validation_result["errors"]:
                            valid_settings[category][key] = value
                
                # Save valid settings
                save_result = self.save_settings(valid_settings)
                if not save_result["success"]:
                    return save_result
            
            # Import prompts if present
            if "prompts" in import_data:
                save_result = self.save_prompts(import_data["prompts"])
                if not save_result["success"]:
                    warnings.append(f"Failed to import prompts: {save_result.get('error', {}).get('message', 'Unknown error')}")
            
            return {
                "success": True,
                "message": "Configuration imported successfully",
                "warnings": warnings
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_JSON",
                    "message": f"Invalid JSON file: {str(e)}",
                    "details": {},
                    "suggestions": ["Ensure the file is a valid JSON configuration"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "IMPORT_ERROR",
                    "message": f"Failed to import configuration: {str(e)}",
                    "details": {},
                    "suggestions": ["Check file path and format"]
                }
            }
    
    # Testing Methods
    def test_configuration(self):
        """
        Run validation tests on current configuration
        
        Returns:
            dict: Test results with passed/failed tests
        """
        try:
            passed = []
            failed = []
            warnings = []
            
            # Get current settings
            settings_result = self.get_settings()
            if not settings_result["success"]:
                return settings_result
            
            settings = settings_result["data"]
            
            # Test 1: Validate all settings against schema
            validation_result = self.validation_service.validate_settings_dict(
                settings,
                SETTINGS_SCHEMA
            )
            
            if validation_result["valid"]:
                passed.append({
                    "test": "Settings Validation",
                    "message": "All settings are valid"
                })
            else:
                for key, error in validation_result["errors"].items():
                    failed.append({
                        "test": f"Setting: {key}",
                        "message": error,
                        "guidance": "Update the setting to a valid value"
                    })
            
            # Add warnings from validation
            for key, warning in validation_result.get("warnings", {}).items():
                warnings.append({
                    "test": f"Setting: {key}",
                    "message": warning
                })
            
            # Test 2: Check path existence for all path settings
            for category, category_settings in settings.items():
                if category in SETTINGS_SCHEMA:
                    for key, value in category_settings.items():
                        if key in SETTINGS_SCHEMA[category]:
                            setting_schema = SETTINGS_SCHEMA[category][key]
                            if setting_schema.get("type") == "path" and value:
                                is_valid, error = self.validation_service.validate_path(
                                    value,
                                    must_exist=True,
                                    is_directory=False,
                                    is_executable=setting_schema.get("file_type") == "executable"
                                )
                                
                                if is_valid:
                                    passed.append({
                                        "test": f"Path Exists: {key}",
                                        "message": f"Path is valid: {value}"
                                    })
                                else:
                                    failed.append({
                                        "test": f"Path Exists: {key}",
                                        "message": error,
                                        "guidance": "Ensure the path exists and is accessible"
                                    })
            
            # Test 3: Check FlexiSIGN executable if configured
            if "flexisign" in settings:
                flexisign_exe = settings["flexisign"].get("FLEXISIGN_EXE_PATH", "")
                if flexisign_exe:
                    exe_path = Path(flexisign_exe)
                    if exe_path.exists() and exe_path.is_file():
                        passed.append({
                            "test": "FlexiSIGN Executable",
                            "message": f"FlexiSIGN executable found at {flexisign_exe}"
                        })
                    else:
                        failed.append({
                            "test": "FlexiSIGN Executable",
                            "message": f"FlexiSIGN executable not found at {flexisign_exe}",
                            "guidance": "Update FLEXISIGN_EXE_PATH to point to the correct executable"
                        })
                else:
                    warnings.append({
                        "test": "FlexiSIGN Executable",
                        "message": "FlexiSIGN executable path not configured"
                    })
            
            # Test 4: Check server URL format
            if "system" in settings:
                server_url = settings["system"].get("SERVER_URL", "")
                if server_url:
                    is_valid, error = self.validation_service.validate_url(server_url)
                    if is_valid:
                        passed.append({
                            "test": "Server URL",
                            "message": f"Server URL is valid: {server_url}"
                        })
                    else:
                        failed.append({
                            "test": "Server URL",
                            "message": error,
                            "guidance": "Update SERVER_URL to a valid URL format"
                        })
            
            return {
                "success": True,
                "data": {
                    "passed": passed,
                    "failed": failed,
                    "warnings": warnings,
                    "summary": {
                        "total_tests": len(passed) + len(failed),
                        "passed_count": len(passed),
                        "failed_count": len(failed),
                        "warning_count": len(warnings)
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "TEST_ERROR",
                    "message": f"Failed to test configuration: {str(e)}",
                    "details": {},
                    "suggestions": ["Check that all configuration files are accessible"]
                }
            }
    
    # Packaging Methods
    def start_build(self, options):
        """
        Start building executable with PyInstaller
        
        Args:
            options (dict): Build options containing:
                - output_name (str): Name for the output executable
                - include_console (bool): Whether to show console window
                - one_file (bool): Whether to bundle into a single file
                - icon (str, optional): Path to icon file
            
        Returns:
            dict: Response with build status
        """
        try:
            # Validate options
            if not options.get('output_name'):
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_OPTIONS",
                        "message": "Output name is required",
                        "details": {},
                        "suggestions": ["Provide an output_name in the options"]
                    }
                }
            
            # Start the build
            success = self.packaging_service.build_executable(options)
            
            if success:
                return {
                    "success": True,
                    "message": "Build started successfully"
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "BUILD_IN_PROGRESS",
                        "message": "A build is already in progress",
                        "details": {},
                        "suggestions": ["Wait for the current build to complete"]
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "BUILD_ERROR",
                    "message": f"Failed to start build: {str(e)}",
                    "details": {},
                    "suggestions": ["Check that PyInstaller is installed: pip install pyinstaller"]
                }
            }
    
    def get_build_status(self):
        """
        Get current build status
        
        Returns:
            dict: Build status information
        """
        try:
            status = self.packaging_service.get_build_status()
            return {
                "success": True,
                "data": status
            }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "STATUS_ERROR",
                    "message": f"Failed to get build status: {str(e)}",
                    "details": {},
                    "suggestions": []
                }
            }
    
    def open_build_folder(self):
        """
        Open folder containing built executable
        
        Returns:
            dict: Response with success status
        """
        try:
            build_dir = Path(self.project_root_str) / "dist"
            if build_dir.exists():
                os.startfile(str(build_dir))
                return {
                    "success": True,
                    "message": f"Opened build folder: {build_dir}"
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "FOLDER_NOT_FOUND",
                        "message": "Build folder does not exist",
                        "details": {},
                        "suggestions": ["Build the application first"]
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "OPEN_ERROR",
                    "message": f"Failed to open build folder: {str(e)}",
                    "details": {},
                    "suggestions": []
                }
            }


def on_closing():
    """
    Handle window closing event.
    Perform cleanup before the application exits.
    """
    print("Settings interface closing...")


def on_loaded():
    """
    Handle window loaded event.
    Called when the frontend has finished loading.
    """
    print("Settings interface loaded successfully")


def main(dev_mode=False):
    """
    Main entry point for the settings interface application.
    Creates and launches the PyWebView window with the React frontend.
    
    Args:
        dev_mode (bool): If True, enables debug mode and uses dev server if available
    """
    try:
        # Determine the path to the built React app
        project_root = Path(__file__).parent.parent
        frontend_path = project_root / "settings_ui" / "dist"
        
        # In development mode, try to use the dev server first
        if dev_mode:
            print("Running in DEVELOPMENT mode")
            # Check if dev server is running on port 5173
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dev_server_available = sock.connect_ex(('localhost', 5173)) == 0
            sock.close()
            
            if dev_server_available:
                print("Using Vite dev server at http://localhost:5173")
                url = "http://localhost:5173"
            else:
                print("Dev server not running, using production build")
                print("To use hot reload, run 'npm run dev' in settings_ui directory")
                if not frontend_path.exists():
                    print("\nERROR: Production build not found either!")
                    print("Please build the frontend first: cd settings_ui && npm run build")
                    sys.exit(1)
                url = str(frontend_path / "index.html")
        else:
            # Production mode - use built files
            # Check if the frontend has been built
            if not frontend_path.exists():
                print("=" * 60)
                print("ERROR: Frontend not built")
                print("=" * 60)
                print("\nThe React frontend needs to be built before running the settings interface.")
                print("\nTo build the frontend:")
                print("  1. Navigate to the settings_ui directory:")
                print("     cd settings_ui")
                print("  2. Install dependencies (if not already done):")
                print("     npm install")
                print("  3. Build the production bundle:")
                print("     npm run build")
                print("\nAfter building, run this script again.")
                print("=" * 60)
                sys.exit(1)
            
            # Verify index.html exists
            index_path = frontend_path / "index.html"
            if not index_path.exists():
                print(f"Error: index.html not found at {index_path}")
                print("The build may be incomplete. Please rebuild the frontend.")
                sys.exit(1)
            
            url = str(index_path)
        
        print("Starting JARVIS Settings Interface...")
        if not dev_mode or not dev_server_available:
            print(f"Frontend path: {frontend_path}")
        
        # Create API instance
        try:
            api = SettingsAPI()
            print("API bridge initialized successfully")
        except Exception as e:
            print(f"Error initializing API: {e}")
            print("\nPlease ensure all required files are present:")
            print("  - local_client/config.py")
            print("  - local_client/config_manager.py")
            print("  - local_client/prompt_manager.py")
            print("  - local_client/validation_service.py")
            print("  - backend/gemini_service.py")
            print("  - local_client/vision_service.py")
            sys.exit(1)
        
        # Create PyWebView window
        window = webview.create_window(
            title="JARVIS Settings",
            url=url,
            js_api=api,
            width=1200,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        
        # Set up event handlers
        window.events.closing += on_closing
        window.events.loaded += on_loaded
        
        print("Launching window...")
        
        # Start the application
        # Enable debug mode in development
        webview.start(debug=dev_mode)
        
        print("Settings interface closed")
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
