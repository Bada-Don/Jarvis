# Requirements Document

## Introduction

This document specifies the requirements for a comprehensive settings interface for the JARVIS local client application. The interface will be built using React and hosted within a PyWebView window, allowing users to configure system settings, modify AI model prompts, and package the application for distribution. This interface will provide a user-friendly way to manage all configurable aspects of the JARVIS automation system without requiring users to manually edit configuration files.

## Glossary

- **JARVIS**: The AI-powered computer automation system consisting of a backend server and local client
- **Local Client**: The Python application that executes automation plans on the user's computer
- **PyWebView**: A lightweight Python library for displaying web content in native OS windows
- **React**: A JavaScript library for building user interfaces
- **Planner Model**: The Gemini AI model that converts natural language commands into structured execution plans
- **Vision Model**: The Gemini AI model that identifies UI elements in screenshots for automation
- **Config.py**: The Python configuration file containing system settings for the local client
- **System Prompt**: The instruction text provided to AI models that defines their behavior and capabilities
- **FlexiSIGN**: A specialized graphics software for creating number plates and signage
- **Execution Plan**: A structured JSON sequence of steps that the local client executes to complete a task

## Requirements

### Requirement 1

**User Story:** As a user, I want to launch a settings interface from the local client, so that I can configure the system without editing code files.

#### Acceptance Criteria

1. WHEN the user runs the settings interface command THEN the system SHALL launch a PyWebView window displaying the React settings interface
2. WHEN the PyWebView window opens THEN the system SHALL load the current configuration values from config.py and display them in the interface
3. WHEN the settings interface is running THEN the system SHALL provide a bridge between the React frontend and Python backend for bidirectional communication
4. WHEN the user closes the settings window THEN the system SHALL terminate the PyWebView process cleanly without leaving orphaned processes

### Requirement 2

**User Story:** As a user, I want to view and edit basic system settings, so that I can customize paths, timing, and behavior without editing config.py directly.

#### Acceptance Criteria

1. WHEN the settings interface displays THEN the system SHALL show all configurable settings from config.py organized into logical categories
2. WHEN the user modifies a setting value THEN the system SHALL validate the input according to the setting's data type and constraints
3. WHEN the user saves changes THEN the system SHALL write the updated values back to config.py while preserving file structure and comments
4. WHEN a setting has a default value THEN the system SHALL display a reset button that restores the default value
5. WHEN the user provides invalid input THEN the system SHALL display clear error messages and prevent saving until corrected

### Requirement 3

**User Story:** As a user, I want to configure file paths and directories, so that the system can locate important folders and applications correctly.

#### Acceptance Criteria

1. WHEN the user edits a path setting THEN the system SHALL provide a file browser button that opens a native file/folder selection dialog
2. WHEN the user selects a path through the browser THEN the system SHALL populate the input field with the absolute path
3. WHEN the user enters a path manually THEN the system SHALL validate that the path exists on the filesystem
4. WHEN a path setting is for a directory THEN the system SHALL verify the path points to a directory and not a file
5. WHEN a path setting is for an executable THEN the system SHALL verify the file exists and has an executable extension

### Requirement 4

**User Story:** As a user, I want to adjust timing and delay settings, so that I can optimize automation speed for my system's performance.

#### Acceptance Criteria

1. WHEN the user views timing settings THEN the system SHALL display all delay values in seconds with clear descriptions
2. WHEN the user modifies a timing value THEN the system SHALL validate the input is a positive number
3. WHEN the user sets a timing value below recommended minimums THEN the system SHALL display a warning but allow the change
4. WHEN the user hovers over a timing setting THEN the system SHALL display a tooltip explaining the setting's purpose and recommended range

### Requirement 5

**User Story:** As a user, I want to view and edit the Planner Model system prompt, so that I can customize how the AI interprets commands and generates execution plans.

#### Acceptance Criteria

1. WHEN the user navigates to the Planner Prompt section THEN the system SHALL display the current GENERAL_SYSTEM_PROMPT text in an editable text area
2. WHEN the user navigates to the FlexiSIGN Planner section THEN the system SHALL display the current FLEXISIGN_SYSTEM_PROMPT text in an editable text area
3. WHEN the user modifies a prompt THEN the system SHALL provide syntax highlighting for JSON examples within the prompt
4. WHEN the user saves prompt changes THEN the system SHALL write the updated prompt to backend/gemini_service.py while preserving code structure
5. WHEN the user clicks a reset button THEN the system SHALL restore the original default prompt from a backup or template

### Requirement 6

**User Story:** As a user, I want to view and edit the Vision Model prompts, so that I can customize how the AI identifies UI elements in screenshots.

#### Acceptance Criteria

