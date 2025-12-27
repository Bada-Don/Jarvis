"""
Folder Operations Module

Provides functions for folder management including creation, deletion, opening, and listing.
Uses command-line utilities where possible and reuses existing path resolution logic.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.1, 10.1, 10.2, 10.4
"""

import os
import shutil
import subprocess
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "local_client"))

from path_resolver import PathResolver, PathResolveResult
from path_config import PathConfig


def create_folder(path: str) -> Dict[str, any]:
    """
    Create a folder at the specified path.
    
    Uses command-line: os.makedirs() with exist_ok=True
    
    Args:
        path: Full or fuzzy path to folder to create
        
    Returns:
        {"success": bool, "message": str, "path": str}
        
    Requirements: 3.1, 3.5, 10.1, 10.2
    """
    try:
        # Requirement 10.1: Descriptive error messages for invalid parameters
        if not path or not path.strip():
            error_msg = "Path cannot be empty. Provide a valid folder path."
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "path": None
            }
        
        logger.info(f"Creating folder: '{path}'")
        
        # Resolve the path using PathResolver
        resolver = PathResolver()
        
        # For creation, we need to handle the case where the folder doesn't exist yet
        # Split into parent and new folder name
        path_parts = path.replace('/', '\\').split('\\')
        
        if len(path_parts) == 1:
            # Single folder name, use default directory
            config = PathConfig.load()
            parent_dir = config.default_save_directory
            folder_name = path_parts[0]
            full_path = os.path.join(parent_dir, folder_name)
            logger.debug(f"Using default directory: {parent_dir}")
        else:
            # Multiple parts - resolve parent, then add new folder
            parent_path = '\\'.join(path_parts[:-1])
            folder_name = path_parts[-1]
            
            # Try to resolve parent path
            parent_result = resolver.resolve(parent_path)
            
            if parent_result.success:
                full_path = os.path.join(parent_result.resolved_path, folder_name)
                logger.debug(f"Resolved parent: {parent_result.resolved_path}")
            else:
                # Parent doesn't exist or couldn't be resolved
                # Try to create the full path as-is
                full_path = os.path.abspath(path)
                logger.debug(f"Parent not found, using absolute path: {full_path}")
        
        # Create the folder using os.makedirs (command-line utility)
        os.makedirs(full_path, exist_ok=True)
        
        logger.info(f"✓ Folder created: {full_path}")
        return {
            "success": True,
            "message": f"Folder created successfully: {full_path}",
            "path": full_path
        }
        
    except PermissionError as e:
        # Requirement 10.2: Logging with context for all failures
        error_msg = f"Permission denied when creating folder '{path}': {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "path": None
        }
    except OSError as e:
        error_msg = f"Failed to create folder '{path}': {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "path": None
        }
    except Exception as e:
        error_msg = f"Unexpected error creating folder '{path}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "path": None
        }


def delete_folder(path: str, confirm_non_empty: bool = True) -> Dict[str, any]:
    """
    Delete a folder with safety checks.
    
    Uses command-line: shutil.rmtree() with confirmation for non-empty folders
    
    Args:
        path: Full or fuzzy path to folder to delete
        confirm_non_empty: Whether to require confirmation for non-empty folders
        
    Returns:
        {"success": bool, "message": str, "was_empty": bool}
        
    Requirements: 3.2, 3.5, 10.1, 10.2, 10.4
    """
    try:
        # Requirement 10.1: Descriptive error messages for invalid parameters
        if not path or not path.strip():
            error_msg = "Path cannot be empty. Provide a valid folder path."
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "was_empty": None
            }
        
        logger.info(f"Attempting to delete folder: '{path}'")
        
        # Resolve the path using PathResolver
        resolver = PathResolver()
        result = resolver.resolve(path)
        
        if not result.success:
            # Requirement 10.4: Clear error messages for missing resources
            error_msg = (
                f"Could not resolve path '{path}': {result.error_message}. "
                f"The folder may not exist or the path is invalid."
            )
            logger.warning(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "was_empty": None
            }
        
        full_path = result.resolved_path
        logger.debug(f"Resolved path: {full_path}")
        
        # Check if path exists
        if not os.path.exists(full_path):
            # Requirement 10.4: Clear error messages for missing resources
            error_msg = f"Folder does not exist: {full_path}"
            logger.warning(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "was_empty": None
            }
        
        # Check if it's a directory
        if not os.path.isdir(full_path):
            error_msg = f"Path is not a folder: {full_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "was_empty": None
            }
        
        # Check if folder is empty
        is_empty = len(os.listdir(full_path)) == 0
        logger.debug(f"Folder is {'empty' if is_empty else 'not empty'}")
        
        # Safety check for non-empty folders
        if not is_empty and confirm_non_empty:
            error_msg = (
                f"Folder is not empty: {full_path}. "
                f"Set confirm_non_empty=False to delete anyway."
            )
            logger.warning(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "was_empty": False
            }
        
        # Delete the folder using shutil.rmtree (command-line utility)
        shutil.rmtree(full_path)
        
        logger.info(f"✓ Folder deleted: {full_path}")
        return {
            "success": True,
            "message": f"Folder deleted successfully: {full_path}",
            "was_empty": is_empty
        }
        
    except PermissionError as e:
        # Requirement 10.2: Logging with context for all failures
        error_msg = f"Permission denied when deleting folder '{path}': {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "was_empty": None
        }
    except OSError as e:
        error_msg = f"Failed to delete folder '{path}': {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "was_empty": None
        }
    except Exception as e:
        error_msg = f"Unexpected error deleting folder '{path}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "message": error_msg,
            "was_empty": None
        }


