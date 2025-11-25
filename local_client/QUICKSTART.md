# FlexiSign Automation - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- Windows PC with FlexiSign Pro installed
- Python 3.7+ installed
- FlexiSign loader/patcher utility

### Step 1: Install Dependencies (30 seconds)

```bash
cd local_client
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install socketio pyautogui psutil pywin32
```

### Step 2: Run Configuration Wizard (2 minutes)

**Important:** Start FlexiSign and its loader/patcher BEFORE running the wizard!

```bash
python setup_wizard.py
```

The wizard will:
1. ✅ Detect your loader/patcher process
2. ✅ Detect FlexiSign process and windows
3. ✅ Create `flexisign_config.json` automatically
4. ✅ Test the configuration

Just follow the prompts and answer the questions.

### Step 3: Test Standalone (30 seconds)

Close FlexiSign completely, then test:

```bash
python flexisign_manager.py
```

You should see:
```
✅ Loader/patcher started successfully
✅ FlexiSign Pro started successfully
✅ FlexiSign Pro is ready! ✓
```

### Step 4: Start JARVIS Client (30 seconds)

**Important:** The loader/patcher requires administrator privileges!

**Option A - Run as Admin (Recommended):**
```bash
# Double-click this file:
run_as_admin.bat
```

**Option B - Start Loader Manually:**
1. Right-click the loader/patcher → "Run as administrator"
2. Then run: `python client.py`

You should see:
```
Connected to Server
```

> **Note:** See [ADMIN_PRIVILEGES_GUIDE.md](ADMIN_PRIVILEGES_GUIDE.md) for detailed info

### Step 5: Test from Mobile App (1 minute)

1. Open the JARVIS mobile app
2. Send a message: "Make a nameplate"
3. Watch the automation run!

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Configuration wizard completed
- [ ] Standalone test passed
- [ ] Client connected to server
- [ ] Mobile app test successful

## 🔧 Manual Configuration (Alternative)

If the wizard doesn't work, edit `flexisign_config.json` manually:

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
    },
    "wait_after_start": 3
  },
  "flexisign_pro": {
    "process_names": ["FlexiSIGN.exe"],
    "exe_path": "C:\\Path\\To\\FlexiSign.exe",
    "window_titles": ["FlexiSIGN-PRO"],
    "wait_after_start": 8
  }
}
```

### Finding Process Names

**Method 1: Task Manager**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to "Details" tab
3. Find FlexiSign and loader processes
4. Copy the exact names

**Method 2: Python Script**
```bash
python -c "import psutil; [print(p.name()) for p in psutil.process_iter()]"
```

**Method 3: Test Script**
```bash
python test_modal.py
```

## 🐛 Troubleshooting

### Problem: "Configuration file not found"
**Solution:** Run `python setup_wizard.py` first

### Problem: "Loader/patcher not detected"
**Solution:** 
1. Start the loader manually
2. Run: `python -c "import psutil; [print(p.name()) for p in psutil.process_iter() if 'scanner' in p.name().lower()]"`
3. Update `process_name` in config

### Problem: "FlexiSign opens in demo mode"
**Solution:** This is exactly what the system prevents! If you see this:
1. The manager will automatically close demo mode windows
2. Start the loader/patcher
3. Restart FlexiSign properly
4. Check logs for details

### Problem: "Modal not being clicked"
**Solution:**
1. Run `python test_modal.py` while modal is visible
2. Find the exact window title
3. Update `startup_modal.title` in config

### Problem: "Connection failed"
**Solution:**
1. Make sure backend server is running: `python backend/server.py`
2. Check `SERVER_URL` in `config.py`
3. Verify firewall isn't blocking port 5000

## 📚 More Information

- **Full Documentation:** See `FLEXISIGN_SETUP.md`
- **Configuration Reference:** See `FLEXISIGN_SETUP.md` → Configuration Reference
- **Advanced Usage:** See `FLEXISIGN_SETUP.md` → Advanced Usage

## 🎯 What the System Does

### Automatic Protection Against Demo Mode

```
❌ OLD BEHAVIOR (Unreliable):
   Start FlexiSign → Sometimes demo mode → Manual intervention needed

✅ NEW BEHAVIOR (Reliable):
   1. Check loader → Start if needed → Handle modal
   2. Check FlexiSign → Close if in demo mode
   3. Start FlexiSign properly → Always works!
```

### Key Features

- ✅ **Never runs in demo mode** - Guaranteed
- ✅ **Automatic modal handling** - No manual clicks
- ✅ **Fail-safe mechanisms** - Recovers from errors
- ✅ **Configuration-driven** - Easy to update
- ✅ **Detailed logging** - Easy to troubleshoot

## 🎉 You're Done!

Your FlexiSign automation is now:
- ✅ Configured
- ✅ Tested
- ✅ Ready to use

Send commands from the mobile app and watch the magic happen! 🚀

---

**Need Help?** Check `FLEXISIGN_SETUP.md` for detailed documentation.
