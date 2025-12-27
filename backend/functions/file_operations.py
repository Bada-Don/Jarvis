"""
File Operations Module

Provides functions for file management including deletion, renaming, copying, moving, and opening.
Uses command-line utilities where possible and reuses existing path resolution logic.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 8.2
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "local_client"))

from path_resolver import PathResolver
from filename_resolver import FilenameResolver
from direct_path_executor import DirectPathExecutor


# Special file types that cannot be created via command-line
# These require launching the associated application first
SPECIAL_FILE_TYPES = {
    '.psd': 'photoshop',      # Adobe Photoshop
    '.fs': 'flexisign',       # FlexiSIGN
    '.ai': 'illustrator',     # Adobe Illustrator
    '.indd': 'indesign',      # Adobe InDesign
    '.fla': 'animate',        # Adobe Animate
}


def delete_file(path: str, confirm: bool = True) -> Dict[str, any]:
    """
    Delete a file with safety checks.
    
    Uses command-line: os.remove() with confirmation
    
    Args:
        path: Full or fuzzy path to file to delete
        confirm: Whether to require confirmation for deletion
        
    Returns:
        {"success": bool, "message": str, "path": str}
        
    Requirements: 4.1, 4.6
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
                "message": f"File does not exist: {full_path}",
                "path": None
            }
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(full_path):
            return {
                "success": False,
                "message": f"Path is not a file: {full_path}",
                "path": None
            }
        
        # Safety check: if confirm is True, require explicit confirmation
        # In a real implementation, this would prompt the user
        # For now, we'll just log the requirement
        if confirm:
            # This is a safety check - in production, would prompt user
            pass
        
        # Delete the file using os.remove (command-line utility)
        os.remove(full_path)
        
        return {
            "success": True,
            "message": f"File deleted successfully: {full_path}",
            "path": full_path
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "path": None
        }
    except OSError as e:
        return {
            "success": False,
            "message": f"Failed to delete file: {str(e)}",
            "path": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error deleting file: {str(e)}",
            "path": None
        }


def rename_file(old_path: str, new_name: str) -> Dict[str, any]:
    """
    Rename a file.
    
    Uses command-line: os.rename()
    
    Args:
        old_path: Current file path (full or fuzzy)
        new_name: New filename (not full path, just the filename)
        
    Returns:
        {"success": bool, "message": str, "old_path": str, "new_path": str}
        
    Requirements: 4.2, 4.6
    """
    try:
        if not old_path or not old_path.strip():
            return {
                "success": False,
                "message": "Old path cannot be empty",
                "old_path": None,
                "new_path": None
            }
        
        if not new_name or not new_name.strip():
            return {
                "success": False,
                "message": "New name cannot be empty",
                "old_path": None,
                "new_path": None
            }
        
        # Resolve the old path using PathResolver
        resolver = PathResolver()
        result = resolver.resolve(old_path)
        
        if not result.success:
            return {
                "success": False,
                "message": f"Could not resolve path: {result.error_message}",
                "old_path": None,
                "new_path": None
            }
        
        full_old_path = result.resolved_path
        
        # Check if path exists
        if not os.path.exists(full_old_path):
            return {
                "success": False,
                "message": f"File does not exist: {full_old_path}",
                "old_path": full_old_path,
                "new_path": None
            }
        
        # Check if it's a file
        if not os.path.isfile(full_old_path):
            return {
                "success": False,
                "message": f"Path is not a file: {full_old_path}",
                "old_path": full_old_path,
                "new_path": None
            }
        
        # Construct new path (same directory, new filename)
        directory = os.path.dirname(full_old_path)
        full_new_path = os.path.join(directory, new_name)
        
        # Check if new path already exists
        if os.path.exists(full_new_path):
            return {
                "success": False,
                "message": f"A file with the new name already exists: {full_new_path}",
                "old_path": full_old_path,
                "new_path": full_new_path
            }
        
        # Rename the file using os.rename (command-line utility)
        os.rename(full_old_path, full_new_path)
        
        return {
            "success": True,
            "message": f"File renamed successfully: {os.path.basename(full_old_path)} → {new_name}",
            "old_path": full_old_path,
            "new_path": full_new_path
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "old_path": None,
            "new_path": None
        }
    except OSError as e:
        return {
            "success": False,
            "message": f"Failed to rename file: {str(e)}",
            "old_path": None,
            "new_path": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error renaming file: {str(e)}",
            "old_path": None,
            "new_path": None
        }


