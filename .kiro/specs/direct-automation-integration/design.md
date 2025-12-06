# Design Document: Direct Automation Integration

## Overview

This feature extends the existing Two-Model Pipeline to support a "direct automation" mode that uses Windows UI Automation (UIA) instead of vision-based element detection. For standard, predictable tasks like creating number plates with specific dimensions and fonts, the Planner Model can generate commands that execute directly via UIA, providing faster and more reliable automation.

The key insight is that FlexiSIGN's UI elements have stable AutomationIds that don't change between sessions. By leveraging these identifiers, we can click buttons, set input values, and navigate tabs without taking screenshots or running AI vision models.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Local Client                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐     ┌─────────────────────────────────────────────┐    │
│  │  Plan Executor  │     │           FlexiSIGN UIA Module              │    │
│  │  (Extended)     │     │                                             │    │
│  ├─────────────────┤     ├─────────────────────────────────────────────┤    │
│  │                 │     │  ┌─────────────────┐  ┌─────────────────┐   │    │
│  │ mode="direct"?  │────▶│  │ Window Manager  │  │ Element Selectors│   │    │
│  │      │          │     │  │ - find_process  │  │ - get_text_tool │   │    │
│  │      ▼          │     │  │ - activate_win  │  │ - get_select_tool│  │    │
│  │ execute_direct_ │     │  │ - get_pid       │  │ - get_scale_tab │   │    │
│  │ command()       │     │  └─────────────────┘  │ - get_width_input│  │    │
│  │      │          │     │                       │ - get_height_input│ │    │
│  │      ▼          │     │  ┌─────────────────┐  │ - get_font_combo │  │    │
│  │ UIA Actions:    │     │  │ Action Helpers  │  └─────────────────┘   │    │
│  │ - create_text   │────▶│  │ - click_element │                        │    │
│  │ - set_dimensions│     │  │ - set_value     │                        │    │
│  │ - set_font      │     │  │ - toggle_checkbox│                       │    │
│  │ - apply_style   │     │  │ - invoke        │                        │    │
│  │ - move_object   │     │  └─────────────────┘                        │    │
│  │                 │     │                                             │    │
│  └─────────────────┘     └─────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────┐                                                        │
│  │ mode="vision"?  │────▶ Existing Vision Pipeline (unchanged)              │
│  └─────────────────┘                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. FlexiSIGN UIA Module (`local_client/flexisign_uia.py`)

A new module that encapsulates all Windows UI Automation interactions with FlexiSIGN.

```python
class FlexiSignUIA:
    """
    Windows UI Automation interface for FlexiSIGN.
    Provides reliable element access via stable AutomationIds.
    """
    
    def __init__(self):
        """Initialize UIA COM object and find FlexiSIGN process."""
        
    def find_and_activate_window(self) -> bool:
        """
        Find FlexiSIGN window and bring to foreground.
        Returns True if successful, False otherwise.
        Implements retry logic with 5-second wait.
        """
        
    def ensure_designcentral_open(self) -> bool:
        """
        Ensure DesignCentral panel is visible.
        Opens with Ctrl+I if not found.
        """
        
    # Tool Actions
    def click_text_tool(self) -> bool:
        """Click the Text Tool (T icon) in the toolbar."""
        
    def click_select_tool(self) -> bool:
        """Click the Select Tool (pointer icon) in the toolbar."""
        
    def click_canvas_center(self) -> bool:
        """Click the center of the canvas area."""
        
    # Dimension Actions
    def set_dimensions(self, width: str, height: str) -> bool:
        """
        Set object dimensions via Scale tab.
        Disables proportional scaling, sets width, then height.
        """
        
    # Font Actions
    def set_font(self, font_name: str) -> bool:
        """
        Set font via Character tab.
        Clicks font combobox, types name, presses Enter.
        """
        
    # Style Actions
    def open_apply_styles(self) -> bool:
        """Open Apply Styles window with Shift+S."""
        
    def apply_style(self, style_name: str = None) -> bool:
        """
        Apply a style. If style_name provided, searches for it.
        """
        
    # Movement Actions
    def move_object(self, direction: str, distance: int) -> bool:
        """
        Move selected object using Shift+Arrow keys.
        direction: 'up', 'down', 'left', 'right'
        distance: number of key presses
        """
        
    def cleanup(self):
        """Release UIA resources."""
```

### 2. Extended Plan Executor (`local_client/plan_executor.py`)

The existing PlanExecutor class will be extended to handle direct automation commands.

