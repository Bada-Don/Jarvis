"""
OCR Service Module for Direct Path Automation

This module provides OCR (Optical Character Recognition) capabilities for
text-based element detection and clicking. It uses EasyOCR for accurate
text detection on screen.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import math
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import numpy as np

# Import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ Warning: EasyOCR not available. Install with: pip install easyocr")


@dataclass
class TextLocation:
    """
    Location of detected text on screen.
    
    Represents a text element found via OCR with its bounding box,
    confidence score, and calculated center point.
    
    Attributes:
        text: The detected text string
        bbox: Bounding box as (x1, y1, x2, y2) - top-left and bottom-right corners
        confidence: OCR confidence score (0.0 to 1.0)
        center: Calculated center point (x, y) of the bounding box
    
    Requirements: 4.2
    """
    text: str
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    center: Tuple[int, int] = field(init=False)
    
    def __post_init__(self):
        """Calculate center point from bounding box."""
        x1, y1, x2, y2 = self.bbox
        # Property 6: Bounding Box Center Calculation
        # Center = ((x1+x2)/2, (y1+y2)/2)
        self.center = ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def distance_to(self, point: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance from center to a given point.
        
        Args:
            point: Target point as (x, y)
        
        Returns:
            Euclidean distance from center to point
        """
        return math.sqrt(
            (self.center[0] - point[0]) ** 2 + 
            (self.center[1] - point[1]) ** 2
        )
    
    def distance_to_region_center(self, region: Tuple[int, int, int, int]) -> float:
        """
        Calculate distance from center to the center of a region.
        
        Args:
            region: Region as (x1, y1, x2, y2)
        
        Returns:
            Euclidean distance from center to region center
        """
        rx1, ry1, rx2, ry2 = region
        region_center = ((rx1 + rx2) // 2, (ry1 + ry2) // 2)
        return self.distance_to(region_center)
    
    def is_within_region(self, region: Tuple[int, int, int, int]) -> bool:
        """
        Check if the text location is within a given region.
        
        Args:
            region: Region as (x1, y1, x2, y2)
        
        Returns:
            True if center is within the region
        """
        rx1, ry1, rx2, ry2 = region
        return (rx1 <= self.center[0] <= rx2 and 
                ry1 <= self.center[1] <= ry2)


def calculate_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
    """
    Calculate the center point of a bounding box.
    
    This is a standalone function for Property 6 testing.
    
    Args:
        bbox: Bounding box as (x1, y1, x2, y2)
    
    Returns:
        Center point as (x, y)
    
    Requirements: 4.2
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) // 2, (y1 + y2) // 2)


def find_closest_to_region(
    locations: List[TextLocation], 
    region: Tuple[int, int, int, int]
) -> Optional[TextLocation]:
    """
    Find the text location closest to the center of a region.
    
    This is a standalone function for Property 7 testing.
    
    Args:
        locations: List of TextLocation objects
        region: Target region as (x1, y1, x2, y2)
    
    Returns:
        TextLocation closest to region center, or None if list is empty
    
    Requirements: 4.3
    """
    if not locations:
        return None
    
    # Calculate region center
    rx1, ry1, rx2, ry2 = region
    region_center = ((rx1 + rx2) // 2, (ry1 + ry2) // 2)
    
    # Find location with minimum distance to region center
    closest = min(locations, key=lambda loc: loc.distance_to(region_center))
    return closest


class OCRService:
    """
    OCR service for text-based element detection using EasyOCR.
    
    Provides methods to detect text in images and find specific text
    elements for clicking. Uses EasyOCR for accurate text detection.
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    
    def __init__(self, confidence_threshold: float = 0.5, languages: List[str] = None):
        """
        Initialize OCR service with EasyOCR.
        
        Args:
            confidence_threshold: Minimum confidence for text detection (0.0 to 1.0)
            languages: List of language codes (default: ['en'] for English)
        """
        self.confidence_threshold = confidence_threshold
        self.languages = languages or ['en']
        
        # Verify EasyOCR is available
        if not EASYOCR_AVAILABLE:
            raise RuntimeError(
                "EasyOCR is not available. Install with: pip install easyocr"
            )
        
        # Initialize EasyOCR reader (lazy loading)
        self._reader = None
    
    @property
    def reader(self):
        """Lazy load EasyOCR reader (initialization is slow)."""
        if self._reader is None:
            print(f"Initializing EasyOCR with languages: {self.languages} (CPU mode)...")
            self._reader = easyocr.Reader(self.languages, gpu=False)
            print("EasyOCR initialized successfully")
        return self._reader
    
    def detect_text(self, image: np.ndarray) -> List[TextLocation]:
        """
        Detect all text in an image with bounding boxes using EasyOCR.
        
        Args:
            image: Image as numpy array (BGR format from OpenCV)
        
        Returns:
            List of TextLocation objects for all detected text
        
        Requirements: 4.1
        """
        # EasyOCR expects RGB format
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Run EasyOCR
        # Result format: [([[x1,y1], [x2,y2], [x3,y3], [x4,y4]], text, confidence), ...]
        results = self.reader.readtext(rgb_image)
        
        locations = []
        
        for detection in results:
            bbox_points, text, confidence = detection
            
            # Skip empty text or low confidence
            text = text.strip()
            if not text or confidence < self.confidence_threshold:
                continue
            
            # Convert polygon points to bounding box (x1, y1, x2, y2)
            x_coords = [point[0] for point in bbox_points]
            y_coords = [point[1] for point in bbox_points]
            
            bbox = (
                int(min(x_coords)),  # x1
                int(min(y_coords)),  # y1
                int(max(x_coords)),  # x2
                int(max(y_coords))   # y2
            )
            
            locations.append(TextLocation(
                text=text,
                bbox=bbox,
                confidence=float(confidence)
            ))
        
        return locations
    
    def _combine_adjacent_words(self, locations: List[TextLocation], max_distance: int = 50) -> List[TextLocation]:
        """
        Combine adjacent words into multi-word phrases.
        
        This helps match multi-word text like "JARVIS Test" when OCR detects
        them as separate words "JARVIS" and "Test".
        
        Args:
            locations: List of TextLocation objects
            max_distance: Maximum horizontal distance to consider words adjacent
        
        Returns:
            List with original locations plus combined multi-word locations
        """
        if not locations:
            return locations
        
        # Sort by vertical position (y), then horizontal (x)
        sorted_locs = sorted(locations, key=lambda loc: (loc.bbox[1], loc.bbox[0]))
        
        combined = []
        
        # Try combining consecutive words on the same line
        for i in range(len(sorted_locs) - 1):
            loc1 = sorted_locs[i]
            loc2 = sorted_locs[i + 1]
            
            # Check if words are on roughly the same line (similar y-coordinate)
            y1 = (loc1.bbox[1] + loc1.bbox[3]) / 2
            y2 = (loc2.bbox[1] + loc2.bbox[3]) / 2
            
            if abs(y1 - y2) > 20:  # Not on same line
                continue
            
            # Check if words are close horizontally
            x1_end = loc1.bbox[2]
            x2_start = loc2.bbox[0]
            distance = x2_start - x1_end
            
            if 0 <= distance <= max_distance:
                # Combine the two words
                combined_text = f"{loc1.text} {loc2.text}"
                combined_bbox = (
                    loc1.bbox[0],  # leftmost x
                    min(loc1.bbox[1], loc2.bbox[1]),  # topmost y
                    loc2.bbox[2],  # rightmost x
                    max(loc1.bbox[3], loc2.bbox[3])   # bottommost y
                )
                combined_confidence = (loc1.confidence + loc2.confidence) / 2
                
                combined.append(TextLocation(
                    text=combined_text,
                    bbox=combined_bbox,
                    confidence=combined_confidence
                ))
        
        # Return original locations plus combined ones
        return locations + combined
    
    def find_text(
        self, 
        image: np.ndarray, 
        target_text: str, 
        fuzzy: bool = True,
        case_sensitive: bool = False
    ) -> List[TextLocation]:
        """
        Find specific text in an image.
        
        Searches for text that matches or contains the target string.
        Automatically combines adjacent words to match multi-word phrases.
        
        Args:
            image: Image as numpy array (BGR format)
            target_text: Text to search for
            fuzzy: If True, match partial text (contains). If False, exact match.
            case_sensitive: If True, match case exactly
        
        Returns:
            List of TextLocation objects matching the target text
        
        Requirements: 4.1, 4.2
        """
        all_text = self.detect_text(image)
        
        # If target has multiple words, combine adjacent detected words
        if ' ' in target_text:
            all_text = self._combine_adjacent_words(all_text)
        
        # Normalize target for comparison
        target = target_text if case_sensitive else target_text.lower()
        
        exact_matches = []
        good_matches = []  # Partial or fuzzy matches
        
        for location in all_text:
            detected = location.text if case_sensitive else location.text.lower()
            
            if fuzzy:
                # Check for exact match first
                if detected == target:
                    exact_matches.append(location)
                # Check for partial match (substring) or fuzzy match
                elif target in detected or detected in target:
                    # Calculate match quality (prefer longer matches)
                    match_quality = len(detected) / len(target) if len(target) > 0 else 0
                    good_matches.append((match_quality, location))
                elif self._is_fuzzy_match(target, detected):
                    # Fuzzy matches get slightly lower quality score
                    match_quality = 0.8 * len(detected) / len(target) if len(target) > 0 else 0
                    good_matches.append((match_quality, location))
            else:
                # Exact match only
                if detected == target:
                    exact_matches.append(location)
        
        # Return exact matches if found
        if exact_matches:
            return exact_matches
        
        # Sort good matches by quality (prefer matches closer to target length)
        if good_matches:
            # Sort by how close the match length is to target length
            # Prefer matches that are closer to the target length
            good_matches.sort(key=lambda x: abs(1.0 - x[0]))
            return [loc for _, loc in good_matches]
        
        return []
    
    def _is_fuzzy_match(self, target: str, detected: str, threshold: float = 0.7) -> bool:
        """
        Check if two strings are similar enough (handles OCR errors).
        
        Uses a simple character-based similarity metric.
        
        Args:
            target: Target string
            detected: Detected string
            threshold: Minimum similarity ratio (0.0 to 1.0)
        
        Returns:
            True if strings are similar enough
        """
        # Simple Levenshtein-like similarity
        # Count matching characters in similar positions
        if not target or not detected:
            return False
        
        # If lengths are very different, not a match
        len_diff = abs(len(target) - len(detected))
        if len_diff > max(len(target), len(detected)) * 0.3:
            return False
        
        # Count matching characters
        matches = 0
        min_len = min(len(target), len(detected))
        
        for i in range(min_len):
            if target[i] == detected[i]:
                matches += 1
        
        # Calculate similarity ratio
        similarity = matches / max(len(target), len(detected))
        
        return similarity >= threshold
    
    def find_text_in_region(
        self, 
        image: np.ndarray, 
        target_text: str,
        region: Tuple[int, int, int, int],
        fuzzy: bool = True,
        case_sensitive: bool = False
    ) -> Optional[TextLocation]:
        """
        Find text within a specific screen region.
        
        Searches for text and returns the match closest to the region center.
        
        Args:
            image: Image as numpy array (BGR format)
            target_text: Text to search for
            region: Search region as (x1, y1, x2, y2)
            fuzzy: If True, match partial text
            case_sensitive: If True, match case exactly
        
        Returns:
            TextLocation closest to region center, or None if not found
        
        Requirements: 4.2, 4.3
        """
        # Find all matches
        matches = self.find_text(image, target_text, fuzzy, case_sensitive)
        
        if not matches:
            return None
        
        # Filter to matches within or near the region
        # First try matches within the region
        within_region = [m for m in matches if m.is_within_region(region)]
        
        if within_region:
            # Return the one closest to region center
            return find_closest_to_region(within_region, region)
        
        # If no matches within region, return closest overall
        # Property 7: Closest Text Selection
        return find_closest_to_region(matches, region)
    
    def get_all_detected_text(self, image: np.ndarray) -> List[str]:
        """
        Get a list of all detected text strings.
        
        Useful for error reporting when target text is not found.
        
        Args:
            image: Image as numpy array (BGR format)
        
        Returns:
            List of detected text strings
        
        Requirements: 4.4
        """
        locations = self.detect_text(image)
        return [loc.text for loc in locations]

