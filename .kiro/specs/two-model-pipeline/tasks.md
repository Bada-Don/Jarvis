# Implementation Plan

- [x] 1. Set up environment configuration





  - [x] 1.1 Create backend .env.example file with GEMINI_API_KEY placeholder


    - Create `backend/.env.example` with documented environment variables
    - _Requirements: 6.4_


  - [x] 1.2 Create local_client .env.example file with GEMINI_API_KEY placeholder


    - Create `local_client/.env.example` with documented environment variables
    - _Requirements: 6.4_
  - [x] 1.3 Update backend requirements.txt with google-generativeai and python-dotenv

    - Add `google-generativeai` and `python-dotenv` packages
    - _Requirements: 6.1_
  - [x] 1.4 Update local_client requirements.txt with google-generativeai and python-dotenv


    - Add `google-generativeai` and `python-dotenv` packages
    - _Requirements: 6.2_

- [-] 2. Implement Backend Planner Model Service



  - [x] 2.1 Create gemini_service.py with GeminiPlannerService class



    - Implement `__init__` to load API key from environment
    - Implement `generate_plan(user_command)` method
    - Include hardcoded system prompt with plate dimensions knowledge base
    - Return parsed JSON execution plan
    - _Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [ ]* 2.2 Write property test for execution plan structure validity
    - **Property 1: Execution Plan Structure Validity**
    - **Validates: Requirements 2.4, 2.5, 2.6**
  - [ ]* 2.3 Write unit tests for GeminiPlannerService
    - Test API key loading from environment
    - Test error handling for missing API key
    - _Requirements: 6.1, 6.3_

- [x] 3. Update Backend Server to use Planner Model





  - [x] 3.1 Modify server.py to integrate GeminiPlannerService


    - Import and initialize GeminiPlannerService
    - Update `/api/process` endpoint to call `generate_plan()`
    - Send execution plan to local client via WebSocket with action `two_model_workflow`
    - Emit status updates for progress tracking
    - _Requirements: 1.1, 1.2, 7.1_

- [ ] 4. Checkpoint - Ensure backend changes work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Local Client Vision Service




  - [x] 5.1 Create vision_service.py with VisionService class





    - Implement `__init__` to load API key and FastSAM model
    - Implement `capture_screenshot()` using pyautogui.screenshot()
    - Implement `run_som_detection()` reusing existing SoM.py functions (filter_boxes, draw_annotations)
    - Implement `map_targets_to_ids()` calling Gemini 2.0 Flash Vision Mapper
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2_
  - [ ]* 5.2 Write property test for SoM annotation consistency
    - **Property 2: SoM Annotation Consistency**
    - **Validates: Requirements 3.3, 3.4**
  - [ ]* 5.3 Write property test for Vision Mapper output structure
    - **Property 3: Vision Mapper Output Structure**
    - **Validates: Requirements 4.2**

- [x] 6. Implement Local Client Plan Executor





  - [x] 6.1 Create plan_executor.py with PlanExecutor class


    - Implement `__init__` with VisionService and status callback
    - Implement `execute_plan()` main orchestration method
    - Implement `execute_keyboard_step()` for keyboard actions (including hotkeys and repeats)
    - Implement `execute_visual_click()` for mouse clicks using ID map and box map
    - Implement single-pass architecture: execute blind steps first, then screenshot once
    - _Requirements: 1.3, 5.1, 5.2, 5.3_
  - [ ]* 6.2 Write property test for coordinate lookup correctness
    - **Property 4: Coordinate Lookup Correctness**
    - **Validates: Requirements 4.4**
  - [ ]* 6.3 Write unit tests for PlanExecutor
    - Test keyboard step execution
    - Test coordinate calculation from box map
    - _Requirements: 4.4_

- [x] 7. Update Local Client to handle two_model_workflow





  - [x] 7.1 Modify client.py to add two_model_workflow action handler


    - Import VisionService and PlanExecutor
    - Add handler for `action == 'two_model_workflow'`
    - Initialize services and execute plan
    - Send progress status updates throughout execution
    - _Requirements: 1.3, 1.4, 7.2, 7.3, 7.4, 7.5_

- [x] 8. Checkpoint - Ensure local client changes work






  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Integration and End-to-End Testing





  - [x] 9.1 Test full pipeline with sample command



    - Send "Make iron number plate set for bike, PB12W3998" from mobile app
    - Verify plan generation on backend
    - Verify screenshot capture and SoM detection on local client
    - Verify Vision Mapper identifies UI elements
    - Verify clicks execute at correct coordinates
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 10. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
