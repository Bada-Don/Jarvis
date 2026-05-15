# VisionService

> God node · 170 connections · `local_client\vision_service.py`

**Community:** [[AI Editor & LLM Engines]]

## Connections by Relation

### calls
- [[execute_two_model_plan()]] `INFERRED`
- [[execute_plan_from_file()]] `INFERRED`
- [[execute_single_step()]] `INFERRED`
- [[execute_verify_task()]] `INFERRED`
- [[.test_vision_service_initialization()]] `INFERRED`
- [[.test_vision_service_missing_api_key()]] `INFERRED`
- [[.test_capture_screenshot()]] `INFERRED`

### contains
- [[vision_service.py]] `EXTRACTED`
- [[vision_service.py]] `EXTRACTED`

### method
- [[.run_som_detection()]] `EXTRACTED`
- [[.capture_screenshot()]] `EXTRACTED`
- [[.verify_task_completion()]] `EXTRACTED`
- [[.map_targets_to_ids()]] `EXTRACTED`
- [[.upload_to_s3()]] `EXTRACTED`
- [[.__init__()]] `EXTRACTED`
- [[._resize_screenshot()]] `EXTRACTED`
- [[.set_device_id()]] `EXTRACTED`

### rationale_for
- [[Vision Service for the Two-Model Pipeline.     Handles screenshot capture, SoM d]] `EXTRACTED`
- [[Vision Service for the Two-Model Pipeline.     Handles screenshot capture, SoM]] `EXTRACTED`

### uses
- [[PlanExecutor]] `INFERRED`
- [[Check if value is a hotkey combination vs regular text with '+'.]] `INFERRED`
- [[Check if value is a hotkey combination vs regular text with '+'.]] `INFERRED`
- [[Execute a hotkey combination like 'ctrl+n' or 'win+r'.]] `INFERRED`
- [[Plan Executor for Two-Model Pipeline Executes execution plans using keyboard/mo]] `INFERRED`
- [[Executes execution plans from the Planner Model.          Features:     - Single]] `INFERRED`
- [[Initialize PlanExecutor.                  Args:             vision_service: Visi]] `INFERRED`
- [[Send status update via callback.]] `INFERRED`
- [[Play audio feedback for execution events.                  Args:             sou]] `INFERRED`
- [[Execute an execution plan from the Planner Model.         Routes to direct or v]] `INFERRED`
- [[Execute an execution plan from the Planner Model.         Routes to direct or vi]] `INFERRED`
- [[Execute plan using UIA (no vision/screenshots).                  Args:]] `INFERRED`
- [[Execute plan using vision-based pipeline (existing logic).                  Args]] `INFERRED`
- [[Execute a single direct automation step.         Dispatches to UIA actions based]] `INFERRED`
- [[Collect all unique visual target names from the sequence.]] `INFERRED`
- [[Collect visual targets from current_index onwards.         Used for adaptive re-]] `INFERRED`
- [[Perform single-pass vision: screenshot, SoM detection, and target mapping.]] `INFERRED`
- [[Determine if this step is likely to launch an application.]] `INFERRED`
- [[Try to determine what app is being launched based on recent typed text.]] `INFERRED`
- [[Execute a keyboard action step with proper timing and window management.]] `INFERRED`

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*