# Design Document

## Overview

JARVIS is an AI-powered computer automation system that converts natural language commands into executable automation plans. The system uses a multi-plane execution architecture that intelligently selects the fastest method for each operation: command-line operations (fastest), direct file I/O (fast), keyboard shortcuts (medium), and vision-based UI automation (slowest, last resort).

The system consists of three main components:
1. **Backend Server** (Flask + SocketIO): Receives commands, generates execution plans using LLM
2. **Local Client** (Python): Executes plans on the user's PC using multiple automation techniques
3. **Mobile App** (React Native): User interface for sending commands and receiving status updates

This document covers both the core automation architecture and the desktop packaging design that enables JARVIS to be distributed as a production-ready application with Firebase-based mobile connectivity.

## Architecture

### System Architecture

```
┌─────────────────┐
│   Mobile App    │
│ (React Native)  │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│ Backend Server  │
│ Flask+SocketIO  │
│                 │
│ ┌─────────────┐ │
│ │Planner Model│ │
│ │Gemini Flash │ │
│ └─────────────┘ │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────────────────────────────┐
│         Local Client (Python)           │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Plan Executor               │  │
│  │  (Multi-Plane Architecture)      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Plane 1: Shell Commands (subprocess)  │
│  Plane 2: File Operations (direct I/O) │
│  Plane 3: Keyboard (pyautogui)         │
│  Plane 4: Vision (FastSAM + Gemini)    │
│                                         │
│  ┌──────────────┐  ┌────────────────┐  │
│  │Vision Service│  │Window Manager  │  │
│  │FastSAM+Gemini│  │Focus Control   │  │
│  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────┘
```

### Multi-Plane Execution Flow

```
User Command → Planner Model → Execution Plan
                                      │
                                      ▼
                            ┌─────────────────┐
                            │ Plan Executor   │
                            └─────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │ Shell Command│  │ File I/O     │  │ Keyboard     │
            │ (Fastest)    │  │ (Fast)       │  │ (Medium)     │
            └──────────────┘  └──────────────┘  └──────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────┐
                                                │ Vision       │
                                                │ (Slow)       │
                                                └──────────────┘
```

## Components and Interfaces

### Backend Server (server.py)

**Responsibilities:**
- Receive commands from mobile app via HTTP POST
- Generate execution plans using Planner Model (Gemini Flash Lite)
- Send plans to Local Client via WebSocket
- Forward status updates from Local Client to mobile app
- Handle permission requests and responses

**Key Interfaces:**
- `POST /api/process`: Receive command, generate plan, send to client
- `WebSocket 'command'`: Send execution plan to Local Client
- `WebSocket 'status_update'`: Receive status from Local Client
- `WebSocket 'permission_request_from_client'`: Forward permission requests
- `WebSocket 'permission_response'`: Forward permission responses
- `WebSocket 'abort_task'`: Forward abort signals

### Planner Service (planner_service.py)

**Responsibilities:**
- Convert natural language to structured JSON execution plans
- Auto-detect execution mode (general vs FlexiSIGN)
- Apply execution priority rules (shell > file > keyboard > vision)
- Generate step sequences with proper ordering

**Key Methods:**
- `generate_plan(text: str) -> dict`: Main entry point for plan generation
- Returns JSON with: `mode`, `sequence` (array of steps), `expected_final_state`

**Step Types Supported:**
- `shell_command`: Execute CMD commands
- `write_file`, `read_file`, `append_file`, `create_directory`: File operations
- `replace_in_file`, `modify_lines`, `insert_at_line`, `delete_lines`: File editing
- `open_file`, `open_folder`, `save_file`: Direct path automation
- `keyboard`: Keyboard input and shortcuts
- `click_text_fast`: OCR-based clicking
- `visual_click`: Vision-based clicking
- FlexiSIGN: `create_text`, `set_dimensions`, `set_font`, `apply_style`

### Local Client (client.py)

**Responsibilities:**
- Connect to Backend Server via WebSocket
- Receive and execute automation plans
- Send status updates and permission requests
- Handle abort signals

**Key Event Handlers:**
- `on_connect()`: Initialize connection and permission service
- `on_command(data)`: Route commands to appropriate executor
- `execute_two_model_plan()`: Main execution entry point with verification and retry

### Plan Executor (plan_executor.py)

**Responsibilities:**
- Execute plans using multi-plane architecture
- Manage window focus and timing
- Handle vision pipeline (screenshot, SoM, mapping)
- Coordinate with permission service
- Perform adaptive UI re-scanning
- Execute verification and retry logic

**Key Methods:**
- `execute_plan(plan, verify=True) -> dict`: Main execution method
- `_execute_vision_plan(plan) -> dict`: Vision-based execution
- `_execute_direct_plan(plan) -> dict`: FlexiSIGN UIA execution
- `_execute_keyboard_step()`: Keyboard actions with window management
- `_execute_visual_click()`: Vision-based clicking
- `_execute_shell_command_step()`: Shell command execution
- `_execute_write_file_step()`: File writing
- `_execute_read_file_step()`: File reading
- `_execute_replace_in_file_step()`: Text replacement
- `_execute_open_file_step()`: Fuzzy path file opening
- `_execute_click_text_fast_step()`: OCR-based clicking

**Timing Configuration:**
- `DELAY_AFTER_STEP = 0.3s`: Default delay between steps
- `DELAY_AFTER_APP_LAUNCH = 3.0s`: Wait for app windows
- `DELAY_AFTER_HOTKEY = 0.5s`: Delay after keyboard shortcuts
- `DELAY_BEFORE_TYPING = 0.2s`: Delay before typing text
- `WINDOW_ACTIVATION_TIMEOUT = 10.0s`: Max wait for window activation

### Vision Service (vision_service.py)

**Responsibilities:**
- Capture screenshots using pyautogui
- Run FastSAM for UI element detection (Set-of-Mark)
- Annotate screenshots with numbered red boxes
- Use Gemini 2.5 Flash to map target names to element IDs
- Verify task completion by comparing screenshots to expected state

