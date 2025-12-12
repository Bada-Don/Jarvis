"""
Path Resolver - Resolve file/folder paths with fuzzy matching

Resolves complete paths by fuzzy matching each component of the path.
Handles typos, case differences, and partial names.

Example:
    "desktop/new brif case/maan 22.pdf"
    → "C:\\Users\\harsh\\OneDrive\\Desktop\\New Briefcase\\Maan 22.pdf"
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
from filename_resolver import FilenameResolver


@dataclass
class PathResolveResult:
    """Result of path resolution."""
    success: bool
    resolved_path: Optional[str] = None
    error_message: Optional[str] = None
    resolution_steps: List[str] = None  # Show how path was resolved
    
    def __post_init__(self):
        if self.resolution_steps is None:
            self.resolution_steps = []


class PathResolver:
    """
    Resolves file/folder paths with fuzzy matching on each component.
    
    Supports:
    - Absolute paths: "C:\\Users\\harsh\\Desktop\\file.txt"
    - Relative to home: "desktop/folder/file.txt"
    - Special folders: "desktop", "documents", "downloads"
    """
    
    # Known special folders
    SPECIAL_FOLDERS = {
        'desktop': 'C:\\Users\\harsh\\OneDrive\\Desktop',
        'documents': 'C:\\Users\\harsh\\Documents',
        'downloads': 'C:\\Users\\harsh\\Downloads',
        'onedrive': 'C:\\Users\\harsh\\OneDrive',
        'home': 'C:\\Users\\harsh',
        'stickers': 'D:\\Stickers\\New Briefcase',
    }
    
    def __init__(self):
        """Initialize path resolver."""
        self.filename_resolver = FilenameResolver()
    
    def resolve(self, path_query: str) -> PathResolveResult:
        """
        Resolve a path query to an actual filesystem path.
        
        Args:
            path_query: Path to resolve (can be fuzzy)
                       Examples: "desktop/jarvis test"
                                "documents/report.pdf"
                                "C:\\Users\\harsh\\Desktop\\file.txt"
        
        Returns:
            PathResolveResult with resolved path
        """
        if not path_query or not path_query.strip():
            return PathResolveResult(
                success=False,
                error_message="Path query cannot be empty"
            )
        
        query = path_query.strip()
        resolution_steps = []
        
        # Normalize path separators
        query = query.replace('/', '\\')
        
        # Split into components
        components = [c for c in query.split('\\') if c]
        
        if not components:
            return PathResolveResult(
                success=False,
                error_message="Invalid path query"
            )
        
        # Check if absolute path
        if len(components[0]) == 2 and components[0][1] == ':':
            # Absolute path like C:\...
            current_dir = components[0] + '\\'
            components = components[1:]
            resolution_steps.append(f"Starting from: {current_dir}")
        else:
            # Check if first component is a special folder
            first_lower = components[0].lower()
            
            if first_lower in self.SPECIAL_FOLDERS:
                current_dir = self.SPECIAL_FOLDERS[first_lower]
                components = components[1:]
                resolution_steps.append(f"Resolved '{components[0] if components else first_lower}' → {current_dir}")
            else:
                # Try to match against special folders
                best_match = None
                best_score = 0.0
                
                for folder_name, folder_path in self.SPECIAL_FOLDERS.items():
                    score = self.filename_resolver._calculate_similarity(first_lower, folder_name)
                    if score > best_score:
                        best_score = score
                        best_match = (folder_name, folder_path)
                
                if best_match and best_score > 0.6:
                    current_dir = best_match[1]
                    components = components[1:]
                    resolution_steps.append(f"Fuzzy matched '{first_lower}' → {best_match[0]} ({current_dir})")
                else:
                    # Default to Desktop
                    current_dir = self.SPECIAL_FOLDERS['desktop']
                    resolution_steps.append(f"Defaulting to Desktop: {current_dir}")
        
        # Resolve each component
        for i, component in enumerate(components):
            is_last = (i == len(components) - 1)
            
            # Check if current_dir exists
            if not os.path.exists(current_dir):
                return PathResolveResult(
                    success=False,
                    error_message=f"Directory does not exist: {current_dir}",
                    resolution_steps=resolution_steps
                )
            
            # Resolve this component
            result = self.filename_resolver.resolve(current_dir, component)
            
            if not result.success:
                return PathResolveResult(
                    success=False,
                    error_message=f"Could not resolve '{component}' in {current_dir}: {result.error_message}",
                    resolution_steps=resolution_steps
                )
            
            # Update current path
            current_dir = result.full_path
            resolution_steps.append(f"  [{i+1}] '{component}' → '{result.resolved_name}' (confidence: {result.confidence:.0f}%)")
        
        # Final path
        return PathResolveResult(
            success=True,
            resolved_path=current_dir,
            resolution_steps=resolution_steps
        )


def resolve_path(path_query: str) -> PathResolveResult:
    """
    Convenience function to resolve a path.
    
    Args:
        path_query: Path to resolve
    
    Returns:
        PathResolveResult with resolved path
    """
    resolver = PathResolver()
    return resolver.resolve(path_query)
