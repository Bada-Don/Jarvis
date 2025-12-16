"""
Low-level UIA helper functions for element finding and interaction.
"""

from typing import Optional, Tuple
import comtypes.gen.UIAutomationClient

from .constants import (
    TreeScope_Subtree,
    UIA_NamePropertyId,
    UIA_ClassNamePropertyId,
    UIA_AutomationIdPropertyId,
    UIA_BoundingRectanglePropertyId,
    UIA_ControlTypePropertyId,
    UIA_InvokePatternId,
    UIA_ValuePatternId,
    UIA_TogglePatternId,
)


class UIAHelpers:
    """Low-level UIA operations for element finding and interaction."""
    
    def __init__(self, uia_instance):
        """
        Initialize UIA helpers.
        
        Args:
            uia_instance: UIA COM object (IUIAutomation)
        """
        self._uia = uia_instance
    
    def make_and_condition(self, conditions):
        """
        Combine conditions with AndCondition.
        
        Args:
            conditions: List of UIA conditions
            
        Returns:
            Combined condition or None if empty
        """
        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return self._uia.CreateAndConditionFromArray(conditions)
    
    def find_first(self, root, *, name=None, class_name=None, automation_id=None,
                   control_type=None, scope=TreeScope_Subtree):
        """
        Generic first-match finder using provided property filters.
        
        Args:
            root: Root element to search from
            name: Element name to match
            class_name: Element class name to match
            automation_id: Element automation ID to match
            control_type: Element control type to match
            scope: Search scope (default: TreeScope_Subtree)
            
        Returns:
            First matching element or None
        """
        if root is None:
            print("DEBUG: find_first called with None root")
            return None
        
        props = []
        if name is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_NamePropertyId, name))
        if class_name is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_ClassNamePropertyId, class_name))
        if automation_id is not None:
            # Ensure automation_id is a string
            aid = str(automation_id) if not isinstance(automation_id, str) else automation_id
            props.append(self._uia.CreatePropertyCondition(UIA_AutomationIdPropertyId, aid))
        if control_type is not None:
            props.append(self._uia.CreatePropertyCondition(UIA_ControlTypePropertyId, control_type))
        
        cond = self.make_and_condition(props)
        if cond is None:
            return None
        result = root.FindFirst(scope, cond)
        return result
    
    def get_bounding_rect(self, element) -> Optional[Tuple[float, float, float, float]]:
        """
        Return bounding rectangle as tuple (left, top, right, bottom).
        
        Args:
            element: UIA element
        
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
