"""
Core FlexiSignUIA class - main orchestrator for FlexiSIGN automation.
"""

from typing import Optional
import comtypes
import comtypes.client

from .constants import (
    IUIAutomation,
    TreeScope_Subtree,
    UIA_ProcessIdPropertyId,
)
from .exceptions import FlexiSignUIAError
from .window_manager import WindowManager
from .uia_helpers import UIAHelpers
from .toolbar import ToolbarSelectors
from .designcentral import DesignCentralSelectors
from .automation import AutomationActions


class FlexiSignUIA:
    """
    Windows UI Automation interface for FlexiSIGN.
    Provides reliable element access via stable AutomationIds.
    
    This is the main entry point for FlexiSIGN automation. It orchestrates
    all lower-level components and provides a clean public API.
    """

    def __init__(self):
        """Initialize UIA COM object and all component managers."""
        self._uia: Optional[IUIAutomation] = None
        self._root = None
        self._com_initialized = False
        
        # Initialize UIA
        self._initialize_uia()
        
        # Initialize component managers
        self._helpers = UIAHelpers(self._uia)
        self._window_manager = WindowManager(self._uia, self._refresh_root)
        self._toolbar = None  # Initialized after root is available
        self._designcentral = None  # Initialized after root is available
        self._automation = None  # Initialized after root is available

    def _initialize_uia(self):
        """Create the UIA COM object."""
        try:
            # Initialize COM for this thread if not already done
            try:
                comtypes.CoInitialize()
                self._com_initialized = True
            except OSError:
                # COM already initialized in this thread, that's fine
                self._com_initialized = False
            
            self._uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=IUIAutomation
            )
        except Exception as e:
            raise FlexiSignUIAError(f"Failed to initialize UI Automation: {e}")

    def cleanup(self):
        """Release UIA resources."""
        self._root = None
        self._window_manager = None
        self._toolbar = None
        self._designcentral = None
        self._automation = None
        self._helpers = None
        self._uia = None
        
        # Uninitialize COM if we initialized it
        if self._com_initialized:
            try:
                comtypes.CoUninitialize()
                self._com_initialized = False
            except:
                pass

    def _refresh_root(self):
        """Refresh the UIA root element for the current PID."""
        pid = self._window_manager.pid if self._window_manager else None
        if self._uia and pid:
            root = self._uia.GetRootElement()
            cond = self._uia.CreatePropertyCondition(UIA_ProcessIdPropertyId, pid)
            self._root = root.FindFirst(TreeScope_Subtree, cond)
            if self._root is None:
                print(f"WARNING: Could not find root element for PID {pid}")
            else:
                print(f"Root element refreshed successfully for PID {pid}")
                # Re-initialize component managers that depend on root
                self._toolbar = ToolbarSelectors(self._root, self._helpers)
                self._designcentral = DesignCentralSelectors(
                    self._root, self._uia, self._helpers, self._refresh_root
                )
                self._automation = AutomationActions(
                    self._toolbar, self._designcentral, self._helpers
                )

    # =========================================================================
    # Window Management - Public API
    # =========================================================================

    def find_and_activate_window(self) -> bool:
        """
        Find FlexiSIGN window and bring to foreground.
        Implements retry logic with 5-second wait.
        
        Returns:
            True if successful, False otherwise.
        """
        return self._window_manager.find_and_activate_window(lambda: self._root)

    # =========================================================================
    # Toolbar Actions - Public API
    # =========================================================================

    def get_text_tool(self):
        """Get the Text Tool button from the toolbar."""
        self._ensure_initialized()
        return self._toolbar.get_text_tool()

    def get_select_tool(self):
        """Get the Select Tool button from the toolbar."""
        self._ensure_initialized()
        return self._toolbar.get_select_tool()

    # =========================================================================
    # DesignCentral - Public API
    # =========================================================================

    def ensure_designcentral_open(self) -> bool:
        """Ensure DesignCentral panel is visible."""
        self._ensure_initialized()
        return self._designcentral.ensure_designcentral_open()

    def get_scale_tab_item(self):
        """Get the Scale tab item in DesignCentral."""
        self._ensure_initialized()
        return self._designcentral.get_scale_tab_item()

    def get_character_tab_item(self):
        """Get the Character tab item in DesignCentral."""
        self._ensure_initialized()
        return self._designcentral.get_character_tab_item()

    def get_scale_width_input(self, ensure_tab_active: bool = True):
        """Get the width input field in the Scale tab."""
        self._ensure_initialized()
        return self._designcentral.get_scale_width_input(ensure_tab_active)

    def get_scale_height_input(self, ensure_tab_active: bool = True):
        """Get the height input field in the Scale tab."""
        self._ensure_initialized()
        return self._designcentral.get_scale_height_input(ensure_tab_active)

    def get_proportional_checkbox(self, ensure_tab_active: bool = True):
        """Get the proportional scaling checkbox in the Scale tab."""
        self._ensure_initialized()
        return self._designcentral.get_proportional_checkbox(ensure_tab_active)

    def get_font_family_combobox(self, ensure_tab_active: bool = True):
        """Get the font family combobox in the Character tab."""
        self._ensure_initialized()
        return self._designcentral.get_font_family_combobox(ensure_tab_active)

    # =========================================================================
    # High-Level Automation Actions - Public API
    # =========================================================================

    def click_text_tool(self) -> bool:
        """Click the Text Tool (T icon) in the toolbar."""
        self._ensure_initialized()
        return self._automation.click_text_tool()

    def click_select_tool(self) -> bool:
        """Click the Select Tool (pointer icon) in the toolbar."""
        self._ensure_initialized()
        return self._automation.click_select_tool()

    def click_canvas_center(self) -> bool:
        """Click the center of the canvas area."""
        self._ensure_initialized()
        return self._automation.click_canvas_center()

    def create_text(self, text: str) -> bool:
        """Create a text object with the specified content."""
        self._ensure_initialized()
        return self._automation.create_text(text)

    def set_dimensions(self, width: str, height: str) -> bool:
        """Set object dimensions via Scale tab."""
        self._ensure_initialized()
        return self._automation.set_dimensions(width, height)

    def set_font(self, font_name: str) -> bool:
        """Set font via Character tab."""
        self._ensure_initialized()
        return self._automation.set_font(font_name)

    def apply_style(self, style_name: str = None) -> bool:
        """Apply a style. If style_name provided, searches for it."""
        self._ensure_initialized()
        return self._automation.apply_style(style_name)

    def move_object(self, direction: str, distance: int) -> bool:
        """Move selected object using Shift+Arrow keys."""
        self._ensure_initialized()
        return self._automation.move_object(direction, distance)

    # =========================================================================
    # Low-Level Helpers - Public API (for advanced usage)
    # =========================================================================

    def invoke(self, element) -> bool:
        """Invoke a button or invokable control using InvokePattern."""
        return self._helpers.invoke(element)

    def set_value(self, element, text: str) -> bool:
        """Set value for an Edit control using ValuePattern."""
        return self._helpers.set_value(element, text)

    def toggle_checkbox(self, element, target_on: bool) -> bool:
        """Set a checkbox to the desired state using TogglePattern."""
        return self._helpers.toggle_checkbox(element, target_on)

    def get_bounding_rect(self, element):
        """Return bounding rectangle as tuple (left, top, right, bottom)."""
        return self._helpers.get_bounding_rect(element)

    def click_element_center(self, element) -> bool:
        """Click the center of a UI element using its bounding rect."""
        self._ensure_initialized()
        return self._automation.click_element_center(element)

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _ensure_initialized(self):
        """Ensure all components are initialized."""
        if self._automation is None:
            raise FlexiSignUIAError(
                "FlexiSignUIA not fully initialized. "
                "Call find_and_activate_window() first."
            )
