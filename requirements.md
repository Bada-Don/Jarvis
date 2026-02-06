# Requirements Document

## Introduction

JARVIS (Joint Agentic and Robotic Virtual Interaction  System) is an AI-powered computer automation assistant that bridges the gap between natural language commands and system execution. The system converts user commands into structured execution plans and executes them using a multi-plane architecture that intelligently selects the fastest execution method for each task.

## Glossary

- **JARVIS_System**: The complete AI automation system including backend server, local client, and mobile interface
- **Planner_Model**: LLM (Gemini Flash Lite) that converts natural language to structured execution plans
- **Vision_Mapper**: LLM (Gemini 2.5 Flash) that identifies UI elements in annotated screenshots
- **Local_Client**: Python application running on user's PC that executes automation commands
- **Backend_Server**: Flask server that handles API requests and WebSocket communication
- **Mobile_App**: React Native application for sending commands to JARVIS
- **Execution_Plan**: JSON structure containing ordered steps to accomplish a task
- **Multi_Plane_Architecture**: Execution strategy that prioritizes command-line > file operations > keyboard > vision
- **SoM_Detection**: Set-of-Mark technique using FastSAM to detect and annotate UI elements
- **Vision_Pipeline**: Screenshot capture, SoM detection, and Vision Mapper identification
- **FlexiSIGN_Mode**: Specialized automation mode for FlexiSIGN design software
- **Direct_Path_Automation**: File/folder operations using fuzzy path matching without UI interaction
- **Permission_Service**: System for requesting user approval for critical operations
- **Debug_Logger**: Comprehensive logging system for execution traceability
- **Verification_System**: Post-execution validation that task completed successfully

## Requirements

### Requirement 1: Natural Language Command Processing

**User Story:** As a user, I want to send natural language commands to JARVIS, so that I can automate computer tasks without writing scripts.

#### Acceptance Criteria

1. WHEN a user sends a text command via the mobile app, THE Backend_Server SHALL receive the command and forward it to the Planner_Model
2. WHEN the Planner_Model receives a command, THE Planner_Model SHALL generate a structured Execution_Plan with ordered steps
3. WHEN an Execution_Plan is generated, THE Backend_Server SHALL send it to the Local_Client via WebSocket
4. THE Planner_Model SHALL support commands for file operations, application launching, web browsing, and UI interaction
5. THE Planner_Model SHALL automatically detect whether to use general mode or FlexiSIGN mode based on command content

### Requirement 2: Multi-Plane Execution Architecture

**User Story:** As a system architect, I want JARVIS to intelligently select the fastest execution method for each operation, so that tasks complete quickly and reliably.

#### Acceptance Criteria

1. WHEN executing a task that can be done via command-line, THE Local_Client SHALL use shell commands FIRST
2. WHEN executing file creation or editing, THE Local_Client SHALL use direct file I/O operations SECOND
3. WHEN executing UI interactions, THE Local_Client SHALL use keyboard shortcuts THIRD
4. WHEN no other method is available, THE Local_Client SHALL use vision-based clicking LAST
5. THE Local_Client SHALL execute shell commands using subprocess with proper path expansion
6. THE Local_Client SHALL support environment variable expansion in paths (%USERPROFILE%, %DESKTOP%, etc.)

### Requirement 3: Vision-Based UI Automation

**User Story:** As a user, I want JARVIS to interact with any application's UI, so that I can automate tasks in applications without APIs.

#### Acceptance Criteria

1. WHEN a visual click is needed, THE Vision_Service SHALL capture a screenshot of the current screen
2. WHEN a screenshot is captured, THE Vision_Service SHALL run FastSAM SoM detection to identify UI elements
3. WHEN UI elements are detected, THE Vision_Service SHALL annotate them with numbered red boxes
4. WHEN targets need identification, THE Vision_Mapper SHALL map target names to element IDs using the annotated image
5. WHEN an element ID is found, THE Plan_Executor SHALL click at the center coordinates of the bounding box
6. THE Vision_Service SHALL cache vision data for reuse within a single execution plan
7. THE Plan_Executor SHALL perform adaptive re-scanning when UI changes are detected

### Requirement 4: File and Code Workspace Control

**User Story:** As a developer, I want to create and edit code files without opening editors, so that I can automate development workflows.

#### Acceptance Criteria