1. WHEN the user navigates to the Vision Prompts section THEN the system SHALL display GENERAL_VISION_PROMPT, VERIFICATION_PROMPT, and FLEXISIGN_VISION_PROMPT in separate editable text areas
2. WHEN the user modifies a vision prompt THEN the system SHALL validate the prompt contains required placeholders for dynamic content
3. WHEN the user saves vision prompt changes THEN the system SHALL write the updated prompts to local_client/vision_service.py while preserving code structure
4. WHEN the user tests a prompt THEN the system SHALL provide a preview mode that shows how the prompt would be formatted with sample data

### Requirement 7

**User Story:** As a user, I want to configure verification and retry settings, so that I can control how the system validates task completion.

#### Acceptance Criteria

1. WHEN the user views verification settings THEN the system SHALL display VERIFICATION_ENABLED, MAX_RETRIES, RETRY_DELAY, VERIFICATION_DELAY, and CONFIDENCE_THRESHOLD with their current values
2. WHEN the user toggles VERIFICATION_ENABLED THEN the system SHALL enable or disable related retry settings accordingly
3. WHEN the user adjusts CONFIDENCE_THRESHOLD THEN the system SHALL validate the value is between 0.0 and 1.0
4. WHEN the user selects a quick preset THEN the system SHALL apply predefined setting combinations for Fast Testing, Production, or Critical Tasks modes

### Requirement 8

**User Story:** As a user, I want to configure FlexiSIGN-specific settings, so that the system can properly interact with the FlexiSIGN application.

#### Acceptance Criteria

1. WHEN the user views FlexiSIGN settings THEN the system SHALL display FLEXISIGN_PROCESS_NAME, FLEXISIGN_EXE_PATH, FLEXISIGN_WINDOW_TITLE, and startup modal settings
2. WHEN the user browses for the FlexiSIGN executable THEN the system SHALL filter the file dialog to show only .exe files
3. WHEN the user toggles STARTUP_MODAL_ENABLED THEN the system SHALL enable or disable related modal settings
4. WHEN the user saves FlexiSIGN settings THEN the system SHALL validate the executable path exists before saving

### Requirement 9

**User Story:** As a developer, I want to package the application as a standalone executable, so that I can distribute it to users without requiring Python installation.

#### Acceptance Criteria

1. WHEN the user clicks the Package Application button THEN the system SHALL initiate a build process using PyInstaller or similar packaging tool
2. WHEN the packaging process runs THEN the system SHALL display real-time progress and log output in the interface
3. WHEN packaging completes successfully THEN the system SHALL create a standalone executable with all dependencies bundled
4. WHEN packaging completes THEN the system SHALL display the output location and provide a button to open the containing folder
5. WHEN packaging fails THEN the system SHALL display detailed error messages and suggest corrective actions

### Requirement 10

**User Story:** As a user, I want to export and import configuration profiles, so that I can share settings or switch between different configurations easily.

#### Acceptance Criteria

1. WHEN the user clicks Export Configuration THEN the system SHALL save all current settings to a JSON file with a user-specified name
2. WHEN the user clicks Import Configuration THEN the system SHALL open a file browser to select a configuration JSON file
3. WHEN the user imports a configuration THEN the system SHALL validate the file structure and apply all valid settings
4. WHEN an imported configuration contains invalid values THEN the system SHALL display warnings for invalid settings and skip them while applying valid ones
5. WHEN the user exports a configuration THEN the system SHALL include metadata such as export date, JARVIS version, and configuration name

### Requirement 11

**User Story:** As a user, I want to test my configuration changes, so that I can verify settings work correctly before using them in production.

#### Acceptance Criteria

1. WHEN the user clicks Test Configuration THEN the system SHALL run a series of validation checks on all settings
2. WHEN testing path settings THEN the system SHALL verify all configured paths exist and are accessible
3. WHEN testing FlexiSIGN settings THEN the system SHALL attempt to detect the FlexiSIGN process or executable
4. WHEN testing completes THEN the system SHALL display a report showing which settings passed or failed validation
5. WHEN a test fails THEN the system SHALL provide specific guidance on how to fix the issue

### Requirement 12

**User Story:** As a user, I want the settings interface to have a clean and intuitive design, so that I can easily find and modify settings without confusion.

#### Acceptance Criteria

1. WHEN the settings interface loads THEN the system SHALL display a navigation sidebar with categorized sections
2. WHEN the user clicks a category in the sidebar THEN the system SHALL display the corresponding settings panel with smooth transitions
3. WHEN the user has unsaved changes THEN the system SHALL display a visual indicator and prompt for confirmation before navigating away
4. WHEN the user searches for a setting THEN the system SHALL filter and highlight matching settings across all categories
5. WHEN the interface displays on different screen sizes THEN the system SHALL adapt the layout responsively while maintaining usability
