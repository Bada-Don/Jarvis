# flexisign_selectors.py
# Python 3.10+
# Provides reusable UIAutomation selector helpers for the FlexiSIGN window you dumped.
# Depends: comtypes, psutil
#
# Usage pattern:
#   uia = create_uia()
#   root = get_root_for_pid(uia, pid)
#   btn = get_text_tool(uia, root)
#   invoke(btn)
#
# IMPORTANT: Tab-dependent elements
# Some elements are only visible when their parent tab is active:
#   - scale_width, scale_height, proportional_checkbox: require Scale tab active
#   - font_dropdown: requires Character tab active
# These functions have an 'ensure_tab_active' parameter (default=True) that automatically
# clicks the parent tab before searching for the element.
#
# This module only builds selectors and small interaction helpers using UIA patterns.
# It intentionally avoids injecting keyboard/mouse itself so you can choose your preferred method.

import psutil
import comtypes.client
from typing import Optional, Tuple

# generate bindings
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

# ControlType constants (from UIA) - use the numeric ids directly
# These are standard UIA control type IDs
UIA_ButtonControlTypeId = 50000
UIA_CheckBoxControlTypeId = 50002
UIA_EditControlTypeId = 50004
UIA_PaneControlTypeId = 50033
UIA_TabControlTypeId = 50018
UIA_TabItemControlTypeId = 50019
UIA_ToolBarControlTypeId = 50021
UIA_WindowControlTypeId = 50032
UIA_MenuBarControlTypeId = 50010

# Aliases for backward compatibility
ButtonControlTypeId = UIA_ButtonControlTypeId
EditControlTypeId = UIA_EditControlTypeId
TabControlTypeId = UIA_TabControlTypeId
TabItemControlTypeId = UIA_TabItemControlTypeId
ToolBarControlTypeId = UIA_ToolBarControlTypeId
WindowControlTypeId = UIA_WindowControlTypeId
MenuBarControlTypeId = UIA_MenuBarControlTypeId

# -----------------------
# Core helpers
# -----------------------
def create_uia() -> IUIAutomation:
    """Create and return the IUIAutomation COM object."""
    return comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}",
        interface=IUIAutomation
    )

def list_processes() -> list[Tuple[int, str]]:
    """Return a list of (pid, name) tuples for running user processes."""
    procs = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            procs.append((p.info["pid"], p.info["name"]))
        except Exception:
            pass
    return procs

def get_root_for_pid(uia: IUIAutomation, pid: int):
    """Return the first top-level element that matches the given process id."""
    root = uia.GetRootElement()
    cond = uia.CreatePropertyCondition(UIA_ProcessIdPropertyId, pid)
    return root.FindFirst(TreeScope_Subtree, cond)

def _make_and(uia: IUIAutomation, conds):
    """Combine conditions with AndCondition."""
    if not conds:
        return None
    if len(conds) == 1:
        return conds[0]
    return uia.CreateAndConditionFromArray(conds)

def _prop_cond(uia: IUIAutomation, prop_id, value):
    return uia.CreatePropertyCondition(prop_id, value)

def find_first(uia: IUIAutomation, root, *, name=None, class_name=None, automation_id=None,
               control_type=None, scope=TreeScope_Subtree):
    """Generic first-match finder using provided property filters."""
    props = []
    if name is not None:
        props.append(_prop_cond(uia, UIA_NamePropertyId, name))
    if class_name is not None:
        props.append(_prop_cond(uia, UIA_ClassNamePropertyId, class_name))
    if automation_id is not None:
        props.append(_prop_cond(uia, UIA_AutomationIdPropertyId, automation_id))
    if control_type is not None:
        props.append(_prop_cond(uia, UIA_ControlTypePropertyId, control_type))

    cond = _make_and(uia, props)
    if cond is None:
        return None
    return root.FindFirst(scope, cond)

def find_all(uia: IUIAutomation, root, *, class_name=None, automation_id=None, control_type=None):
    """Return all matching elements (IUIAutomationElementArray) or None."""
    props = []
    if class_name is not None:
        props.append(_prop_cond(uia, UIA_ClassNamePropertyId, class_name))
    if automation_id is not None:
        props.append(_prop_cond(uia, UIA_AutomationIdPropertyId, automation_id))
    if control_type is not None:
        props.append(_prop_cond(uia, UIA_ControlTypePropertyId, control_type))
    cond = _make_and(uia, props)
    if cond is None:
        return None
    return root.FindAll(TreeScope_Subtree, cond)