1. WHEN a write_file step is executed, THE File_Operations_Module SHALL create or overwrite the file with provided content
2. WHEN a read_file step is executed, THE File_Operations_Module SHALL return the file contents
3. WHEN an append_file step is executed, THE File_Operations_Module SHALL append content to an existing file
4. WHEN a create_directory step is executed, THE File_Operations_Module SHALL create the directory and parent directories
5. THE File_Operations_Module SHALL expand environment variables and user home directory in paths
6. THE File_Operations_Module SHALL create parent directories automatically if they don't exist
7. THE File_Operations_Module SHALL handle file encoding properly (default UTF-8)

### Requirement 5: Intelligent File Editing

**User Story:** As a user, I want to modify existing files with targeted edits, so that I don't have to rewrite entire files.

#### Acceptance Criteria

1. WHEN a replace_in_file step is executed, THE File_Editor SHALL find and replace text using exact string matching
2. WHEN a modify_lines step is executed, THE File_Editor SHALL replace specific line numbers with new content
3. WHEN an insert_at_line step is executed, THE File_Editor SHALL insert content at the specified line number
4. WHEN a delete_lines step is executed, THE File_Editor SHALL remove the specified line range
5. THE File_Editor SHALL generate unified diffs showing changes before and after
6. THE File_Editor SHALL preserve file encoding and line endings
7. THE File_Editor SHALL validate line numbers before attempting modifications

### Requirement 6: Direct Path Automation

**User Story:** As a user, I want to open files and folders using fuzzy path matching, so that I don't need to type exact paths or navigate through UI.

#### Acceptance Criteria

1. WHEN an open_file step is executed with a fuzzy path, THE Direct_Path_Executor SHALL resolve the path and open the file
2. WHEN an open_folder step is executed with a fuzzy path, THE Direct_Path_Executor SHALL resolve the path and open the folder in Explorer
3. WHEN a save_file step is executed, THE Direct_Path_Executor SHALL trigger Ctrl+S, wait for the Save dialog, and type the full path
4. THE Direct_Path_Executor SHALL support special folder aliases (desktop, documents, downloads, stickers)
5. THE Direct_Path_Executor SHALL resolve paths with fuzzy matching (handles typos, case differences, partial names)
6. THE Direct_Path_Executor SHALL automatically find file extensions without user specifying them
7. THE Direct_Path_Executor SHALL handle overwrite dialogs based on configured policy

### Requirement 7: OCR-Based Text Clicking

**User Story:** As a user, I want to click on UI elements by their visible text, so that automation is faster than vision-based detection.

#### Acceptance Criteria

1. WHEN a click_text_fast step is executed, THE Text_Clicker SHALL capture a screenshot and perform OCR
2. WHEN text is found via OCR, THE Text_Clicker SHALL click at the center of the text bounding box
3. WHEN a window_title is specified, THE Text_Clicker SHALL filter OCR results to that window
4. THE Text_Clicker SHALL support fuzzy text matching (partial matches, case-insensitive)
5. THE Text_Clicker SHALL return success status and clicked coordinates
6. THE Text_Clicker SHALL handle multiple matches by clicking the first occurrence
7. WHEN text is not found, THE Text_Clicker SHALL return failure status with error message

### Requirement 8: Window Management and Focus

**User Story:** As a system, I want to ensure the correct window is focused before input, so that keyboard and mouse actions go to the intended application.

#### Acceptance Criteria

1. WHEN an app is launched, THE Window_Manager SHALL wait for the window to appear with configurable timeout
2. WHEN a window appears, THE Window_Manager SHALL activate it and bring it to the foreground
3. WHEN keyboard input is needed, THE Window_Manager SHALL ensure the foreground window is active
4. WHEN a modal dialog is open, THE Window_Manager SHALL be suppressed to avoid stealing focus
5. THE Window_Manager SHALL track the last activated window handle
6. THE Window_Manager SHALL support window title matching with partial strings
7. THE Window_Manager SHALL poll for window existence with exponential backoff

### Requirement 9: Permission System for Critical Operations

**User Story:** As a user, I want to approve critical operations before they execute, so that I maintain control over destructive actions.

#### Acceptance Criteria

1. WHEN a critical operation is detected, THE Permission_Service SHALL send a permission request to the mobile app
2. WHEN a permission request is sent, THE Local_Client SHALL pause execution and wait for user response
3. WHEN the user approves, THE Permission_Service SHALL allow the operation to proceed
4. WHEN the user denies, THE Permission_Service SHALL skip the operation and continue with remaining steps
5. THE Permission_Service SHALL identify critical operations (delete_file, delete_folder, shell commands with destructive keywords)
6. THE Permission_Service SHALL support task abortion at any point during execution
7. WHEN abort is requested, THE Plan_Executor SHALL stop execution immediately and report aborted status