**Key Methods:**
- `capture_screenshot() -> np.ndarray`: Capture screen as BGR image
- `run_som_detection(image) -> (annotated_image, box_map)`: FastSAM detection
- `map_targets_to_ids(annotated_image, targets, mode) -> dict`: Vision Mapper
- `verify_task_completion(expected_state) -> dict`: Post-execution verification

**Vision Mapper Prompts:**
- General mode: Identifies buttons, text fields, icons, menus, taskbar items
- FlexiSIGN mode: Identifies text tool, select tool, canvas, dimension inputs

### File Operations (file_operations.py)

**Responsibilities:**
- Direct file I/O without UI interaction
- Path expansion (environment variables, user home)
- Parent directory creation
- Encoding handling

**Key Functions:**
- `write_file(path, content, encoding='utf-8') -> (success, message)`
- `read_file(path, encoding='utf-8') -> (success, message, content)`
- `append_file(path, content, encoding='utf-8') -> (success, message)`
- `create_directory(path) -> (success, message)`

### File Editor (file_editor.py)

**Responsibilities:**
- Intelligent file editing with minimal token usage
- Search/replace operations
- Line-specific modifications
- Diff generation

**Key Methods:**
- `read_file_with_context(path) -> (success, message, file_data)`: Read with line numbers
- `replace_in_file(path, old_text, new_text, count=-1) -> (success, message, diff)`
- `modify_lines(path, line_number, new_content, num_lines=1) -> (success, message, diff)`
- `insert_at_line(path, line_number, content) -> (success, message, diff)`
- `delete_lines(path, start_line, end_line) -> (success, message, diff)`

### Window Manager (window_manager.py)

**Responsibilities:**
- Wait for application windows to appear
- Activate and bring windows to foreground
- Ensure focus before keyboard/mouse input
- Track last activated window

**Key Methods:**
- `wait_and_activate(app_name, timeout) -> bool`: Wait for window and activate
- `ensure_foreground_before_input()`: Ensure active window is in foreground
- `get_foreground_window_title() -> str`: Get current window title

### Permission Service (permission_service.py)

**Responsibilities:**
- Identify critical operations (delete, destructive shell commands)
- Request user approval via mobile app
- Handle abort signals
- Pause execution until permission granted/denied

**Key Methods:**
- `is_critical_operation(step) -> bool`: Check if step needs permission
- `request_permission_for_step(step) -> bool`: Request and wait for permission
- `is_abort_requested() -> bool`: Check if user aborted task

### Debug Logger (debug_logger.py)

**Responsibilities:**
- Create session directories with timestamps
- Log all execution artifacts (plans, screenshots, maps, results)
- Provide traceability for debugging

**Key Methods:**
- `create_new_session() -> DebugLogger`: Create new session
- `log_planner_output(plan)`: Save execution plan
- `log_screenshot(image)`: Save original screenshot
- `log_annotated_image(image)`: Save SoM-annotated image
- `log_box_map(box_map)`: Save bounding box coordinates
- `log_vision_mapper_output(id_map, targets)`: Save target mappings
- `log_step_execution(order, type, details, success=True)`: Log step execution
- `log_verification_result(result, expected_state)`: Save verification result
- `complete(success)`: Finalize session

## Data Models

### Execution Plan

```json
{
  "mode": "general" | "flexisign",
  "sequence": [
    {
      "order": 1,
      "type": "shell_command" | "keyboard" | "visual_click" | ...,
      "desc": "Human-readable description",
      // Type-specific fields
    }
  ],
  "expected_final_state": "Description of what screen should look like"
}
```

### Step Types

**Shell Command:**
```json
{
  "type": "shell_command",
  "command": "mkdir \"%USERPROFILE%\\OneDrive\\Desktop\\Folder\"",
  "desc": "Create folder on Desktop"
}
```

**File Operations:**
```json
{
  "type": "write_file",
  "path": "%USERPROFILE%\\OneDrive\\Desktop\\script.py",
  "content": "print('Hello')",
  "desc": "Write Python script"
}
```

**Keyboard:**
```json
{
  "type": "keyboard",
  "value": "ctrl+s" | "enter" | "Hello World",
  "repeats": 1,
  "desc": "Press Ctrl+S to save"
}
```

**Visual Click:**
```json
{
  "type": "visual_click",
  "target_name": "button_submit",
  "desc": "Click Submit button"
}
```

**OCR Click:**
```json
{
  "type": "click_text_fast",
  "window_title": "Notepad",
  "text": "File",
  "desc": "Click File menu"
}
```

### Vision Data

**Box Map:**
```json
{
  "1": [x1, y1, x2, y2],
  "2": [x1, y1, x2, y2],
  ...
}
```

**ID Map:**
```json
{
  "button_submit": 45,
  "search_box": 12,
  "unknown_element": null
}
```

### Verification Result

