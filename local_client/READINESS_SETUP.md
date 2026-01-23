# Readiness Detection Setup Guide

## Overview

The readiness detection system provides deterministic state detection for robust automation. It works out-of-the-box with graceful degradation, but installing optional dependencies enhances capabilities.

---

## Installation

### Core System (Already Installed)
The readiness detection system works immediately with existing dependencies:
- ✅ Browser readiness detection (window title monitoring)
- ✅ File system readiness detection (path polling)
- ⚠️ Basic desktop app readiness (window state only)

### Enhanced Desktop App Detection (Optional)

For full desktop application readiness detection with UI Automation:

```bash
pip install uiautomation
```

**What this enables:**
- UI Automation tree access
- Control counting (verifies UI is populated)
- Splash screen vs main window detection
- Framework-agnostic app state detection

**Without this:**
- System falls back to window state checks only
- Still works, just less sophisticated
- No errors or failures

---

## Verification

Test if UI Automation is available:

```python
python -c "import uiautomation; print('✓ UI Automation available')"
```

If successful, you'll see: `✓ UI Automation available`

If not installed, you'll see: `ModuleNotFoundError` (this is OK, system will use fallback)

---

## Configuration

### Timeout Settings

Edit `local_client/plan_executor.py` if you need to adjust timeouts:

```python
# In _wait_for_readiness_before_vision method:

# Browser page load timeout
result = self._browser_detector.wait_for_page_load(
    browser_name=app_lower,
    timeout=15.0,  # ← Adjust this (seconds)
    min_stable_time=1.0  # ← How long title must be stable
)

# Desktop app readiness timeout
result = self._desktop_detector.wait_for_app_ready(
    window_title_pattern=window_title,
    timeout=15.0,  # ← Adjust this (seconds)
    check_cpu_stable=False,  # ← Enable CPU monitoring
    min_control_count=5  # ← Minimum UI controls expected
)

# File system readiness timeout
readiness_result = self._filesystem_detector.wait_for_folder_accessible(
    resolved_path,
    timeout=3.0  # ← Adjust this (seconds)
)
```

### Retry Settings

Edit `local_client/plan_executor.py` for folder creation retry logic:

```python
# In _execute_open_folder_step method:

max_retries = 3  # ← Number of retry attempts
retry_delay = 0.5  # ← Delay between retries (seconds)
```

---

## Troubleshooting

### Issue: "Readiness detector not available"

**Cause:** Import failed for `readiness_detector.py`

**Solution:**
1. Check file exists: `local_client/readiness_detector.py`
2. Check for syntax errors: `python -m py_compile local_client/readiness_detector.py`
3. System will fall back to 2-second delay (still works)

### Issue: Desktop app readiness always times out

**Cause:** UI Automation not available or app has unusual UI structure

**Solutions:**
1. Install `uiautomation`: `pip install uiautomation`
2. Increase timeout in configuration
3. Disable CPU check: `check_cpu_stable=False`
4. Lower control count: `min_control_count=3`

### Issue: Browser readiness takes too long

**Cause:** Page has dynamic content that keeps changing title

**Solutions:**
1. Reduce `min_stable_time` (e.g., from 1.0 to 0.5 seconds)
2. Increase `timeout` if page legitimately takes long to load
3. Check if page has infinite loading indicators

### Issue: Folder creation still fails

**Cause:** File system operation is very slow or permissions issue

**Solutions:**
1. Increase `max_retries` (e.g., from 3 to 5)
2. Increase `retry_delay` (e.g., from 0.5 to 1.0 seconds)
3. Check folder permissions
4. Check antivirus isn't blocking folder creation

---

## Performance Tuning

### For Faster Execution (Less Robust)

```python
# Reduce timeouts
timeout=5.0  # Instead of 15.0
min_stable_time=0.5  # Instead of 1.0

# Reduce retries
max_retries=2  # Instead of 3
retry_delay=0.3  # Instead of 0.5
```

### For Maximum Reliability (Slower)

```python
# Increase timeouts
timeout=30.0  # Instead of 15.0
min_stable_time=2.0  # Instead of 1.0

# Increase retries
max_retries=5  # Instead of 3
retry_delay=1.0  # Instead of 0.5

# Enable CPU monitoring
check_cpu_stable=True  # Instead of False
```

---

## Testing

### Test Browser Readiness

```python
from local_client.readiness_detector import get_browser_detector

detector = get_browser_detector()
result = detector.wait_for_page_load('chrome', timeout=15.0)

print(f"State: {result.state}")
print(f"Message: {result.message}")
print(f"Elapsed: {result.elapsed_time:.2f}s")
```

### Test Desktop App Readiness

```python
from local_client.readiness_detector import get_desktop_detector

detector = get_desktop_detector()
result = detector.wait_for_app_ready('Notepad', timeout=10.0)

print(f"State: {result.state}")
print(f"Message: {result.message}")
print(f"Elapsed: {result.elapsed_time:.2f}s")
```

### Test File System Readiness

```python
from local_client.readiness_detector import get_filesystem_detector
import os

detector = get_filesystem_detector()

# Create a test folder
os.makedirs('test_folder', exist_ok=True)

# Test detection
result = detector.wait_for_folder_accessible('test_folder', timeout=5.0)

print(f"State: {result.state}")
print(f"Message: {result.message}")
```

---

## Monitoring

### Enable Verbose Logging

The readiness detectors use the status callback for logging. To see detailed logs:

1. Check console output when running JARVIS
2. Look for messages like:
   - "Waiting for chrome page to load..."
   - "Page loading: Gmail - ..."
   - "✓ Page ready: Gmail"
   - "Waiting for application: Notepad"
   - "✓ Application ready: Notepad"

### Debug Mode

For even more detailed logging, edit `readiness_detector.py`:

```python
# Add debug prints in key methods
def wait_for_page_load(self, ...):
    print(f"[DEBUG] Starting page load detection for {browser_name}")
    # ... rest of method
```

---

## Best Practices

1. **Don't disable readiness detection** unless you have a specific reason
2. **Start with default timeouts** and only adjust if needed
3. **Monitor console output** to understand what's happening
4. **Install uiautomation** for best desktop app support
5. **Test with slow networks** to ensure timeouts are adequate
6. **Use retry logic** for file system operations
7. **Keep min_stable_time >= 0.5s** for browser detection

---

## Support

If you encounter issues:

1. Check console logs for error messages
2. Verify all dependencies are installed
3. Test individual detectors in isolation
4. Adjust timeouts based on your system speed
5. Report issues with full error messages and logs
