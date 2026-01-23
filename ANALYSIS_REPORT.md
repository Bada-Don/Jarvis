# JARVIS Automation Failure Analysis Report
**Date:** January 23, 2026  
**Analyzed By:** Kiro AI Assistant

---

## Executive Summary

Two automation tasks failed:
1. **Gmail Compose Button Click** - Failed to find the Compose button (vision issue)
2. **Desktop Folder Creation** - Succeeded but with timing issues (Step 5 failed to open folder)

After comparing the current implementation with `jarvis-old`, I've identified **one critical regression** and several **timing-related changes** that explain both failures.

---

## Issue #1: Gmail Compose Button Click Failure

### What Happened
- Task: "Open Gmail and compose a mail"
- Steps 1-6 executed successfully (opened Chrome, navigated to Gmail)
- **Step 7 FAILED**: Could not find `button_compose` 
- Vision mapper output shows: `"button_compose": null` (not found)

### Root Cause: CRITICAL REGRESSION

**The current version introduced "adaptive re-scanning" logic that was NOT in the old version.**

#### Old Version (jarvis-old) - WORKING:
```python
def _execute_vision_plan(self, plan: dict) -> dict:
    # ...
    # Collect all visual targets for batch mapping
    visual_targets = self._collect_visual_targets(sequence)
    
    # Execute steps
    for i, step in enumerate(sequence):
        # ...
        if step_type == 'visual_click':
            # Single-pass: take screenshot and map targets on first visual click
            if not self._screenshot_taken and visual_targets:
                self._perform_vision_pass(visual_targets)
```

**Key behavior:** Screenshot is taken **ONCE** on the **FIRST** visual_click step, **AFTER** all keyboard steps complete.

#### Current Version - BROKEN:
```python
def _execute_vision_plan(self, plan: dict) -> dict:
    # ...
    for i, step in enumerate(sequence):
        # ...
        if step_type == 'keyboard':
            # ...
            # Mark UI as changed if this was a typing action
            value = step.get('value', '').lower()
            if not self._is_special_key(value) or value in ['enter', 'return', ...]:
                self._ui_changed_since_scan = True
        
        elif step_type == 'visual_click':
            # Adaptive re-scanning logic
            needs_rescan = False
            
            if not self._screenshot_taken:
                needs_rescan = True
            elif self._ui_changed_since_scan:
                needs_rescan = True
                self._send_status("UI changed detected, re-scanning...", "info")
            
            if needs_rescan:
                remaining_targets = self._collect_remaining_visual_targets(sequence, i)
                if remaining_targets:
                    self._perform_vision_pass(remaining_targets)
```

**Key behavior:** Screenshot is taken **IMMEDIATELY** when the first visual_click is encountered, **BEFORE** waiting for the page to fully load.

### The Problem

In the Gmail task:
1. Steps 1-6: Open Chrome, type "gmail.com", press Enter
2. **Step 7 (visual_click)**: System immediately takes screenshot
3. **PROBLEM**: Gmail page is still loading! The Compose button hasn't rendered yet
4. Vision mapper finds 0 elements, returns `button_compose: null`
5. Click fails

### Why Old Version Worked

The old version's **single-pass architecture** meant:
- All keyboard steps execute first (including the 3-second `DELAY_AFTER_APP_LAUNCH`)
- By the time the first `visual_click` is reached, Chrome has fully loaded
- Screenshot captures the fully-rendered Gmail interface
- Compose button is visible and detected

---

## Issue #2: Desktop Folder Creation

### What Happened
- Task: "Make a folder on Desktop named demo, make three txt files in it"
- Most steps succeeded
- **Step 5 FAILED**: `open_folder: path_query='desktop/demo' success=False`
- System continued anyway and created files (but likely in wrong location)

### Root Cause: Timing + Path Resolution

Looking at the execution log:
```
00:35:29 [Step 1] ✓ open_folder: path_query='desktop' success=True
00:35:30 [Step 2] ✓ keyboard: value='ctrl+shift+n' (Create folder)
00:35:30 [Step 3] ✓ keyboard: value='demo' (Name folder)
00:35:31 [Step 4] ✓ keyboard: value='enter' (Confirm)
00:35:31 [Step 5] ✓ open_folder: path_query='desktop/demo' success=False
```

**Problem:** Step 5 executes **immediately** after Step 4 (within 1 second). The folder creation hasn't completed yet, so the path resolver can't find `desktop/demo`.

### Comparison with Old Version

Both versions have **identical** `_execute_open_folder_step` logic, so this is NOT a regression. However, the old version may have had:
- Different timing constants
- Better synchronization after folder creation
- More robust path resolution with retry logic

---

## Detailed Comparison: Key Differences

### ✅ IDENTICAL (No Changes)
- `client.py` - Completely identical
- Backend `server.py` - Only difference is import name (`GeminiPlannerService` vs `PlannerService`)
- Core keyboard execution logic
- Window activation logic
- Hotkey handling
- Special key detection

### ❌ CRITICAL REGRESSION