```json
{
  "success": true | false,
  "confidence": 0.95,
  "current_state": "Description of actual screen state",
  "missing_elements": ["element1", "element2"],
  "corrective_actions": ["action1", "action2"]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Command Processing Properties

**Property 1: Command routing integrity**
*For any* user command sent via the mobile app, the Backend_Server should receive it, forward it to the Planner_Model, and the Planner_Model should generate a valid Execution_Plan with all required fields (mode, sequence, expected_final_state).
**Validates: Requirements 1.1, 1.2, 1.3**

**Property 2: Mode detection accuracy**
*For any* command containing FlexiSIGN-specific keywords (plate, bike, car, iron, glass, dimensions), the Planner_Model should set mode to "flexisign", otherwise mode should be "general".
**Validates: Requirements 1.5**

### Multi-Plane Execution Properties

**Property 3: Execution priority ordering**
*For any* task that can be accomplished via shell command, the generated plan should contain shell_command steps before any keyboard or visual_click steps for the same operation.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

**Property 4: Environment variable expansion**
*For any* path containing environment variables (%USERPROFILE%, %DESKTOP%, etc.), the system should expand them to their actual values before execution.
**Validates: Requirements 2.5, 2.6**

### Vision Pipeline Properties

**Property 5: Vision data caching**
*For any* execution plan with multiple visual_click steps, the Vision_Service should perform screenshot and SoM detection only once (or when UI changes), reusing the cached data for subsequent clicks.
**Validates: Requirements 3.6**

**Property 6: Bounding box center calculation**
*For any* bounding box [x1, y1, x2, y2], the click coordinates should be at the center point ((x1+x2)/2, (y1+y2)/2).
**Validates: Requirements 3.5**

**Property 7: Adaptive re-scanning**
*For any* execution where UI changes are detected (after typing, Enter, Backspace, Delete, or visual clicks), the Plan_Executor should set the UI changed flag and perform a new vision pass before the next visual_click.
**Validates: Requirements 3.7, 17.1, 17.2, 17.4**

### File Operations Properties

**Property 8: File write-read round trip**
*For any* valid file path and content, writing the content to the file and then reading it back should return the exact same content.
**Validates: Requirements 4.1, 4.2**

**Property 9: Append increases file size**
*For any* existing file, appending content should increase the file size and the new content should appear at the end of the file.
**Validates: Requirements 4.3**

**Property 10: Parent directory creation**
*For any* nested directory path, creating the directory should also create all parent directories that don't exist.
**Validates: Requirements 4.4, 4.6**

**Property 11: Path expansion consistency**
*For any* path containing ~ or environment variables, the expanded path should be consistent across all file operations (write, read, append, create_directory).
**Validates: Requirements 4.5**

### File Editing Properties

**Property 12: Text replacement correctness**
*For any* file containing old_text, replacing old_text with new_text should result in a file where old_text no longer appears and new_text appears in its place.
**Validates: Requirements 5.1**

**Property 13: Line modification accuracy**
*For any* file and valid line number N, modifying line N with new content should result in line N containing exactly the new content.
**Validates: Requirements 5.2**

**Property 14: Line insertion correctness**
*For any* file with L lines, inserting content at line N should result in a file with L+1 lines where line N contains the inserted content.
**Validates: Requirements 5.3**

**Property 15: Line deletion correctness**
*For any* file with L lines, deleting lines N to M should result in a file with L-(M-N+1) lines.
**Validates: Requirements 5.4**

**Property 16: Diff generation**
*For any* file modification operation, the File_Editor should generate a unified diff showing the changes.
**Validates: Requirements 5.5**

### Direct Path Automation Properties

**Property 17: Fuzzy path resolution**
*For any* fuzzy path query (with typos, case differences, or partial names), the Direct_Path_Executor should resolve it to the correct full path if a matching file/folder exists.
**Validates: Requirements 6.1, 6.2, 6.5**

**Property 18: Special folder alias resolution**
*For any* path starting with special folder aliases (desktop, documents, downloads, stickers), the system should resolve them to the correct absolute paths.
**Validates: Requirements 6.4**

**Property 19: Extension-less path resolution**
*For any* file path without an extension, the system should automatically find and resolve to the file with the correct extension.
**Validates: Requirements 6.6**

### OCR-Based Clicking Properties

**Property 20: Text click success**
*For any* visible text on screen, the Text_Clicker should find it via OCR and click at the center of its bounding box.
**Validates: Requirements 7.1, 7.2**

**Property 21: Window title filtering**
*For any* click_text_fast step with a window_title specified, the Text_Clicker should only consider OCR results from that window.
**Validates: Requirements 7.3**

**Property 22: Fuzzy text matching**
*For any* text query, the Text_Clicker should match it case-insensitively and support partial matches.
**Validates: Requirements 7.4**

**Property 23: Text not found handling**
*For any* text that doesn't exist on screen, the Text_Clicker should return failure status with an error message.
**Validates: Requirements 7.7**

### Window Management Properties

**Property 24: Window activation after launch**
*For any* app launch step, the Window_Manager should wait for the window to appear and then activate it before proceeding.
**Validates: Requirements 8.1, 8.2**

**Property 25: Focus before input**
*For any* keyboard or mouse input step, the Window_Manager should ensure the foreground window is active before executing the input.
**Validates: Requirements 8.3**

**Property 26: Modal dialog focus suppression**
*For any* save_file or open_file step, the Window_Manager should be suppressed during dialog interaction to prevent focus stealing.
**Validates: Requirements 8.4**

### Permission System Properties

**Property 27: Critical operation detection**
*For any* step with type delete_file, delete_folder, or shell_command containing destructive keywords, the Permission_Service should identify it as critical.
**Validates: Requirements 9.5**

**Property 28: Permission request pause**
*For any* critical operation, execution should pause until the user approves or denies the permission request.
**Validates: Requirements 9.2**

**Property 29: Denied operation skip**
*For any* permission request that is denied, the operation should be skipped and execution should continue with remaining steps.
**Validates: Requirements 9.4**

**Property 30: Abort stops execution**
*For any* execution in progress, when abort is requested, the Plan_Executor should stop immediately and return aborted status.
**Validates: Requirements 9.6, 9.7**

### Verification and Retry Properties

**Property 31: Verification screenshot capture**
*For any* completed execution plan with expected_final_state, the Vision_Service should capture a screenshot and compare it to the expected state.
**Validates: Requirements 10.1**

**Property 32: Verification result structure**
*For any* verification operation, the result should contain success (bool), confidence (float), current_state (string), missing_elements (array), and corrective_actions (array).
**Validates: Requirements 10.6**

**Property 33: Retry on verification failure**
*For any* execution where verification fails and retry_count < MAX_RETRIES, the Plan_Executor should retry the entire plan.
**Validates: Requirements 10.3**

### Debug Logging Properties

**Property 34: Session directory creation**
*For any* execution start, the Debug_Logger should create a new session directory with timestamp format YYYY-MM-DD_HH-MM-SS.
**Validates: Requirements 11.1**

**Property 35: Artifact logging completeness**
*For any* execution, the Debug_Logger should save planner_output.json, screenshot.png (if vision used), annotated.png (if vision used), box_map.json (if vision used), vision_mapper_output.json (if vision used), and session_info.json.
**Validates: Requirements 11.2, 11.3, 11.4, 11.7**

**Property 36: Step execution logging**
*For any* step executed, the Debug_Logger should log the step order, type, details, and success status.
**Validates: Requirements 11.5**

### Readiness Detection Properties

**Property 37: Readiness before vision**
*For any* execution plan with visual_click or click_text_fast steps, the Plan_Executor should wait for readiness before the first vision operation.
**Validates: Requirements 13.7**

**Property 38: Readiness timeout**
*For any* readiness detection operation, if the timeout is exceeded, the detector should return timeout status and allow execution to proceed.
**Validates: Requirements 13.5**

### WebSocket Communication Properties

**Property 39: Automatic reconnection**
*For any* WebSocket disconnection, the Local_Client should attempt to reconnect with exponential backoff until successful.
**Validates: Requirements 14.2**

**Property 40: Status update transmission**
*For any* status update emitted by the Local_Client, it should be received by the Backend_Server and forwarded to the mobile app.
**Validates: Requirements 14.4**

**Property 41: Large payload support**
*For any* payload up to 50MB, the WebSocket connection should transmit it successfully without truncation.
**Validates: Requirements 14.7**

### Audio Feedback Properties

**Property 42: Start sound playback**
*For any* execution start, if audio is available, the Plan_Executor should play the start sound without blocking execution.
**Validates: Requirements 15.1, 15.5**

**Property 43: Completion sound playback**
*For any* successful execution completion, if audio is available, the Plan_Executor should play the completion sound.
**Validates: Requirements 15.2**

**Property 44: Graceful audio failure**
*For any* execution, if audio files are missing or pygame is not installed, the system should continue without crashing.
**Validates: Requirements 15.6, 15.7**

### Shell Command Properties

**Property 45: Environment variable expansion in commands**
*For any* shell command containing environment variables, the Shell_Executor should expand them before execution.
**Validates: Requirements 16.2**

**Property 46: Command chaining**
*For any* shell command with & operator, the Shell_Executor should execute all chained commands in sequence.
**Validates: Requirements 16.3**

**Property 47: Error continuation**
*For any* shell command that fails, the Shell_Executor should log the error and continue with remaining steps.
**Validates: Requirements 16.7**

### Configuration Properties

**Property 48: Configuration loading**
*For any* Local_Client startup, the system should load configuration from config.py and apply the settings.
**Validates: Requirements 19.1**

**Property 49: Retry settings respect**
*For any* verification failure, the system should respect MAX_RETRIES and RETRY_DELAY from configuration.
**Validates: Requirements 19.6**

### Error Handling Properties

**Property 50: Step failure continuation**
*For any* non-critical step failure, the Plan_Executor should log the error and continue with remaining steps.
**Validates: Requirements 20.1**

**Property 51: Missing target reporting**
*For any* visual_click step where the target is not found in the ID map, the Plan_Executor should report which target was missing.
**Validates: Requirements 20.3**

**Property 52: File operation error messages**
*For any* file operation failure, the File_Operations_Module should return a tuple with success=False and a descriptive error message.
**Validates: Requirements 20.4**

## Error Handling

### Error Categories

1. **Planner Errors**: Invalid API key, model unavailable, malformed response
   - Action: Return error to mobile app, don't send to Local Client

2. **Vision Errors**: FastSAM failure, Vision Mapper timeout, target not found
   - Action: Log error, skip visual_click step, continue execution

3. **File Operation Errors**: Permission denied, file not found, encoding error
   - Action: Return error tuple, log error, continue execution

4. **Window Management Errors**: Window not found, activation timeout
   - Action: Log warning, continue with fallback delay

5. **Permission Errors**: User denied, timeout waiting for response
   - Action: Skip operation, continue execution

6. **WebSocket Errors**: Connection lost, message send failure
   - Action: Attempt reconnection, queue messages for retry

### Error Recovery Strategies

- **Retry with backoff**: WebSocket reconnection, window activation
- **Graceful degradation**: Audio playback failure, window manager unavailable
- **Skip and continue**: Permission denied, vision target not found
- **Fallback methods**: Window activation timeout → use fixed delay
- **User notification**: Critical errors reported via status updates

## Testing Strategy

### Unit Testing

Unit tests verify specific examples, edge cases, and error conditions:

- **Planner Service**: Test mode detection, step type generation, path expansion
- **File Operations**: Test write/read/append with various paths and encodings
- **File Editor**: Test replace/modify/insert/delete with edge cases (empty files, invalid line numbers)
- **Vision Service**: Test screenshot capture, SoM detection, ID mapping
- **Window Manager**: Test window finding, activation, focus management
- **Permission Service**: Test critical operation detection, permission flow
- **Debug Logger**: Test session creation, artifact logging

### Property-Based Testing

Property tests verify universal properties across all inputs using a PBT library (e.g., Hypothesis for Python):

- **Minimum 100 iterations per property test** (due to randomization)
- Each property test references its design document property number
- Tag format: `# Feature: jarvis-automation-system, Property N: [property text]`

