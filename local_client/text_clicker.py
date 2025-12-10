"""
Text-Based Clicker Module for Direct Path Automation

This module provides text-based clicking capabilities using OCR to find
and click on UI elements by their text labels. This approach reduces
reliance on expensive vision model calls.

Requirements: 4.1, 4.2, 4.3, 4.4, 3.3
"""

import time
from dataclasses import dataclass
from typing import Optional, List, Tuple

import pyautogui

# Configure pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from ocr_service import OCRService, TextLocation
    OCR_SERVICE_AVAILABLE = True
except ImportError:
    OCR_SERVICE_AVAILABLE = False


@dataclass
class ClickResult:
    """
    Result of a text-based click operation.
    
    Attributes:
        success: Whether the click was performed successfully
        target_text: The text that was searched for
        clicked_location: The (x, y) coordinates where the click occurred, or None if failed
        all_matches: List of all TextLocation objects that matched the target
        error_message: Description of the error if the operation failed
    
    Requirements: 4.4
    """
    success: bool
    target_text: str
    clicked_location: Optional[Tuple[int, int]]
    all_matches: List['TextLocation']
    error_message: Optional[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'target_text': self.target_text,
            'clicked_location': list(self.clicked_location) if self.clicked_location else None,
            'all_matches': [
                {
                    'text': m.text,
                    'bbox': list(m.bbox),
                    'confidence': m.confidence,
                    'center': list(m.center)
                }
                for m in self.all_matches
            ],
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClickResult':
        """Create from dictionary."""
        # Note: all_matches will be empty when deserializing since we don't
        # have the full TextLocation objects
        return cls(
            success=data['success'],
            target_text=data['target_text'],
            clicked_location=tuple(data['clicked_location']) if data['clicked_location'] else None,
            all_matches=[],  # Cannot fully reconstruct TextLocation objects
            error_message=data.get('error_message')
        )


def create_failure_result(
    target_text: str,
    error_message: str,
    all_matches: Optional[List['TextLocation']] = None
) -> ClickResult:
    """
    Create a failure ClickResult with proper error reporting.
    
    This is a helper function for Property 8 testing.
    
    Args:
        target_text: The text that was searched for
        error_message: Description of the failure
        all_matches: Optional list of all detected text (for debugging)
    
    Returns:
        ClickResult indicating failure with error details
    
    Requirements: 4.4
    """
    return ClickResult(
        success=False,
        target_text=target_text,
        clicked_location=None,
        all_matches=all_matches or [],
        error_message=error_message
    )


def create_success_result(
    target_text: str,
    clicked_location: Tuple[int, int],
    all_matches: List['TextLocation']
) -> ClickResult:
    """
    Create a success ClickResult.
    
    Args:
        target_text: The text that was searched for
        clicked_location: The (x, y) coordinates where the click occurred
        all_matches: List of all matching TextLocation objects
    
    Returns:
        ClickResult indicating success
    """
    return ClickResult(
        success=True,
        target_text=target_text,
        clicked_location=clicked_location,
        all_matches=all_matches,
        error_message=None
    )


class TextBasedClicker:
    """
    Click on elements by finding their text on screen using OCR.
    
    This class provides methods to locate UI elements by their text labels
    and perform clicks at the center of the text's bounding box.
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 3.3
    """
    
    # Default region for File Explorer file list (approximate)
    # This covers the main content area where files are displayed
    FILE_LIST_REGION = (200, 150, 1200, 800)
    
    # Timing configuration
    DELAY_AFTER_CLICK = 0.3
    DELAY_BETWEEN_CLICKS = 0.1
    
    def __init__(self, ocr_service: Optional['OCRService'] = None):
        """
        Initialize TextBasedClicker.
        
        Args:
            ocr_service: OCRService instance for text detection.
                        If None, creates a new instance.
        
        Raises:
            RuntimeError: If OCR service is not available
        """
        if not OCR_SERVICE_AVAILABLE:
            raise RuntimeError(
                "OCR service not available. Ensure ocr_service.py is accessible."
            )
        
        self.ocr = ocr_service if ocr_service else OCRService()
    
    def _capture_screenshot(self) -> 'np.ndarray':
        """
        Capture a screenshot of the current screen.
        
        Returns:
            Screenshot as numpy array in BGR format
        
        Requirements: 4.1
        """
        import cv2
        from PIL import ImageGrab
        
        # Capture screenshot using PIL
        screenshot = ImageGrab.grab()
        
        # Convert to numpy array (RGB)
        screenshot_np = np.array(screenshot)
        
        # Convert RGB to BGR for OpenCV compatibility
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        return screenshot_bgr
    
    def click_text(
        self,
        target_text: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        fuzzy: bool = True,
        case_sensitive: bool = False
    ) -> ClickResult:
        """
        Find and click on text on the screen.
        
        Captures a screenshot, performs OCR to find the target text,
        calculates the center of the text's bounding box, and clicks there.
        
        Args:
            target_text: Text to find and click
            region: Optional region to constrain search (x1, y1, x2, y2)
            fuzzy: If True, match partial text. If False, exact match.
            case_sensitive: If True, match case exactly
        
        Returns:
            ClickResult with success status and click location
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        if not target_text:
            return create_failure_result(
                target_text="",
                error_message="Target text cannot be empty"
            )
        
        try:
            # Capture screenshot
            screenshot = self._capture_screenshot()
            
            # Find target text
            if region:
                # Search within region, get closest match
                match = self.ocr.find_text_in_region(
                    screenshot, target_text, region, fuzzy, case_sensitive
                )
                matches = [match] if match else []
            else:
                # Search entire screen
                matches = self.ocr.find_text(
                    screenshot, target_text, fuzzy, case_sensitive
                )
            
            # Handle no matches found
            if not matches:
                # Get all detected text for error reporting (Property 8)
                all_detected = self.ocr.detect_text(screenshot)
                detected_texts = [loc.text for loc in all_detected]
                
                return create_failure_result(
                    target_text=target_text,
                    error_message=f"Target text '{target_text}' not found. "
                                  f"Detected text: {detected_texts[:20]}",  # Limit for readability
                    all_matches=all_detected
                )
            
            # Select the best match
            # If region specified, use closest to region center (Property 7)
            if region and len(matches) > 1:
                from ocr_service import find_closest_to_region
                best_match = find_closest_to_region(matches, region)
            else:
                # Use first match (highest confidence typically)
                best_match = matches[0]
            
            # Get click coordinates (center of bounding box - Property 6)
            click_x, click_y = best_match.center
            
            # Perform the click
            pyautogui.click(click_x, click_y)
            time.sleep(self.DELAY_AFTER_CLICK)
            
            return create_success_result(
                target_text=target_text,
                clicked_location=(click_x, click_y),
                all_matches=matches
            )
            
        except Exception as e:
            return create_failure_result(
                target_text=target_text,
                error_message=f"Error during click_text: {str(e)}"
            )
    
    def click_file_in_explorer(
        self,
        filename: str,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> ClickResult:
        """
        Click on a file in File Explorer by its filename.
        
        Specialized method for selecting files in File Explorer's file list.
        Uses a default region covering the typical file list area.
        
        Args:
            filename: Name of the file to click (with or without extension)
            region: Optional custom region. If None, uses FILE_LIST_REGION.
        
        Returns:
            ClickResult with success status and click location
        
        Requirements: 3.3, 4.1, 4.2, 4.3, 4.4
        """
        # Use default file list region if not specified
        search_region = region or self.FILE_LIST_REGION
        
        return self.click_text(
            target_text=filename,
            region=search_region,
            fuzzy=True,  # Allow partial match for filenames
            case_sensitive=False  # Windows filenames are case-insensitive
        )
    
    def double_click_text(
        self,
        target_text: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        fuzzy: bool = True,
        case_sensitive: bool = False
    ) -> ClickResult:
        """
        Find and double-click on text on the screen.
        
        Used for opening files or activating items that require double-click.
        
        Args:
            target_text: Text to find and double-click
            region: Optional region to constrain search (x1, y1, x2, y2)
            fuzzy: If True, match partial text. If False, exact match.
            case_sensitive: If True, match case exactly
        
        Returns:
            ClickResult with success status and click location
        
        Requirements: 3.3, 4.1, 4.2
        """
        if not target_text:
            return create_failure_result(
                target_text="",
                error_message="Target text cannot be empty"
            )
        
        try:
            # Capture screenshot
            screenshot = self._capture_screenshot()
            
            # Find target text
            if region:
                match = self.ocr.find_text_in_region(
                    screenshot, target_text, region, fuzzy, case_sensitive
                )
                matches = [match] if match else []
            else:
                matches = self.ocr.find_text(
                    screenshot, target_text, fuzzy, case_sensitive
                )
            
            # Handle no matches found
            if not matches:
                all_detected = self.ocr.detect_text(screenshot)
                detected_texts = [loc.text for loc in all_detected]
                
                return create_failure_result(
                    target_text=target_text,
                    error_message=f"Target text '{target_text}' not found. "
                                  f"Detected text: {detected_texts[:20]}",
                    all_matches=all_detected
                )
            
            # Select the best match
            if region and len(matches) > 1:
                from ocr_service import find_closest_to_region
                best_match = find_closest_to_region(matches, region)
            else:
                best_match = matches[0]
            
            # Get click coordinates
            click_x, click_y = best_match.center
            
            # Perform double-click
            pyautogui.doubleClick(click_x, click_y)
            time.sleep(self.DELAY_AFTER_CLICK)
            
            return create_success_result(
                target_text=target_text,
                clicked_location=(click_x, click_y),
                all_matches=matches
            )
            
        except Exception as e:
            return create_failure_result(
                target_text=target_text,
                error_message=f"Error during double_click_text: {str(e)}"
            )
    
    def get_all_visible_text(self) -> List[str]:
        """
        Get all visible text on the current screen.
        
        Useful for debugging and understanding what text is detectable.
        
        Returns:
            List of all detected text strings
        """
        try:
            screenshot = self._capture_screenshot()
            return self.ocr.get_all_detected_text(screenshot)
        except Exception:
            return []