# -----------------------
# Specific element getters
# -----------------------
# Many elements in your dump have stable names. Where names are blank, we select by container + index.
# Toolbar AutomationId values observed in your dump:
#   View toolbar: AutomationId 60161 (ToolbarWindow32)
#   Main tool toolbar: AutomationId 60272 (ToolbarWindow32)
# Top-level DesignCentral TabControl: AutomationId 12320 (SysTabControl32)
# DesignCentral edits: AutomationId 10609..10612
# Proportional checkbox AutomationId: 11117

def _get_main_toolbar(uia, root):
    # toolbar with AutomationId 60272
    return find_first(uia, root, class_name="ToolbarWindow32", automation_id=str(60272),
                      control_type=ToolBarControlTypeId)

def get_button_in_toolbar(uia, toolbar_elem, button_name: str):
    """Find a button by its visible name under a toolbar element."""
    if toolbar_elem is None:
        return None
    return find_first(uia, toolbar_elem, name=button_name, control_type=ButtonControlTypeId)

def get_select_tool(uia, root):
    return get_button_in_toolbar(uia, _get_main_toolbar(uia, root), "Select Tool")

def get_text_tool(uia, root):
    return get_button_in_toolbar(uia, _get_main_toolbar(uia, root), "Text Tool")

def get_rectangle_tool(uia, root):
    return get_button_in_toolbar(uia, _get_main_toolbar(uia, root), "Rectangle Tool")

def get_oval_tool(uia, root):
    """
    Oval tool is not directly accessible in the toolbar.
    
    To activate it, use one of these methods:
    1. Press keyboard shortcut 'O' (recommended - simplest)
    2. Double-click Rectangle Tool and select from menu
    
    This function returns None as it requires keyboard/mouse interaction.
    Use activate_oval_tool() helper instead.
    """
    return None  # Not directly accessible - use activate_oval_tool() helper

def activate_oval_tool():
    """
    Activate the Oval Tool using keyboard shortcut.
    
    This is the simplest method to activate the Oval Tool.
    Requires: pyautogui or similar keyboard automation library
    
    Returns: True if shortcut was sent (doesn't verify tool activation)
    
    Example:
        activate_oval_tool()
        # Oval tool is now active, draw oval by clicking and dragging
    """
    try:
        import pyautogui
        pyautogui.press('o')
        return True
    except ImportError:
        # Fallback: user can send 'O' key manually
        print("pyautogui not installed. Please press 'O' key manually to activate Oval Tool")
        print("Install with: pip install pyautogui")
        return False

def _get_view_toolbar(uia, root):
    return find_first(uia, root, class_name="ToolbarWindow32", automation_id=str(60161),
                      control_type=ToolBarControlTypeId)

def get_zoom_to_page(uia, root):
    return get_button_in_toolbar(uia, _get_view_toolbar(uia, root), "Zoom to Page")

def get_zoom_to_selected(uia, root):
    return get_button_in_toolbar(uia, _get_view_toolbar(uia, root), "Zoom to Selected")

def get_save_button(uia, root):
    # Save is on the Standard toolbar (AutomationId 60256)
    toolbar = find_first(uia, root, class_name="ToolbarWindow32", automation_id=str(60256),
                         control_type=ToolBarControlTypeId)
    return get_button_in_toolbar(uia, toolbar, "Save") if toolbar else None

def get_cut_plot(uia, root):
    toolbar = find_first(uia, root, class_name="ToolbarWindow32", automation_id=str(60256),
                         control_type=ToolBarControlTypeId)
    return get_button_in_toolbar(uia, toolbar, "Cut/Plot") if toolbar else None

# -----------------------
# DesignCentral specific getters
# -----------------------
def _get_designcentral(uia, root):
    # DesignCentral is a WindowControl with Name "DesignCentral" and Class "#32770"
    return find_first(uia, root, name="DesignCentral", class_name="#32770", control_type=WindowControlTypeId)

def _get_designcentral_pane(uia, root):
    # The actual pane containing controls is a child PaneControl with Class "#32770"
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    return find_first(uia, dc, class_name="#32770", control_type=UIA_PaneControlTypeId)

def get_scale_tab_item(uia, root):
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    # TabControl AutomationId 12320
    tabcontrol = find_first(uia, dc, class_name="SysTabControl32", automation_id=str(12320),
                            control_type=TabControlTypeId)
    if not tabcontrol:
        return None
    # Scale tab is the first TabItem (index 0)
    walker = uia.ControlViewWalker
    child = walker.GetFirstChildElement(tabcontrol)
    while child:
        try:
            ctrl_type = child.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
            if ctrl_type == TabItemControlTypeId:
                return child
        except:
            pass
        child = walker.GetNextSiblingElement(child)
    return None