**Example Property Tests:**

```python
# Feature: jarvis-automation-system, Property 8: File write-read round trip
@given(st.text(), st.text(min_size=1))
def test_file_write_read_round_trip(path, content):
    """For any valid file path and content, writing then reading should return same content."""
    success, _ = write_file(path, content)
    assert success
    success, _, read_content = read_file(path)
    assert success
    assert read_content == content

# Feature: jarvis-automation-system, Property 6: Bounding box center calculation
@given(st.floats(min_value=0, max_value=1000), 
       st.floats(min_value=0, max_value=1000),
       st.floats(min_value=0, max_value=1000),
       st.floats(min_value=0, max_value=1000))
def test_bounding_box_center(x1, y1, x2, y2):
    """For any bounding box, click coordinates should be at center."""
    assume(x2 > x1 and y2 > y1)
    cx, cy = calculate_center([x1, y1, x2, y2])
    assert cx == (x1 + x2) / 2
    assert cy == (y1 + y2) / 2

# Feature: jarvis-automation-system, Property 4: Environment variable expansion
@given(st.sampled_from(['%USERPROFILE%', '%DESKTOP%', '%DOCUMENTS%']))
def test_environment_variable_expansion(env_var):
    """For any path with environment variables, they should be expanded."""
    path = f"{env_var}\\test.txt"
    expanded = expand_path(path)
    assert env_var not in expanded
    assert '\\' in expanded or '/' in expanded

# Feature: jarvis-automation-system, Property 17: Fuzzy path resolution
@given(st.text(min_size=3, max_size=20))
def test_fuzzy_path_resolution(query):
    """For any fuzzy path query, if a match exists, it should resolve correctly."""
    # Create a test file with known name
    test_file = create_test_file("TestFile123.txt")
    
    # Test with variations
    variations = [query.lower(), query.upper(), query[:5]]
    for variant in variations:
        result = resolve_fuzzy_path(variant)
        if result.success:
            assert test_file in result.resolved_path
```

