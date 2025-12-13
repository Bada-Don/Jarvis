# FlexiSIGN Diagnostic Tools

This directory contains diagnostic scripts to help troubleshoot FlexiSIGN automation issues.

## Available Tools

### 1. check_designcentral.py
**Purpose:** Comprehensive diagnostic for DesignCentral panel detection and accessibility.

**Usage:**
```cmd
python check_designcentral.py
```

**What it checks:**
- FlexiSIGN window detection
- Window activation
- DesignCentral panel visibility
- DesignCentral opening functionality (Ctrl+I)
- All key UI elements (tabs, inputs, comboboxes)

**Output:**
- Step-by-step diagnostic results
- Detailed error messages if issues found
- Troubleshooting tips

**When to use:**
- DesignCentral-related automation fails
- Need to verify FlexiSIGN UIA setup
- Troubleshooting element detection issues

---

### 2. test_designcentral_fix.py
**Purpose:** Quick test to verify DesignCentral detection and opening works.

**Usage:**
```cmd
python test_designcentral_fix.py
```

**What it tests:**
- Initial DesignCentral state detection
- `ensure_designcentral_open()` function
- Final state verification

**Output:**
- Pass/Fail result
- State transitions (closed → open)
- Troubleshooting tips if failed

**When to use:**
- Quick verification after fixing DesignCentral issues
- Testing ensure_designcentral_open() function
- Validating FlexiSIGN setup

---

### 3. test_plan.py (Enhanced)
**Purpose:** Execute FlexiSIGN plans from JSON files with proper initialization.

**Usage:**
```cmd
python test_plan.py test_plans/open_flexi_save_file.json
```

**Enhancements:**
- Automatic FlexiSIGN initialization for direct/flexisign mode plans
- Window activation before execution
- Mode detection and appropriate setup

**When to use:**
- Testing FlexiSIGN automation plans
- Debugging plan execution issues
- Validating plan JSON structure

---

## Common Issues and Solutions

### Issue: "DesignCentral panel is CLOSED"

**Symptoms:**
- `ensure_designcentral_open()` returns False
- Automation fails at dimension/font setting steps

**Solutions:**
1. Run `python check_designcentral.py` for detailed diagnostics
2. Manually press Ctrl+I in FlexiSIGN to verify hotkey works
3. Check if DesignCentral is docked (View → DesignCentral)
4. Restart FlexiSIGN and try again

---

### Issue: "FlexiSIGN window NOT FOUND"

**Symptoms:**
- Scripts can't find FlexiSIGN window
- Window detection fails

**Solutions:**
1. Ensure FlexiSIGN is running
2. Check window title contains "FlexiSIGN-PRO"
3. Verify FlexiSIGN is not minimized
4. Check config.py for correct FLEXISIGN_WINDOW_TITLE

---

### Issue: "test_plan.py doesn't initialize FlexiSIGN"

**Symptoms:**
- Plans work via mobile app but not test_plan.py
- FlexiSIGN window not activated before execution
- Direct mode plans fail

**Solutions:**
1. Ensure plan has `"mode": "direct"` or `"mode": "flexisign"`
2. Verify flexisign_manager.py is available
3. Check that FlexiSIGN path in config.py is correct
4. Run with updated test_plan.py (includes FlexiSignManager)

---

### Issue: "Root element not found"

**Symptoms:**
- Window activates but UIA can't access elements
- "Root element refreshed successfully" not shown

**Solutions:**
1. Wait 5 seconds after FlexiSIGN starts
2. Ensure FlexiSIGN window is in foreground
3. Check if FlexiSIGN process is running (Task Manager)
4. Restart FlexiSIGN with admin privileges

---

## Diagnostic Workflow

### For DesignCentral Issues:

1. **Run comprehensive diagnostic:**
   ```cmd
   python check_designcentral.py
   ```

2. **If diagnostic passes, test the fix:**
   ```cmd
   python test_designcentral_fix.py
   ```

3. **If both pass, test your plan:**
   ```cmd
   python test_plan.py test_plans/your_plan.json
   ```

### For Plan Execution Issues:

1. **Verify plan structure:**
   - Check `"mode"` field is set correctly
   - Ensure all required fields present
   - Validate JSON syntax

2. **Test with diagnostic:**
   ```cmd
   python test_plan.py test_plans/your_plan.json
   ```

3. **Check debug logs:**
   - Located in `debug_logs/<session_id>/`
   - Review step execution logs
   - Check for error messages

---

## Configuration Requirements

### config.py Settings:

```python
# FlexiSIGN-specific settings
FLEXISIGN_PROCESS_NAME = "Production Suite Scanner 10.5.1 Build 1806 Protected"
FLEXISIGN_EXE_PATH = r"D:\Program Files\...\FlexiSIGN.exe"
FLEXISIGN_WINDOW_TITLE = "FlexiSIGN-PRO"
```

### Verification Settings:

```python
# For faster testing, disable verification
VERIFICATION_ENABLED = False
MAX_RETRIES = 0
```

---

## Tips for Successful Automation

1. **Always run FlexiSIGN first** before executing plans
2. **Keep FlexiSIGN window visible** (not minimized)
3. **Use direct mode** for FlexiSIGN-specific tasks
4. **Test with diagnostic tools** before running full automation
5. **Check debug logs** if issues occur
6. **Disable verification** during development for faster iteration

---

## Getting Help

If diagnostic tools show errors:

1. Review the error messages and troubleshooting tips
2. Check the configuration in config.py
3. Verify FlexiSIGN version matches expected version
4. Check debug logs for detailed execution traces
5. Try manual operations in FlexiSIGN to verify functionality

For persistent issues:
- Restart FlexiSIGN
- Restart the local client
- Check Windows UI Automation is enabled
- Verify no other automation tools are interfering
