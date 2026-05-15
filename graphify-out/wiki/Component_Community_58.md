# Component Community 58

> 8 nodes · cohesion 0.25

## Key Concepts

- **.wait_for_page_load()** (6 connections) — `local_client\readiness_detector.py`
- **._find_browser_window()** (3 connections) — `local_client\readiness_detector.py`
- **._get_settle_time()** (3 connections) — `local_client\readiness_detector.py`
- **._wait_for_window_visible()** (3 connections) — `local_client\readiness_detector.py`
- **Wait for browser page to finish loading.                  Strategy:         1** (1 connections) — `local_client\readiness_detector.py`
- **Find browser window handle.** (1 connections) — `local_client\readiness_detector.py`
- **Determine appropriate settle time based on page type.         Heavy JavaScript** (1 connections) — `local_client\readiness_detector.py`
- **Wait for window to be visible and enabled.** (1 connections) — `local_client\readiness_detector.py`

## Relationships

- [[AI Editor & LLM Engines]] (5 shared connections)

## Source Files

- `local_client\readiness_detector.py`

## Audit Trail

- EXTRACTED: 19 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*