### Integration Testing

Integration tests verify component interactions:

- **Backend → Local Client**: Test WebSocket command transmission
- **Planner → Executor**: Test plan generation and execution
- **Vision Service → Plan Executor**: Test vision pipeline integration
- **Permission Service → Plan Executor**: Test permission flow
- **Debug Logger → All Components**: Test logging integration

### System Testing

End-to-end tests verify complete workflows:

- **Simple command**: "Open Notepad" → Verify Notepad opens
- **File creation**: "Create folder AI Lab on Desktop" → Verify folder exists
- **Code workflow**: "Create Python file with bubble sort" → Verify file created with correct content
- **Vision workflow**: "Click Submit button" → Verify button clicked
- **Permission workflow**: "Delete file test.txt" → Verify permission requested
- **Verification workflow**: Execute plan → Verify task completion → Verify retry on failure

### Test Coverage Goals

- **Unit tests**: 80%+ code coverage
- **Property tests**: All 52 correctness properties implemented
- **Integration tests**: All component interfaces tested
- **System tests**: All major workflows tested

### Continuous Testing

- Run unit tests on every commit
- Run property tests nightly (longer execution time)
- Run integration tests before releases
- Run system tests manually for major features

## Implementation Notes

### Performance Considerations

- **Vision pipeline**: Expensive (3-5 seconds), use caching and adaptive re-scanning
- **Shell commands**: Fast (0.1 seconds), prefer over UI automation
- **File operations**: Fast (0.1 seconds), prefer over UI-based file creation
- **Keyboard actions**: Medium (0.3-0.5 seconds per step)
- **OCR clicking**: Medium (1-2 seconds), faster than vision
- **Window activation**: Variable (0-10 seconds), use timeouts

### Security Considerations

- **Permission system**: Required for delete operations and destructive shell commands
- **Path validation**: Sanitize paths to prevent directory traversal
- **Command injection**: Validate shell commands for malicious content
- **API key protection**: Store Gemini API key in environment variables
- **WebSocket authentication**: Consider adding authentication for production

### Scalability Considerations

- **Concurrent executions**: Currently single-threaded, consider task queue for multiple users
- **Vision model caching**: Cache FastSAM model in memory (loaded once)
- **Debug log cleanup**: Implement automatic cleanup of old debug sessions
- **WebSocket connections**: Support multiple Local Clients per Backend Server

### Future Enhancements

- **Voice activation**: "Hey JARVIS" wake word detection
- **Multi-monitor support**: Handle multiple screens in vision pipeline
- **Mac/Linux support**: Port Local Client to other operating systems
- **Local model support**: Replace Gemini with local LLM for offline operation
- **Task scheduling**: Schedule automation tasks for future execution
- **Conversation memory**: Remember context across multiple commands
- **Learning from corrections**: Improve plans based on verification failures

---

## Desktop Packaging Architecture

### Overview

JARVIS is packaged as a production-ready desktop application with Firebase-based mobile connectivity. The packaging system transforms the multi-component development setup into a single distributable package that users can install and run with minimal configuration.

### Packaging Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│         Desktop Application Package (ZIP)               │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │              UI Layer                             │ │
│  │  ┌─────────────────┐  ┌──────────────────────┐  │ │
│  │  │  Settings UI    │  │  First-Run Modal     │  │ │
│  │  │  React + Vite   │  │  Aceternity UI       │  │ │
│  │  └─────────────────┘  └──────────────────────┘  │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │            Backend Layer                          │ │
│  │  ┌─────────────────┐  ┌──────────────────────┐  │ │
│  │  │  Flask Server   │  │  Planner Service     │  │ │
│  │  │  Port 5000      │  │  Gemini API          │  │ │
│  │  └─────────────────┘  └──────────────────────┘  │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │           Execution Layer                         │ │
│  │  ┌─────────────────┐  ┌──────────────────────┐  │ │
│  │  │  Local Client   │  │  Vision Service      │  │ │
│  │  │  Python         │  │  Plan Executor       │  │ │
│  │  └─────────────────┘  └──────────────────────┘  │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │          Process Manager                          │ │
│  │  ┌─────────────────┐  ┌──────────────────────┐  │ │
│  │  │ Launcher Script │  │ System Tray Manager  │  │ │
│  │  └─────────────────┘  └──────────────────────┘  │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Firebase Connection
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Cloud Services                             │
│  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │ Firebase Realtime   │  │  Firebase Auth           │ │
│  │ Database            │  │  (Anonymous)             │ │
│  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Mobile Connection
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Mobile App                                 │
│  ┌─────────────────────┐  ┌──────────────────────────┐ │
│  │ React Native App    │  │  QR Scanner              │ │
│  └─────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Packaged Application Directory Structure

