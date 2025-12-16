"""
UIA constants and control type IDs for FlexiSIGN automation.
"""

import comtypes.client

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

# Export all constants
__all__ = [
    'IUIAutomation',
    'TreeScope_Subtree',
    'UIA_NamePropertyId',
    'UIA_ClassNamePropertyId',
    'UIA_AutomationIdPropertyId',
    'UIA_BoundingRectanglePropertyId',
    'UIA_ControlTypePropertyId',
    'UIA_ProcessIdPropertyId',
    'UIA_InvokePatternId',
    'UIA_ValuePatternId',
    'UIA_TogglePatternId',
    'UIA_ButtonControlTypeId',
    'UIA_CheckBoxControlTypeId',
    'UIA_ComboBoxControlTypeId',
    'UIA_EditControlTypeId',
    'UIA_PaneControlTypeId',
    'UIA_TabControlTypeId',
    'UIA_TabItemControlTypeId',
    'UIA_ToolBarControlTypeId',
    'UIA_WindowControlTypeId',
]
