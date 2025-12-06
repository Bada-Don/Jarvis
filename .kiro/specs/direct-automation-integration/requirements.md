# Requirements Document

## Introduction

This feature integrates the robust Windows UI Automation (UIA) approach from the experimental automation sample into the main application pipeline. For simple, predictable tasks like "Make an Iron plate set, PB12W3958", the Planner Model can generate commands that execute directly via UIA without requiring vision-based element detection. This provides faster, more reliable automation for standard workflows by leveraging FlexiSIGN's stable UI element identifiers (AutomationIds) and the proven window activation mechanism.

## Glossary

- **UI Automation (UIA)**: Microsoft's accessibility framework that provides programmatic access to UI elements via stable identifiers
- **AutomationId**: A stable identifier assigned to UI elements that doesn't change between sessions
- **Direct Automation**: Execution mode where commands are executed via UIA without vision/screenshot analysis
- **Vision-Based Automation**: Existing execution mode using Set-of-Mark detection and Gemini Vision Mapper
- **DesignCentral**: FlexiSIGN's property panel containing tabs for Scale, Rotate, and Character settings
- **FlexiSIGN Manager**: Component responsible for launching and managing the FlexiSIGN application window
- **Plan Executor**: Component that interprets and executes automation commands from the Planner Model

## Requirements

### Requirement 1

**User Story:** As a user, I want the system to automatically bring FlexiSIGN to the foreground before automation, so that commands execute reliably.

#### Acceptance Criteria

1. WHEN the Local Client starts a direct automation workflow THEN the Local Client SHALL detect the FlexiSIGN process by window title containing "FlexiSIGN"
2. WHEN the FlexiSIGN process is detected THEN the Local Client SHALL retrieve the process ID (PID) from the window handle
3. WHEN the PID is retrieved THEN the Local Client SHALL activate the FlexiSIGN window and bring it to the foreground
4. IF the FlexiSIGN window cannot be activated THEN the Local Client SHALL wait 5 seconds and retry once before reporting an error

### Requirement 2

**User Story:** As a user, I want to create text objects with specific content, so that I can automate number plate text entry.

#### Acceptance Criteria

1. WHEN the Planner Model generates a "create_text" command with a "text" parameter THEN the Plan Executor SHALL click the Text Tool using UIA
2. WHEN the Text Tool is active THEN the Plan Executor SHALL click the canvas center and type the specified text
3. WHEN text entry completes THEN the Plan Executor SHALL click the Select Tool to finalize the text object
4. WHEN the text object is selected THEN the Plan Executor SHALL report success status

### Requirement 3

**User Story:** As a user, I want to set object dimensions precisely, so that number plates have correct sizes.

#### Acceptance Criteria

1. WHEN the Planner Model generates a "set_dimensions" command with "width" and "height" parameters THEN the Plan Executor SHALL navigate to the Scale tab in DesignCentral
2. WHEN the Scale tab is active THEN the Plan Executor SHALL disable proportional scaling by unchecking the proportional checkbox
3. WHEN proportional scaling is disabled THEN the Plan Executor SHALL set the width input field to the specified width value
4. WHEN the width is set THEN the Plan Executor SHALL set the height input field to the specified height value
5. WHEN both dimensions are set THEN the Plan Executor SHALL press Enter to confirm the values

### Requirement 4

**User Story:** As a user, I want to change text font, so that number plates use the correct typography.

#### Acceptance Criteria

1. WHEN the Planner Model generates a "set_font" command with a "font_name" parameter THEN the Plan Executor SHALL navigate to the Character tab in DesignCentral
2. WHEN the Character tab is active THEN the Plan Executor SHALL click the font family combobox
3. WHEN the font combobox is focused THEN the Plan Executor SHALL type the font name and press Enter to apply

### Requirement 5

**User Story:** As a user, I want to apply predefined styles to objects, so that I can quickly format number plates.

#### Acceptance Criteria

1. WHEN the Planner Model generates an "apply_style" command THEN the Plan Executor SHALL press Shift+S to open the Apply Styles window
2. WHEN the Apply Styles window opens THEN the Plan Executor SHALL wait for the window to be ready before proceeding
3. IF a "style_name" parameter is provided THEN the Plan Executor SHALL type the style name to search and press Enter to apply

### Requirement 6

**User Story:** As a user, I want to move objects on the canvas, so that I can position front and back plates correctly.

#### Acceptance Criteria

1. WHEN the Planner Model generates a "move_object" command with "direction" and "distance" parameters THEN the Plan Executor SHALL use arrow keys with Shift modifier for larger movements
2. WHEN the direction is "up" THEN the Plan Executor SHALL press Shift+Up the specified number of times
3. WHEN the direction is "down" THEN the Plan Executor SHALL press Shift+Down the specified number of times
4. WHEN the direction is "left" THEN the Plan Executor SHALL press Shift+Left the specified number of times
5. WHEN the direction is "right" THEN the Plan Executor SHALL press Shift+Right the specified number of times

### Requirement 7

**User Story:** As a developer, I want the Planner Model to choose between direct automation and vision-based automation, so that simple tasks execute faster.

#### Acceptance Criteria

1. WHEN the Planner Model receives a standard number plate request THEN the Planner Model SHALL generate a plan with mode "direct" for UIA-based execution
2. WHEN the Planner Model receives a complex or non-standard request THEN the Planner Model SHALL generate a plan with mode "vision" for vision-based execution
3. WHEN the Plan Executor receives a plan with mode "direct" THEN the Plan Executor SHALL use UIA commands without taking screenshots
4. WHEN the Plan Executor receives a plan with mode "vision" THEN the Plan Executor SHALL use the existing vision-based pipeline

### Requirement 8

**User Story:** As a developer, I want the UIA integration to be modular, so that it can be maintained independently.

#### Acceptance Criteria

1. THE Local Client SHALL have a dedicated FlexiSIGN UIA module containing all element selectors and interaction helpers
2. THE FlexiSIGN UIA module SHALL expose functions for each supported action (create_text, set_dimensions, set_font, apply_style, move_object)
3. THE FlexiSIGN UIA module SHALL handle UIA initialization and cleanup internally
4. THE FlexiSIGN UIA module SHALL provide clear error messages when UI elements cannot be found

### Requirement 9

**User Story:** As a user, I want to ensure DesignCentral is open before setting properties, so that dimension and font changes work reliably.

#### Acceptance Criteria

1. WHEN the Plan Executor needs to access DesignCentral controls THEN the Plan Executor SHALL first check if DesignCentral window is visible
2. IF DesignCentral is not visible THEN the Plan Executor SHALL press Ctrl+I to open DesignCentral
3. WHEN DesignCentral opens THEN the Plan Executor SHALL wait for the window to be ready before accessing controls

