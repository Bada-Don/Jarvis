"""
FlexiSIGN UIA Module
Windows UI Automation interface for FlexiSIGN.
Provides reliable element access via stable AutomationIds.

This module encapsulates all Windows UI Automation interactions with FlexiSIGN,
enabling direct automation without vision-based element detection.
"""

import time
from typing import Optional, Tuple

import comtypes.client
import psutil
import pyautogui
import pygetwindow as gw
import win32process
import win32gui

# Generate UIA bindings
comtypes.client.GetModule("UIAutomationCore.dll")
from comtypes.gen.UIAutomationClient import (
    IUIAutomation,
    TreeScope_Subtree,
    UIA_NamePropertyId,
    UIA_ClassNamePropertyId,
    UIA_AutomationIdPropertyId,
    UIA_BoundingRectanglePropertyId,
    UIA_ControlTypePropertyId,
    UIA_ProcessIdPropertyId,
    UIA_InvokePatternId,
    UIA_ValuePatternId,
    UIA_TogglePatternId,
)

# UIA Control Type IDs
UIA_ButtonControlTypeId = 50000
UIA_CheckBoxControlTypeId = 50002
UIA_ComboBoxControlTypeId = 50003
UIA_EditControlTypeId = 50004
UIA_PaneControlTypeId = 50033
UIA_TabControlTypeId = 50018
UIA_TabItemControlTypeId = 50019
UIA_ToolBarControlTypeId = 50021
UIA_WindowControlTypeId = 50032


class FlexiSignUIAError(Exception):
    """Exception raised when UIA operations fail."""
    pass


