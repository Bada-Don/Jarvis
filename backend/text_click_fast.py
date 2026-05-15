"""
Fast Text-Based Clicking Module

This module provides ultra-fast text-based clicking using direct window targeting
and pytesseract OCR. Much faster than vision-based clicking with FastSAM.

Use this when:
- Clicking on text labels, buttons with text, menu items
- Clicking on contact names, file names, chat names
- Any UI element that has readable text

Do NOT use this for:
- Icons without text
- Images
- Complex UI elements without clear text labels
"""

import time
from typing import Optional, Tuple
import pygetwindow as gw
import pytesseract
from PIL import Image
import win32api
import win32con

# Constants for mouse events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

def _move_to(x, y):
    """Simulates moving the mouse to absolute coordinates."""
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)

    win32api.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y, 0, 0)

def _click(x, y):
    """Simulates a mouse click at absolute coordinates."""
    _move_to(x, y) # Move to the location first
    win32api.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# Configure pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class FastTextClicker:
    """
    Fast text-based clicking using window-specific OCR.
    
    This is significantly faster than vision-based clicking because:
    1. Only scans the target window (not entire screen)
    2. Uses lightweight pytesseract directly
    3. No FastSAM model loading or inference
    4. No multimodal LLM calls
    """
    
    def __init__(self):
        """Initialize the fast text clicker."""
        pass
    
    def click_text_in_window(
        self,
        window_title: str,
        target_text: str,
        case_sensitive: bool = False,
        activate_window: bool = True,
        fuzzy_match: bool = True
    ) -> dict:
        """
        Find and click on text within a specific window.
        
        Args:
            window_title: Partial or full title of the window to search in
            target_text: Text to find and click on
            case_sensitive: Whether to match case exactly
            activate_window: Whether to activate/focus the window first
            fuzzy_match: If True, matches partial text (e.g., "Harshit" matches "Harshit Singla")
        
        Returns:
            dict with:
                - success: bool
                - clicked_location: (x, y) or None
                - error_message: str or None
                - window_title: str (actual window title found)
                - detected_texts: list of all detected text (for debugging)
        """
        try:
            # 1. Find and activate the window
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                return {
                    'success': False,
                    'clicked_location': None,
                    'error_message': f"Could not find window with title containing '{window_title}'",
                    'window_title': None,
                    'detected_texts': []
                }
            
            window = windows[0]
            
            if activate_window:
                # Restore if minimized and activate
                if window.isMinimized:
                    window.restore()
                window.activate()
                
                # Wait for window to come to foreground and content to load
                time.sleep(1.0)
            
            # 2. Take screenshot of ONLY that window
            region = (window.left, window.top, window.width, window.height)
            screenshot_pil = ImageGrab.grab(bbox=region)
            screenshot = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
            
            # 3. Use OCR to get text and coordinates
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            n_boxes = len(data['text'])
            detected_texts = []
            
            # Split target text into words for fuzzy matching
            target_words = target_text.lower().split() if not case_sensitive else target_text.split()
            
            # 4. Search for the text
            best_match = None
            best_match_score = 0
            
            for i in range(n_boxes):
                detected_text = data['text'][i].strip()
                
                if not detected_text:
                    continue
                
                detected_texts.append(detected_text)
                
                # Exact match logic
                if case_sensitive:
                    exact_match = target_text in detected_text
                else:
                    exact_match = target_text.lower() in detected_text.lower()
                
                if exact_match:
                    # Get local coordinates (relative to screenshot)
                    (x, y, w, h) = (data['left'][i], data['top'][i], 
                                   data['width'][i], data['height'][i])
                    
                    # Calculate global screen coordinates
                    click_x = window.left + x + (w / 2)
                    click_y = window.top + y + (h / 2)
                    
                    # Move and click
                    _move_to(click_x, click_y)
                    _click(click_x, click_y)
                    
                    return {
                        'success': True,
                        'clicked_location': (int(click_x), int(click_y)),
                        'error_message': None,
                        'window_title': window.title,
                        'matched_text': detected_text,
                        'detected_texts': detected_texts[:20]  # Limit for debugging
                    }
                
                # Fuzzy match logic (check if any target word is in detected text)
                if fuzzy_match:
                    detected_lower = detected_text.lower() if not case_sensitive else detected_text
                    match_count = sum(1 for word in target_words if word in detected_lower)
                    
                    if match_count > best_match_score:
                        best_match_score = match_count
                        best_match = {
                            'index': i,
                            'text': detected_text,
                            'score': match_count
                        }
            
            # If fuzzy match found, click on best match
            if fuzzy_match and best_match and best_match_score > 0:
                i = best_match['index']
                (x, y, w, h) = (data['left'][i], data['top'][i], 
                               data['width'][i], data['height'][i])
                
                click_x = window.left + x + (w / 2)
                click_y = window.top + y + (h / 2)
                
                _move_to(click_x, click_y)
                _click(click_x, click_y)
                
                return {
                    'success': True,
                    'clicked_location': (int(click_x), int(click_y)),
                    'error_message': None,
                    'window_title': window.title,
                    'matched_text': best_match['text'],
                    'match_type': 'fuzzy',
                    'detected_texts': detected_texts[:20]
                }
            
            # Text not found
            return {
                'success': False,
                'clicked_location': None,
                'error_message': f"Could not find text '{target_text}' in window '{window.title}'. Detected: {detected_texts[:10]}",
                'window_title': window.title,
                'detected_texts': detected_texts[:20]
            }
            
        except Exception as e:
            return {
                'success': False,
                'clicked_location': None,
                'error_message': f"Error during click_text_in_window: {str(e)}",
                'window_title': None,
                'detected_texts': []
            }
    
    def click_text_anywhere(
        self,
        target_text: str,
        case_sensitive: bool = False
    ) -> dict:
        """
        Find and click on text anywhere on the screen.
        
        This scans the entire screen, so it's slower than click_text_in_window
        but still much faster than vision-based clicking.
        
        Args:
            target_text: Text to find and click on
            case_sensitive: Whether to match case exactly
        
        Returns:
            dict with success, clicked_location, error_message
        """
        try:
            # Take full screenshot
            screenshot_pil = ImageGrab.grab()
            screenshot = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
            
            # Use OCR to get text and coordinates
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            n_boxes = len(data['text'])
            
            # Search for the text
            for i in range(n_boxes):
                detected_text = data['text'][i].strip()
                
                if not detected_text:
                    continue
                
                # Match logic
                if case_sensitive:
                    match = target_text in detected_text
                else:
                    match = target_text.lower() in detected_text.lower()
                
                if match:
                    # Get coordinates
                    (x, y, w, h) = (data['left'][i], data['top'][i], 
                                   data['width'][i], data['height'][i])
                    
                    # Calculate click position (center of text)
                    click_x = x + (w / 2)
                    click_y = y + (h / 2)
                    
                    # Move and click
                    _move_to(click_x, click_y)
                    _click(click_x, click_y)
                    
                    return {
                        'success': True,
                        'clicked_location': (int(click_x), int(click_y)),
                        'error_message': None,
                        'matched_text': detected_text
                    }
            
            # Text not found
            return {
                'success': False,
                'clicked_location': None,
                'error_message': f"Could not find text '{target_text}' on screen"
            }
            
        except Exception as e:
            return {
                'success': False,
                'clicked_location': None,
                'error_message': f"Error during click_text_anywhere: {str(e)}"
            }


# Convenience functions for backward compatibility
def click_text_in_window(window_title: str, target_text: str) -> dict:
    """
    Convenience function to click text in a window.
    
    Args:
        window_title: Window title to search in
        target_text: Text to click on
    
    Returns:
        Result dictionary
    """
    clicker = FastTextClicker()
    return clicker.click_text_in_window(window_title, target_text)


def click_text_anywhere(target_text: str) -> dict:
    """
    Convenience function to click text anywhere on screen.
    
    Args:
        target_text: Text to click on
    
    Returns:
        Result dictionary
    """
    clicker = FastTextClicker()
    return clicker.click_text_anywhere(target_text)
