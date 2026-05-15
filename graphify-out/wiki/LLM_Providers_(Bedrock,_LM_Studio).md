# LLM Providers (Bedrock, LM Studio)

> 136 nodes · cohesion 0.02

## Key Concepts

- **LocalProvider** (55 connections) — `backend\llm_provider.py`
- **AWSBedrockProvider** (27 connections) — `Jarvis-aws-migration\backend\llm_provider.py`
- **PlannerService** (18 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **SkillManager** (16 connections) — `backend\newPlanner_service.py`
- **LLMProvider** (9 connections) — `Jarvis-aws-migration\backend\llm_provider.py`
- **.generate_plan()** (9 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **TestLLMProviders** (8 connections) — `Jarvis-aws-migration\backend\test_providers.py`
- **safe_json_loads()** (8 connections) — `local_client\json_utils.py`
- **.generate_next_steps()** (7 connections) — `backend\newPlanner_service.py`
- **.init_provider()** (7 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **.generate_plan()** (7 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **llm_provider.py** (6 connections) — `backend\llm_provider.py`
- **.generate_content()** (6 connections) — `backend\llm_provider.py`
- **.init_provider()** (6 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **.build_prompt()** (6 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **Planner Service for Multi-Agent Pipeline  This module implements a Router -> Pla** (6 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **Planner Service for Two-Model Pipeline  This module provides the PlannerService** (6 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **test_local_provider.py** (6 connections) — `backend\test_local_provider.py`
- **llm_provider.py** (6 connections) — `Jarvis-aws-migration\backend\llm_provider.py`
- **test_providers.py** (6 connections) — `Jarvis-aws-migration\backend\test_providers.py`
- **.route_command()** (5 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **._resolve_placeholders()** (5 connections) — `Jarvis-aws-migration\backend\newPlanner_service.py`
- **Service class for generating execution plans using an LLM.          Supports two** (5 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **Initialize the PlannerService.                  Args:             api_key: Optio** (5 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- **Initialize the LLM provider based on configuration.** (5 connections) — `Jarvis-aws-migration\backend\planner_service.py`
- *... and 111 more nodes in this community*

## Relationships

- [[AI Editor & LLM Engines]] (106 shared connections)
- [[AWS Service Hub & Cloud Integration]] (21 shared connections)
- [[Application Launcher & Lifecycle]] (5 shared connections)
- [[Email & File System Utilities]] (1 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\llm_provider.py`
- `Jarvis-aws-migration\backend\newPlanner_service.py`
- `Jarvis-aws-migration\backend\planner_service.py`
- `Jarvis-aws-migration\backend\test_aws_integration.py`
- `Jarvis-aws-migration\backend\test_providers.py`
- `Jarvis-aws-migration\backend\test_resolution.py`
- `Jarvis-aws-migration\local_client\json_utils.py`
- `backend\llm_provider.py`
- `backend\newPlanner_service.py`
- `backend\planner_service.py`
- `backend\test_local_provider.py`
- `backend\test_providers.py`
- `local_client\json_utils.py`

## Audit Trail

- EXTRACTED: 341 (58%)
- INFERRED: 242 (42%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*