```python
class PlanExecutor:
    # ... existing code ...
    
    def __init__(self, vision_service: VisionService, status_callback: callable):
        # ... existing init ...
        self._flexisign_uia: Optional[FlexiSignUIA] = None
    
    def execute_plan(self, plan: dict) -> bool:
        """
        Execute plan - routes to direct or vision mode based on plan['mode'].
        """
        mode = plan.get('mode', 'vision')
        
        if mode == 'direct':
            return self._execute_direct_plan(plan)
        else:
            return self._execute_vision_plan(plan)  # existing logic
    
    def _execute_direct_plan(self, plan: dict) -> bool:
        """
        Execute plan using UIA (no vision/screenshots).
        """
        # Initialize UIA if needed
        if not self._flexisign_uia:
            self._flexisign_uia = FlexiSignUIA()
        
        # Activate FlexiSIGN window
        if not self._flexisign_uia.find_and_activate_window():
            self._send_status("Failed to activate FlexiSIGN window", "error")
            return False
        
        # Execute each command
        for step in plan.get('sequence', []):
            self._execute_direct_step(step)
        
        return True
    
    def _execute_direct_step(self, step: dict) -> bool:
        """
        Execute a single direct automation step.
        Supports: create_text, set_dimensions, set_font, apply_style, move_object, keyboard
        """
```

### 3. Updated Planner Model Prompt

The Planner Model's system prompt will be updated to support direct automation mode:

```text
You are the Automation Planner for a FlexiSIGN number plate machine.
Your goal is to parse user commands into a JSON Execution Plan.

### EXECUTION MODES:
1. **direct**: Use for standard number plate tasks. Commands execute via UI Automation (faster, more reliable).
2. **vision**: Use for complex or non-standard tasks requiring visual element detection.

### DIRECT MODE COMMANDS:
- create_text: Create text object with specified content
- set_dimensions: Set width and height of selected object
- set_font: Change font of selected text
- apply_style: Apply a predefined style (opens with Shift+S)
- move_object: Move object using arrow keys
- keyboard: Raw keyboard input (hotkeys, typing)

### EXAMPLE OUTPUT (Direct Mode):
{
  "mode": "direct",
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "New Page"},
    {"order": 2, "type": "create_text", "text": "PB12W3998", "desc": "Create plate text"},
    {"order": 3, "type": "set_font", "font_name": "Blackberry", "desc": "Set plate font"},
    {"order": 4, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set front plate size"},
    {"order": 5, "type": "move_object", "direction": "up", "distance": 10, "desc": "Move plate up"}
  ]
}
```

## Data Models

### Direct Command Schema

```json
{
  "mode": "direct",
  "sequence": [
    {
      "order": 1,
      "type": "keyboard",
      "value": "ctrl+n",
      "desc": "New Page"
    },
    {
      "order": 2,
      "type": "create_text",
      "text": "PB12W3998",
      "desc": "Create plate text"
    },
    {
      "order": 3,
      "type": "set_dimensions",
      "width": "8",
      "height": "1.2",
      "desc": "Set front plate size"
    },
    {
      "order": 4,
      "type": "set_font",
      "font_name": "Blackberry",
      "desc": "Set plate font"
    },
    {
      "order": 5,
      "type": "apply_style",
      "style_name": "Iron Plate",
      "desc": "Apply iron plate style"
    },
    {
      "order": 6,
      "type": "move_object",
      "direction": "up",
      "distance": 10,
      "desc": "Move plate up"
    }
  ]
}
```

### Command Type Definitions

| Type | Required Fields | Optional Fields | Description |
|------|-----------------|-----------------|-------------|
| keyboard | value | repeats | Raw keyboard input |
| create_text | text | - | Create text object |
| set_dimensions | width, height | - | Set object size |
| set_font | font_name | - | Change font |
| apply_style | - | style_name | Apply style (Shift+S) |
| move_object | direction, distance | - | Move with arrow keys |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Window Detection Correctness

*For any* list of window titles, the FlexiSIGN detection function SHALL return True if and only if at least one title contains the substring "FlexiSIGN" (case-insensitive).

**Validates: Requirements 1.1**

### Property 2: Direct Mode Command Routing

*For any* execution plan with mode="direct", the Plan Executor SHALL NOT invoke screenshot capture or vision mapping functions, and SHALL invoke UIA-based execution functions.

**Validates: Requirements 7.3**

### Property 3: Vision Mode Command Routing

*For any* execution plan with mode="vision", the Plan Executor SHALL invoke the existing vision-based pipeline including screenshot capture and vision mapping.