def open_folder(path: str) -> Dict[str, any]:
    """
    Open a folder in Windows Explorer.
    
    Uses: subprocess.Popen(['explorer', path])
    Reuses: PathResolver for fuzzy path matching
    
    Args:
        path: Full or fuzzy path to folder
        
    Returns:
        {"success": bool, "message": str, "path": str}
        
    Requirements: 3.3, 3.5, 8.1
    """
    try:
        if not path or not path.strip():
            return {
                "success": False,
                "message": "Path cannot be empty",
                "path": None
            }
        
        # Resolve the path using PathResolver
        resolver = PathResolver()
        result = resolver.resolve(path)
        
        if not result.success:
            return {
                "success": False,
                "message": f"Could not resolve path: {result.error_message}",
                "path": None
            }
        
        full_path = result.resolved_path
        
        # Check if path exists
        if not os.path.exists(full_path):
            return {
                "success": False,
                "message": f"Folder does not exist: {full_path}",
                "path": None
            }
        
        # Check if it's a directory
        if not os.path.isdir(full_path):
            return {
                "success": False,
                "message": f"Path is not a folder: {full_path}",
                "path": None
            }
        
        # Open folder in Windows Explorer using subprocess
        subprocess.Popen(['explorer', full_path])
        
        return {
            "success": True,
            "message": f"Folder opened successfully: {full_path}",
            "path": full_path
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "message": "Windows Explorer not found (not on Windows?)",
            "path": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to open folder: {str(e)}",
            "path": None
        }


def list_folder(path: str) -> Dict[str, any]:
    """
    List contents of a folder.
    
    Uses: os.listdir()
    
    Args:
        path: Full or fuzzy path to folder
        
    Returns:
        {"success": bool, "contents": List[str], "message": str, "path": str}
        
    Requirements: 3.4, 3.5
    """
    try:
        if not path or not path.strip():
            return {
                "success": False,
                "contents": [],
                "message": "Path cannot be empty",
                "path": None
            }
        
        # Resolve the path using PathResolver
        resolver = PathResolver()
        result = resolver.resolve(path)
        
        if not result.success:
            return {
                "success": False,
                "contents": [],
                "message": f"Could not resolve path: {result.error_message}",
                "path": None
            }
        
        full_path = result.resolved_path
        
        # Check if path exists
        if not os.path.exists(full_path):
            return {
                "success": False,
                "contents": [],
                "message": f"Folder does not exist: {full_path}",
                "path": None
            }
        
        # Check if it's a directory
        if not os.path.isdir(full_path):
            return {
                "success": False,
                "contents": [],
                "message": f"Path is not a folder: {full_path}",
                "path": None
            }
        
        # List folder contents using os.listdir (command-line utility)
        contents = os.listdir(full_path)
        
        # Sort for consistent output
        contents.sort()
        
        return {
            "success": True,
            "contents": contents,
            "message": f"Listed {len(contents)} items in folder: {full_path}",
            "path": full_path
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "contents": [],
            "message": f"Permission denied: {str(e)}",
            "path": None
        }
    except OSError as e:
        return {
            "success": False,
            "contents": [],
            "message": f"Failed to list folder: {str(e)}",
            "path": None
        }
    except Exception as e:
        return {
            "success": False,
            "contents": [],
            "message": f"Unexpected error listing folder: {str(e)}",
            "path": None
        }
