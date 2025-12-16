"""
FlexiSIGN UIA Package
Windows UI Automation interface for FlexiSIGN.
Provides reliable element access via stable AutomationIds.

This package encapsulates all Windows UI Automation interactions with FlexiSIGN,
enabling direct automation without vision-based element detection.
"""

from .core import FlexiSignUIA
from .exceptions import FlexiSignUIAError

__all__ = ['FlexiSignUIA', 'FlexiSignUIAError']