### Requirement 10: Task Verification and Retry

**User Story:** As a user, I want JARVIS to verify that tasks completed successfully, so that I know the automation worked correctly.

#### Acceptance Criteria

1. WHEN an execution plan completes, THE Vision_Service SHALL capture a screenshot and compare it to the expected final state
2. WHEN verification is performed, THE Vision_Mapper SHALL analyze the screenshot and determine if the expected state is achieved
3. WHEN verification fails, THE Plan_Executor SHALL retry the entire plan up to a configurable maximum
4. WHEN verification succeeds, THE Plan_Executor SHALL report success with confidence score
5. THE Verification_System SHALL identify missing UI elements and suggest corrective actions
6. THE Verification_System SHALL return structured results (success, confidence, current_state, missing_elements, corrective_actions)
7. THE Verification_System SHALL be configurable (enabled/disabled, retry count, retry delay, confidence threshold)

### Requirement 11: Debug Logging and Traceability

**User Story:** As a developer, I want comprehensive logs of each execution, so that I can diagnose issues and improve the system.

#### Acceptance Criteria

1. WHEN an execution starts, THE Debug_Logger SHALL create a new session directory with timestamp
2. WHEN the Planner_Model generates a plan, THE Debug_Logger SHALL save the plan JSON
3. WHEN a screenshot is captured, THE Debug_Logger SHALL save the original and annotated images
4. WHEN vision mapping occurs, THE Debug_Logger SHALL save the ID map and box map
5. WHEN each step executes, THE Debug_Logger SHALL log the step details and success status
6. WHEN verification runs, THE Debug_Logger SHALL save the verification result
7. WHEN execution completes, THE Debug_Logger SHALL save a session summary with success status

### Requirement 12: FlexiSIGN Direct Automation

**User Story:** As a FlexiSIGN user, I want JARVIS to automate number plate creation using direct UI Automation, so that tasks complete faster without vision detection.

#### Acceptance Criteria

1. WHEN FlexiSIGN mode is detected, THE Plan_Executor SHALL use FlexiSIGN_UIA for direct automation
2. WHEN create_text is executed, THE FlexiSIGN_UIA SHALL create a text object with specified content
3. WHEN set_dimensions is executed, THE FlexiSIGN_UIA SHALL set width and height in the DesignCentral panel
4. WHEN set_font is executed, THE FlexiSIGN_UIA SHALL select the specified font from the dropdown
5. WHEN apply_style is executed, THE FlexiSIGN_UIA SHALL apply the specified style or default style
6. THE FlexiSIGN_UIA SHALL ensure the DesignCentral panel is open before setting properties
7. THE FlexiSIGN_UIA SHALL use Windows UI Automation API for reliable element access

### Requirement 13: Readiness Detection

**User Story:** As a system, I want to wait for applications and pages to be ready before interacting, so that automation doesn't fail due to timing issues.

#### Acceptance Criteria

1. WHEN a browser is launched, THE Browser_Detector SHALL wait for the page to finish loading
2. WHEN the desktop is accessed, THE Desktop_Detector SHALL wait for icons and UI elements to render
3. WHEN file operations occur, THE Filesystem_Detector SHALL wait for file system operations to complete
4. THE Readiness_Detectors SHALL check for loading indicators, spinners, and progress bars
5. THE Readiness_Detectors SHALL use configurable timeouts to avoid infinite waiting
6. THE Readiness_Detectors SHALL return readiness state (ready, loading, timeout)
7. THE Plan_Executor SHALL wait for readiness before first visual click or text click

### Requirement 14: WebSocket Communication

**User Story:** As a system architect, I want real-time bidirectional communication between components, so that status updates and commands flow efficiently.

#### Acceptance Criteria

1. WHEN the Local_Client starts, THE Local_Client SHALL connect to the Backend_Server via WebSocket
2. WHEN connection is lost, THE Local_Client SHALL automatically reconnect with exponential backoff
3. WHEN a command is sent, THE Backend_Server SHALL emit it to the Local_Client via WebSocket
4. WHEN status updates occur, THE Local_Client SHALL emit them to the Backend_Server via WebSocket
5. WHEN permission requests occur, THE Local_Client SHALL emit them to the Backend_Server for forwarding to mobile app
6. THE WebSocket_Connection SHALL support long-running tasks with extended ping timeouts
7. THE WebSocket_Connection SHALL handle large payloads (up to 50MB for images)

### Requirement 15: Audio Feedback

**User Story:** As a user, I want audio cues when tasks start and complete, so that I know JARVIS is working without watching the screen.