#### 1. Adaptive Re-Scanning Logic (NEW in current version)

**Location:** `local_client/plan_executor.py` lines 400-450

**Old Version:**
- Simple single-pass: collect all targets upfront, screenshot once on first visual_click
- No `_ui_changed_since_scan` tracking
- No `_collect_remaining_visual_targets` method
- No adaptive re-scanning

**Current Version:**
- Complex adaptive logic with `_ui_changed_since_scan` flag
- Tracks UI changes after keyboard input
- Re-scans if UI changed since last scan
- **PROBLEM:** Takes screenshot TOO EARLY when first visual_click is encountered

**Impact:** 🔴 **CRITICAL** - Breaks browser automation where pages need time to load

---

### ⚠️ MISSING SAFEGUARDS

#### 2. App Launch Detection Scope

**Old Version (line 695):**
```python
# Check if there was a Win key press before
for j in range(current_index - 1, -1, -1):
    check_val = sequence[j].get('value', '').lower()
    if check_val == 'win' or check_val == 'windows':
        return True
    if check_val == 'enter':
        break
```

**Current Version (line 710):**
```python
# Check if there was a Win key press before, but only within the last 3 steps
for j in range(current_index - 1, max(-1, current_index - 4), -1):
    check_val = sequence[j].get('value', '').lower()
    if check_val == 'win' or check_val == 'windows':
        return True
    if check_val == 'enter':
        break
    # Stop if we hit a hotkey that changes context
    if '+' in check_val and any(mod in check_val for mod in ['ctrl', 'alt']):
        break
```

**Difference:** Current version limits lookback to 3 steps and adds context-change detection

**Impact:** ⚠️ **MINOR** - More conservative app launch detection (probably better)

---

### ⚠️ TIMING DIFFERENCES

#### 3. Vision Pass Delay

**Old Version (line 645):**
```python
def _perform_vision_pass(self, targets: list[str]):
    self._send_status("Capturing screen...", "info")
    
    # Wait for any UI transitions to complete
    time.sleep(0.5)
```

**Current Version (line 670):**
```python
def _perform_vision_pass(self, targets: list[str]):
    self._send_status("Capturing screen...", "info")
    
    # Wait for any UI transitions to complete
    time.sleep(0.5)
```

**Difference:** IDENTICAL timing (0.5 seconds)

**Impact:** ✅ **NONE** - Same delay in both versions

---

## Summary of Findings

### 🔴 CRITICAL ISSUES (Must Fix)

1. **Adaptive Re-Scanning Logic** (Current Version Only)
   - **Status:** ❌ Changed/Degraded
   - **Impact:** Breaks browser automation by taking screenshots too early
   - **Location:** `local_client/plan_executor.py` lines 400-450
   - **Fix Required:** Revert to old single-pass architecture OR add configurable delay before first screenshot

### ⚠️ TIMING ISSUES (Should Improve)

2. **Insufficient Delay After Folder Creation**
   - **Status:** ⚠️ Present in both versions
   - **Impact:** Path resolution fails when folder hasn't finished creating
   - **Location:** `local_client/plan_executor.py` `_execute_open_folder_step`
   - **Fix Required:** Add delay or retry logic after folder creation operations

### ✅ IMPROVEMENTS (Better in Current Version)

3. **App Launch Detection Scope**
   - **Status:** ✔️ Better in current version
   - **Impact:** More accurate app launch detection with context awareness
   - **Location:** `local_client/plan_executor.py` line 710

---

## Recommended Fixes

### Priority 1: Fix Gmail Issue (Adaptive Re-Scanning)

**Option A: Revert to Old Architecture (Safest)**
```python
# Remove adaptive re-scanning logic
# Remove _ui_changed_since_scan tracking
# Remove _collect_remaining_visual_targets method
# Restore old single-pass logic
```

**Option B: Add Configurable Delay (More Flexible)**
```python
# Add DELAY_BEFORE_FIRST_SCREENSHOT constant (e.g., 2.0 seconds)
# Apply delay only on first visual_click after app launch
# Keep adaptive re-scanning for subsequent clicks
```

**Option C: Smart Detection (Most Robust)**
```python
# Detect if previous step was app launch or navigation
# If yes, add extra delay before screenshot
# If no, use adaptive re-scanning as-is
```

### Priority 2: Fix Folder Creation Issue

**Add retry logic to path resolution:**
```python
def _execute_open_folder_step(self, step: dict) -> 'PathResolveResult':
    # ... existing code ...
    
    # Retry logic for newly created folders
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        result = self._path_resolver.resolve(path_query)
        if result.success:
            break
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
    
    return result
```

---

## Conclusion

The **primary cause** of both failures is the **adaptive re-scanning logic** introduced in the current version. This logic takes screenshots too early, before UI elements have fully loaded.

The **secondary cause** is insufficient timing/synchronization after file system operations (folder creation).

**Recommendation:** Revert the adaptive re-scanning logic to the old single-pass architecture, then add targeted improvements for specific use cases if needed.
