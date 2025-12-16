"""
High-level automation actions for FlexiSIGN.
Orchestrates complex workflows using lower-level components.
"""

import time
import pyautogui

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
            pyautogui.click(center_x, center_y)
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
            screen_width, screen_height = pyautogui.size()
            # Offset slightly left and down to account for toolbars/panels
            canvas_x = screen_width // 2
            canvas_y = screen_height // 2
            pyautogui.click(canvas_x, canvas_y)
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
        pyautogui.typewrite(text, interval=0.02)
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
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(width, interval=0.02)
        
        # Confirm width value
        pyautogui.press('enter')
        time.sleep(0.4)
        
        # Step 4: Set height using UIA ValuePattern
        height_input = self._designcentral.get_scale_height_input(ensure_tab_active=False)
        if not self._helpers.set_value(height_input, height):
            # Fallback: click, select all, and type
            self.click_element_center(height_input)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.typewrite(height, interval=0.02)
        
        # Confirm height value
        pyautogui.press('enter')
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
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.typewrite(font_name, interval=0.02)
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.2)
        
        return True
    
    def open_apply_styles(self) -> bool:
        """
        Open Apply Styles window by pressing Shift+S.
        
        Returns:
            True if Apply Styles window opened successfully, False otherwise.
        """
        try:
            pyautogui.hotkey('shift', 's')
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
            pyautogui.typewrite(style_name, interval=0.02)
            time.sleep(0.2)
            pyautogui.press('enter')
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
        pyautogui.hotkey('esc')
        time.sleep(0.1)  # Wait for deselection to complete
        pyautogui.hotkey('esc')
        time.sleep(0.1)  # Wait for deselection to complete
        
        # Press Ctrl+A first to ensure object is selected
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)  # Wait for selection to complete
        
        # Execute key press the specified number of times with Shift modifier
        for _ in range(distance):
            pyautogui.hotkey('shift', arrow_key)
            time.sleep(0.05)  # Small delay between presses
        
        time.sleep(0.1)  # Final delay for UI to settle
        return True
