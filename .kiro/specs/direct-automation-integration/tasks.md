# Implementation Plan

- [x] 1. Create FlexiSIGN UIA Module foundation





  - [x] 1.1 Create flexisign_uia.py with FlexiSignUIA class skeleton


    - Create `local_client/flexisign_uia.py` with class structure
    - Import comtypes, psutil, pyautogui, and pygetwindow
    - Implement `__init__` to create UIA COM object
    - Implement `cleanup` method for resource release
    - _Requirements: 8.1, 8.3_


  - [x] 1.2 Implement window detection and activation

    - Implement `find_flexisign_window()` to detect FlexiSIGN by window title
    - Implement `get_pid_from_window()` to retrieve PID from window handle
    - Implement `activate_window()` to bring window to foreground
    - Implement `find_and_activate_window()` with 5-second retry logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 1.3 Write property test for window detection






    - **Property 1: Window Detection Correctness**
    - **Validates: Requirements 1.1**

- [x] 2. Implement UIA element selectors





  - [x] 2.1 Port element selectors from automation_sample


    - Copy and adapt `create_uia`, `get_root_for_pid`, `find_first` from elements.py
    - Implement `get_text_tool()`, `get_select_tool()` selectors
    - Implement `get_scale_tab_item()`, `get_character_tab_item()` selectors
    - Implement `get_scale_width_input()`, `get_scale_height_input()` selectors
    - Implement `get_proportional_checkbox()` selector
    - Implement `get_font_family_combobox()` selector
    - _Requirements: 8.2_


  - [x] 2.2 Implement interaction helpers

    - Implement `click_element_center()` using bounding rect
    - Implement `invoke()` for button clicks via InvokePattern
    - Implement `set_value()` for input fields via ValuePattern
    - Implement `toggle_checkbox()` for checkbox state via TogglePattern
    - _Requirements: 8.2_

  - [ ]* 2.3 Write property test for UIA element not found error
    - **Property 9: UIA Element Not Found Error**
    - **Validates: Requirements 8.4**

- [x] 3. Implement DesignCentral management





  - [x] 3.1 Implement DesignCentral detection and auto-open


    - Implement `_get_designcentral()` to find DesignCentral window
    - Implement `ensure_designcentral_open()` with Ctrl+I fallback
    - Add wait time after opening for UI to stabilize
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]* 3.2 Write property test for DesignCentral auto-open
    - **Property 8: DesignCentral Auto-Open**
    - **Validates: Requirements 9.1, 9.2**

- [x] 4. Implement direct automation actions






  - [x] 4.1 Implement create_text action

    - Implement `click_text_tool()` using UIA selector
    - Implement `click_canvas_center()` using screen center calculation
    - Implement `click_select_tool()` using UIA selector
    - Implement `create_text(text: str)` orchestrating the full sequence
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 4.2 Write property test for create text action sequence
    - **Property 4: Create Text Action Sequence**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 4.3 Implement set_dimensions action


    - Implement `_navigate_to_scale_tab()` to activate Scale tab
    - Implement `_disable_proportional_scaling()` to uncheck checkbox
    - Implement `set_dimensions(width: str, height: str)` orchestrating the full sequence
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 4.4 Write property test for set dimensions action sequence
    - **Property 5: Set Dimensions Action Sequence**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

  - [x] 4.5 Implement set_font action


    - Implement `_navigate_to_character_tab()` to activate Character tab
    - Implement `set_font(font_name: str)` orchestrating the full sequence
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 4.6 Write property test for set font action sequence
    - **Property 6: Set Font Action Sequence**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 4.7 Implement apply_style action


    - Implement `open_apply_styles()` pressing Shift+S
    - Implement `apply_style(style_name: str = None)` with optional search
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 4.8 Implement move_object action


    - Implement `move_object(direction: str, distance: int)` using Shift+Arrow
    - Map direction strings to arrow key names
    - Execute key press the specified number of times
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 4.9 Write property test for move object direction mapping
    - **Property 7: Move Object Direction Mapping**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [x] 5. Checkpoint - Ensure UIA module works





  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Extend Plan Executor for direct mode





  - [x] 6.1 Add direct mode routing to PlanExecutor


    - Add `_flexisign_uia` attribute to `__init__`
    - Modify `execute_plan()` to check mode and route accordingly
    - Implement `_execute_direct_plan()` for direct mode execution
    - Keep existing `_execute_vision_plan()` logic unchanged
    - _Requirements: 7.3, 7.4_

  - [ ]* 6.2 Write property test for direct mode command routing
    - **Property 2: Direct Mode Command Routing**
    - **Validates: Requirements 7.3**

  - [ ]* 6.3 Write property test for vision mode command routing
    - **Property 3: Vision Mode Command Routing**
    - **Validates: Requirements 7.4**

  - [x] 6.4 Implement direct step execution


    - Implement `_execute_direct_step()` to dispatch to UIA actions
    - Handle create_text, set_dimensions, set_font, apply_style, move_object types
    - Handle keyboard type using existing keyboard execution logic
    - Send status updates for each step
    - _Requirements: 2.1, 3.1, 4.1, 5.1, 6.1_

- [x] 7. Update Planner Model for direct mode





  - [x] 7.1 Update gemini_service.py planner prompt


    - Add direct mode documentation to system prompt
    - Add direct command types (create_text, set_dimensions, set_font, apply_style, move_object)
    - Add example output for direct mode plans
    - Update mode selection guidance (standard tasks → direct, complex → vision)
    - _Requirements: 7.1, 7.2_

- [ ] 8. Checkpoint - Ensure integration works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Integration testing
  - [ ] 9.1 Test full direct automation workflow
    - Test "Make iron number plate set for bike, PB12W3998" with direct mode
    - Verify window activation
    - Verify text creation with correct content
    - Verify dimension setting (8x1.2 for front, 10x1.5 for back)
    - Verify font application
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 7.1_

  - [ ]* 9.2 Write integration tests for direct automation
    - Test create_text → set_dimensions → set_font workflow
    - Test error handling when FlexiSIGN is not running
    - Test fallback to vision mode for complex requests
    - _Requirements: 7.1, 7.2, 8.4_

- [ ] 10. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

