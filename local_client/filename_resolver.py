"""
Filename Resolver - Fuzzy match filenames without UI/OCR

This module provides fuzzy filename matching by reading directory contents
directly from the filesystem, bypassing UI and OCR completely.

Advantages:
- Zero OCR dependency
- Zero UI dependency
- Works regardless of Explorer view mode
- Absolute correctness in spelling, casing, spacing
- Fast and reliable
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class ResolveResult:
    """Result of filename resolution."""
    success: bool
    resolved_name: Optional[str] = None
    full_path: Optional[str] = None
    confidence: float = 0.0
    error_message: Optional[str] = None
    candidates: List[Tuple[str, float]] = None  # List of (filename, score) tuples
    
    def __post_init__(self):
        if self.candidates is None:
            self.candidates = []


class FilenameResolver:
    """
    Resolves approximate filenames to exact matches using fuzzy matching.
    
    Uses Levenshtein distance for fuzzy matching to handle:
    - Typos
    - Partial names
    - Case differences
    - Spacing differences
    """
    
    def __init__(self):
        """Initialize the filename resolver."""
        pass
    
    def resolve(
        self, 
        directory: str, 
        approximate_query: str,
        top_n: int = 5
    ) -> ResolveResult:
        """
        Resolve an approximate filename to the best match in a directory.
        
        Args:
            directory: Directory path to search in
            approximate_query: Approximate filename to match
            top_n: Number of top candidates to return
        
        Returns:
            ResolveResult with the best match and candidates
        """
        # Validate directory
        if not directory:
            return ResolveResult(
                success=False,
                error_message="Directory path cannot be empty"
            )
        
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return ResolveResult(
                success=False,
                error_message=f"Directory does not exist: {directory}"
            )
        
        if not dir_path.is_dir():
            return ResolveResult(
                success=False,
                error_message=f"Path is not a directory: {directory}"
            )
        
        # Validate query
        if not approximate_query or not approximate_query.strip():
            return ResolveResult(
                success=False,
                error_message="Query cannot be empty"
            )
        
        query = approximate_query.strip()
        
        # Get all items in directory
        try:
            items = list(dir_path.iterdir())
        except PermissionError:
            return ResolveResult(
                success=False,
                error_message=f"Permission denied accessing directory: {directory}"
            )
        except Exception as e:
            return ResolveResult(
                success=False,
                error_message=f"Error reading directory: {str(e)}"
            )
        
        if not items:
            return ResolveResult(
                success=False,
                error_message=f"Directory is empty: {directory}"
            )
        
        # Score each item
        scored_items = []
        for item in items:
            name = item.name
            score = self._calculate_similarity(query, name)
            scored_items.append((name, score, str(item)))
        
        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Get top candidates
        candidates = [(name, score) for name, score, _ in scored_items[:top_n]]
        
        # Best match
        best_name, best_score, best_path = scored_items[0]
        
        # Determine if match is good enough
        # Score > 0.6 is generally a good match
        if best_score < 0.3:
            return ResolveResult(
                success=False,
                error_message=f"No good match found for '{query}' (best: '{best_name}' with score {best_score:.2f})",
                candidates=candidates
            )
        
        return ResolveResult(
            success=True,
            resolved_name=best_name,
            full_path=best_path,
            confidence=best_score * 100,  # Convert to percentage
            candidates=candidates
        )
    
    def _calculate_similarity(self, query: str, target: str) -> float:
        """
        Calculate similarity score between query and target.
        
        Uses multiple metrics:
        1. Exact match (case-insensitive)
        2. Substring match
        3. Levenshtein distance
        4. Token-based matching
        
        Args:
            query: Query string
            target: Target filename
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        query_lower = query.lower()
        target_lower = target.lower()
        
        # Exact match (case-insensitive)
        if query_lower == target_lower:
            return 1.0
        
        # Exact substring match
        if query_lower in target_lower:
            # Score based on how much of the target is matched
            return 0.8 + (0.2 * len(query_lower) / len(target_lower))
        
        # Reverse substring (target in query)
        if target_lower in query_lower:
            return 0.7 + (0.2 * len(target_lower) / len(query_lower))
        
        # Token-based matching (for multi-word names)
        query_tokens = set(query_lower.split())
        target_tokens = set(target_lower.split())
        
        if query_tokens and target_tokens:
            common_tokens = query_tokens & target_tokens
            if common_tokens:
                token_score = len(common_tokens) / max(len(query_tokens), len(target_tokens))
                if token_score > 0.5:
                    return 0.6 + (0.3 * token_score)
        
        # Levenshtein distance
        distance = self._levenshtein_distance(query_lower, target_lower)
        max_len = max(len(query_lower), len(target_lower))
        
        if max_len == 0:
            return 0.0
        
        # Normalize to 0-1 range
        similarity = 1.0 - (distance / max_len)
        
        # Scale down Levenshtein-only matches
        return similarity * 0.6
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.
        
        Args:
            s1: First string
            s2: Second string
        
        Returns:
            Edit distance (number of operations to transform s1 to s2)
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]


def resolve_filename(directory: str, approximate_query: str) -> ResolveResult:
    """
    Convenience function to resolve a filename.
    
    Args:
        directory: Directory path to search in
        approximate_query: Approximate filename to match
    
    Returns:
        ResolveResult with the best match
    """
    resolver = FilenameResolver()
    return resolver.resolve(directory, approximate_query)
