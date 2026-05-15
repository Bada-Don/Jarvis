# Email & File System Utilities

> 185 nodes · cohesion 0.02

## Key Concepts

- **PlanExecutor** (202 connections) — `local_client\plan_executor.py`
- **._send_status()** (38 connections) — `local_client\plan_executor.py`
- **._execute_vision_plan()** (37 connections) — `local_client\plan_executor.py`
- **test_direct_automation_integration.py** (17 connections) — `Jarvis-aws-migration\local_client\tests\test_direct_automation_integration.py`
- **test_direct_automation_integration.py** (17 connections) — `local_client\tests\test_direct_automation_integration.py`
- **.execute_single_step()** (13 connections) — `local_client\plan_executor.py`
- **execute_plan_from_file()** (12 connections) — `local_client\test_plan.py`
- **._execute_keyboard_step()** (11 connections) — `local_client\plan_executor.py`
- **._execute_direct_plan()** (9 connections) — `local_client\plan_executor.py`
- **._execute_write_file_step()** (9 connections) — `local_client\plan_executor.py`
- **filter_boxes()** (9 connections) — `local_client\vision_service.py`
- **TestFilterBoxes** (9 connections) — `local_client\tests\test_integration_local_client.py`
- **file_operations.py** (8 connections) — `backend\file_operations.py`
- **file_operations.py** (8 connections) — `Jarvis-aws-migration\backend\file_operations.py`
- **._execute_read_file_step()** (8 connections) — `local_client\plan_executor.py`
- **get_click_coordinates()** (8 connections) — `local_client\plan_executor.py`
- **draw_annotations()** (8 connections) — `local_client\vision_service.py`
- **.run_som_detection()** (8 connections) — `local_client\vision_service.py`
- **test_integration_local_client.py** (8 connections) — `Jarvis-aws-migration\local_client\tests\test_integration_local_client.py`
- **TestDrawAnnotations** (8 connections) — `local_client\tests\test_integration_local_client.py`
- **TestCoordinateLookup** (8 connections) — `local_client\tests\test_integration_local_client.py`
- **TestPlanExecutorKeyboard** (8 connections) — `local_client\tests\test_integration_local_client.py`
- **TestVisionServiceIntegration** (8 connections) — `local_client\tests\test_integration_local_client.py`
- **._resolve_placeholders()** (8 connections) — `local_client\plan_executor.py`
- **test_integration_local_client.py** (8 connections) — `local_client\tests\test_integration_local_client.py`
- *... and 160 more nodes in this community*

## Relationships

- [[AI Editor & LLM Engines]] (171 shared connections)
- [[AWS Service Hub & Cloud Integration]] (46 shared connections)
- [[Application Launcher & Lifecycle]] (36 shared connections)
- [[Debug Logging & Pipeline Monitoring]] (6 shared connections)
- [[Window Management & Activation]] (4 shared connections)
- [[FlexiSIGN Automation Actions]] (1 shared connections)
- [[LLM Providers (Bedrock, LM Studio)]] (1 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\email_service.py`
- `Jarvis-aws-migration\backend\file_operations.py`
- `Jarvis-aws-migration\local_client\plan_executor.py`
- `Jarvis-aws-migration\local_client\test_agent.py`
- `Jarvis-aws-migration\local_client\test_plan.py`
- `Jarvis-aws-migration\local_client\tests\test_direct_automation_integration.py`
- `Jarvis-aws-migration\local_client\tests\test_integration_local_client.py`
- `Jarvis-aws-migration\local_client\vision_service.py`
- `backend\email_service.py`
- `backend\file_operations.py`
- `local_client\plan_executor.py`
- `local_client\test_plan.py`
- `local_client\tests\test_direct_automation_integration.py`
- `local_client\tests\test_integration_local_client.py`
- `local_client\vision_service.py`

## Audit Trail

- EXTRACTED: 715 (70%)
- INFERRED: 312 (30%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*