#### Acceptance Criteria

1. WHEN execution starts, THE Plan_Executor SHALL play a start sound
2. WHEN execution completes successfully, THE Plan_Executor SHALL play a completion sound
3. THE Audio_System SHALL use pygame mixer for audio playback
4. THE Audio_System SHALL load audio files from the assets directory
5. THE Audio_System SHALL play sounds in the background without blocking execution
6. WHEN audio files are missing, THE Audio_System SHALL fail gracefully without crashing
7. WHEN pygame is not installed, THE Audio_System SHALL disable audio feedback

### Requirement 16: Shell Command Execution

**User Story:** As a user, I want to execute shell commands for file operations, so that tasks complete faster than UI-based methods.

#### Acceptance Criteria

1. WHEN a shell_command step is executed, THE Plan_Executor SHALL run the command using subprocess
2. THE Shell_Executor SHALL expand environment variables in commands (%USERPROFILE%, %DESKTOP%, etc.)
3. THE Shell_Executor SHALL support command chaining with & operator
4. THE Shell_Executor SHALL wait for command completion before proceeding
5. THE Shell_Executor SHALL capture command output and errors
6. THE Shell_Executor SHALL handle commands with spaces in paths using proper quoting
7. WHEN a command fails, THE Shell_Executor SHALL log the error and continue execution

### Requirement 17: Adaptive UI Scanning

**User Story:** As a system, I want to re-scan the UI when changes are detected, so that vision-based clicks work correctly after navigation or UI updates.

#### Acceptance Criteria

1. WHEN UI changes are detected, THE Plan_Executor SHALL mark the UI as changed
2. WHEN a visual click is needed after UI changes, THE Plan_Executor SHALL perform a new vision pass
3. WHEN re-scanning occurs, THE Plan_Executor SHALL collect remaining visual targets from the current step forward
4. THE Plan_Executor SHALL detect UI changes after keyboard typing, Enter key, Backspace, Delete, and visual clicks
5. THE Plan_Executor SHALL NOT re-scan after navigation keys (arrows, Tab) that don't change content
6. THE Plan_Executor SHALL cache vision data between steps when UI hasn't changed
7. THE Plan_Executor SHALL wait for UI to settle before re-scanning (configurable delay)

### Requirement 18: Mobile App Interface

**User Story:** As a user, I want to send commands and receive status updates via mobile app, so that I can control my PC from anywhere.

#### Acceptance Criteria

1. WHEN the mobile app sends a command, THE Backend_Server SHALL receive it via HTTP POST
2. WHEN execution starts, THE Backend_Server SHALL send progress updates to the mobile app
3. WHEN permission is needed, THE Backend_Server SHALL send permission requests to the mobile app
4. WHEN the user responds to permission, THE Mobile_App SHALL send the response to the Backend_Server
5. WHEN the user aborts a task, THE Mobile_App SHALL send an abort signal to the Backend_Server
6. THE Mobile_App SHALL display real-time progress with percentage and status messages
7. THE Mobile_App SHALL support voice input for commands (future enhancement)

### Requirement 19: Configuration Management

**User Story:** As a user, I want to configure JARVIS behavior, so that I can customize automation to my preferences.

#### Acceptance Criteria

1. THE System SHALL load configuration from config.py in the local_client directory
2. THE Configuration SHALL include server URL, verification settings, retry settings, and timing delays
3. THE Configuration SHALL support path aliases for special folders (desktop, documents, stickers)
4. THE Configuration SHALL support overwrite policies for file operations (always, never, ask)
5. THE Configuration SHALL support verification confidence thresholds
6. THE Configuration SHALL support maximum retry counts and retry delays
7. THE Configuration SHALL support custom timing delays for different action types

### Requirement 20: Error Handling and Recovery

**User Story:** As a user, I want JARVIS to handle errors gracefully, so that one failure doesn't crash the entire system.

#### Acceptance Criteria

1. WHEN a step fails, THE Plan_Executor SHALL log the error and continue with remaining steps
2. WHEN a critical error occurs, THE Plan_Executor SHALL report the error to the user and stop execution
3. WHEN vision detection fails, THE Plan_Executor SHALL report which targets were not found
4. WHEN file operations fail, THE File_Operations_Module SHALL return error messages with details
5. WHEN permission is denied, THE Permission_Service SHALL skip the operation and continue
6. WHEN WebSocket disconnects, THE Local_Client SHALL attempt reconnection automatically
7. WHEN the Planner_Model fails, THE Backend_Server SHALL return an error response to the mobile app
