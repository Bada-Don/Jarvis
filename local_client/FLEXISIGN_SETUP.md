# FlexiSign Pro Automation - Complete Setup Guide

## Overview

The new FlexiSign automation system ensures that FlexiSign Pro **never runs in demo/restricted mode**. It intelligently manages the loader/patcher and main application to guarantee proper operation every time.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FlexiSign Manager                         │
│  (Intelligent automation with fail-safe mechanisms)         │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Loader Check │   │ Window Check │   │ Process Kill │
│  & Startup   │   │  & Cleanup   │   │  (Failsafe)  │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Key Features

### 1. **Loader/Patcher Priority**
- Always checks if loader/patcher is running FIRST
- Starts loader/patcher if not running
- Handles startup modal automatically

### 2. **Demo Mode Detection**
- Detects if FlexiSign is running without loader/patcher
- Automatically closes demo mode windows
- Restarts FlexiSign properly with loader active

### 3. **Fail-Safe Mechanisms**
- Graceful window closing (WM_CLOSE)
- Force kill if graceful close fails
- Timeout protection on all operations
- Detailed logging for troubleshooting

### 4. **Configuration-Driven**
- All paths and settings in `flexisign_config.json`
- No code changes needed for different setups
- Easy to update for version changes

## Installation

### Step 1: Verify Files

Ensure these files exist in `local_client/`:
```
local_client/
├── client.py                    # Main client (updated)
├── flexisign_manager.py         # New manager class
├── flexisign_config.json        # Configuration file
└── FLEXISIGN_SETUP.md          # This file
```

### Step 2: Configure Settings

Edit `flexisign_config.json`:

```json
{
  "loader_patcher": {
    "process_name": "YOUR_LOADER_PROCESS_NAME",
    "exe_path": "C:\\Path\\To\\Loader.exe",
    "startup_modal": {
      "enabled": true,
      "title": "Modal Title",
      "button": "OK",
      "timeout": 15
    }
  },
  "flexisign_pro": {
    "process_names": ["FlexiSIGN", "flexisign.exe"],
    "exe_path": "C:\\Path\\To\\FlexiSign.exe",
    "window_titles": ["FlexiSIGN-PRO", "FlexiSIGN"]
  }
}
```

### Step 3: Find Your Process Names

Run this command to see all running processes:
```bash
python -c "import psutil; [print(p.name()) for p in psutil.process_iter()]"
```

Or use the test script:
```bash
python test_modal.py
```

### Step 4: Test the Manager

Test standalone (without server):
```bash
python flexisign_manager.py
```

Expected output:
```
[12:34:56] ℹ️ ============================================================
[12:34:56] ℹ️ Starting FlexiSign Pro automation...
[12:34:56] ℹ️ ============================================================
[12:34:56] ⚠️ Loader/patcher is NOT running - starting it now
[12:34:57] ℹ️ Starting loader/patcher...
[12:35:00] ℹ️ Waiting for modal: 'FlexiSIGN' (timeout: 15s)
[12:35:02] ✅ Modal detected: 'FlexiSIGN'
[12:35:03] ✅ Modal closed successfully
[12:35:03] ✅ Loader/patcher started successfully
[12:35:03] ℹ️ FlexiSign Pro is not running - starting it now
[12:35:04] ℹ️ Starting FlexiSign Pro...
[12:35:12] ✅ FlexiSign Pro started successfully
[12:35:12] ℹ️ Bringing window to front: 'FlexiSIGN-PRO'
[12:35:13] ℹ️ ============================================================
[12:35:13] ✅ FlexiSign Pro is ready! ✓
[12:35:13] ℹ️ ============================================================
```

## How It Works

### Startup Sequence

```
1. Check Loader/Patcher
   ├─ Running? → Continue
   └─ Not Running? → Start it + Handle modal

2. Check FlexiSign Windows
   ├─ No windows? → Continue
   ├─ Windows exist + Loader was running? → Bring to front
   └─ Windows exist + Loader was NOT running? → CLOSE ALL (demo mode!)

3. Start FlexiSign Pro
   ├─ Already running? → Bring to front
   └─ Not running? → Start it

4. Verify & Return
   └─ FlexiSign Pro ready with loader active ✓
```

### Demo Mode Prevention

The system prevents demo mode by:

1. **Never starting FlexiSign without loader**
2. **Detecting existing demo mode windows** (loader not running)
3. **Closing and restarting** if demo mode detected
4. **Verifying loader is active** before allowing FlexiSign to run

## Configuration Reference

### Loader/Patcher Settings

