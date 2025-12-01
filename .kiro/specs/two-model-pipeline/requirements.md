# Requirements Document

## Introduction

This feature implements a Two-Model Pipeline for automating FlexiSIGN number plate creation. The system uses two AI models in sequence: Model 1 (Gemini Flash Lite) on the backend server creates an execution plan from user commands, while Model 2 (Gemini 2.0 Flash) on the local client maps UI element names to Set-of-Mark IDs from screenshots. The pipeline enables intelligent, vision-guided automation of the FlexiSIGN desktop application.

## Glossary

- **Execution Plan**: A JSON structure containing ordered steps (keyboard actions and visual clicks) to automate FlexiSIGN
- **Set-of-Mark (SoM)**: An image annotation technique that draws red bounding boxes with numeric IDs on detected UI elements
- **Visual Target**: A named UI element (e.g., "text_tool", "width_input") that Model 2 must locate in the screenshot
- **Box Map**: A JSON dictionary mapping element IDs to bounding box coordinates [x1, y1, x2, y2]
- **Planner Model**: Gemini Flash Lite model that converts user commands into execution plans (runs on backend)
- **Vision Mapper Model**: Gemini 2.0 Flash model that maps visual target names to SoM IDs (runs on local client)
- **Local Client**: The Python application running on the Windows machine where FlexiSIGN is installed
- **Backend Server**: The Flask server that receives mobile app requests and coordinates the pipeline

## Requirements

### Requirement 1

**User Story:** As a user, I want to send a number plate creation command from my mobile app, so that the system automatically creates the plate in FlexiSIGN.

#### Acceptance Criteria

1. WHEN a user sends a command like "Make iron number plate set for bike, PB12W3998" THEN the Backend Server SHALL parse the command and generate an execution plan using the Planner Model
2. WHEN the Backend Server generates an execution plan THEN the Backend Server SHALL send the plan to the Local Client via WebSocket
3. WHEN the Local Client receives an execution plan THEN the Local Client SHALL execute keyboard actions and visual clicks in the specified order
4. WHEN all steps complete successfully THEN the Local Client SHALL send a success status update to the mobile app via the Backend Server

### Requirement 2

**User Story:** As a system operator, I want the Planner Model to understand plate dimensions, so that it generates correct size parameters without hallucination.

#### Acceptance Criteria

1. WHEN the Planner Model receives a "bike iron" plate request THEN the Planner Model SHALL use dimensions Front (8 x 1.2) and Back (10 x 1.5)
2. WHEN the Planner Model receives a "bike glass" plate request THEN the Planner Model SHALL use dimensions Front (6 x 1.2) and Back (10 x 1.5)
3. WHEN the Planner Model receives a "car normal" plate request THEN the Planner Model SHALL use dimensions Front (14 x 2.3) and Back (14 x 2.4)
4. WHEN the Planner Model generates an execution plan THEN the Planner Model SHALL output valid JSON with "sequence" array containing ordered steps
5. WHEN a step requires keyboard input THEN the step SHALL have type "keyboard" with "value" field
6. WHEN a step requires clicking a UI element THEN the step SHALL have type "visual_click" with "target_name" field

### Requirement 3

**User Story:** As a system operator, I want the Local Client to capture screenshots and run Set-of-Mark detection, so that UI elements can be identified for clicking.

#### Acceptance Criteria

1. WHEN the Local Client needs to perform visual clicks THEN the Local Client SHALL capture a screenshot using pyautogui.screenshot()
2. WHEN a screenshot is captured THEN the Local Client SHALL run FastSAM model to detect UI element bounding boxes
3. WHEN FastSAM detection completes THEN the Local Client SHALL draw Set-of-Mark annotations (red boxes with numeric IDs) on the image
4. WHEN annotations are drawn THEN the Local Client SHALL generate a box map JSON mapping element IDs to coordinates

### Requirement 4

**User Story:** As a system operator, I want the Vision Mapper Model to identify UI elements from the annotated screenshot, so that visual clicks can be executed accurately.

#### Acceptance Criteria

1. WHEN the Local Client has an annotated screenshot and a list of visual targets THEN the Local Client SHALL send both to the Vision Mapper Model
2. WHEN the Vision Mapper Model receives the image and target list THEN the Vision Mapper Model SHALL return a JSON mapping target names to element IDs
3. WHEN the Vision Mapper Model cannot find a target element THEN the Vision Mapper Model SHALL omit that target from the response or return null for its ID
4. WHEN the Local Client receives the ID map THEN the Local Client SHALL use the box map to convert IDs to click coordinates

### Requirement 5

**User Story:** As a system operator, I want the execution to follow a single-pass architecture, so that the screenshot is only taken once per workflow.

#### Acceptance Criteria

1. WHEN the Local Client starts executing a plan THEN the Local Client SHALL execute initial keyboard-only steps (like Ctrl+N) before taking the screenshot
2. WHEN the screenshot is taken THEN the Local Client SHALL reuse the same SoM detection and ID map for all subsequent visual clicks
3. WHEN multiple steps reference the same visual target THEN the Local Client SHALL use the same cached coordinates for all clicks

### Requirement 6

**User Story:** As a developer, I want proper API key configuration, so that Gemini models can be accessed securely.

#### Acceptance Criteria

1. WHEN the Backend Server starts THEN the Backend Server SHALL load the Gemini API key from environment variables
2. WHEN the Local Client starts THEN the Local Client SHALL load the Gemini API key from environment variables
3. WHEN an API key is missing THEN the system SHALL log an error and fail gracefully with a clear message
4. THE system SHALL provide an .env.example file documenting required environment variables

### Requirement 7

**User Story:** As a user, I want real-time progress updates on my mobile app, so that I know what the system is doing.

#### Acceptance Criteria

1. WHEN the Backend Server sends a plan to the Local Client THEN the Backend Server SHALL emit a status update "Processing your request..."
2. WHEN the Local Client starts screenshot capture THEN the Local Client SHALL emit a status update "Capturing screen..."
3. WHEN the Local Client starts SoM detection THEN the Local Client SHALL emit a status update "Analyzing UI elements..."
4. WHEN the Local Client starts Vision Mapper THEN the Local Client SHALL emit a status update "Identifying targets..."
5. WHEN the Local Client executes each step THEN the Local Client SHALL emit progress updates with percentage completion
