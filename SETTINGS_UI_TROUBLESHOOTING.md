# Settings UI Troubleshooting Guide

## Issue: Empty Prompt Fields in PyWebView

If you see empty prompt fields in the PyWebView app but they work in `npm run dev`, follow these steps:

### Step 1: Verify Backend is Working

```bash
python local_client/test_pywebview_simulation.py
```

Expected output: "✓ PyWebView should receive prompts correctly!"

If this fails, there's a backend issue. Otherwise, continue to Step 2.

### Step 2: Rebuild Frontend

The PyWebView app loads from `settings_ui/dist/`, not the dev server.

```bash
cd settings_ui
npm run build
cd ..
```

### Step 3: Clear Python Cache

```bash
# Windows PowerShell
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse

# Or manually delete:
# - local_client/__pycache__/
# - backend/__pycache__/
```

### Step 4: Restart PyWebView Completely

1. Close the PyWebView app completely (check Task Manager)
2. Run: `python local_client/run_settings.py`

### Step 5: Check Browser Console

When PyWebView opens, press F12 to open developer tools and check for:
- JavaScript errors in Console tab
- Failed network requests in Network tab
- Check what data `get_settings()` returns

### Step 6: Enable Debug Mode

Run with debug logging:

```bash
python local_client/run_settings.py --dev
```

This will show:
- What URL is being loaded
- API initialization status
- Any Python errors

### Step 7: Verify Files Are Correct

Check that the changes are in place:

```bash
# Check backend has raw strings
python -c "import backend.gemini_service as g; print('GENERAL starts with:', g.GENERAL_SYSTEM_PROMPT[:50])"

# Check prompt manager can read them
python -c "from local_client.prompt_manager import read_all_prompts; from pathlib import Path; p = read_all_prompts(Path('.')); print('Loaded prompts:', list(p.get('planner', {}).keys()))"
```

## Common Issues

### Issue: "Mock data" showing in prompts
**Cause:** Running `npm run dev` instead of PyWebView
**Solution:** Use `python local_client/run_settings.py` for production

### Issue: Old UI showing
**Cause:** Frontend not rebuilt after changes
**Solution:** Run `cd settings_ui && npm run build`

### Issue: Prompts still empty after rebuild
**Cause:** Python modules cached
**Solution:** Delete `__pycache__` folders and restart

### Issue: SyntaxError about unicode
**Cause:** Missing `r` prefix on prompt strings
**Solution:** Already fixed - verify with Step 7 above

## Quick Fix Script

Run this to do all cleanup steps:

```bash
python local_client/fix_settings_cache.py
```

## Still Not Working?

1. Check that these files exist and are recent:
   - `settings_ui/dist/index.html`
   - `settings_ui/dist/assets/*.js`

2. Verify the API bridge is working:
   ```bash
   python local_client/test_pywebview_simulation.py
   ```

3. Check file timestamps:
   ```bash
   # PowerShell
   Get-ChildItem settings_ui/dist/assets/*.js | Select-Object Name, LastWriteTime
   ```

4. Try running with explicit path:
   ```bash
   python -m local_client.run_settings
   ```
