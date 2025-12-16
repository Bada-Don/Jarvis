"""
DesignCentral panel element selectors and operations for FlexiSIGN.
"""

import time
import pyautogui

from .constants import (
    UIA_WindowControlTypeId,
    UIA_TabControlTypeId,
    UIA_TabItemControlTypeId,
    UIA_EditControlTypeId,
    UIA_CheckBoxControlTypeId,
    UIA_ComboBoxControlTypeId,
    UIA_ClassNamePropertyId,
    UIA_ControlTypePropertyId,
)
from .exceptions import FlexiSignUIAError


class DesignCentralSelectors:
    """Selectors and operations for DesignCentral panel in FlexiSIGN."""
    
    def __init__(self, root_element, uia_instance, uia_helpers, root_refresh_callback):
        """
        Initialize DesignCentral selectors.
        
        Args:
            root_element: Root UIA element
            uia_instance: UIA COM object
            uia_helpers: UIAHelpers instance for element finding
            root_refresh_callback: Callback to refresh root element
        """
        self._root = root_element
        self._uia = uia_instance
        self._helpers = uia_helpers
        self._refresh_root = root_refresh_callback
    
    def get_designcentral(self):
        """
        Get the DesignCentral window.
        
        IMPORTANT: There are two elements with name "DesignCentral":
        1. The actual window: Name="DesignCentral", Class="#32770", Type=Window (only when open)
        2. A checkbox: Name="DesignCentral", Class="", Type=CheckBox (always present)
        
        We must match ALL three properties to get the window, not the checkbox.
        
        Returns:
            UIA element for DesignCentral window if open, None otherwise.
        """
        if self._root is None:
            return None
        
        # Find element matching name, class, and control type
        element = self._helpers.find_first(
            self._root,
            name="DesignCentral",
            class_name="#32770",
            control_type=UIA_WindowControlTypeId
        )
        
        # Additional validation: verify we got the window, not the checkbox
        if element is not None:
            try:
                # Double-check the class name is actually "#32770"
                actual_class = element.GetCurrentPropertyValue(UIA_ClassNamePropertyId)
                actual_type = element.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
                
                # Verify it's a window with the correct class
                if actual_class == "#32770" and actual_type == UIA_WindowControlTypeId:
                    return element
                else:
                    # We got the checkbox or wrong element, return None
                    print(f"DEBUG: Found element but wrong type - Class: '{actual_class}', Type: {actual_type}")
                    return None
            except Exception as e:
                print(f"DEBUG: Error validating DesignCentral element: {e}")
                return None
        
        return None
    
    def ensure_designcentral_open(self) -> bool:
        """
        Ensure DesignCentral panel is visible.
        Opens with Ctrl+I if not found.
        
        IMPORTANT: This method distinguishes between:
        - DesignCentral window (Class="#32770", Type=Window) - only when open
        - DesignCentral checkbox (Class="", Type=CheckBox) - always present
        
        Returns:
            True if DesignCentral window is visible (either already open or successfully opened),
            False if unable to open DesignCentral window.
        """
        print("DEBUG: Checking if DesignCentral is already open...")
        
        # First check if DesignCentral is already visible
        dc = self.get_designcentral()
        if dc is not None:
            print("DEBUG: DesignCentral window already open")
            return True
        
        print("DEBUG: DesignCentral window not found, pressing Ctrl+I to open...")
        
        # DesignCentral not visible, press Ctrl+I to open it
        pyautogui.hotkey('ctrl', 'i')
        
        # Wait for UI to stabilize after opening
        time.sleep(0.5)
        
        # Refresh root to pick up new window
        self._refresh_root()
        
        # Retry once to find DesignCentral
        print("DEBUG: Checking for DesignCentral window after Ctrl+I (attempt 1)...")
        dc = self.get_designcentral()
        if dc is not None:
            print("DEBUG: DesignCentral window found after Ctrl+I")
            return True
        
        # If still not found, wait a bit more and try again
        print("DEBUG: DesignCentral window not found, waiting longer...")
        time.sleep(0.5)
        self._refresh_root()
        
        print("DEBUG: Checking for DesignCentral window (attempt 2)...")
        dc = self.get_designcentral()
        
        if dc is not None:
            print("DEBUG: DesignCentral window found on second attempt")
            return True
        else:
            print("DEBUG: DesignCentral window still not found after all attempts")
            return False
    
    def get_designcentral_tabcontrol(self):
        """
        Get the tab control within DesignCentral (AutomationId 12320).
        
        Returns:
            UIA element for tab control or None if not found
        """
        dc = self.get_designcentral()
        if dc is None:
            return None
        return self._helpers.find_first(
            dc,
            class_name="SysTabControl32",
            automation_id="12320",
            control_type=UIA_TabControlTypeId
        )
    
    def get_tab_item_by_index(self, index: int):
        """
        Get a tab item by its index within the DesignCentral tab control.
        
        Args:
            index: 0-based index (0=Scale, 1=Rotate, 2=Character)
            
        Returns:
            UIA element for the tab item, or None if not found.
        """
        tabcontrol = self.get_designcentral_tabcontrol()
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
            UIA element for Scale tab
            
        Raises:
            FlexiSignUIAError: If Scale tab cannot be found.
        """
        element = self.get_tab_item_by_index(0)
        if element is None:
            raise FlexiSignUIAError("Scale tab not found in DesignCentral")
        return element
    
    def get_rotate_tab_item(self):
        """
        Get the Rotate tab item in DesignCentral (index 1).
        
        Returns:
            UIA element for Rotate tab or None if not found
        """
        return self.get_tab_item_by_index(1)
    
    def get_character_tab_item(self):
        """
        Get the Character tab item in DesignCentral (index 2).
        
        Returns:
            UIA element for Character tab
            
        Raises:
            FlexiSignUIAError: If Character tab cannot be found.
        """
        element = self.get_tab_item_by_index(2)
        if element is None:
            raise FlexiSignUIAError("Character tab not found in DesignCentral")
        return element
    
    def get_scale_width_input(self, ensure_tab_active: bool = True):
        """
        Get the width input field in the Scale tab (AutomationId 10609).
        
        Args:
            ensure_tab_active: If True, clicks Scale tab first to ensure visibility.
            
        Returns:
            UIA element for width input
            
        Raises:
            FlexiSignUIAError: If width input cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self._helpers.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self.get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Dimension input not found - DesignCentral not available")
        
        element = self._helpers.find_first(
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
            UIA element for height input
            
        Raises:
            FlexiSignUIAError: If height input cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self._helpers.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self.get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Dimension input not found - DesignCentral not available")
        
        element = self._helpers.find_first(
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
            UIA element for proportional checkbox
            
        Raises:
            FlexiSignUIAError: If proportional checkbox cannot be found.
        """
        if ensure_tab_active:
            try:
                scale_tab = self.get_scale_tab_item()
                self._helpers.invoke(scale_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self.get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Proportional checkbox not found - DesignCentral not available")
        
        element = self._helpers.find_first(
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
            UIA element for font family combobox
            
        Raises:
            FlexiSignUIAError: If font combobox cannot be found.
        """
        if ensure_tab_active:
            try:
                char_tab = self.get_character_tab_item()
                self._helpers.invoke(char_tab)
                time.sleep(0.1)
            except FlexiSignUIAError:
                pass
        
        dc = self.get_designcentral()
        if dc is None:
            raise FlexiSignUIAError("Font combobox not found - DesignCentral not available")
        
        element = self._helpers.find_first(
            dc,
            automation_id="10825",
            control_type=UIA_ComboBoxControlTypeId
        )
        if element is None:
            raise FlexiSignUIAError("Font combobox not found")
        return element
