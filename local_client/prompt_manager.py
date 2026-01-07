"""
Prompt Manager for JARVIS Settings Interface

This module provides the PromptManager class for reading and writing
AI model prompts from Python source files using AST manipulation.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Prompt schema defining which prompts exist in which files
PROMPT_SCHEMA = {
    "planner": {
        "GENERAL_SYSTEM_PROMPT": {
            "file": "backend/planner_service.py",
            "variable": "GENERAL_SYSTEM_PROMPT",
            "language": "markdown",
            "description": "System prompt for general computer automation",
            "required_placeholders": []
        },
        "FLEXISIGN_SYSTEM_PROMPT": {
            "file": "backend/planner_service.py",
            "variable": "FLEXISIGN_SYSTEM_PROMPT",
            "language": "markdown",
            "description": "System prompt for FlexiSIGN automation",
            "required_placeholders": []
        }
    },
    "vision": {
        "GENERAL_VISION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "GENERAL_VISION_PROMPT",
            "language": "markdown",
            "description": "Vision prompt for general UI element identification",
            "required_placeholders": []
        },
        "VERIFICATION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "VERIFICATION_PROMPT",
            "language": "markdown",
            "description": "Prompt for task verification",
            "required_placeholders": []
        },
        "FLEXISIGN_VISION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "FLEXISIGN_VISION_PROMPT",
            "language": "markdown",
            "description": "Vision prompt for FlexiSIGN UI elements",
            "required_placeholders": []
        }
    }
}


class PromptManager:
    """
    Manages AI model prompts in Python source files.
    Uses AST for safe extraction and regex for safe updates.
    """
    
    def __init__(self, service_path: str):
        """
        Initialize PromptManager with path to a service file
        
        Args:
            service_path: Path to the Python service file (e.g., planner_service.py)
        """
        self.service_path = Path(service_path)
        
        if not self.service_path.exists():
            raise FileNotFoundError(f"Service file not found: {service_path}")
    
    def read_prompts(self) -> Dict[str, str]:
        """
        Extract prompt constants from Python file using regex (more reliable than AST for strings with escape sequences)
        
        Returns:
            dict: Mapping of prompt variable names to their values
        """
        prompts = {}
        
        # Read the file content with proper encoding
        with open(self.service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # For each known prompt variable, extract its value using regex
        for category, category_prompts in PROMPT_SCHEMA.items():
            for var_name in category_prompts.keys():
                # Pattern to match: VAR_NAME = """...""" or VAR_NAME = r"""..."""
                # Also handles '''...''' and r'''...'''
                # Using DOTALL to match across newlines
                pattern = rf'{var_name}\s*=\s*r?"""(.*?)"""|{var_name}\s*=\s*r?\'\'\'(.*?)\'\'\''
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    # Get the captured group (either from """ or ''')
                    value = match.group(1) if match.group(1) is not None else match.group(2)
                    if value is not None:
                        prompts[var_name] = value
        
        return prompts
    
    def write_prompts(self, prompts: Dict[str, str]) -> bool:
        """
        Update prompt constants in Python file safely
        
        Args:
            prompts: Dictionary mapping prompt variable names to new values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read current file content
            with open(self.service_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update each prompt in the content
            for var_name, new_value in prompts.items():
                if self._is_prompt_variable(var_name):
                    content = self._update_prompt_in_content(content, var_name, new_value)
            
            # Write back to file
            with open(self.service_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error writing prompts: {e}")
            return False
    
    def validate_prompt(self, prompt: str, required_placeholders: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that a prompt contains required placeholders
        
        Args:
            prompt: The prompt text to validate
            required_placeholders: List of required placeholder strings
            
        Returns:
            tuple: (is_valid, missing_placeholders)
        """
        missing = []
        
        for placeholder in required_placeholders:
            if placeholder not in prompt:
                missing.append(placeholder)
        
        is_valid = len(missing) == 0
        return is_valid, missing
    
    def _is_prompt_variable(self, var_name: str) -> bool:
        """
        Check if a variable name is a known prompt variable
        
        Args:
            var_name: Variable name to check
            
        Returns:
            bool: True if this is a prompt variable
        """
        for category, prompts in PROMPT_SCHEMA.items():
            if var_name in prompts:
                return True
        return False
    
    def _update_prompt_in_content(self, content: str, var_name: str, new_value: str) -> str:
        """
        Update a single prompt variable in the file content
        
        Uses regex to find and replace the string value while preserving
        the file structure and formatting (including raw string prefix if present).
        
        Args:
            content: Current file content
            var_name: Variable name to update
            new_value: New prompt value
            
        Returns:
            Updated content
        """
        # Escape the new value for use in a triple-quoted string
        escaped_value = new_value.replace('\\', '\\\\').replace('"""', r'\"\"\"')
        
        # Pattern to match the variable assignment with triple-quoted string
        # This handles both """ and ''' quotes, with or without raw string prefix
        # Pattern: VAR_NAME = """...""" or VAR_NAME = r"""..."""
        pattern = rf'({var_name}\s*=\s*)(r?""".*?"""|r?\'\'\'.*?\'\'\')'
        
        # Replacement with raw triple-quoted string (preserves backslashes)
        replacement = rf'\1r"""{escaped_value}"""'
        
        # Use DOTALL flag to match across newlines
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        return updated_content
    
    def get_prompt_metadata(self, var_name: str) -> Optional[Dict]:
        """
        Get metadata for a prompt variable from the schema
        
        Args:
            var_name: Variable name
            
        Returns:
            dict: Metadata or None if not found
        """
        for category, prompts in PROMPT_SCHEMA.items():
            if var_name in prompts:
                return prompts[var_name]
        return None


def read_all_prompts(project_root: Path) -> Dict[str, Dict[str, str]]:
    """
    Read all prompts from all service files
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        dict: All prompts organized by category
    """
    all_prompts = {
        "planner": {},
        "vision": {}
    }
    
    # Track which files we've already processed
    processed_files = set()
    
    for category, prompts in PROMPT_SCHEMA.items():
        for var_name, metadata in prompts.items():
            file_path = project_root / metadata["file"]
            
            # Only read each file once
            if str(file_path) not in processed_files:
                try:
                    manager = PromptManager(str(file_path))
                    file_prompts = manager.read_prompts()
                    
                    # Add prompts to the appropriate category
                    for prompt_var, prompt_value in file_prompts.items():
                        # Find which category this prompt belongs to
                        for cat, cat_prompts in PROMPT_SCHEMA.items():
                            if prompt_var in cat_prompts:
                                all_prompts[cat][prompt_var] = prompt_value
                                break
                    
                    processed_files.add(str(file_path))
                    
                except Exception as e:
                    print(f"Error reading prompts from {file_path}: {e}")
    
    return all_prompts


def write_prompts_to_file(file_path: Path, prompts: Dict[str, str]) -> bool:
    """
    Write multiple prompts to a single file
    
    Args:
        file_path: Path to the service file
        prompts: Dictionary of prompts to write
        
    Returns:
        bool: True if successful
    """
    try:
        manager = PromptManager(str(file_path))
        return manager.write_prompts(prompts)
    except Exception as e:
        print(f"Error writing prompts to {file_path}: {e}")
        return False
