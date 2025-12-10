"""
OCR Service Module for Direct Path Automation

This module provides OCR (Optical Character Recognition) capabilities for
text-based element detection and clicking. It uses Windows OCR or pytesseract
to detect text on screen and locate UI elements by their text labels.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import math
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import numpy as np

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Try to import Windows OCR (winocr)
try:
    import winocr
    WINOCR_AVAILABLE = True
except ImportError:
    WINOCR_AVAILABLE = False


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
    OCR service for text-based element detection.
    
    Provides methods to detect text in images and find specific text
    elements for clicking. Supports both Windows OCR and pytesseract.
    
    Requirements: 4.1, 4.2, 4.3, 4.4
    """
    
    def __init__(self, confidence_threshold: float = 0.5, use_windows_ocr: bool = True):
        """
        Initialize OCR service.
        
        Args:
            confidence_threshold: Minimum confidence for text detection (0.0 to 1.0)
            use_windows_ocr: Prefer Windows OCR over pytesseract if available
        """
        self.confidence_threshold = confidence_threshold
        self.use_windows_ocr = use_windows_ocr and WINOCR_AVAILABLE
        
        # Verify at least one OCR engine is available
        if not PYTESSERACT_AVAILABLE and not WINOCR_AVAILABLE:
            raise RuntimeError(
                "No OCR engine available. Install pytesseract or winocr."
            )
    
    def detect_text(self, image: np.ndarray) -> List[TextLocation]:
        """
        Detect all text in an image with bounding boxes.
        
        Captures a screenshot and performs OCR to locate all text elements.
        
        Args:
            image: Image as numpy array (BGR format from OpenCV)
        
        Returns:
            List of TextLocation objects for all detected text
        
        Requirements: 4.1
        """
        if self.use_windows_ocr:
            return self._detect_text_windows(image)
        else:
            return self._detect_text_tesseract(image)
    
    def _detect_text_tesseract(self, image: np.ndarray) -> List[TextLocation]:
        """
        Detect text using pytesseract.
        
        Args:
            image: Image as numpy array (BGR format)
        
        Returns:
            List of TextLocation objects
        """
        if not PYTESSERACT_AVAILABLE:
            raise RuntimeError("pytesseract is not available")
        
        # Convert BGR to RGB for PIL
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Get detailed OCR data
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
        
        locations = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = float(data['conf'][i])
            
            # Skip empty text or low confidence
            if not text or conf < 0:
                continue
            
            # Normalize confidence to 0-1 range (tesseract uses 0-100)
            confidence = conf / 100.0
            
            if confidence < self.confidence_threshold:
                continue
            
            # Extract bounding box
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            
            bbox = (x, y, x + w, y + h)
            
            locations.append(TextLocation(
                text=text,
                bbox=bbox,
                confidence=confidence
            ))
        
        return locations
    
    def _detect_text_windows(self, image: np.ndarray) -> List[TextLocation]:
        """
        Detect text using Windows OCR.
        
        Args:
            image: Image as numpy array (BGR format)
        
        Returns:
            List of TextLocation objects
        """
        # Fall back to tesseract if Windows OCR not available
        if not WINOCR_AVAILABLE:
            return self._detect_text_tesseract(image)
        
        # Convert BGR to RGB for PIL
        import cv2
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        # Run Windows OCR
        import asyncio
        
        async def run_ocr():
            return await winocr.recognize_pil(pil_image, 'en')
        
        # Run async OCR
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_ocr())
        
        locations = []
        
        for line in result.lines:
            for word in line.words:
                text = word.text.strip()
                if not text:
                    continue
                
                # Windows OCR provides bounding box
                bbox = (
                    int(word.bounding_rect.x),
                    int(word.bounding_rect.y),
                    int(word.bounding_rect.x + word.bounding_rect.width),
                    int(word.bounding_rect.y + word.bounding_rect.height)
                )
                
                # Windows OCR doesn't provide confidence, use 1.0
                confidence = 1.0
                
                locations.append(TextLocation(
                    text=text,
                    bbox=bbox,
                    confidence=confidence
                ))
        
        return locations
    
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
        
        # Normalize target for comparison
        target = target_text if case_sensitive else target_text.lower()
        
        matches = []
        for location in all_text:
            detected = location.text if case_sensitive else location.text.lower()
            
            if fuzzy:
                # Partial match - target is contained in detected text
                # or detected text is contained in target
                if target in detected or detected in target:
                    matches.append(location)
            else:
                # Exact match
                if detected == target:
                    matches.append(location)
        
        return matches
    
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

