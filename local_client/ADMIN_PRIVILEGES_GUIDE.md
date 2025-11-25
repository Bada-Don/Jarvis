# Administrator Privileges Guide

## Why Admin Rights Are Needed

The FlexiSign loader/patcher utility requires administrator privileges to:
- Bypass software protection mechanisms
- Modify system-level processes
- Access protected memory regions

## Solutions

### Option 1: Run Client as Administrator (Recommended)

**Windows:**

1. **Using the Batch File:**
   ```
   Double-click: run_as_admin.bat
   ```
   This will automatically request admin privileges.

2. **Manual Method:**
   - Right-click `cmd.exe` or PowerShell
   - Select "Run as administrator"
   - Navigate to local_client folder
   - Run: `python client.py`

3. **Create Shortcut:**
   - Right-click `client.py` → Send to → Desktop (create shortcut)
   - Right-click the shortcut → Properties
   - Click "Advanced" → Check "Run as administrator"
   - Click OK

### Option 2: Start Loader/Patcher Manually

If you don't want to run the client as admin:

1. **Start the loader/patcher manually BEFORE running the client:**
   - Right-click the loader/patcher executable
   - Select "Run as administrator"
   - Click OK on any dialogs

2. **Then start the client normally:**
   ```bash
   python client.py
   ```

3. **The client will detect the running loader and continue**

### Option 3: Disable UAC for the Loader (Not Recommended)

You can configure the loader to always run with admin rights:

1. Right-click loader executable → Properties
2. Compatibility tab
3. Check "Run this program as an administrator"
4. Click OK

**Warning:** This is less secure and not recommended.

## How the System Handles This

### Automatic Elevation

The FlexiSign Manager tries to start the loader with admin rights automatically:

```python
# Uses Windows ShellExecute with "runas" verb
ctypes.windll.shell32.ShellExecuteW(
    None,
    "runas",  # Request elevation
    exe_path,
    None,
    None,
    1
)
```

### Fallback Behavior

If elevation fails:
1. System checks if loader is already running
2. If not, shows error message
3. Waits for user to start loader manually
4. Continues when loader is detected

### Error Messages

**"Failed to start loader/patcher"**
- The system couldn't start the loader
- Usually means admin rights are needed

**"Please start the loader/patcher manually"**
- Start the loader yourself with admin rights
- The automation will continue once detected

## Testing Admin Privileges

### Check if Running as Admin

```python
import ctypes
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
print(f"Running as admin: {is_admin}")
```

### Test Loader Startup

```bash
# Run this to test
python -c "from flexisign_manager import FlexiSignManager; m = FlexiSignManager(); m.start_loader_patcher()"
```

## Troubleshooting

### Problem: "The requested operation requires elevation"

**Solution:**
- Run the client as administrator
- OR start the loader manually first

### Problem: UAC prompt appears every time

**Solution:**
- Use the batch file (`run_as_admin.bat`)
- OR configure loader to always run as admin
- OR start loader manually before client

### Problem: Loader starts but immediately closes

**Solution:**
- Check if loader requires additional files
- Verify the exe path in config is correct
- Check Windows Event Viewer for errors

### Problem: Client can't detect running loader

**Solution:**
- Verify process name in config matches exactly
- Check Task Manager for the actual process name
- Update `process_name` in `flexisign_config.json`

## Best Practices

### For Development

1. **Always run client as admin during development**
   ```bash
   # PowerShell as admin
   cd local_client
   python client.py
   ```

2. **Keep loader running in background**
   - Start it once at system startup
   - Client will detect it automatically

### For Production

1. **Create a Windows Service**
   - Run client as a Windows service with admin rights
   - Starts automatically on boot
   - No UAC prompts

2. **Use Task Scheduler**
   - Create scheduled task
   - Configure to run with highest privileges
   - Trigger on system startup

3. **Start Loader at Startup**
   - Add loader to Windows startup folder
   - Configure to run as admin
   - Client will always find it running

## Security Considerations

### Why This Is Safe

- Only the loader/patcher needs admin rights
- Client can run with normal privileges if loader is already running
- No network access with elevated privileges
- All automation is local

### Minimize Risk

1. **Run only loader as admin, not the entire client**
2. **Use Task Scheduler with specific privileges**
3. **Audit what the loader does** (if possible)
4. **Keep loader updated** to latest version

## Alternative Approaches

### Virtual Machine

Run FlexiSign in a VM with admin rights:
- No UAC prompts
- Isolated environment
- Easy to reset if issues occur

### Docker/Container

Not applicable for Windows GUI apps, but worth mentioning for future Linux support.

## Summary

**Quick Start:**
1. Double-click `run_as_admin.bat`
2. Click "Yes" on UAC prompt
3. Client starts with admin rights
4. Loader starts automatically
5. Everything works! ✅

**Alternative:**
1. Start loader manually as admin
2. Run client normally
3. Client detects running loader
4. Everything works! ✅

Choose the method that works best for your workflow!
