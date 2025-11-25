# JARVIS Local Client

The local client runs on your Windows PC and executes automation commands received from the JARVIS backend server.

## 📁 Directory Structure

```
local_client/
├── client.py                    # Main client (connects to server)
├── flexisign_manager.py         # FlexiSign automation manager
├── flexisign_config.json        # FlexiSign configuration
├── config.py                    # General client configuration
├── setup_wizard.py              # Interactive setup wizard
├── test_modal.py                # Window detection helper
├── requirements.txt             # Python dependencies
├── QUICKSTART.md               # 5-minute setup guide ⭐ START HERE
├── FLEXISIGN_SETUP.md          # Detailed FlexiSign documentation
└── README_MAIN.md              # This file
```

## 🚀 Quick Start

**New users:** Follow [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup.

**TL;DR:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (with FlexiSign running)
python setup_wizard.py

# 3. Test
python flexisign_manager.py

# 4. Run client
python client.py
```

## 📖 Documentation

### For New Users
- **[QUICKSTART.md](QUICKSTART.md)** - Start here! 5-minute setup guide

### For FlexiSign Setup
- **[FLEXISIGN_SETUP.md](FLEXISIGN_SETUP.md)** - Complete FlexiSign automation guide
  - Architecture overview
  - Configuration reference
  - Troubleshooting
  - Advanced usage

### For Developers
- **[config.py](config.py)** - General client settings
- **[flexisign_config.json](flexisign_config.json)** - FlexiSign-specific settings

## 🎯 What Does This Do?

The local client:

1. **Connects to JARVIS backend** via WebSocket
2. **Receives automation commands** from mobile app
3. **Controls FlexiSign Pro** with intelligent automation
4. **Prevents demo mode** by managing loader/patcher
5. **Sends status updates** back to mobile app

## 🔧 Components

### Main Client (`client.py`)
- Connects to backend server
- Receives and executes commands
- Sends status updates
- Integrates with FlexiSign Manager

### FlexiSign Manager (`flexisign_manager.py`)
- Ensures loader/patcher is running
- Detects and prevents demo mode
- Manages FlexiSign startup
- Handles modal dialogs
- Provides fail-safe mechanisms

### Configuration Files

**`flexisign_config.json`** - FlexiSign-specific settings:
- Loader/patcher paths and settings
- FlexiSign Pro paths and settings
- Window titles and process names
- Timing configurations

**`config.py`** - General client settings:
- Server URL
- Process names
- Modal settings
- Timing values

## 🛠️ Setup Tools

### Setup Wizard (`setup_wizard.py`)
Interactive wizard that:
- Detects running processes
- Finds window titles
- Creates configuration automatically
- Tests the setup

**Usage:**
```bash
python setup_wizard.py
```

### Test Modal (`test_modal.py`)
Helper script to identify window titles:
- Lists all visible windows
- Updates every 2 seconds
- Helps find modal titles

**Usage:**
```bash
python test_modal.py
```

## 📋 Requirements

### System Requirements
- Windows 10/11
- Python 3.7 or higher
- FlexiSign Pro installed
- FlexiSign loader/patcher utility

### Python Dependencies
Install with: `pip install -r requirements.txt`

- `python-socketio` - Server communication
- `pyautogui` - GUI automation
- `psutil` - Process management
- `pywin32` - Windows API access
- `Pillow` - Image processing

## 🔌 Server Connection

The client connects to the JARVIS backend server:

**Default:** `http://localhost:5000`

**Change in `config.py`:**
```python
SERVER_URL = 'http://192.168.1.100:5000'  # Your server IP
```

## 🎮 Usage

### Start the Client

```bash
python client.py
```

Expected output:
```
Starting Jarvis Local Client...
Connected to Server
```

### Send Commands from Mobile App

The mobile app sends commands like:
- "Make a nameplate for Dr. Sharma"
- "Create a 15x10 sticker"

The client:
1. Receives the command
2. Ensures FlexiSign is ready
3. Executes the automation
4. Sends status updates

### Monitor Status

Watch the console for:
- ✅ Success messages (green)
- ⚠️ Warnings (yellow)
- ❌ Errors (red)
- ℹ️ Info messages (blue)

## 🐛 Troubleshooting

### Client won't connect
```bash
# Check if server is running
curl http://localhost:5000

# Check firewall settings
# Verify SERVER_URL in config.py
```

### FlexiSign issues
See [FLEXISIGN_SETUP.md](FLEXISIGN_SETUP.md) → Troubleshooting section

### Process detection issues
```bash
# List all processes
python -c "import psutil; [print(p.name()) for p in psutil.process_iter()]"

# Test window detection
python test_modal.py
```

### Configuration issues
```bash
# Re-run setup wizard
python setup_wizard.py

# Or edit manually
notepad flexisign_config.json
```

## 🔄 Workflow Example

```
Mobile App                Backend Server           Local Client
    |                          |                        |
    |--"Make nameplate"------->|                        |
    |                          |                        |
    |                          |--Command-------------->|
    |                          |                        |
    |                          |                   [Check loader]
    |                          |                   [Start if needed]
    |                          |                   [Handle modal]
    |                          |                   [Start FlexiSign]
    |                          |                        |
    |                          |<--Status: "Starting"---|
    |<--Status update----------|                        |
    |                          |                        |
    |                          |                   [Execute steps]
    |                          |                   [Type text]
    |                          |                        |
    |                          |<--Status: "Complete"---|
    |<--Status update----------|                        |
    |                          |                        |
```

## 🔐 Security Notes

- Client runs with your user permissions
- Can control mouse/keyboard (by design)
- Only connects to configured server
- No external network access
- All automation is local

## 🚀 Advanced Usage

### Custom Workflows

Edit backend `server.py` to add custom steps:

```python
{
    "action": "flexisign_workflow",
    "steps": [
        {"type": "notification", "message": "Starting..."},
        {"type": "press_key", "key": "ctrl+n"},
        {"type": "type_text", "text": "Custom text"},
        {"type": "press_key", "key": "ctrl+s"}
    ]
}
```

### Programmatic Usage

```python
from flexisign_manager import FlexiSignManager

manager = FlexiSignManager()
if manager.ensure_proper_state():
    # FlexiSign is ready
    # Your automation code here
    pass
```

### Multiple Configurations

```bash
# Use different config file
python flexisign_manager.py --config my_config.json
```

## 📊 Status Codes

The client sends these status types:

- `info` - Informational message
- `success` - Operation succeeded
- `warning` - Non-critical issue
- `error` - Operation failed

## 🔄 Auto-Reload

The client supports auto-reload:
- Edit `client.py` and save
- Client automatically restarts
- No need to manually restart

## 📝 Logging

Logs are printed to console with timestamps:

```
[12:34:56] ℹ️ Starting FlexiSign automation...
[12:34:57] ✅ Loader/patcher started successfully
[12:35:05] ✅ FlexiSign Pro is ready! ✓
```

Enable verbose logging in `flexisign_config.json`:
```json
"debug": {
  "verbose_logging": true
}
```

## 🤝 Contributing

To add new automation features:

1. Add step type in `client.py` → `execute_command()`
2. Update backend workflow in `server.py`
3. Test thoroughly
4. Document in this README

## 📞 Support

**Issues?**
1. Check [QUICKSTART.md](QUICKSTART.md) troubleshooting
2. Check [FLEXISIGN_SETUP.md](FLEXISIGN_SETUP.md) troubleshooting
3. Enable verbose logging
4. Check console output

**Common Issues:**
- Connection failed → Check server is running
- FlexiSign demo mode → Run setup wizard again
- Modal not clicked → Update modal title in config
- Process not found → Verify paths in config

## 📜 License

Part of the JARVIS project.

## 🎉 Summary

The local client is the "hands" of JARVIS - it executes commands on your PC with intelligent automation that ensures FlexiSign Pro always runs properly, never in demo mode.

**Key Features:**
- ✅ Automatic loader/patcher management
- ✅ Demo mode prevention
- ✅ Modal dialog handling
- ✅ Fail-safe mechanisms
- ✅ Real-time status updates
- ✅ Configuration-driven
- ✅ Easy setup with wizard

**Get Started:** [QUICKSTART.md](QUICKSTART.md)