def get_rotate_tab_item(uia, root):
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    tabcontrol = find_first(uia, dc, class_name="SysTabControl32", automation_id=str(12320),
                            control_type=TabControlTypeId)
    if not tabcontrol:
        return None
    # Rotate tab is the second TabItem (index 1)
    walker = uia.ControlViewWalker
    child = walker.GetFirstChildElement(tabcontrol)
    idx = 0
    while child:
        try:
            ctrl_type = child.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
            if ctrl_type == TabItemControlTypeId:
                if idx == 1:
                    return child
                idx += 1
        except:
            pass
        child = walker.GetNextSiblingElement(child)
    return None

def get_character_tab_item(uia, root):
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    tabcontrol = find_first(uia, dc, class_name="SysTabControl32", automation_id=str(12320),
                            control_type=TabControlTypeId)
    if not tabcontrol:
        return None
    # Character tab is the third TabItem (index 2)
    walker = uia.ControlViewWalker
    child = walker.GetFirstChildElement(tabcontrol)
    idx = 0
    while child:
        try:
            ctrl_type = child.GetCurrentPropertyValue(UIA_ControlTypePropertyId)
            if ctrl_type == TabItemControlTypeId:
                if idx == 2:
                    return child
                idx += 1
        except:
            pass
        child = walker.GetNextSiblingElement(child)
    return None

def get_scale_width_input(uia, root, ensure_tab_active=True):
    # First edit control (width) - AutomationId 10609
    # Only visible when Scale tab is active
    if ensure_tab_active:
        scale_tab = get_scale_tab_item(uia, root)
        if scale_tab:
            invoke(scale_tab)  # Click the scale tab to make elements visible
            import time
            time.sleep(0.1)  # Brief wait for UI to update
    
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    return find_first(uia, dc, automation_id=str(10609), control_type=EditControlTypeId, scope=TreeScope_Subtree)

def get_scale_height_input(uia, root, ensure_tab_active=True):
    # Second edit control (height) - AutomationId 10610
    # Only visible when Scale tab is active
    if ensure_tab_active:
        scale_tab = get_scale_tab_item(uia, root)
        if scale_tab:
            invoke(scale_tab)
            import time
            time.sleep(0.1)
    
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    return find_first(uia, dc, automation_id=str(10610), control_type=EditControlTypeId, scope=TreeScope_Subtree)

def get_proportional_checkbox(uia, root, ensure_tab_active=True):
    # Proportional checkbox - AutomationId 11117, ControlType CheckBox
    # Only visible when Scale tab is active
    if ensure_tab_active:
        scale_tab = get_scale_tab_item(uia, root)
        if scale_tab:
            invoke(scale_tab)
            import time
            time.sleep(0.1)
    
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    # It's a CheckBoxControl, not ButtonControl
    UIA_CheckBoxControlTypeId = 50002
    return find_first(uia, dc, automation_id=str(11117), control_type=UIA_CheckBoxControlTypeId, scope=TreeScope_Subtree)

def get_font_dropdown(uia, root, ensure_tab_active=True):
    """Get font dropdown - only visible when Character tab is active."""
    if ensure_tab_active:
        char_tab = get_character_tab_item(uia, root)
        if char_tab:
            invoke(char_tab)  # Click character tab to make font controls visible
            import time
            time.sleep(0.1)
    
    dc = _get_designcentral(uia, root)
    if not dc:
        return None
    # First Edit under DesignCentral when Character tab is active
    edits = find_all(uia, dc, control_type=EditControlTypeId)
    if edits and edits.Length > 0:
        return edits.GetElement(0)
    return None

# -----------------------
# Interaction helpers
# -----------------------
def invoke(element):
    """Invoke a button or invokable control if it supports InvokePattern."""
    if element is None:
        return False
    try:
        patt = element.GetCurrentPattern(UIA_InvokePatternId)
        if patt:
            patt_obj = patt.QueryInterface(comtypes.gen.UIAutomationClient.IUIAutomationInvokePattern)
            patt_obj.Invoke()
            return True
    except Exception:
        # some controls expose Invoke through GetCurrentPattern returning IUnknown - handle generically
        try:
            # fallback: try to call element.SetFocus() then attempt keyboard/mouse externally
            element.SetFocus()
            return True
        except Exception:
            return False
    return False

def set_value(element, text: str):
    """Set value for an Edit control using ValuePattern if available."""
    if element is None:
        return False
    try:
        patt = element.GetCurrentPattern(UIA_ValuePatternId)
        if patt:
            patt_obj = patt.QueryInterface(comtypes.gen.UIAutomationClient.IUIAutomationValuePattern)
            patt_obj.SetValue(text)
            return True
    except Exception:
        try:
            element.SetFocus()
            # caller should send keyboard input after focus if ValuePattern not supported
            return True
        except Exception:
            return False
    return False

