# Foreground Window Management

> 29 nodes · cohesion 0.11

## Key Concepts

- **WindowManager** (16 connections) — `local_client\window_manager.py`
- **.activate_window()** (8 connections) — `local_client\window_manager.py`
- **get_window_manager()** (6 connections) — `local_client\window_manager.py`
- **.log()** (5 connections) — `local_client\window_manager.py`
- **.wait_for_window()** (5 connections) — `local_client\window_manager.py`
- **.ensure_foreground_before_input()** (5 connections) — `local_client\window_manager.py`
- **.find_window_for_app()** (4 connections) — `local_client\window_manager.py`
- **.is_window_foreground()** (4 connections) — `local_client\window_manager.py`
- **._force_foreground()** (4 connections) — `local_client\window_manager.py`
- **.wait_and_activate()** (4 connections) — `local_client\window_manager.py`
- **window_manager.py** (3 connections) — `Jarvis-aws-migration\local_client\window_manager.py`
- **.find_windows_by_title()** (3 connections) — `local_client\window_manager.py`
- **.is_window_minimized()** (3 connections) — `local_client\window_manager.py`
- **window_manager.py** (3 connections) — `local_client\window_manager.py`
- **.get_foreground_window_title()** (2 connections) — `local_client\window_manager.py`
- **Window Manager for JARVIS Handles window detection, activation, and focus manag** (2 connections) — `local_client\window_manager.py`
- **.__init__()** (1 connections) — `local_client\window_manager.py`
- **Manages window detection and activation for automation tasks.     Ensures targe** (1 connections) — `local_client\window_manager.py`
- **Find all windows matching any of the given title patterns.                  Re** (1 connections) — `local_client\window_manager.py`
- **Find a window for a known application.                  Args:             app** (1 connections) — `local_client\window_manager.py`
- **Check if a window is minimized.** (1 connections) — `local_client\window_manager.py`
- **Check if a window is the foreground window.** (1 connections) — `local_client\window_manager.py`
- **Bring a window to the foreground and ensure it's active.         Uses multiple** (1 connections) — `local_client\window_manager.py`
- **Force a window to foreground using thread attachment trick.         This bypass** (1 connections) — `local_client\window_manager.py`
- **Wait for a window to appear for a given application.                  Args:** (1 connections) — `local_client\window_manager.py`
- *... and 4 more nodes in this community*

## Relationships

- [[Window Management & Activation]] (1 shared connections)
- [[AI Editor & LLM Engines]] (1 shared connections)

## Source Files

- `Jarvis-aws-migration\local_client\window_manager.py`
- `local_client\window_manager.py`

## Audit Trail

- EXTRACTED: 88 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*