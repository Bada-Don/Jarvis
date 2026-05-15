# AWS Service Hub & Cloud Integration

> 269 nodes · cohesion 0.01

## Key Concepts

- **PlannerService** (72 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **Session** (72 connections) — `backend\session_manager.py`
- **SessionManager** (67 connections) — `backend\session_manager.py`
- **AWSServiceHub** (37 connections) — `Jarvis-aws-migration\backend\aws_service_hub.py`
- **SummarizationBuffer** (36 connections) — `backend\summarization_buffer.py`
- **server.py** (32 connections) — `backend\server.py`
- **StepResult** (32 connections) — `backend\step_result.py`
- **server.py** (16 connections) — `Jarvis-aws-migration\backend\server.py`
- **send_status_dual()** (14 connections) — `Jarvis-aws-migration\backend\server.py`
- **_react_loop()** (12 connections) — `backend\server.py`
- **send_command_dual()** (10 connections) — `Jarvis-aws-migration\backend\server.py`
- **TestDirectAutomationPlanGeneration** (9 connections) — `local_client\tests\test_direct_automation_integration.py`
- **process_instruction()** (8 connections) — `Jarvis-aws-migration\backend\server.py`
- **TestDirectModeExecution** (8 connections) — `local_client\tests\test_direct_automation_integration.py`
- **TestDirectAutomationActions** (8 connections) — `local_client\tests\test_direct_automation_integration.py`
- **TestFullDirectWorkflow** (8 connections) — `local_client\tests\test_direct_automation_integration.py`
- **_check_expected_observation()** (7 connections) — `backend\server.py`
- **Get or create a unique device ID for this backend instance.     Reads from cano** (7 connections) — `backend\server.py`
- **Send command via both WebSocket (for backward compatibility) and Firebase.** (7 connections) — `backend\server.py`
- **Send status update via both WebSocket and Firebase.          Args:         st** (7 connections) — `backend\server.py`
- **Lazily load ObservationModule only when step observations are processed.** (7 connections) — `backend\server.py`
- **Keep planner context bounded during repeated ReAct replanning.** (7 connections) — `backend\server.py`
- **Resolve planner placeholders and environment variables in a local path.** (7 connections) — `backend\server.py`
- **Extract quoted or simple bare paths following a Windows command keyword.** (7 connections) — `backend\server.py`
- **Extract likely output file paths from shell redirections.** (7 connections) — `backend\server.py`
- *... and 244 more nodes in this community*

## Relationships

- [[Application Launcher & Lifecycle]] (48 shared connections)
- [[Email & File System Utilities]] (46 shared connections)
- [[LLM Providers (Bedrock, LM Studio)]] (21 shared connections)
- [[Session Management & Web Browser]] (3 shared connections)
- [[AI Editor & LLM Engines]] (2 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\aws_service_hub.py`
- `Jarvis-aws-migration\backend\newPlanner_service.py`
- `Jarvis-aws-migration\backend\print_prompts.py`
- `Jarvis-aws-migration\backend\server.py`
- `Jarvis-aws-migration\backend\test_dynamodb_history.py`
- `Jarvis-aws-migration\backend\test_shell_command.py`
- `backend\print_prompts.py`
- `backend\server.py`
- `backend\session_manager.py`
- `backend\step_result.py`
- `backend\summarization_buffer.py`
- `backend\test_shell_command.py`
- `local_client\tests\test_direct_automation_integration.py`

## Audit Trail

- EXTRACTED: 631 (53%)
- INFERRED: 553 (47%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*