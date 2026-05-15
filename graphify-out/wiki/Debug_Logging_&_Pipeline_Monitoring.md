# Debug Logging & Pipeline Monitoring

> 46 nodes · cohesion 0.06

## Key Concepts

- **DebugLogger** (18 connections) — `local_client\debug_logger.py`
- **get_debug_logger()** (11 connections) — `local_client\debug_logger.py`
- **._log()** (9 connections) — `local_client\debug_logger.py`
- **.capture_screenshot()** (7 connections) — `local_client\vision_service.py`
- **create_new_session()** (6 connections) — `local_client\debug_logger.py`
- **.verify_task_completion()** (6 connections) — `local_client\vision_service.py`
- **._save_session_info()** (5 connections) — `local_client\debug_logger.py`
- **.map_targets_to_ids()** (5 connections) — `local_client\vision_service.py`
- **debug_logger.py** (4 connections) — `Jarvis-aws-migration\local_client\debug_logger.py`
- **.log_verification_result()** (4 connections) — `local_client\debug_logger.py`
- **.complete()** (4 connections) — `local_client\debug_logger.py`
- **.upload_to_s3()** (4 connections) — `Jarvis-aws-migration\local_client\vision_service.py`
- **debug_logger.py** (4 connections) — `local_client\debug_logger.py`
- **.set_user_command()** (3 connections) — `local_client\debug_logger.py`
- **.log_planner_output()** (3 connections) — `local_client\debug_logger.py`
- **.log_screenshot()** (3 connections) — `local_client\debug_logger.py`
- **.log_annotated_image()** (3 connections) — `local_client\debug_logger.py`
- **.log_box_map()** (3 connections) — `local_client\debug_logger.py`
- **.log_vision_mapper_output()** (3 connections) — `local_client\debug_logger.py`
- **.log_step_execution()** (3 connections) — `local_client\debug_logger.py`
- **.log_error()** (3 connections) — `local_client\debug_logger.py`
- **._resize_screenshot()** (3 connections) — `local_client\vision_service.py`
- **.__init__()** (2 connections) — `local_client\debug_logger.py`
- **Debug Logger for Two-Model Pipeline  Saves all model outputs, screenshots, and** (2 connections) — `local_client\debug_logger.py`
- **Logs all pipeline data to a timestamped debug folder.          Creates folder** (1 connections) — `local_client\debug_logger.py`
- *... and 21 more nodes in this community*

## Relationships

- [[Email & File System Utilities]] (6 shared connections)
- [[AI Editor & LLM Engines]] (5 shared connections)
- [[Application Launcher & Lifecycle]] (3 shared connections)

## Source Files

- `Jarvis-aws-migration\local_client\debug_logger.py`
- `Jarvis-aws-migration\local_client\vision_service.py`
- `local_client\debug_logger.py`
- `local_client\vision_service.py`

## Audit Trail

- EXTRACTED: 126 (90%)
- INFERRED: 14 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*