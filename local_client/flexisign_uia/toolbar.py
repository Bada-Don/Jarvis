"""
Toolbar element selectors for FlexiSIGN.
"""

from .constants import UIA_ToolBarControlTypeId, UIA_ButtonControlTypeId
from .exceptions import FlexiSignUIAError


class ToolbarSelectors:
    """Selectors for toolbar elements in FlexiSIGN."""
    
    def __init__(self, root_element, uia_helpers):
        """
        Initialize toolbar selectors.
        
        Args:
            root_element: Root UIA element
            uia_helpers: UIAHelpers instance for element finding
        """
        self._root = root_element
        self._helpers = uia_helpers
    
    def get_main_toolbar(self):
        """
        Get the main tool toolbar (AutomationId 60272).
        
        Returns:
            UIA element for main toolbar or None if not found
        """
        if self._root is None:
            print("ERROR: get_main_toolbar called but root is None")
            return None
        toolbar = self._helpers.find_first(
            self._root,
            class_name="ToolbarWindow32",
            automation_id="60272",
            control_type=UIA_ToolBarControlTypeId
        )
        if toolbar is None:
            print("WARNING: Main toolbar (AutomationId 60272) not found")
        return toolbar
    
    def get_button_in_toolbar(self, toolbar_elem, button_name: str):
        """
        Find a button by its visible name under a toolbar element.
        
        Args:
            toolbar_elem: Toolbar element to search in
            button_name: Name of the button to find
            
        Returns:
            UIA element for button or None if not found
        """
        if toolbar_elem is None:
            return None
        return self._helpers.find_first(
            toolbar_elem,
            name=button_name,
            control_type=UIA_ButtonControlTypeId
        )
    
    def get_text_tool(self):
        """
        Get the Text Tool button from the toolbar.
        
        Returns:
            UIA element for Text Tool
            
        Raises:
            FlexiSignUIAError: If Text Tool cannot be found.
        """
        toolbar = self.get_main_toolbar()
        element = self.get_button_in_toolbar(toolbar, "Text Tool")
        if element is None:
            raise FlexiSignUIAError("Text Tool not found in toolbar")
        return element
    
    def get_select_tool(self):
        """
        Get the Select Tool button from the toolbar.
        
        Returns:
            UIA element for Select Tool
            
        Raises:
            FlexiSignUIAError: If Select Tool cannot be found.
        """
        toolbar = self.get_main_toolbar()
        element = self.get_button_in_toolbar(toolbar, "Select Tool")
        if element is None:
            raise FlexiSignUIAError("Select Tool not found in toolbar")
        return element