```
JARVIS/
├── runtime/
│   ├── python/          # Embedded Python 3.10+
│   └── node/            # Embedded Node.js 18+
├── app/
│   ├── backend/         # Flask server + dependencies
│   ├── local_client/    # Automation client + dependencies
│   └── settings_ui/     # Built React app (dist/)
├── assets/
│   ├── weights/         # FastSAM-s.pt
│   ├── icons/           # Application icons
│   └── config/          # Default configuration templates
├── data/
│   ├── config.py        # User configuration (created on first run)
│   ├── firebase.json    # Firebase credentials
│   └── logs/            # Application logs
├── JARVIS.exe           # Main launcher
├── README.txt           # Quick start guide
└── LICENSE.txt          # License information
```

## Packaging Components

### Packaging System

**Technology**: PyInstaller + Vite + Custom build scripts

**Interface**:
```python
class PackagingSystem:
    def bundle_python_components() -> Path:
        """Bundle backend and local_client with PyInstaller"""
        
    def bundle_nodejs_components() -> Path:
        """Bundle settings_ui with Vite build"""
        
    def include_assets() -> None:
        """Copy FastSAM weights, icons, configs"""
        
    def create_launcher() -> Path:
        """Generate main launcher executable"""
        
    def create_distribution() -> Path:
        """Create final ZIP file with version info"""
```

### First-Run Setup Wizard

**Technology**: React + Aceternity UI Modal + Framer Motion

**Interface**:
```typescript
interface FirstRunSetupProps {
  onComplete: (config: Configuration) => void;
  onSkip: () => void;
}

interface Configuration {
  apiKeys: {
    gemini: string;
    openai?: string;
  };
  paths: {
    desktop: string;
    documents: string;
    downloads: string;
  };
  system: {
    username: string;
  };
}

class FirstRunSetup extends React.Component<FirstRunSetupProps> {
  validateApiKey(key: string, provider: 'gemini' | 'openai'): Promise<boolean>;
  validatePath(path: string): boolean;
  saveConfiguration(config: Configuration): Promise<void>;
  generatePairingCode(): string;
}
```

**Component Structure**:
```
settings_ui/src/components/
├── ui/
│   └── AnimatedModal.jsx       # Adapted from Aceternity UI
├── setup/
│   ├── FirstRunSetup.jsx       # Main setup wizard
│   ├── ApiKeyStep.jsx          # API key input step
│   ├── PathConfigStep.jsx      # Path configuration step
│   └── PairingStep.jsx         # QR code pairing step
└── utils/
    └── cn.js                   # Class name utility
```

### Firebase Integration

**Technology**: Firebase Realtime Database + Firebase Admin SDK

**Data Structure**:
```json
{
  "devices": {
    "{deviceId}": {
      "type": "desktop" | "mobile",
      "paired": true,
      "lastSeen": 1234567890,
      "version": "1.0.0"
    }
  },
  "pairing": {
    "{pairingToken}": {
      "desktopId": "{deviceId}",
      "expiresAt": 1234567890,
      "used": false
    }
  },
  "messages": {
    "{deviceId}": {
      "commands": {
        "{messageId}": {
          "type": "command",
          "text": "open notepad",
          "timestamp": 1234567890,
          "processed": false
        }
      },
      "status": {
        "{messageId}": {
          "type": "status",
          "message": "Processing...",
          "progress": 50,
          "timestamp": 1234567890
        }
      }
    }
  }
}
```

**Security Rules**:
```javascript
{
  "rules": {
    "devices": {
      "$deviceId": {
        ".read": "auth != null && auth.uid == $deviceId",
        ".write": "auth != null && auth.uid == $deviceId"
      }
    },
    "pairing": {
      "$token": {
        ".read": "auth != null",
        ".write": "auth != null && !data.exists()"
      }
    },
    "messages": {
      "$deviceId": {
        ".read": "auth != null && (auth.uid == $deviceId || root.child('devices/' + auth.uid + '/pairedWith').val() == $deviceId)",
        ".write": "auth != null"
      }
    }
  }
}
```

**Interface**:
```python
class FirebaseService:
    def __init__(self, credentials_path: str):
        """Initialize Firebase with service account"""
        
    def generate_pairing_token(self, desktop_id: str, ttl: int = 300) -> str:
        """Generate time-limited pairing token"""
        
    def verify_pairing_token(self, token: str, mobile_id: str) -> bool:
        """Verify and consume pairing token"""
        
    def pair_devices(self, desktop_id: str, mobile_id: str) -> str:
        """Create persistent device pairing"""
        
    def send_command(self, device_id: str, command: dict) -> None:
        """Send command to device"""
        
    def send_status(self, device_id: str, status: dict) -> None:
        """Send status update to device"""
        
    def listen_for_commands(self, device_id: str, callback: Callable) -> None:
        """Listen for incoming commands"""
        
    def update_presence(self, device_id: str) -> None:
        """Update device last-seen timestamp"""
```

### Device Pairing System

**Desktop Side**:
```python
class PairingManager:
    def __init__(self, firebase: FirebaseService):
        self.firebase = firebase
        self.device_id = self._get_or_create_device_id()
        
    def _get_or_create_device_id(self) -> str:
        """Load or generate unique device ID"""
        
    def generate_pairing_qr(self) -> tuple[str, bytes]:
        """Generate pairing token and QR code image"""
        token = self.firebase.generate_pairing_token(self.device_id)
        qr_image = self._create_qr_code(token)
        return token, qr_image
        
    def _create_qr_code(self, data: str) -> bytes:
        """Create QR code image using qrcode library"""
        
    def check_pairing_status(self, token: str) -> bool:
        """Check if pairing completed"""
        
    def is_paired(self) -> bool:
        """Check if device is already paired"""
        
    def unpair(self) -> None:
        """Remove pairing and require re-pairing"""
```

**Mobile Side**:
```typescript
class PairingManager {
  constructor(firebase: FirebaseService) {}
  
  async scanQRCode(): Promise<string> {
    // Use React Native Camera to scan QR code
  }
  
  async submitPairingToken(token: string): Promise<boolean> {
    // Send token to Firebase for verification
  }
  
  async isPaired(): Promise<boolean> {
    // Check if device has valid pairing
  }
  
  getDeviceId(): string {
    // Get stored device ID from secure storage
  }
}
```

### Application Launcher

**Technology**: Python + subprocess + pystray (system tray)