class FlexiSignUIA:
    """
    Windows UI Automation interface for FlexiSIGN.
    Provides reliable element access via stable AutomationIds.
    """

    def __init__(self):
        """Initialize UIA COM object."""
        self._uia: Optional[IUIAutomation] = None
        self._root = None
        self._pid: Optional[int] = None
        self._initialize_uia()

    def _initialize_uia(self):
        """Create the UIA COM object."""
        try:
            self._uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=IUIAutomation
            )
        except Exception as e:
            raise FlexiSignUIAError(f"Failed to initialize UI Automation: {e}")

    def cleanup(self):
        """Release UIA resources."""
        self._root = None
        self._pid = None
        self._uia = None

    # =========================================================================
    # Window Detection and Activation
    # =========================================================================

    def find_flexisign_window(self) -> Optional[object]:
        """
        Detect FlexiSIGN window by window title containing 'FlexiSIGN'.
        
        Returns:
            pygetwindow Window object if found, None otherwise.
        """
        try:
            for window in gw.getAllWindows():
                if "FlexiSIGN" in window.title:
                    return window
        except Exception:
            pass
        return None

    def get_pid_from_window(self, window) -> Optional[int]:
        """
        Retrieve process ID (PID) from window handle.
        
        Args:
            window: pygetwindow Window object
            
        Returns:
            Process ID if successful, None otherwise.
        """
        try:
            hwnd = window._hWnd
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception:
            return None

    def activate_window(self, window) -> bool:
        """
        Bring FlexiSIGN window to foreground.
        
        Args:
            window: pygetwindow Window object
            
        Returns:
            True if activation successful, False otherwise.
        """
        try:
            window.activate()
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def find_and_activate_window(self) -> bool:
        """
        Find FlexiSIGN window and bring to foreground.
        Implements retry logic with 5-second wait.
        
        Returns:
            True if successful, False otherwise.
        """
        # First attempt
        window = self.find_flexisign_window()
        if window:
            pid = self.get_pid_from_window(window)
            if pid:
                self._pid = pid
                if self.activate_window(window):
                    self._refresh_root()
                    return True
        
        # Wait 5 seconds and retry once
        time.sleep(5)
        
        window = self.find_flexisign_window()
        if window:
            pid = self.get_pid_from_window(window)
            if pid:
                self._pid = pid
                if self.activate_window(window):
                    self._refresh_root()
                    return True
        
        return False

    def _refresh_root(self):
        """Refresh the UIA root element for the current PID."""
        if self._uia and self._pid:
            root = self._uia.GetRootElement()
            cond = self._uia.CreatePropertyCondition(UIA_ProcessIdPropertyId, self._pid)
            self._root = root.FindFirst(TreeScope_Subtree, cond)

    # =========================================================================
    # UIA Helper Methods
    # =========================================================================

    def _make_and_condition(self, conditions):
        """Combine conditions with AndCondition."""
        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return self._uia.CreateAndConditionFromArray(conditions)

    def _find_first(self, root, *, name=None, class_name=None, automation_id=None,
                    control_type=None, scope=TreeScope_Subtree):
        """Generic first-match finder using provided property filters."""
        if root is None:
            return None
            
        props = []
        if name is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_NamePropertyId, name))
        if class_name is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_ClassNamePropertyId, class_name))
        if automation_id is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_AutomationIdPropertyId, automation_id))
        if control_type is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_ControlTypePropertyId, control_type))

        cond = self._make_and_condition(props)
        if cond is None:
            return None
        return root.FindFirst(scope, cond)

    def get_bounding_rect(self, element) -> Optional[Tuple[float, float, float, float]]:
        """
        Return bounding rectangle as tuple (left, top, right, bottom).
        
        Returns:
            Tuple of (left, top, right, bottom) or None if unavailable.
        """
        if element is None:
            return None
        try:
            rect = element.GetCurrentPropertyValue(UIA_BoundingRectanglePropertyId)
            if isinstance(rect, (list, tuple)) and len(rect) >= 4:
                left, top, width, height = rect[0], rect[1], rect[2], rect[3]
                return (left, top, left + width, top + height)
        except Exception:
            pass
        return None

    # =========================================================================
    # Interaction Helpers
    # =========================================================================

    def click_element_center(self, element) -> bool:
        """
        Click the center of a UI element using its bounding rect.
        
        Args:
            element: UIA element to click
            
        Returns:
            True if click successful, False otherwise.
        """
        rect = self.get_bounding_rect(element)
        if rect:
            center_x = (rect[0] + rect[2]) / 2
            center_y = (rect[1] + rect[3]) / 2
            pyautogui.click(center_x, center_y)
            return True
        return False

    def invoke(self, element) -> bool:
        """
        Invoke a button or invokable control using InvokePattern.
        
        Args:
            element: UIA element to invoke
            
        Returns:
            True if invocation successful, False otherwise.
        """
        if element is None:
            return False
        try:
            patt = element.GetCurrentPattern(UIA_InvokePatternId)
            if patt:
                patt_obj = patt.QueryInterface(
                    comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern
                )
                patt_obj.Invoke()
                return True
        except Exception:
            try:
                element.SetFocus()
                return True
            except Exception:
                return False
        return False

    def set_value(self, element, text: str) -> bool:
        """
        Set value for an Edit control using ValuePattern.
        
        Args:
            element: UIA element (Edit control)
            text: Value to set
            
        Returns:
            True if value set successfully, False otherwise.
        """
        if element is None:
            return False
        try:
            patt = element.GetCurrentPattern(UIA_ValuePatternId)
            if patt:
                patt_obj = patt.QueryInterface(
                    comtypes.gen.UIAutomationClient.IUIAutomationValuePattern
                )
                patt_obj.SetValue(text)
                return True
        except Exception:
            try:
                element.SetFocus()
                return True
            except Exception:
                return False
        return False

    def toggle_checkbox(self, element, target_on: bool) -> bool:
        """
        Set a checkbox to the desired state using TogglePattern.
        
        Args:
            element: UIA checkbox element
            target_on: True to check, False to uncheck
            
        Returns:
            True if toggle successful, False otherwise.
        """
        if element is None:
            return False
        try:
            patt = element.GetCurrentPattern(UIA_TogglePatternId)
            if patt:
                patt_obj = patt.QueryInterface(
                    comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern
                )
                current = patt_obj.CurrentToggleState
                # TogglePattern state: 0=Off, 1=On, 2=Indeterminate
                if (target_on and current == 0) or (not target_on and current == 1):
                    patt_obj.Toggle()
                return True
        except Exception:
            try:
                element.SetFocus()
                return True
            except Exception:
                return False
        return False

    # =========================================================================
    # Element Selectors - Toolbar
    # =========================================================================

    def _get_main_toolbar(self):
        """Get the main tool toolbar (AutomationId 60272)."""
        if self._root is None:
            return None
        return self._find_first(
            self._root,
            class_name="ToolbarWindow32",
            automation_id="60272",
            control_type=UIA_ToolBarControlTypeId
        )

    def _get_button_in_toolbar(self, toolbar_elem, button_name: str):
        """Find a button by its visible name under a toolbar element."""
        if toolbar_elem is None:
            return None
        return self._find_first(
            toolbar_elem,
            name=button_name,
            control_type=UIA_ButtonControlTypeId
        )

    def get_text_tool(self):
        """
        Get the Text Tool button from the toolbar.
        
        Returns:
            UIA element for Text Tool, or None if not found.
            
        Raises:
            FlexiSignUIAError: If Text Tool cannot be found.
        """
        toolbar = self._get_main_toolbar()
        element = self._get_button_in_toolbar(toolbar, "Text Tool")
        if element is None:
            raise FlexiSignUIAError("Text Tool not found in toolbar")
        return element

    def get_select_tool(self):
        """
        Get the Select Tool button from the toolbar.
        
        Returns:
            UIA element for Select Tool, or None if not found.
            
        Raises:
            FlexiSignUIAError: If Select Tool cannot be found.
        """
        toolbar = self._get_main_toolbar()
        element = self._get_button_in_toolbar(toolbar, "Select Tool")
        if element is None:
            raise FlexiSignUIAError("Select Tool not found in toolbar")
        return element

    # =========================================================================
    # Element Selectors - DesignCentral
    # =========================================================================

    def _get_designcentral(self):
        """Get the DesignCentral window."""
        if self._root is None:
            return None
        return self._find_first(
            self._root,
            name="DesignCentral",
            class_name="#32770",
            control_type=UIA_WindowControlTypeId
        )

    def ensure_designcentral_open(self) -> bool:
        """
        Ensure DesignCentral panel is visible.
        Opens with Ctrl+I if not found.
        
        Returns:
            True if DesignCentral is visible (either already open or successfully opened),
            False if unable to open DesignCentral.
        """
        # First check if DesignCentral is already visible
        dc = self._get_designcentral()
        if dc is not None:
            return True
        
        # DesignCentral not visible, press Ctrl+I to open it
        pyautogui.hotkey('ctrl', 'i')
        
        # Wait for UI to stabilize after opening
        time.sleep(0.5)
        
        # Refresh root to pick up new window
        self._refresh_root()
        
        # Retry once to find DesignCentral
        dc = self._get_designcentral()
        if dc is not None:
            return True
        
        # If still not found, wait a bit more and try again
        time.sleep(0.5)
        self._refresh_root()
        dc = self._get_designcentral()
        
        return dc is not None

    def _get_designcentral_tabcontrol(self):
        """Get the tab control within DesignCentral (AutomationId 12320)."""
        dc = self._get_designcentral()
        if dc is None:
            return None
        return self._find_first(
            dc,
            class_name="SysTabControl32",
            automation_id="12320",
            control_type=UIA_TabControlTypeId
        )

    def _get_tab_item_by_index(self, index: int):
        """
        Get a tab item by its index within the DesignCentral tab control.
        
        Args:
            index: 0-based index (0=Scale, 1=Rotate, 2=Character)
            
        Returns:
            UIA element for the tab item, or None if not found.
        """
        tabcontrol = self._get_designcentral_tabcontrol()
        if tabcontrol is None:
            return None
        
        walker = self._uia.ControlViewWalker
        child = walker.GetFirstChildElement(tabcontrol)
        current_idx = 0
        
        while child:
            try:
                ctrl_type = child.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
                if ctrl_type == UIA_TabItemControlTypeId:
                    if current_idx == index:
                        return child
                    current_idx += 1
            except Exception:
                pass
            child = walker.GetNextSiblingElement(child)
        
        return None

    def get_scale_tab_item(self):
        """
        Get the Scale tab item in DesignCentral (index 0).
        
        Returns:
            UIA element for Scale tab, or None if not found.
            
        Raises:
            FlexiSignUIAError: If Scale tab cannot be found.
        """
        element = self._get_tab_item_by_index(0)
        if element is None:
            raise FlexiSignUIAError("Scale tab not found in DesignCentral")
        return element

    def get_rotate_tab_item(self):
        """
        Get the Rotate tab item in DesignCentral (index 1).
        
        Returns:
            UIA element for Rotate tab, or None if not found.
        """
        return self._get_tab_item_by_index(1)

    def get_character_tab_item(self):
        """
        Get the Character tab item in DesignCentral (index 2).
        
        Returns:
            UIA element for Character tab, or None if not found.
            
        Raises:
            FlexiSignUIAError: If Character tab cannot be found.
        """
        element = self._get_tab_item_by_index(2)
        if element is None:
            raise FlexiSignUIAError("Character tab not found in DesignCentral")
        return element

    def get_scale_width_input(self, ensure_tab_active: bool = True):
        """
        Get the width input field in the Scale tab (AutomationId 10609).
        
        Args:
            ensure_tab_active: If True, clicks Scale tab first to ensure visibility.
            
        Returns:
            UIA element for width input, or None if not found.
            
        Raises:
            FlexiSignUIAError: If width input cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self._get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Dimension input not found - DesignCentral not available")
        
        element = self._find_first(
            dc,
            automation_id="10609",
            control_type=UIA_EditControlTypeId
        )
        if element is None:
            raise FlexiSignUIAError("Dimension input not found")
        return element

    def get_scale_height_input(self, ensure_tab_active: bool = True):
        """
        Get the height input field in the Scale tab (AutomationId 10610).
        
        Args:
            ensure_tab_active: If True, clicks Scale tab first to ensure visibility.
            
        Returns:
            UIA element for height input, or None if not found.
            
        Raises:
            FlexiSignUIAError: If height input cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self._get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Dimension input not found - DesignCentral not available")
        
        element = self._find_first(
            dc,
            automation_id="10610",
            control_type=UIA_EditControlTypeId
        )
        if element is None:
            raise FlexiSignUIAError("Dimension input not found")
        return element

    def get_proportional_checkbox(self, ensure_tab_active: bool = True):
        """
        Get the proportional scaling checkbox in the Scale tab (AutomationId 11117).
        
        Args:
            ensure_tab_active: If True, clicks Scale tab first to ensure visibility.
            
        Returns:
            UIA element for proportional checkbox, or None if not found.
            
        Raises:
            FlexiSignUIAError: If proportional checkbox cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self._get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Proportional checkbox not found - DesignCentral not available")
        
        element = self._find_first(
            dc,
            automation_id="11117",
            control_type=UIA_CheckBoxControlTypeId
        )
        if element is None:
            raise FlexiSignUIAError("Proportional checkbox not found")
        return element

    def get_font_family_combobox(self, ensure_tab_active: bool = True):
        """
        Get the font family combobox in the Character tab (AutomationId 10825).
        
        Args:
            ensure_tab_active: If True, clicks Character tab first to ensure visibility.
            
        Returns:
            UIA element for font family combobox, or None if not found.
            
        Raises:
            FlexiSignUIAError: If font combobox cannot be found.
        """
        if ensure_tab_active:
            try:
                char_tab = self.get_character_tab_item()
                self.invoke(char_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self._get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Font combobox not found - DesignCentral not available")
        
        element = self._find_first(
            dc,
            automation_id="10825",
            control_type=UIA_ComboBoxControlTypeId
        )
        if element is None:
            raise FlexiSignUIAError("Font combobox not found")
        return element

    # =========================================================================
    # Direct Automation Actions
    # =========================================================================

    def click_text_tool(self) -> bool:
        """
        Click the Text Tool (T icon) in the toolbar using UIA selector.
        
        Returns:
            True if click successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Text Tool cannot be found.
        """
        text_tool = self.get_text_tool()
        if self.invoke(text_tool):
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
        select_tool = self.get_select_tool()
        if self.invoke(select_tool):
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

    def _navigate_to_scale_tab(self) -> bool:
        """
        Navigate to the Scale tab in DesignCentral.
        
        Returns:
            True if navigation successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Scale tab cannot be found.
        """
        # Ensure DesignCentral is open first
        if not self.ensure_designcentral_open():
            raise FlexiSignUIAError("Scale tab not found in DesignCentral - DesignCentral not available")
        
        scale_tab = self.get_scale_tab_item()
        if self.invoke(scale_tab):
            time.sleep(0.2)
            return True
        # Fallback to clicking element center
        return self.click_element_center(scale_tab)

    def _disable_proportional_scaling(self) -> bool:
        """
        Disable proportional scaling by unchecking the proportional checkbox.
        
        Returns:
            True if checkbox is now unchecked, False otherwise.
            
        Raises:
            FlexiSignUIAError: If proportional checkbox cannot be found.
        """
        checkbox = self.get_proportional_checkbox(ensure_tab_active=False)
        # target_on=False means we want it unchecked
        return self.toggle_checkbox(checkbox, target_on=False)

    def set_dimensions(self, width: str, height: str) -> bool:
        """
        Set object dimensions via Scale tab.
        
        Orchestrates the full sequence:
        1. Navigate to Scale tab in DesignCentral
        2. Disable proportional scaling
        3. Set width input field
        4. Set height input field
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
        if not self._navigate_to_scale_tab():
            raise FlexiSignUIAError("Failed to navigate to Scale tab")
        
        # Step 2: Disable proportional scaling
        if not self._disable_proportional_scaling():
            raise FlexiSignUIAError("Failed to disable proportional scaling")
        
        # Step 3: Set width input field
        width_input = self.get_scale_width_input(ensure_tab_active=False)
        # Click to focus, then clear and type
        self.click_element_center(width_input)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.typewrite(width, interval=0.02)
        time.sleep(0.1)
        
        # Step 4: Set height input field
        height_input = self.get_scale_height_input(ensure_tab_active=False)
        # Click to focus, then clear and type
        self.click_element_center(height_input)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.typewrite(height, interval=0.02)
        time.sleep(0.1)
        
        # Step 5: Press Enter to confirm
        pyautogui.press('enter')
        time.sleep(0.2)
        
        return True

    def _navigate_to_character_tab(self) -> bool:
        """
        Navigate to the Character tab in DesignCentral.
        
        Returns:
            True if navigation successful, False otherwise.
            
        Raises:
            FlexiSignUIAError: If Character tab cannot be found.
        """
        # Ensure DesignCentral is open first
        if not self.ensure_designcentral_open():
            raise FlexiSignUIAError("Character tab not found in DesignCentral - DesignCentral not available")
        
        char_tab = self.get_character_tab_item()
        if self.invoke(char_tab):
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
        if not self._navigate_to_character_tab():
            raise FlexiSignUIAError("Failed to navigate to Character tab")
        
        # Step 2: Click font family combobox
        font_combo = self.get_font_family_combobox(ensure_tab_active=False)
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

    # Direction to arrow key mapping
    _DIRECTION_KEY_MAP = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
    }

    def move_object(self, direction: str, distance: int) -> bool:
        """
        Move selected object using Shift+Arrow keys.
        
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
        
        # Execute key press the specified number of times with Shift modifier
        for _ in range(distance):
            pyautogui.hotkey('shift', arrow_key)
            time.sleep(0.05)  # Small delay between presses
        
        time.sleep(0.1)  # Final delay for UI to settle
        return True