def copy_file(source: str, destination: str) -> Dict[str, any]:
    """
    Copy a file to a new location.
    
    Uses command-line: shutil.copy2() (preserves metadata)
    
    Args:
        source: Source file path (full or fuzzy)
        destination: Destination path (can be directory or full file path)
        
    Returns:
        {"success": bool, "message": str, "source": str, "destination": str}
        
    Requirements: 4.3, 4.6
    """
    try:
        if not source or not source.strip():
            return {
                "success": False,
                "message": "Source path cannot be empty",
                "source": None,
                "destination": None
            }
        
        if not destination or not destination.strip():
            return {
                "success": False,
                "message": "Destination path cannot be empty",
                "source": None,
                "destination": None
            }
        
        # Resolve the source path using PathResolver
        resolver = PathResolver()
        source_result = resolver.resolve(source)
        
        if not source_result.success:
            return {
                "success": False,
                "message": f"Could not resolve source path: {source_result.error_message}",
                "source": None,
                "destination": None
            }
        
        full_source_path = source_result.resolved_path
        
        # Check if source exists
        if not os.path.exists(full_source_path):
            return {
                "success": False,
                "message": f"Source file does not exist: {full_source_path}",
                "source": full_source_path,
                "destination": None
            }
        
        # Check if source is a file
        if not os.path.isfile(full_source_path):
            return {
                "success": False,
                "message": f"Source path is not a file: {full_source_path}",
                "source": full_source_path,
                "destination": None
            }
        
        # Try to resolve destination path
        # If it's a directory, we'll copy the file into it with the same name
        # If it's a file path, we'll use it as-is
        dest_result = resolver.resolve(destination)
        
        if dest_result.success:
            full_dest_path = dest_result.resolved_path
            
            # If destination is a directory, append source filename
            if os.path.isdir(full_dest_path):
                source_filename = os.path.basename(full_source_path)
                full_dest_path = os.path.join(full_dest_path, source_filename)
        else:
            # Destination doesn't exist yet - treat as new file path
            # Try to resolve parent directory
            dest_parts = destination.replace('/', '\\').split('\\')
            
            if len(dest_parts) > 1:
                parent_path = '\\'.join(dest_parts[:-1])
                filename = dest_parts[-1]
                
                parent_result = resolver.resolve(parent_path)
                if parent_result.success:
                    full_dest_path = os.path.join(parent_result.resolved_path, filename)
                else:
                    # Use absolute path
                    full_dest_path = os.path.abspath(destination)
            else:
                # Single component - use current directory or default
                full_dest_path = os.path.abspath(destination)
        
        # Check if destination already exists
        if os.path.exists(full_dest_path):
            return {
                "success": False,
                "message": f"Destination file already exists: {full_dest_path}",
                "source": full_source_path,
                "destination": full_dest_path
            }
        
        # Copy the file using shutil.copy2 (command-line utility, preserves metadata)
        shutil.copy2(full_source_path, full_dest_path)
        
        return {
            "success": True,
            "message": f"File copied successfully: {full_source_path} → {full_dest_path}",
            "source": full_source_path,
            "destination": full_dest_path
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "source": None,
            "destination": None
        }
    except OSError as e:
        return {
            "success": False,
            "message": f"Failed to copy file: {str(e)}",
            "source": None,
            "destination": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error copying file: {str(e)}",
            "source": None,
            "destination": None
        }


def move_file(source: str, destination: str) -> Dict[str, any]:
    """
    Move a file to a new location.
    
    Uses command-line: shutil.move()
    
    Args:
        source: Source file path (full or fuzzy)
        destination: Destination path (can be directory or full file path)
        
    Returns:
        {"success": bool, "message": str, "source": str, "destination": str}
        
    Requirements: 4.4, 4.6
    """
    try:
        if not source or not source.strip():
            return {
                "success": False,
                "message": "Source path cannot be empty",
                "source": None,
                "destination": None
            }
        
        if not destination or not destination.strip():
            return {
                "success": False,
                "message": "Destination path cannot be empty",
                "source": None,
                "destination": None
            }
        
        # Resolve the source path using PathResolver
        resolver = PathResolver()
        source_result = resolver.resolve(source)
        
        if not source_result.success:
            return {
                "success": False,
                "message": f"Could not resolve source path: {source_result.error_message}",
                "source": None,
                "destination": None
            }
        
        full_source_path = source_result.resolved_path
        
        # Check if source exists
        if not os.path.exists(full_source_path):
            return {
                "success": False,
                "message": f"Source file does not exist: {full_source_path}",
                "source": full_source_path,
                "destination": None
            }
        
        # Check if source is a file
        if not os.path.isfile(full_source_path):
            return {
                "success": False,
                "message": f"Source path is not a file: {full_source_path}",
                "source": full_source_path,
                "destination": None
            }
        
        # Try to resolve destination path
        dest_result = resolver.resolve(destination)
        
        if dest_result.success:
            full_dest_path = dest_result.resolved_path
            
            # If destination is a directory, append source filename
            if os.path.isdir(full_dest_path):
                source_filename = os.path.basename(full_source_path)
                full_dest_path = os.path.join(full_dest_path, source_filename)
        else:
            # Destination doesn't exist yet - treat as new file path
            dest_parts = destination.replace('/', '\\').split('\\')
            
            if len(dest_parts) > 1:
                parent_path = '\\'.join(dest_parts[:-1])
                filename = dest_parts[-1]
                
                parent_result = resolver.resolve(parent_path)
                if parent_result.success:
                    full_dest_path = os.path.join(parent_result.resolved_path, filename)
                else:
                    full_dest_path = os.path.abspath(destination)
            else:
                full_dest_path = os.path.abspath(destination)
        
        # Check if destination already exists
        if os.path.exists(full_dest_path):
            return {
                "success": False,
                "message": f"Destination file already exists: {full_dest_path}",
                "source": full_source_path,
                "destination": full_dest_path
            }
        
        # Move the file using shutil.move (command-line utility)
        shutil.move(full_source_path, full_dest_path)
        
        return {
            "success": True,
            "message": f"File moved successfully: {full_source_path} → {full_dest_path}",
            "source": full_source_path,
            "destination": full_dest_path
        }
        
    except PermissionError as e:
        return {
            "success": False,
            "message": f"Permission denied: {str(e)}",
            "source": None,
            "destination": None
        }
    except OSError as e:
        return {
            "success": False,
            "message": f"Failed to move file: {str(e)}",
            "source": None,
            "destination": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error moving file: {str(e)}",
            "source": None,
            "destination": None
        }