**Interface**:
```python
class ApplicationLauncher:
    def __init__(self):
        self.processes = {}
        self.tray_icon = None
        
    def start(self) -> None:
        """Start all components in correct order"""
        self._start_backend()
        self._start_local_client()
        self._start_settings_ui()
        self._create_system_tray()
        
    def _start_backend(self) -> subprocess.Popen:
        """Start Flask backend server"""
        
    def _start_local_client(self) -> subprocess.Popen:
        """Start local automation client"""
        
    def _start_settings_ui(self) -> subprocess.Popen:
        """Start Settings UI with PyWebView"""
        
    def _create_system_tray(self) -> None:
        """Create system tray icon with menu"""
        
    def _monitor_processes(self) -> None:
        """Monitor and restart crashed components"""
        
    def shutdown(self) -> None:
        """Gracefully shutdown all components"""
```

**System Tray Menu**:
```
JARVIS
├── Show Settings
├── Pairing Status: ✓ Paired
├── Backend: ✓ Running
├── Client: ✓ Running
├── ───────────────
├── Restart All
├── View Logs
├── ───────────────
└── Quit
```

### Configuration Management

**Interface**:
```python
class ConfigurationManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_or_create()
        
    def _load_or_create(self) -> dict:
        """Load existing config or create from template"""
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        
    def save(self) -> None:
        """Save configuration to disk"""
        
    def validate(self) -> list[str]:
        """Validate configuration and return errors"""
        
    def backup(self) -> Path:
        """Create configuration backup"""
        
    def restore(self, backup_path: Path) -> None:
        """Restore from backup"""
        
    def is_first_run(self) -> bool:
        """Check if this is first run"""
        
    def mark_configured(self) -> None:
        """Mark first-run setup as complete"""
```

**Configuration Schema**:
```python
DEFAULT_CONFIG = {
    "version": "1.0.0",
    "first_run_complete": False,
    "system": {
        "server_url": "http://localhost:5000",
        "windows_username": "",
    },
    "llm": {
        "provider": "gemini",
        "gemini_api_key": "",
        "openai_api_key": "",
    },
    "paths": {
        "desktop": "",
        "documents": "",
        "downloads": "",
    },
    "firebase": {
        "device_id": "",
        "paired": False,
        "paired_device_id": "",
    },
    "timing": {
        "action_delay": 0.5,
        "app_launch_wait": 5,
    },
    "verification": {
        "enabled": True,
        "max_retries": 2,
    }
}
```

## Packaging Data Models

### Device Model
```python
@dataclass
class Device:
    id: str
    type: Literal["desktop", "mobile"]
    paired: bool
    paired_with: Optional[str]
    last_seen: datetime
    version: str
    
    def to_dict(self) -> dict:
        """Convert to Firebase-compatible dict"""
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """Create from Firebase data"""
```

### Pairing Token Model
```python
@dataclass
class PairingToken:
    token: str
    desktop_id: str
    expires_at: datetime
    used: bool
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        
    def is_expired(self) -> bool:
        """Check if token has expired"""
```

### Message Model
```python
@dataclass
class Message:
    id: str
    type: Literal["command", "status", "progress", "error", "completion"]
    content: dict
    timestamp: datetime
    processed: bool
    
    def to_dict(self) -> dict:
        """Convert to Firebase-compatible dict"""
```

### Configuration Model
```python
@dataclass
class Configuration:
    version: str
    first_run_complete: bool
    system: SystemConfig
    llm: LLMConfig
    paths: PathsConfig
    firebase: FirebaseConfig
    timing: TimingConfig
    verification: VerificationConfig
    
    def validate(self) -> list[str]:
        """Validate all configuration sections"""
        
    def to_dict(self) -> dict:
        """Convert to saveable dict"""
```

## Packaging Correctness Properties

### Property 53: Configuration Persistence
*For any* configuration changes made through the Settings UI, saving the configuration and restarting the application should result in the same configuration being loaded.
**Validates: Requirements 29.1, 29.2**

### Property 54: Component Startup Order
*For any* application launch, the Backend Server should start before the Local Client, and both should be running before the Settings UI becomes interactive.
**Validates: Requirements 28.1**

### Property 55: Pairing Token Expiration
*For any* generated pairing token, attempting to use it after its expiration time should result in rejection.
**Validates: Requirements 25.2, 25.6**

### Property 56: Device Authentication
*For any* message sent from a mobile device, the message should only be processed if the device has a valid Device_Identifier that matches a paired desktop.
**Validates: Requirements 25.11, 26.4**

### Property 57: Message Ordering
*For any* sequence of commands sent from the mobile app, they should be processed by the desktop in the same order they were sent.
**Validates: Requirements 27.7**

### Property 58: Firebase Reconnection
*For any* network disconnection, when connectivity is restored, the system should automatically reconnect to Firebase and resume message processing.
**Validates: Requirements 24.5, 24.9**

### Property 59: Configuration Validation
*For any* configuration file, loading it should either succeed with valid configuration or fail with specific error messages for each invalid field.
**Validates: Requirements 29.4, 30.1**

### Property 60: API Key Validation
*For any* API key entered during first-run setup, the system should verify it works before allowing setup completion.
**Validates: Requirements 22.6**

### Property 61: Path Validation
*For any* system path entered during first-run setup, the system should verify the path exists before allowing setup completion.
**Validates: Requirements 22.7**

### Property 62: Component Crash Recovery
*For any* component crash, the launcher should detect it within 5 seconds and restart the component automatically.
**Validates: Requirements 30.4, 30.5**

### Property 63: Pairing Uniqueness
*For any* desktop device, it should only be paired with one mobile device at a time, and attempting to pair with a second device should require unpairing the first.
**Validates: Requirements 25.11**

### Property 64: Message Cleanup
*For any* successfully delivered message, it should be removed from Firebase within 60 seconds to prevent accumulation.
**Validates: Requirements 27.8**

### Property 65: Configuration Backup
*For any* configuration save operation, a backup of the previous configuration should be created before writing the new one.
**Validates: Requirements 29.5**

