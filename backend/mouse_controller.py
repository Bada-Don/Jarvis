"""
Mouse Controller Module
Performs deterministic mouse actions based on Set-of-Mark output
"""

import time
from typing import List, Dict, Tuple
import win32api
import win32con

# Constants for mouse events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

# Constants for keyboard events
KEYEVENTF_KEYUP = 0x0002

def _send_key(vk_code, is_down):
    """Sends a single key event."""
    if is_down:
        win32api.keybd_event(vk_code, 0, 0, 0)
    else:
        win32api.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def _hotkey(key1, key2):
    """Simulates pressing a hotkey combination."""
    # Map common keys to virtual key codes
    key_map = {
        'win': win32con.VK_LWIN,
        'alt': win32con.VK_MENU,
        'tab': win32con.VK_TAB,
        'shift': win32con.VK_SHIFT,
        'ctrl': win32con.VK_CONTROL,
        'enter': win32con.VK_RETURN,
        '6': 0x36 # Virtual key code for '6'
    }
    vk1 = key_map.get(key1.lower())
    vk2 = key_map.get(key2.lower())

    if vk1 and vk2:
        _send_key(vk1, True)
        _send_key(vk2, True)
        _send_key(vk2, False)
        _send_key(vk1, False)
    else:
        print(f"Warning: Hotkey '{key1}+{key2}' not supported by pywin32 mapping.")

def _click(x, y):
    """Simulates a mouse click at absolute coordinates."""
    # Convert to absolute screen coordinates (0-65535)
    # Get screen dimensions
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)

    win32api.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y, 0, 0)
    win32api.mouse_event(MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    win32api.mouse_event(MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)


def calculate_center(x1: float, y1: float, x2: float, y2: float) -> Tuple[int, int]:
    """Calculate center coordinates of bounding box"""
    center_x = int((x1 + x2) // 2)
    center_y = int((y1 + y2) // 2)
    return center_x, center_y


def perform_click_sequence(order: List[int], box_map: Dict[int, List[float]]) -> None:
    """
    Execute sequential mouse clicks at element centers with Win+6 prefix
    
    Args:
        order: List of element IDs to click in sequence, e.g. [42, 61, 35]
        box_map: Dict mapping element ID to bounding box [x1, y1, x2, y2]
    """
    print("Starting click sequence...")
    
    # Press Win + 6 first
    print("Pressing Win + 6...")
    _hotkey('win', '6')
    time.sleep(1)  # Fixed 1sec sleep
    
    # Execute clicks in order
    for i, element_id in enumerate(order):
        if element_id not in box_map:
            print(f"Warning: Element ID {element_id} not found in box_map, skipping...")
            continue
        
        # Get bounding box coordinates
        x1, y1, x2, y2 = box_map[element_id]
        
        # Calculate center coordinates
        center_x, center_y = calculate_center(x1, y1, x2, y2)
        
        print(f"Step {i+1}: Clicking element {element_id} at ({center_x}, {center_y})")
        
        # Perform absolute click
        _click(center_x, center_y)
        
        # Fixed 1sec sleep between actions
        time.sleep(1)
    
    print("Click sequence completed!")


def load_box_map_from_json(json_path: str) -> Dict[int, List[float]]:
    """Load bounding box mapping from JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


def save_box_map_to_json(box_map: Dict[int, List[float]], json_path: str) -> None:
    """Save bounding box mapping to JSON file"""
    with open(json_path, 'w') as f:
        json.dump(box_map, f, indent=2)


# Example usage functions
def demo_click_sequence():
    """Demo function showing how to use the mouse controller"""
    # Example box mapping (element_id -> [x1, y1, x2, y2])
    box_map = {
        42: [100, 200, 150, 250],  # Element 42 at coordinates
        61: [300, 400, 350, 450],  # Element 61 at coordinates  
        35: [500, 100, 550, 150]   # Element 35 at coordinates
    }
    
    # Click sequence order
    click_order = [42, 61, 35]
    
    # Execute the sequence
    perform_click_sequence(click_order, box_map)


if __name__ == "__main__":
    # Run demo if executed directly
    print("Running demo click sequence...")
    print("Make sure you have the target application ready!")
    print("Starting in 3 seconds...")
    time.sleep(3)
    demo_click_sequence()