def toggle_checkbox(element, target_on: bool):
    """Try to set a checkbox/toggle to the desired state using TogglePattern (best-effort)."""
    if element is None:
        return False
    try:
        patt = element.GetCurrentPattern(UIA_TogglePatternId)
        if patt:
            patt_obj = patt.QueryInterface(comtypes.gen.UIAutomationClient.IUIAutomationTogglePattern)
            current = patt_obj.CurrentToggleState
            # TogglePattern state: 0=Off,1=On,2=Indeterminate
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

def get_bounding_rect(element):
    """Return bounding rectangle as tuple (left, top, right, bottom) or None."""
    if element is None:
        return None
    try:
        rect = element.GetCurrentPropertyValue(UIA_BoundingRectanglePropertyId)
        # rect is a SAFEARRAY of 4 doubles: left, top, width, height in some bindings; adapt
        # In comtypes it's often returned as a tuple/list: (left, top, width, height)
        if isinstance(rect, (list, tuple)) and len(rect) >= 4:
            left, top, width, height = rect[0], rect[1], rect[2], rect[3]
            return (left, top, left + width, top + height)
    except Exception:
        return None
    return None

# -----------------------
# Convenience "get all" mapping
# -----------------------
def get_all_selectors(uia, root, check_tab_elements=True) -> dict:
    """
    Get all selectors. 
    
    If check_tab_elements=True, will activate tabs to check their child elements.
    If False, only checks elements that are currently visible.
    """
    result = {
        "select_tool": get_select_tool(uia, root),
        "text_tool": get_text_tool(uia, root),
        "rectangle_tool": get_rectangle_tool(uia, root),
        "oval_tool": get_oval_tool(uia, root),
        "zoom_to_page": get_zoom_to_page(uia, root),
        "zoom_to_selected": get_zoom_to_selected(uia, root),
        "save": get_save_button(uia, root),
        "cut_plot": get_cut_plot(uia, root),
        "scale_tab": get_scale_tab_item(uia, root),
        "rotate_tab": get_rotate_tab_item(uia, root),
        "character_tab": get_character_tab_item(uia, root),
    }
    
    if check_tab_elements:
        # Check Scale tab elements (activate Scale tab first)
        result["scale_width"] = get_scale_width_input(uia, root, ensure_tab_active=True)
        result["scale_height"] = get_scale_height_input(uia, root, ensure_tab_active=False)  # Already active
        result["proportional_checkbox"] = get_proportional_checkbox(uia, root, ensure_tab_active=False)
        
        # Check Character tab elements (activate Character tab)
        result["font_dropdown"] = get_font_dropdown(uia, root, ensure_tab_active=True)
    else:
        # Just check without switching tabs
        result["scale_width"] = get_scale_width_input(uia, root, ensure_tab_active=False)
        result["scale_height"] = get_scale_height_input(uia, root, ensure_tab_active=False)
        result["proportional_checkbox"] = get_proportional_checkbox(uia, root, ensure_tab_active=False)
        result["font_dropdown"] = get_font_dropdown(uia, root, ensure_tab_active=False)
    
    return result

# -----------------------
# Example usage helper
# -----------------------
if __name__ == "__main__":
    import sys

    uia = create_uia()
    procs = list_processes()
    for i, (pid, name) in enumerate(procs):
        print(f"{i}: {name} (PID {pid})")
    idx = int(input("Select index: "))
    pid = procs[idx][0]
    root = get_root_for_pid(uia, pid)
    if not root:
        print("No root element for PID", pid)
        sys.exit(1)

    print("\n=== Testing all selectors ===")
    sels = get_all_selectors(uia, root)
    for k, v in sels.items():
        print(f"{k}: {'FOUND' if v else 'MISSING'}")
    
    print("\n=== Example: Working with Scale tab elements ===")
    # These will automatically click the Scale tab first
    width_input = get_scale_width_input(uia, root, ensure_tab_active=True)
    if width_input:
        print("Width input found, setting value to 5.0")
        set_value(width_input, "5.0")
    
    print("\n=== Example: Working with Character tab elements ===")
    # This will automatically click the Character tab first
    font_dropdown = get_font_dropdown(uia, root, ensure_tab_active=True)
    if font_dropdown:
        print("Font dropdown found")
        # You can now interact with it
    
    print("\n=== Example: Activating Oval Tool ===")
    print("Oval tool requires keyboard shortcut 'O'")
    print("Call activate_oval_tool() to activate it")
    # activate_oval_tool()  # Uncomment to actually activate it
