# Requirements Document

## Introduction

This document specifies the requirements for a "Direct Path Automation" feature that enables file operations (open, save) to bypass complex UI navigation by directly typing file paths into system dialogs. This approach reduces API costs, increases efficiency, and improves accuracy for file-related automation tasks. The feature also includes text-based element clicking for File Explorer scenarios, similar to the Self-Operating Computer approach.

## Glossary

- **Direct Path Automation**: A method of file operations that uses absolute file paths typed directly into dialog boxes instead of navigating through UI elements
- **File Dialog**: System dialogs triggered by Ctrl+S (Save) or Ctrl+O (Open) that accept file paths in the filename field
- **File Explorer**: Windows file management application where address bar navigation (Ctrl+L) is used
- **Text-Based Clicking**: Locating UI elements by finding text on screen and clicking the center of the text's bounding box
- **OCR**: Optical Character Recognition - technology to detect and locate text in images
- **Planner Model**: The Gemini model that converts natural language commands into execution plans
- **Plan Executor**: The component that executes the generated plans

## Requirements

### Requirement 1

**User Story:** As an automation user, I want to save files by typing the full destination path directly, so that I can avoid complex UI navigation and ensure files are saved to the exact location with the correct name.

#### Acceptance Criteria

1. WHEN the Planner Model receives a save file command THEN the Planner Model SHALL generate a plan that uses Ctrl+S followed by typing the full absolute path (e.g., "C:\Users\harsh\OneDrive\Desktop\file_name.file_extension") in the filename field
2. WHEN the Plan Executor types a file path in a Save dialog THEN the Plan Executor SHALL press Enter to confirm the save operation
3. WHEN constructing a save path THEN the Planner Model SHALL include the complete directory path, filename, and file extension
4. WHEN a save operation is requested without a specified directory THEN the Planner Model SHALL use a configurable default directory path

### Requirement 2

**User Story:** As an automation user, I want to open files by typing the full source path directly, so that I can quickly access files without navigating through folder hierarchies.

#### Acceptance Criteria

1. WHEN the Planner Model receives an open file command THEN the Planner Model SHALL generate a plan that uses Ctrl+O followed by typing the full absolute path in the filename field
2. WHEN the Plan Executor types a file path in an Open dialog THEN the Plan Executor SHALL press Enter to confirm the open operation
3. WHEN constructing an open path THEN the Planner Model SHALL validate that the path includes a valid file extension

### Requirement 3

**User Story:** As an automation user, I want to navigate to folders in File Explorer using the address bar, so that I can quickly access directories without clicking through the folder tree.

#### Acceptance Criteria

1. WHEN navigating in File Explorer THEN the Plan Executor SHALL press Ctrl+L to focus the address bar before typing the path
2. WHEN a directory path is typed in the File Explorer address bar THEN the Plan Executor SHALL press Enter to navigate to that directory
3. WHEN the target is a file within File Explorer THEN the system SHALL use text-based clicking to select the file after navigating to its parent directory

### Requirement 4

**User Story:** As an automation user, I want the system to click on files by finding their text labels on screen, so that I can select specific files without relying on expensive vision model calls.

#### Acceptance Criteria

1. WHEN a text-based click is requested THEN the system SHALL capture a screenshot and perform OCR to locate the target text
2. WHEN the target text is found THEN the system SHALL calculate the center point of the text's bounding box and perform a click at that location
3. WHEN multiple instances of the target text exist THEN the system SHALL select the instance closest to the expected location (e.g., file list area)
4. IF the target text is not found THEN the system SHALL report the failure and provide the list of detected text elements

### Requirement 5

**User Story:** As an automation user, I want the system to handle path-related errors gracefully, so that automation does not fail silently when issues occur.

#### Acceptance Criteria

1. IF a file already exists at the save destination THEN the system SHALL detect the overwrite confirmation dialog and handle it according to a configurable policy (overwrite, rename, or abort)
2. IF a specified path does not exist for an open operation THEN the system SHALL detect the error dialog and report the failure with the invalid path
3. IF a specified directory does not exist for a save operation THEN the system SHALL detect the error and report that the directory path is invalid
4. WHEN an error dialog appears THEN the system SHALL capture the dialog text and include it in the error report

### Requirement 6

**User Story:** As an automation user, I want to configure default paths and behaviors, so that I can customize the direct path automation to my workflow.

#### Acceptance Criteria

1. WHEN the system initializes THEN the system SHALL load path configuration from a JSON configuration file
2. WHEN a default save directory is configured THEN the Planner Model SHALL use that directory when no specific path is provided
3. WHEN an overwrite policy is configured THEN the system SHALL follow that policy when file conflicts occur
4. WHEN the configuration file is missing THEN the system SHALL use sensible defaults (Desktop directory, prompt on overwrite)

### Requirement 7

**User Story:** As a developer, I want the path automation to be serializable and deserializable, so that execution plans can be saved, reviewed, and replayed.

#### Acceptance Criteria

1. WHEN a direct path operation is included in an execution plan THEN the operation SHALL be represented as a JSON-serializable step type
2. WHEN deserializing a path operation THEN the system SHALL reconstruct the complete operation with all path components
3. WHEN serializing a path operation THEN the system SHALL include the operation type, full path, and any error handling configuration

