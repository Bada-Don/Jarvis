# Application Launcher & Lifecycle

> 456 nodes · cohesion 0.01

## Key Concepts

- **FirebaseService** (127 connections) — `local_client\firebase_service.py`
- **ErrorHandler** (108 connections) — `local_client\error_handler.py`
- **ConfigurationError** (72 connections) — `local_client\error_handler.py`
- **SettingsAPI** (67 connections) — `local_client\settings_app.py`
- **FlexiSignManager** (60 connections) — `local_client\flexisign_manager.py`
- **ComponentError** (58 connections) — `local_client\error_handler.py`
- **NetworkError** (55 connections) — `local_client\error_handler.py`
- **PairingManager** (46 connections) — `local_client\pairing_manager.py`
- **PackagingService** (42 connections) — `local_client\packaging_service.py`
- **PromptManager** (39 connections) — `local_client\prompt_manager.py`
- **PairingError** (36 connections) — `local_client\error_handler.py`
- **ApplicationLauncher** (34 connections) — `Jarvis-aws-migration\application_launcher.py`
- **ValidationService** (31 connections) — `local_client\validation_service.py`
- **RuntimeError** (28 connections) — `local_client\error_handler.py`
- **ObservationModule** (24 connections) — `local_client\observation_module.py`
- **ApplicationLauncher** (17 connections) — `application_launcher.py`
- **client.py** (14 connections) — `local_client\client.py`
- **client.py** (13 connections) — `Jarvis-aws-migration\local_client\client.py`
- **error_handler.py** (13 connections) — `Jarvis-aws-migration\local_client\error_handler.py`
- **error_handler.py** (13 connections) — `local_client\error_handler.py`
- **execute_two_model_plan()** (12 connections) — `local_client\client.py`
- **JARVIS Local Client Connects to the backend server and executes automation comm** (12 connections) — `local_client\client.py`
- **Handle commands received from AWS polling.** (12 connections) — `Jarvis-aws-migration\local_client\client.py`
- **Get or create a unique device ID for this client instance.     Reads from canoni** (12 connections) — `Jarvis-aws-migration\local_client\client.py`
- **Handle commands received from Firebase.     Route raw text commands through the** (12 connections) — `Jarvis-aws-migration\local_client\client.py`
- *... and 431 more nodes in this community*

## Relationships

- [[AI Editor & LLM Engines]] (57 shared connections)
- [[AWS Service Hub & Cloud Integration]] (48 shared connections)
- [[Email & File System Utilities]] (36 shared connections)
- [[Configuration & Settings Management]] (33 shared connections)
- [[System Tray & App Entry Point]] (16 shared connections)
- [[FlexiSIGN Window Utilities]] (15 shared connections)
- [[Firebase Data Viewer]] (9 shared connections)
- [[LLM Providers (Bedrock, LM Studio)]] (5 shared connections)
- [[Debug Logging & Pipeline Monitoring]] (3 shared connections)
- [[Session Management & Web Browser]] (3 shared connections)
- [[Window Management & Activation]] (2 shared connections)
- [[Settings Validation Service]] (2 shared connections)

## Source Files

- `Jarvis-aws-migration\application_launcher.py`
- `Jarvis-aws-migration\local_client\client.py`
- `Jarvis-aws-migration\local_client\error_handler.py`
- `Jarvis-aws-migration\local_client\firebase_service.py`
- `Jarvis-aws-migration\local_client\fix_settings_cache.py`
- `Jarvis-aws-migration\local_client\packaging_service.py`
- `Jarvis-aws-migration\local_client\pairing_manager.py`
- `Jarvis-aws-migration\local_client\permission_service.py`
- `Jarvis-aws-migration\local_client\prompt_manager.py`
- `Jarvis-aws-migration\local_client\settings_app.py`
- `Jarvis-aws-migration\local_client\setup_wizard.py`
- `Jarvis-aws-migration\local_client\test_config_profile.py`
- `Jarvis-aws-migration\local_client\test_configuration_api.py`
- `Jarvis-aws-migration\local_client\test_full_settings_flow.py`
- `Jarvis-aws-migration\local_client\test_packaging_service.py`
- `Jarvis-aws-migration\local_client\test_pywebview_connection.py`
- `Jarvis-aws-migration\local_client\test_pywebview_simulation.py`
- `Jarvis-aws-migration\local_client\test_reset_functionality.py`
- `Jarvis-aws-migration\local_client\test_settings_api.py`
- `Jarvis-aws-migration\local_client\test_settings_prompts.py`

## Audit Trail

- EXTRACTED: 1221 (47%)
- INFERRED: 1352 (53%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*