**Validates: Requirements 7.4**

### Property 4: Create Text Action Sequence

*For any* create_text command with a non-empty text parameter, the execution SHALL invoke Text Tool click, canvas click, text typing, and Select Tool click in that order.

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 5: Set Dimensions Action Sequence

*For any* set_dimensions command with valid width and height parameters, the execution SHALL navigate to Scale tab, disable proportional scaling, set width value, set height value, and confirm with Enter in that order.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 6: Set Font Action Sequence

*For any* set_font command with a non-empty font_name parameter, the execution SHALL navigate to Character tab, click font combobox, type font name, and press Enter in that order.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 7: Move Object Direction Mapping

*For any* move_object command, the direction parameter SHALL map to the correct arrow key: "up"→Up, "down"→Down, "left"→Left, "right"→Right, and the key SHALL be pressed with Shift modifier the specified number of times.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

### Property 8: DesignCentral Auto-Open

*For any* command that requires DesignCentral access (set_dimensions, set_font), if DesignCentral is not visible, the system SHALL press Ctrl+I before attempting to access DesignCentral controls.

**Validates: Requirements 9.1, 9.2**

### Property 9: UIA Element Not Found Error

*For any* UIA element lookup that fails to find the target element, the FlexiSIGN UIA module SHALL raise an exception with a message containing the element name that was not found.

**Validates: Requirements 8.4**

## Error Handling

### Window Activation Errors

| Error Condition | Handling Strategy |
|----------------|-------------------|
| FlexiSIGN window not found | Wait 5 seconds, retry once, then return error with message "FlexiSIGN window not found" |
| Window activation failed | Log warning, continue execution (window may still be usable) |
| PID retrieval failed | Return error with message "Could not get FlexiSIGN process ID" |

### UIA Element Errors

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Text Tool not found | Return error with message "Text Tool not found in toolbar" |
| Select Tool not found | Return error with message "Select Tool not found in toolbar" |
| DesignCentral not found | Press Ctrl+I to open, wait 0.5s, retry once |
| Scale tab not found | Return error with message "Scale tab not found in DesignCentral" |
| Width/Height input not found | Return error with message "Dimension input not found" |
| Font combobox not found | Return error with message "Font combobox not found" |

### Graceful Degradation

- If direct mode fails to find a UI element, log the error and continue with remaining steps
- If window activation fails after retry, report error but don't crash
- All errors should be reported to the mobile app via status updates

## Testing Strategy

### Unit Testing

Unit tests will cover:
- Window title matching logic for FlexiSIGN detection
- Command type routing (direct vs vision mode)
- Direction-to-key mapping for move_object
- Error message generation for missing elements

### Property-Based Testing

Property-based tests will use the `hypothesis` library (Python) to verify:

1. **Window Detection Property**: Generate random window title lists, verify detection logic
2. **Mode Routing Property**: Generate random plans with different modes, verify correct execution path
3. **Action Sequence Properties**: Generate random command parameters, verify action sequences
4. **Direction Mapping Property**: Generate random directions and distances, verify key mappings

Each property-based test will:
- Run a minimum of 100 iterations
- Be tagged with the corresponding correctness property reference
- Use format: `**Feature: direct-automation-integration, Property {number}: {property_text}**`

### Integration Testing

Integration tests will verify:
- Full create_text → set_dimensions → set_font workflow
- Window activation and DesignCentral auto-open
- Error handling when FlexiSIGN is not running

## File Structure

```
local_client/
├── flexisign_uia.py          # NEW: FlexiSIGN UIA module
├── plan_executor.py          # MODIFIED: Add direct mode support
├── client.py                 # MODIFIED: Initialize UIA module
├── tests/
│   ├── test_flexisign_uia.py # NEW: UIA module tests
│   └── test_plan_executor_direct.py # NEW: Direct mode tests

backend/
├── gemini_service.py         # MODIFIED: Update planner prompt for direct mode
```

## Migration Notes

### Backward Compatibility

- Existing vision-based plans (mode="vision" or no mode specified) continue to work unchanged
- The default mode remains "vision" for backward compatibility
- No changes required to mobile app or WebSocket protocol

### Gradual Rollout

1. Phase 1: Implement FlexiSIGN UIA module with basic actions
2. Phase 2: Extend Plan Executor with direct mode routing
3. Phase 3: Update Planner Model prompt to generate direct mode plans
4. Phase 4: Test with standard number plate workflows
5. Phase 5: Expand direct mode support to more complex workflows

