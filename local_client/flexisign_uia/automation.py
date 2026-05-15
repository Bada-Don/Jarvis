"""
High-level automation actions for FlexiSIGN.
Orchestrates complex workflows using lower-level components.
"""

import time
import win32api
import win32con

# Constants for mouse events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
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
    key_map = {
        'ctrl': win32con.VK_CONTROL,
        'shift': win32con.VK_SHIFT,
        'alt': win32con.VK_MENU,
        'esc': win32con.VK_ESCAPE,
        'enter': win32con.VK_RETURN,
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
        'up': win32con.VK_UP, 'down': win32con.VK_DOWN, 'left': win32con.VK_LEFT, 'right': win32con.VK_RIGHT,
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

def _press(key):
    """Simulates pressing a single key."""
    key_map = {
        'enter': win32con.VK_RETURN,
        'esc': win32con.VK_ESCAPE,
        'up': win32con.VK_UP, 'down': win32con.VK_DOWN, 'left': win32con.VK_LEFT, 'right': win32con.VK_RIGHT,
    }
    vk_code = key_map.get(key.lower())
    if vk_code:
        _send_key(vk_code, True)
        _send_key(vk_code, False)
    else:
        print(f"Warning: Key '{key}' not supported by pywin32 mapping.")

def _typewrite(text, interval=0.0):
    """Simulates typing a string of text."""
    for char in text:
        # This is a simplified approach. For full character support,
        # one would need to map characters to virtual key codes or use SendInput.
        # For now, we'll assume basic alphanumeric and symbols that map directly.
        if 'a' <= char.lower() <= 'z' or '0' <= char <= '9':
            vk_code = ord(char.upper())
            _send_key(vk_code, True)
            _send_key(vk_code, False)
        elif char == ' ':
            _send_key(win32con.VK_SPACE, True)
            _send_key(win32con.VK_SPACE, False)
        elif char == '.':
            _send_key(win32con.VK_OEM_PERIOD, True)
            _send_key(win32con.VK_OEM_PERIOD, False)
        elif char == '/':
            _send_key(win32con.VK_OEM_2, True)
            _send_key(win32con.VK_OEM_2, False)
        # Add more character mappings as needed
        time.sleep(interval)

def _click(x, y):
    """Simulates a mouse click at absolute coordinates."""
    screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)

    win32api.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y, 0, 0)
    win32api.mouse_event(MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    win32api.mouse_event(MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)

from .exceptions import FlexiSignUIAError


class AutomationActions:
    """High-level automation actions for FlexiSIGN workflows."""
    
    # Direction to arrow key mapping
    _DIRECTION_KEY_MAP = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
    }
    
    def __init__(self, toolbar_selectors, designcentral_selectors, uia_helpers):
        """
        Initialize automation actions.
        
        Args:
            toolbar_selectors: ToolbarSelectors instance
            designcentral_selectors: DesignCentralSelectors instance
            uia_helpers: UIAHelpers instance
        """
        self._toolbar = toolbar_selectors
        self._designcentral = designcentral_selectors
        self._helpers = uia_helpers
    
    def click_element_center(self, element) -> bool:
        """
        Click the center of a UI element using its bounding rect.
        
        Args:
            element: UIA element to click
            
        Returns:
            True if click successful, False otherwise.
        """
        rect = self._helpers.get_bounding_rect(element)
        if rect:
            center_x = (rect[0] + rect[2]) / 2
            center_y = (rect[1] + rect[3]) / 2
            _click(center_x, center_y)
            return True
        return False
    
    def click_text_tool(self) -> bool:
        """
        Click the Text Tool (T icon) in the toolbar using UIA selector.
        
        Returns:
            True if click successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Text Tool cannot be found.
        """
        text_tool = self._toolbar.get_text_tool()
        if self._helpers.invoke(text_tool):
            time.sleep(0.2)
            return True
        # Fallback to clicking element center
        return self.click_element_center(text_tool)
    
    def click_canvas_center(self) -> bool:
        """
        Click the center of the canvas area using screen center calculation.
        
        The canvas is approximated as the center of the screen, offset slightly
        to account for toolbars and panels.
        
        Returns:
            True if click successful, False otherwise.
        """
        try:
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            # Offset slightly left and down to account for toolbars/panels
            canvas_x = screen_width // 2
            canvas_y = screen_height // 2
            _click(canvas_x, canvas_y)
            time.sleep(0.2)
            return True
        except Exception:
            return False
    
    def click_select_tool(self) -> bool:
        """
        Click the Select Tool (pointer icon) in the toolbar using UIA selector.
        
        Returns:
            True if click successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Select Tool cannot be found.
        """
        select_tool = self._toolbar.get_select_tool()
        if self._helpers.invoke(select_tool):
            time.sleep(0.2)
            return True
        # Fallback to clicking element center
        return self.click_element_center(select_tool)
    
    def create_text(self, text: str) -> bool:
        """
        Create a text object with the specified content.
        
        Orchestrates the full sequence:
        1. Click Text Tool
        2. Click canvas center
        3. Type the specified text
        4. Click Select Tool to finalize
        
        Args:
            text: The text content to create
            
        Returns:
            True if text creation successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If any step fails due to missing UI elements.
        """
        # Step 1: Click Text Tool
        if not self.click_text_tool():
            raise FlexiSignUIAError("Failed to click Text Tool")
        
        # Step 2: Click canvas center
        if not self.click_canvas_center():
            raise FlexiSignUIAError("Failed to click canvas center")
        
        # Step 3: Type the specified text
        time.sleep(0.2)
        _typewrite(text, interval=0.02)
        time.sleep(0.2)
        
        # Step 4: Click Select Tool to finalize
        if not self.click_select_tool():
            raise FlexiSignUIAError("Failed to click Select Tool")
        
        return True
    
    def navigate_to_scale_tab(self) -> bool:
        """
        Navigate to the Scale tab in DesignCentral.
        
        Returns:
            True if navigation successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Scale tab cannot be found.
        """
        # Ensure DesignCentral is open first
        if not self._designcentral.ensure_designcentral_open():
            raise FlexiSignUIAError("Scale tab not found in DesignCentral - DesignCentral not available")
        
        scale_tab = self._designcentral.get_scale_tab_item()
        if self._helpers.invoke(scale_tab):
            time.sleep(0.2)
            return True
        # Fallback to clicking element center
        return self.click_element_center(scale_tab)
    
    def disable_proportional_scaling(self) -> bool:
        """
        Disable proportional scaling by unchecking the proportional checkbox.
        
        Returns:
            True if checkbox is now unchecked, False otherwise.
            
        Raises:
            FlexiSignUIAError: If proportional checkbox cannot be found.
        """
        checkbox = self._designcentral.get_proportional_checkbox(ensure_tab_active=False)
        # target_on=False means we want it unchecked
        return self._helpers.toggle_checkbox(checkbox, target_on=False)
    
    def set_dimensions(self, width: str, height: str) -> bool:
        """
        Set object dimensions via Scale tab.
        
        Orchestrates the full sequence:
        1. Navigate to Scale tab in DesignCentral
        2. Disable proportional scaling
        3. Set width input field using UIA ValuePattern
        4. Set height input field using UIA ValuePattern
        5. Press Enter to confirm
        
        Args:
            width: Width value as string (e.g., "8")
            height: Height value as string (e.g., "1.2")
            
        Returns:
            True if dimensions set successfully, False otherwise.
            
        Raises:
            FlexiSignUIAError: If any step fails due to missing UI elements.
        """
        # Step 1: Navigate to Scale tab
        if not self.navigate_to_scale_tab():
            raise FlexiSignUIAError("Failed to navigate to Scale tab")
        
        # Step 2: Disable proportional scaling
        if not self.disable_proportional_scaling():
            raise FlexiSignUIAError("Failed to disable proportional scaling")
        
        # Step 3: Set width using UIA ValuePattern (cleanly replaces existing value)
        width_input = self._designcentral.get_scale_width_input(ensure_tab_active=False)
        if not self._helpers.set_value(width_input, width):
            # Fallback: click, select all, and type
            self.click_element_center(width_input)
            time.sleep(0.2)
            _hotkey('ctrl', 'a')
            time.sleep(0.1)
            _typewrite(width, interval=0.02)
        
        # Confirm width value
        _press('enter')
        time.sleep(0.4)
        
        # Step 4: Set height using UIA ValuePattern
        height_input = self._designcentral.get_scale_height_input(ensure_tab_active=False)
        if not self._helpers.set_value(height_input, height):
            # Fallback: click, select all, and type
            self.click_element_center(height_input)
            time.sleep(0.2)
            _hotkey('ctrl', 'a')
            time.sleep(0.1)
            _typewrite(height, interval=0.02)
        
        # Confirm height value
        _press('enter')
        time.sleep(0.4)
        
        return True
    
    def navigate_to_character_tab(self) -> bool:
        """
        Navigate to the Character tab in DesignCentral.
        
        Returns:
            True if navigation successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Character tab cannot be found.
        """
        # Ensure DesignCentral is open first
        if not self._designcentral.ensure_designcentral_open():
            raise FlexiSignUIAError("Character tab not found in DesignCentral - DesignCentral not available")
        
        char_tab = self._designcentral.get_character_tab_item()
        if self._helpers.invoke(char_tab):
            time.sleep(0.2)
            return True
        # Fallback to clicking element center
        return self.click_element_center(char_tab)
    
    def set_font(self, font_name: str) -> bool:
        """
        Set font via Character tab.
        
        Orchestrates the full sequence:
        1. Navigate to Character tab in DesignCentral
        2. Click font family combobox
        3. Type font name and press Enter to apply
        
        Args:
            font_name: Name of the font to apply (e.g., "Blackberry")
            
        Returns:
            True if font set successfully, False otherwise.
            
        Raises:
            FlexiSignUIAError: If any step fails due to missing UI elements.
        """
        # Step 1: Navigate to Character tab
        if not self.navigate_to_character_tab():
            raise FlexiSignUIAError("Failed to navigate to Character tab")
        
        # Step 2: Click font family combobox
        font_combo = self._designcentral.get_font_family_combobox(ensure_tab_active=False)
        self.click_element_center(font_combo)
        time.sleep(0.2)
        
        # Step 3: Type font name and press Enter
        _hotkey('ctrl', 'a')
        time.sleep(0.05)
        _typewrite(font_name, interval=0.02)
        time.sleep(0.1)
        _press('enter')
        time.sleep(0.2)
        
        return True
    
    def open_apply_styles(self) -> bool:
        """
        Open Apply Styles window by pressing Shift+S.
        
        Returns:
            True if Apply Styles window opened successfully, False otherwise.
        """
        try:
            _hotkey('shift', 's')
            # Wait for the Apply Styles window to open
            time.sleep(0.5)
            return True
        except Exception:
            return False
    
    def apply_style(self, style_name: str = None) -> bool:
        """
        Apply a style. If style_name provided, searches for it.
        
        Orchestrates the sequence:
        1. Press Shift+S to open Apply Styles window
        2. Wait for window to be ready
        3. If style_name provided, type to search and press Enter
        
        Args:
            style_name: Optional name of the style to search and apply.
                       If None, just opens the Apply Styles window.
            
        Returns:
            True if style applied successfully, False otherwise.
        """
        # Step 1: Open Apply Styles window
        if not self.open_apply_styles():
            raise FlexiSignUIAError("Failed to open Apply Styles window")
        
        # Step 2: Wait for window to be ready
        time.sleep(0.3)
        
        # Step 3: If style_name provided, search and apply
        if style_name:
            _typewrite(style_name, interval=0.02)
            time.sleep(0.2)
            _press('enter')
            time.sleep(0.2)
        
        return True
    
    def move_object(self, direction: str, distance: int) -> bool:
        """
        Move selected object using Shift+Arrow keys.
        First presses Ctrl+A to ensure object is selected before moving.
        
        Args:
            direction: Direction to move ('up', 'down', 'left', 'right')
            distance: Number of key presses (each press moves a fixed amount)
            
        Returns:
            True if movement successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If direction is invalid.
        """
        # Map direction string to arrow key name
        direction_lower = direction.lower()
        if direction_lower not in self._DIRECTION_KEY_MAP:
            raise FlexiSignUIAError(
                f"Invalid direction '{direction}'. Must be one of: up, down, left, right"
            )
        
        arrow_key = self._DIRECTION_KEY_MAP[direction_lower]
        
        # Press Esc first to ensure objects are deselected
        _hotkey('esc')
        time.sleep(0.1)  # Wait for deselection to complete
        _hotkey('esc')
        time.sleep(0.1)  # Wait for deselection to complete
        
        # Press Ctrl+A first to ensure object is selected
        _hotkey('ctrl', 'a')
        time.sleep(0.1)  # Wait for selection to complete
        
        # Execute key press the specified number of times with Shift modifier
        for _ in range(distance):
            _hotkey('shift', arrow_key)
            time.sleep(0.05)  # Small delay between presses
        
        time.sleep(0.1)  # Final delay for UI to settle
        return True
