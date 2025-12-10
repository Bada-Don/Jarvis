# Implementation Plan

- [x] 1. Create Path Configuration Module





  - [x] 1.1 Create `local_client/path_config.py` with PathConfig dataclass


    - Define fields: default_save_directory, default_open_directory, overwrite_policy, dialog_wait_timeout
    - Implement `load()` classmethod to read from JSON config file
    - Implement `save()` method to persist configuration
    - Implement `get_full_save_path()` and `get_full_open_path()` helper methods
    - _Requirements: 6.1, 6.4, 1.4_
  - [ ]* 1.2 Write property test for configuration loading
    - **Property 10: Configuration Loading**
    - **Validates: Requirements 6.1**
  - [ ]* 1.3 Write property test for default directory application
    - **Property 4: Default Directory Application**
    - **Validates: Requirements 1.4, 6.2**

- [x] 2. Create OCR Service Module






  - [x] 2.1 Create `local_client/ocr_service.py` with TextLocation dataclass and OCRService class

    - Define TextLocation with text, bbox, confidence, center fields
    - Implement `detect_text()` using Windows OCR or pytesseract
    - Implement `find_text()` for searching specific text with fuzzy matching
    - Implement `find_text_in_region()` for constrained search
    - _Requirements: 4.1, 4.2_
  - [ ]* 2.2 Write property test for bounding box center calculation
    - **Property 6: Bounding Box Center Calculation**
    - **Validates: Requirements 4.2**
  - [ ]* 2.3 Write property test for closest text selection
    - **Property 7: Closest Text Selection**
    - **Validates: Requirements 4.3**

- [x] 3. Create Text-Based Clicker Module






  - [x] 3.1 Create `local_client/text_clicker.py` with TextBasedClicker class

    - Implement `click_text()` to find and click on text via OCR
    - Implement `click_file_in_explorer()` for File Explorer file selection
    - Implement `double_click_text()` for opening files
    - Implement ClickResult dataclass for return values
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 3.3_
  - [ ]* 3.2 Write property test for OCR failure reporting
    - **Property 8: OCR Failure Reporting**
    - **Validates: Requirements 4.4**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create Direct Path Executor Module






  - [x] 5.1 Create `local_client/direct_path_executor.py` with DirectPathExecutor class

    - Implement `execute_save()` with Ctrl+S, path typing, Enter sequence
    - Implement `execute_open()` with Ctrl+O, path typing, Enter sequence
    - Implement `navigate_explorer()` with Ctrl+L, path typing, Enter sequence
    - Implement `_wait_for_dialog()` helper for dialog detection
    - Implement `_handle_overwrite_dialog()` for file conflict handling
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 5.1_
  - [ ]* 5.2 Write property test for Explorer navigation sequence
    - **Property 5: Explorer Navigation Sequence**
    - **Validates: Requirements 3.1, 3.2**
  - [ ]* 5.3 Write property test for error path reporting
    - **Property 9: Error Path Reporting**
    - **Validates: Requirements 5.2, 5.3**
  - [ ]* 5.4 Write property test for overwrite policy enforcement
    - **Property 11: Overwrite Policy Enforcement**
    - **Validates: Requirements 6.3**

- [ ] 6. Define New Step Types and Data Models
  - [ ] 6.1 Create `local_client/path_step_types.py` with step dataclasses
    - Define SaveFileStep, OpenFileStep, NavigateExplorerStep, ClickTextStep dataclasses
    - Implement JSON serialization methods (to_dict, from_dict)
    - Implement ExecutionResult and ClickResult dataclasses
    - _Requirements: 7.1, 7.2, 7.3_
  - [ ]* 6.2 Write property test for path construction completeness
    - **Property 3: Path Construction Completeness**
    - **Validates: Requirements 1.3, 2.3**
  - [ ]* 6.3 Write property test for serialization round-trip
    - **Property 12: Path Operation Serialization Round-Trip**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Integrate with Plan Executor
  - [ ] 8.1 Update `local_client/plan_executor.py` to handle new step types
    - Add imports for DirectPathExecutor, TextBasedClicker, PathConfig
    - Add step type handlers for save_file, open_file, navigate_explorer, click_text
    - Initialize DirectPathExecutor and TextBasedClicker in constructor
    - Route new step types to appropriate executor methods
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1_
  - [ ]* 8.2 Write property test for save plan generation
    - **Property 1: Save Plan Generation Correctness**
    - **Validates: Requirements 1.1, 1.2**
  - [ ]* 8.3 Write property test for open plan generation
    - **Property 2: Open Plan Generation Correctness**
    - **Validates: Requirements 2.1, 2.2**

- [ ] 9. Update Planner Model Prompts
  - [ ] 9.1 Update `backend/gemini_service.py` with direct path operation instructions
    - Add documentation for save_file, open_file, navigate_explorer, click_text step types
    - Add examples showing direct path usage patterns
    - Update validation to accept new step types
    - _Requirements: 1.1, 2.1, 3.1, 4.1_

- [ ] 10. Create Default Configuration File
  - [ ] 10.1 Create `local_client/direct_path_config.json` with default settings
    - Set default_save_directory to Desktop path
    - Set default_open_directory to Documents path
    - Set overwrite_policy to "prompt"
    - Set dialog_wait_timeout to 2.0 seconds
    - _Requirements: 6.1, 6.4_

- [ ] 11. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