```json
"loader_patcher": {
  "process_name": "Exact process name from Task Manager",
  "exe_path": "Full path to loader executable",
  "startup_modal": {
    "enabled": true,              // Set false if no modal
    "title": "Modal window title", // Partial match OK
    "button": "OK",                // Button text (not used, presses Enter)
    "timeout": 15                  // Seconds to wait for modal
  },
  "wait_after_start": 3            // Seconds to wait after starting
}
```

### FlexiSign Pro Settings

```json
"flexisign_pro": {
  "process_names": [
    "FlexiSIGN",                   // List all possible process names
    "flexisign.exe"
  ],
  "exe_path": "Full path to FlexiSign executable",
  "window_titles": [
    "FlexiSIGN-PRO",               // List all possible window titles
    "FlexiSIGN"
  ],
  "demo_mode_indicators": [        // Keywords that indicate demo mode
    "trial", "demo", "evaluation"
  ],
  "wait_after_start": 8            // Seconds to wait after starting
}
```

### Timing Settings

```json
"timing": {
  "process_check_interval": 0.5,   // How often to check processes
  "window_check_interval": 1,      // How often to check windows
  "modal_check_interval": 0.5,     // How often to check for modals
  "window_close_wait": 2           // Wait after closing windows
}
```

## Troubleshooting

### Problem: Loader/patcher not detected

**Solution:**
1. Open Task Manager while loader is running
2. Find the exact process name
3. Update `loader_patcher.process_name` in config

### Problem: Modal not being clicked

**Solution:**
1. Run `python test_modal.py` while modal is visible
2. Find the exact window title
3. Update `loader_patcher.startup_modal.title` in config
4. Increase `timeout` if modal appears slowly

### Problem: FlexiSign still opens in demo mode

**Solution:**
1. Check logs - is loader actually starting?
2. Verify `exe_path` is correct for loader
3. Increase `wait_after_start` for loader
4. Check if loader requires admin privileges

### Problem: Windows won't close

**Solution:**
1. The system will try graceful close first
2. If that fails, it force kills the process
3. Check logs for error messages
4. Verify you have permissions to close windows

## Testing Scenarios

### Test 1: Cold Start (Nothing Running)
```bash
# Kill everything first
taskkill /F /IM FlexiSIGN.exe
taskkill /F /IM "Production Suite Scanner*"

# Run manager
python flexisign_manager.py
```

**Expected:** Loader starts → Modal handled → FlexiSign starts → Ready

### Test 2: Loader Already Running
```bash
# Start loader manually first
# Then run manager
python flexisign_manager.py
```

**Expected:** Detects loader → Starts FlexiSign → Ready

### Test 3: Demo Mode Detection
```bash
# Start FlexiSign WITHOUT loader
# Then run manager
python flexisign_manager.py
```

**Expected:** Detects demo mode → Closes FlexiSign → Starts loader → Restarts FlexiSign → Ready

### Test 4: Everything Already Running
```bash
# Start loader + FlexiSign properly
# Then run manager
python flexisign_manager.py
```

**Expected:** Detects everything OK → Brings window to front → Ready

## Integration with JARVIS

The manager is automatically used by the main client when you send a FlexiSign workflow command from the mobile app.

The backend workflow is now simplified:
```python
{
    "action": "flexisign_workflow",
    "steps": [
        {"type": "notification", "message": "Starting..."},
        # Manager handles all startup automatically
        {"type": "press_key", "key": "t"},
        {"type": "type_text", "text": "Your text here"}
    ]
}
```

## Advanced Usage

### Custom Workflow Steps

After FlexiSign is ready, you can add custom steps:

```python
steps = [
    {"type": "press_key", "key": "ctrl+n"},      # New file
    {"type": "type_text", "text": "Hello"},      # Type text
    {"type": "click_center"},                     # Click center
    {"type": "press_key", "key": "ctrl+s"}       # Save
]
```

### Programmatic Usage

```python
from flexisign_manager import FlexiSignManager

manager = FlexiSignManager('flexisign_config.json')

# Ensure FlexiSign is ready
if manager.ensure_proper_state():
    print("Ready to automate!")
    # Your automation code here
else:
    print("Failed to start FlexiSign")
```

## Support

If you encounter issues:

1. **Enable verbose logging** in config:
   ```json
   "debug": {
     "verbose_logging": true,
     "list_all_windows": true
   }
   ```

2. **Check the logs** - they show exactly what's happening

3. **Test standalone** - Run `python flexisign_manager.py` to isolate issues

4. **Verify paths** - Make sure all exe_path values are correct

## Summary

✅ **Loader/patcher always starts first**  
✅ **Demo mode automatically detected and fixed**  
✅ **Fail-safe mechanisms prevent stuck states**  
✅ **Configuration-driven (no code changes needed)**  
✅ **Detailed logging for troubleshooting**  
✅ **Works reliably every time**

The system guarantees FlexiSign Pro never runs in restricted mode!
