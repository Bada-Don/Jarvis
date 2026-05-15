# PlanExecutor

> God node · 202 connections · `local_client\plan_executor.py`

**Community:** [[Email & File System Utilities]]

## Connections by Relation

### calls
- [[execute_two_model_plan()]] `INFERRED`
- [[execute_plan_from_file()]] `INFERRED`
- [[execute_single_step()]] `INFERRED`
- [[execute_verify_task()]] `INFERRED`
- [[test_direct_mode_uses_uia()]] `INFERRED`
- [[test_direct_mode_window_activation()]] `INFERRED`
- [[test_direct_mode_window_activation_failure()]] `INFERRED`
- [[test_create_text_action()]] `INFERRED`
- [[test_set_dimensions_action()]] `INFERRED`
- [[test_set_dimensions_back_plate()]] `INFERRED`
- [[test_set_font_action()]] `INFERRED`
- [[test_apply_style_action()]] `INFERRED`
- [[test_move_object_action()]] `INFERRED`
- [[test_full_workflow_execution()]] `INFERRED`
- [[test_workflow_with_both_plate_sizes()]] `INFERRED`
- [[.setUp()]] `INFERRED`

### contains
- [[plan_executor.py]] `EXTRACTED`
- [[plan_executor.py]] `EXTRACTED`

### method
- [[._send_status()]] `EXTRACTED`
- [[._execute_vision_plan()]] `EXTRACTED`
- [[.__init__()]] `EXTRACTED`
- [[.execute_single_step()]] `EXTRACTED`
- [[._execute_keyboard_step()]] `EXTRACTED`
- [[._execute_direct_plan()]] `EXTRACTED`
- [[._execute_write_file_step()]] `EXTRACTED`
- [[._execute_read_file_step()]] `EXTRACTED`
- [[._resolve_placeholders()]] `EXTRACTED`
- [[.execute_plan()]] `EXTRACTED`
- [[._is_special_key()]] `EXTRACTED`
- [[._execute_open_file_step()]] `EXTRACTED`
- [[._execute_open_folder_step()]] `EXTRACTED`
- [[._execute_direct_step()]] `EXTRACTED`
- [[._perform_vision_pass()]] `EXTRACTED`
- [[._handle_app_launch()]] `EXTRACTED`
- [[._execute_visual_click()]] `EXTRACTED`
- [[._execute_save_file_step()]] `EXTRACTED`
- [[._execute_resolve_filename_step()]] `EXTRACTED`
- [[._execute_navigate_explorer_step()]] `EXTRACTED`

### rationale_for
- [[Executes execution plans from the Planner Model.          Features:     - Single]] `EXTRACTED`
- [[Main execution engine for JARVIS plans.     Handles sequential execution of plan]] `EXTRACTED`

### uses
- [[WindowManager]] `INFERRED`
- [[VisionService]] `INFERRED`
- [[DirectPathExecutor]] `INFERRED`
- [[FileEditor]] `INFERRED`
- [[FilenameResolver]] `INFERRED`
- [[AIEditorEngine]] `INFERRED`
- [[TextBasedClicker]] `INFERRED`
- [[GeminiProvider]] `INFERRED`
- [[OpenAIProvider]] `INFERRED`
- [[ExecutionResult]] `INFERRED`
- [[ClickResult]] `INFERRED`
- [[PathConfig]] `INFERRED`
- [[PathResolveResult]] `INFERRED`
- [[PathResolver]] `INFERRED`
- [[ResolveResult]] `INFERRED`
- [[CustomBrowser]] `INFERRED`
- [[BrowserUseAgent]] `INFERRED`
- [[PermissionService]] `INFERRED`
- [[FastTextClicker]] `INFERRED`
- [[ReadinessState]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*