### Property 66: First-Run Detection
*For any* application launch, if no configuration file exists or first_run_complete is false, the first-run modal should be displayed.
**Validates: Requirements 22.1**

### Property 67: QR Code Generation
*For any* pairing token, generating a QR code and then scanning it should produce the original token string.
**Validates: Requirements 25.3, 25.4**

## Packaging Error Handling

### Packaging-Specific Error Categories

1. **Configuration Errors**
   - Missing or invalid API keys
   - Invalid system paths
   - Corrupted configuration file
   - Missing Firebase credentials

2. **Network Errors**
   - Firebase connection failure
   - API endpoint unreachable
   - Timeout errors
   - Rate limiting

3. **Component Errors**
   - Backend server crash
   - Local client crash
   - Settings UI crash
   - Process startup failure

4. **Pairing Errors**
   - Expired pairing token
   - Invalid pairing token
   - Already paired device
   - QR code scan failure

5. **Runtime Errors**
   - Permission denied
   - Disk space full
   - Memory exhaustion
   - Dependency missing

### Packaging Error Handler

```python
class ErrorHandler:
    def handle_configuration_error(self, error: ConfigurationError) -> None:
        """Display user-friendly message and offer to reset"""
        
    def handle_network_error(self, error: NetworkError) -> None:
        """Show offline status and queue operations"""
        
    def handle_component_crash(self, component: str, error: Exception) -> None:
        """Log error, attempt restart, notify user if fails"""
        
    def handle_pairing_error(self, error: PairingError) -> None:
        """Display specific error and offer retry/regenerate"""
        
    def handle_runtime_error(self, error: RuntimeError) -> None:
        """Log detailed error, show user-friendly message"""
```

### Error Recovery Procedures

1. **Configuration Recovery**:
   - Attempt to load backup configuration
   - If backup fails, use default configuration
   - Prompt user to reconfigure

2. **Network Recovery**:
   - Implement exponential backoff for reconnection
   - Queue operations while offline
   - Process queue when connection restored

3. **Component Recovery**:
   - Restart crashed component up to 3 times
   - If restart fails, notify user and offer manual restart
   - Log crash details for debugging

4. **Pairing Recovery**:
   - Generate new pairing token on expiration
   - Clear invalid pairing state
   - Guide user through re-pairing process

## Packaging Testing Strategy

### Property-Based Testing for Packaging

**Example Property Tests**:

```python
from hypothesis import given, strategies as st

@given(st.text(), st.text())
def test_property_53_configuration_persistence(key, value):
    """Property 53: Configuration round-trip"""
    # Feature: jarvis-desktop-packaging, Property 53: Configuration Persistence
    config = Configuration()
    config.set(key, value)
    config.save()
    loaded = Configuration.load()
    assert loaded.get(key) == value

@given(st.integers(min_value=1, max_value=300))
def test_property_55_pairing_token_expiration(ttl_seconds):
    """Property 55: Pairing token expiration"""
    # Feature: jarvis-desktop-packaging, Property 55: Pairing Token Expiration
    token = generate_pairing_token(ttl=ttl_seconds)
    time.sleep(ttl_seconds + 1)
    assert is_token_valid(token) == False

@given(st.lists(st.text(), min_size=1, max_size=10))
def test_property_57_message_ordering(commands):
    """Property 57: Message ordering preservation"""
    # Feature: jarvis-desktop-packaging, Property 57: Message Ordering
    for cmd in commands:
        send_command(cmd)
    received = get_received_commands()
    assert received == commands

@given(st.text(min_size=10, max_size=100))
def test_property_67_qr_code_round_trip(token):
    """Property 67: QR code generation and scanning"""
    # Feature: jarvis-desktop-packaging, Property 67: QR Code Generation
    qr_image = generate_qr_code(token)
    scanned_token = scan_qr_code(qr_image)
    assert scanned_token == token
```

### Integration Testing for Packaging

**Test Scenarios**:
1. Full application startup and shutdown
2. First-run setup workflow
3. Device pairing workflow
4. Command execution from mobile to desktop
5. Component crash and recovery
6. Configuration save and restore
7. Firebase connection and reconnection

### Performance Testing for Packaging

**Metrics**:
- Application startup time: < 10 seconds
- First-run modal display time: < 2 seconds
- QR code generation time: < 1 second
- Firebase message latency: < 500ms
- Component restart time: < 5 seconds
- Configuration save time: < 100ms

### Security Testing for Packaging

**Test Areas**:
- Pairing token cannot be reused
- Expired tokens are rejected
- Unauthorized devices cannot send commands
- Firebase security rules prevent unauthorized access
- API keys are stored securely
- Device identifiers are cryptographically secure

## Packaging Implementation Notes

### Build Process

1. **Python Bundling**:
   - Use PyInstaller with `--onedir` mode
   - Include hidden imports for Firebase SDK
   - Bundle FastSAM weights as data files
   - Create spec file for reproducible builds

2. **Node.js Bundling**:
   - Use Vite build for production
   - Optimize bundle size with tree-shaking
   - Include only production dependencies
   - Generate source maps for debugging

3. **Asset Management**:
   - Copy FastSAM weights to assets/weights/
   - Include application icons in multiple sizes
   - Package configuration templates
   - Include Firebase credentials template

4. **Distribution**:
   - Create portable folder structure
   - Generate launcher executable
   - Create ZIP archive with version number
   - Generate checksums for verification

### Packaging Security Considerations

- **Firebase Security**: Implement strict security rules
- **Token Storage**: Use encrypted storage for device IDs
- **API Keys**: Store in secure configuration files
- **Network**: Use HTTPS/TLS for all communication
- **Pairing**: Time-limited tokens with rate limiting

### Packaging Future Enhancements

- **Auto-update**: Implement automatic update checking
- **Installer**: Create Windows installer (NSIS/Inno Setup)
- **Code Signing**: Sign executables for Windows SmartScreen
- **Multi-platform**: Support macOS and Linux
- **Cloud Sync**: Sync configuration across devices