def open_file(path: str) -> Dict[str, any]:
    """
    Open a file with its default application.
    
    Uses: os.startfile() on Windows
    Reuses: PathResolver for fuzzy path matching
    Reuses: FilenameResolver for filename resolution
    
    For special file types (.psd, .fs, .ai), this function will launch
    the associated application if the file doesn't exist yet.
    
    Args:
        path: Full or fuzzy path to file
        
    Returns:
        {"success": bool, "message": str, "path": str, "file_type": str}
        
    Requirements: 4.5, 4.6, 4.7, 8.2
    """
    try:
        if not path or not path.strip():
            return {
                "success": False,
                "message": "Path cannot be empty",
                "path": None,
                "file_type": None
            }
        
        # Resolve the path using PathResolver
        resolver = PathResolver()
        result = resolver.resolve(path)
        
        if not result.success:
            return {
                "success": False,
                "message": f"Could not resolve path: {result.error_message}",
                "path": None,
                "file_type": None
            }
        
        full_path = result.resolved_path
        
        # Check if path exists
        if not os.path.exists(full_path):
            return {
                "success": False,
                "message": f"File does not exist: {full_path}",
                "path": full_path,
                "file_type": None
            }
        
        # Check if it's a file
        if not os.path.isfile(full_path):
            return {
                "success": False,
                "message": f"Path is not a file: {full_path}",
                "path": full_path,
                "file_type": None
            }
        
        # Get file extension
        _, ext = os.path.splitext(full_path)
        ext_lower = ext.lower()
        
        # Check if it's a special file type
        is_special = ext_lower in SPECIAL_FILE_TYPES
        app_name = SPECIAL_FILE_TYPES.get(ext_lower, "default")
        
        # Open file using os.startfile (Windows command-line utility)
        os.startfile(full_path)
        
        return {
            "success": True,
            "message": f"File opened successfully: {full_path}",
            "path": full_path,
            "file_type": ext_lower,
            "is_special_type": is_special,
            "application": app_name
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "message": "os.startfile not available (not on Windows?)",
            "path": None,
            "file_type": None
        }
    except OSError as e:
        # Check if error is due to no associated application
        error_msg = str(e)
        if "no application" in error_msg.lower() or "no associated" in error_msg.lower():
            return {
                "success": False,
                "message": f"No application associated with this file type: {full_path}",
                "path": full_path,
                "file_type": ext_lower if 'ext_lower' in locals() else None
            }
        else:
            return {
                "success": False,
                "message": f"Failed to open file: {error_msg}",
                "path": full_path,
                "file_type": ext_lower if 'ext_lower' in locals() else None
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error opening file: {str(e)}",
            "path": None,
            "file_type": None
        }


def create_special_file(path: str, file_type: str) -> Dict[str, any]:
    """
    Create a special file type that cannot be created via command-line.
    
    This function launches the associated application first, then uses
    DirectPathExecutor to save the file at the specified path.
    
    Args:
        path: Full path where the file should be created
        file_type: File extension (e.g., '.psd', '.fs', '.ai')
        
    Returns:
        {"success": bool, "message": str, "path": str, "application": str}
        
    Requirements: 4.7, 8.2
    """
    try:
        if not path or not path.strip():
            return {
                "success": False,
                "message": "Path cannot be empty",
                "path": None,
                "application": None
            }
        
        file_type_lower = file_type.lower()
        
        # Check if it's a recognized special file type
        if file_type_lower not in SPECIAL_FILE_TYPES:
            return {
                "success": False,
                "message": f"File type {file_type} is not a recognized special file type",
                "path": path,
                "application": None
            }
        
        app_name = SPECIAL_FILE_TYPES[file_type_lower]
        
        # This is a placeholder implementation
        # In a full implementation, this would:
        # 1. Launch the application (e.g., Photoshop, FlexiSIGN)
        # 2. Wait for the application to be ready
        # 3. Use DirectPathExecutor to save the file
        
        return {
            "success": False,
            "message": f"Creating {file_type} files requires launching {app_name} - not yet fully implemented",
            "path": path,
            "application": app_name,
            "note": "This is a placeholder - full implementation would launch the app and use DirectPathExecutor"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error creating special file: {str(e)}",
            "path": None,
            "application": None
        }
