# AI Editor & LLM Engines

> 256 nodes · cohesion 0.08

## Key Concepts

- **VisionService** (170 connections) — `local_client\vision_service.py`
- **DirectPathExecutor** (165 connections) — `local_client\direct_path_executor.py`
- **FileEditor** (164 connections) — `Jarvis-aws-migration\backend\file_editor.py`
- **FilenameResolver** (159 connections) — `local_client\filename_resolver.py`
- **AIEditorEngine** (156 connections) — `Jarvis-aws-migration\backend\ai_editor_engine.py`
- **TextBasedClicker** (154 connections) — `local_client\text_clicker.py`
- **GeminiProvider** (151 connections) — `Jarvis-aws-migration\backend\llm_provider.py`
- **OpenAIProvider** (151 connections) — `Jarvis-aws-migration\backend\llm_provider.py`
- **ExecutionResult** (151 connections) — `local_client\direct_path_executor.py`
- **ClickResult** (150 connections) — `local_client\text_clicker.py`
- **PathConfig** (149 connections) — `local_client\path_config.py`
- **PathResolveResult** (149 connections) — `local_client\path_resolver.py`
- **PathResolver** (149 connections) — `local_client\path_resolver.py`
- **ResolveResult** (147 connections) — `local_client\filename_resolver.py`
- **CustomBrowser** (134 connections) — `web-automation-module\src\browser\custom_browser.py`
- **BrowserUseAgent** (128 connections) — `web-automation-module\src\agent\browser_use\browser_use_agent.py`
- **PermissionService** (125 connections) — `local_client\permission_service.py`
- **FastTextClicker** (100 connections) — `Jarvis-aws-migration\backend\text_click_fast.py`
- **ReadinessState** (94 connections) — `local_client\readiness_detector.py`
- **DesktopAppReadinessDetector** (66 connections) — `local_client\readiness_detector.py`
- **BrowserReadinessDetector** (65 connections) — `local_client\readiness_detector.py`
- **ReadinessResult** (62 connections) — `local_client\readiness_detector.py`
- **Check if value is a hotkey combination vs regular text with '+'.** (25 connections) — `Jarvis-aws-migration\local_client\plan_executor.py`
- **Check if value is a hotkey combination vs regular text with '+'.** (24 connections) — `local_client\plan_executor.py`
- **Execute a hotkey combination like 'ctrl+n' or 'win+r'.** (24 connections) — `local_client\plan_executor.py`
- *... and 231 more nodes in this community*

## Relationships

- [[Window Management & Activation]] (190 shared connections)
- [[Email & File System Utilities]] (171 shared connections)
- [[LLM Providers (Bedrock, LM Studio)]] (106 shared connections)
- [[Session Management & Web Browser]] (76 shared connections)
- [[Application Launcher & Lifecycle]] (57 shared connections)
- [[Text Processing & Similarity]] (13 shared connections)
- [[Filename Fuzzy Resolver]] (9 shared connections)
- [[Fast Text-Based Clicker]] (6 shared connections)
- [[Component Community 53]] (6 shared connections)
- [[Component Community 52]] (5 shared connections)
- [[Component Community 58]] (5 shared connections)
- [[Debug Logging & Pipeline Monitoring]] (5 shared connections)

## Source Files

- `Jarvis-aws-migration\backend\ai_editor_engine.py`
- `Jarvis-aws-migration\backend\file_editor.py`
- `Jarvis-aws-migration\backend\llm_provider.py`
- `Jarvis-aws-migration\backend\text_click_fast.py`
- `Jarvis-aws-migration\local_client\path_resolver.py`
- `Jarvis-aws-migration\local_client\plan_executor.py`
- `Jarvis-aws-migration\local_client\readiness_detector.py`
- `Jarvis-aws-migration\local_client\vision_service.py`
- `Jarvis-aws-migration\web-automation-module\src\agent\browser_use\browser_use_agent.py`
- `backend\file_editor.py`
- `backend\llm_provider.py`
- `backend\newPlanner_service.py`
- `backend\text_click_fast.py`
- `local_client\direct_path_executor.py`
- `local_client\filename_resolver.py`
- `local_client\path_config.py`
- `local_client\path_resolver.py`
- `local_client\permission_service.py`
- `local_client\plan_executor.py`
- `local_client\readiness_detector.py`

## Audit Trail

- EXTRACTED: 458 (8%)
- INFERRED: 5238 (92%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*