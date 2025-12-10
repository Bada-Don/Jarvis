"""
Path Step Types Module for Direct Path Automation

This module defines the step dataclasses for direct path operations in execution plans.
These step types enable file save/open operations, File Explorer navigation, and
text-based clicking to be serialized, reviewed, and replayed.

Requirements: 7.1, 7.2, 7.3
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple, List, Dict, Any, Union


@dataclass
class SaveFileStep:
    """
    Step to save a file using direct path typing.
    
    Represents a save operation that uses Ctrl+S followed by typing
    the full absolute path in the filename field.
    
    Attributes:
        order: Execution order in the plan
        path: Full absolute path including filename and extension
        overwrite_policy: Policy for file conflicts ("overwrite", "rename", "abort", "prompt")
        desc: Human-readable description of the step
        type: Step type identifier (always "save_file")
    
    Requirements: 7.1, 7.2, 7.3
    """
    order: int
    path: str
    overwrite_policy: str = "prompt"
    desc: str = ""
    type: str = field(default="save_file", init=False)
    
    def __post_init__(self):
        """Validate step fields."""
        if not self.path:
            raise ValueError("path cannot be empty")
        
        valid_policies = {"overwrite", "rename", "abort", "prompt"}
        if self.overwrite_policy not in valid_policies:
            raise ValueError(
                f"Invalid overwrite_policy '{self.overwrite_policy}'. "
                f"Must be one of: {valid_policies}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the step
        
        Requirements: 7.1
        """
        return {
            "order": self.order,
            "type": self.type,
            "path": self.path,
            "overwrite_policy": self.overwrite_policy,
            "desc": self.desc
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveFileStep':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with step data
        
        Returns:
            SaveFileStep instance
        
        Requirements: 7.2
        """
        return cls(
            order=data["order"],
            path=data["path"],
            overwrite_policy=data.get("overwrite_policy", "prompt"),
            desc=data.get("desc", "")
        )


@dataclass
class OpenFileStep:
    """
    Step to open a file using direct path typing.
    
    Represents an open operation that uses Ctrl+O followed by typing
    the full absolute path in the filename field.
    
    Attributes:
        order: Execution order in the plan
        path: Full absolute path to the file to open
        desc: Human-readable description of the step
        type: Step type identifier (always "open_file")
    
    Requirements: 7.1, 7.2, 7.3
    """
    order: int
    path: str
    desc: str = ""
    type: str = field(default="open_file", init=False)
    
    def __post_init__(self):
        """Validate step fields."""
        if not self.path:
            raise ValueError("path cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the step
        
        Requirements: 7.1
        """
        return {
            "order": self.order,
            "type": self.type,
            "path": self.path,
            "desc": self.desc
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenFileStep':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with step data
        
        Returns:
            OpenFileStep instance
        
        Requirements: 7.2
        """
        return cls(
            order=data["order"],
            path=data["path"],
            desc=data.get("desc", "")
        )


@dataclass
class NavigateExplorerStep:
    """
    Step to navigate File Explorer to a directory.
    
    Represents a navigation operation that uses Ctrl+L to focus the
    address bar, types the directory path, and presses Enter.
    
    Attributes:
        order: Execution order in the plan
        directory: Full directory path to navigate to
        desc: Human-readable description of the step
        type: Step type identifier (always "navigate_explorer")
    
    Requirements: 7.1, 7.2, 7.3
    """
    order: int
    directory: str
    desc: str = ""
    type: str = field(default="navigate_explorer", init=False)
    
    def __post_init__(self):
        """Validate step fields."""
        if not self.directory:
            raise ValueError("directory cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the step
        
        Requirements: 7.1
        """
        return {
            "order": self.order,
            "type": self.type,
            "directory": self.directory,
            "desc": self.desc
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NavigateExplorerStep':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with step data
        
        Returns:
            NavigateExplorerStep instance
        
        Requirements: 7.2
        """
        return cls(
            order=data["order"],
            directory=data["directory"],
            desc=data.get("desc", "")
        )


@dataclass
class ClickTextStep:
    """
    Step to click on text found via OCR.
    
    Represents a text-based click operation that captures a screenshot,
    performs OCR to find the target text, and clicks at the center of
    the text's bounding box.
    
    Attributes:
        order: Execution order in the plan
        text: Text to find and click
        double_click: If True, perform double-click instead of single click
        region: Optional region constraint as (x1, y1, x2, y2)
        desc: Human-readable description of the step
        type: Step type identifier (always "click_text")
    
    Requirements: 7.1, 7.2, 7.3
    """
    order: int
    text: str
    double_click: bool = False
    region: Optional[Tuple[int, int, int, int]] = None
    desc: str = ""
    type: str = field(default="click_text", init=False)
    
    def __post_init__(self):
        """Validate step fields."""
        if not self.text:
            raise ValueError("text cannot be empty")
        
        if self.region is not None:
            if len(self.region) != 4:
                raise ValueError("region must be a tuple of 4 integers (x1, y1, x2, y2)")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the step
        
        Requirements: 7.1
        """
        result = {
            "order": self.order,
            "type": self.type,
            "text": self.text,
            "double_click": self.double_click,
            "desc": self.desc
        }
        
        if self.region is not None:
            result["region"] = list(self.region)
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClickTextStep':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with step data
        
        Returns:
            ClickTextStep instance
        
        Requirements: 7.2
        """
        region = data.get("region")
        if region is not None:
            region = tuple(region)
        
        return cls(
            order=data["order"],
            text=data["text"],
            double_click=data.get("double_click", False),
            region=region,
            desc=data.get("desc", "")
        )



@dataclass
class ExecutionResult:
    """
    Result of a direct path operation.
    
    Represents the outcome of executing a save, open, navigate, or click_text
    operation, including success status and any error details.
    
    Attributes:
        success: Whether the operation completed successfully
        operation: Type of operation ("save", "open", "navigate", "click_text")
        path: The path that was used in the operation
        error_type: Type of error if failed (e.g., "file_exists", "path_not_found")
        error_message: Human-readable error description
        dialog_detected: Text from any error/confirmation dialog
    
    Requirements: 7.1, 7.2, 7.3
    """
    success: bool
    operation: str
    path: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    dialog_detected: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the result
        
        Requirements: 7.1
        """
        return {
            "success": self.success,
            "operation": self.operation,
            "path": self.path,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "dialog_detected": self.dialog_detected
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionResult':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with result data
        
        Returns:
            ExecutionResult instance
        
        Requirements: 7.2
        """
        return cls(
            success=data["success"],
            operation=data["operation"],
            path=data.get("path"),
            error_type=data.get("error_type"),
            error_message=data.get("error_message"),
            dialog_detected=data.get("dialog_detected")
        )


@dataclass
class ClickResult:
    """
    Result of a text-based click operation.
    
    Represents the outcome of a click_text operation, including the
    click location and any detected text matches.
    
    Attributes:
        success: Whether the click was performed successfully
        target_text: The text that was searched for
        clicked_location: The (x, y) coordinates where the click occurred
        all_matches_count: Number of text matches found
        error_message: Description of the error if the operation failed
    
    Requirements: 7.1, 7.2, 7.3
    """
    success: bool
    target_text: str
    clicked_location: Optional[Tuple[int, int]] = None
    all_matches_count: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the result
        
        Requirements: 7.1
        """
        return {
            "success": self.success,
            "target_text": self.target_text,
            "clicked_location": list(self.clicked_location) if self.clicked_location else None,
            "all_matches_count": self.all_matches_count,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClickResult':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary with result data
        
        Returns:
            ClickResult instance
        
        Requirements: 7.2
        """
        clicked_location = data.get("clicked_location")
        if clicked_location is not None:
            clicked_location = tuple(clicked_location)
        
        return cls(
            success=data["success"],
            target_text=data["target_text"],
            clicked_location=clicked_location,
            all_matches_count=data.get("all_matches_count", 0),
            error_message=data.get("error_message")
        )


# Type alias for any path step type
PathStep = Union[SaveFileStep, OpenFileStep, NavigateExplorerStep, ClickTextStep]


# Step type registry for deserialization
STEP_TYPE_REGISTRY: Dict[str, type] = {
    "save_file": SaveFileStep,
    "open_file": OpenFileStep,
    "navigate_explorer": NavigateExplorerStep,
    "click_text": ClickTextStep
}


def step_from_dict(data: Dict[str, Any]) -> PathStep:
    """
    Create a step instance from a dictionary based on the type field.
    
    Factory function that deserializes any path step type from its
    dictionary representation.
    
    Args:
        data: Dictionary with step data including "type" field
    
    Returns:
        Appropriate step instance (SaveFileStep, OpenFileStep, etc.)
    
    Raises:
        ValueError: If the step type is unknown
    
    Requirements: 7.2
    """
    step_type = data.get("type")
    
    if step_type not in STEP_TYPE_REGISTRY:
        raise ValueError(f"Unknown step type: {step_type}")
    
    step_class = STEP_TYPE_REGISTRY[step_type]
    return step_class.from_dict(data)


def step_to_dict(step: PathStep) -> Dict[str, Any]:
    """
    Convert any path step to a dictionary.
    
    Convenience function that calls to_dict() on any step type.
    
    Args:
        step: Any path step instance
    
    Returns:
        Dictionary representation of the step
    
    Requirements: 7.1
    """
    return step.to_dict()
