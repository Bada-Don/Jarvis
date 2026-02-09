# JARVIS Application Launcher

## Overview

The JARVIS Application Launcher is a comprehensive system for managing all JARVIS components with automatic monitoring, crash recovery, and system tray integration.

## Components

### 1. ApplicationLauncher (`application_launcher.py`)

The core launcher class that manages the lifecycle of all JARVIS components:

- **Backend Server**: Flask API server (port 5000)
- **Local Client**: Automation executor
- **Settings UI**: Configuration interface

**Features:**
- ✅ Starts components in correct order
- ✅ Monitors component health
- ✅ Automatically restarts crashed components
- ✅ Graceful shutdown handling
- ✅ Detailed logging
- ✅ Process status reporting

### 2. SystemTrayManager (`system_tray_manager.py`)

Provides system tray icon and menu for easy application control:

**Features:**
- ✅ System tray icon with menu
- ✅ Show Settings option
- ✅ Component status display
- ✅ Restart all components
- ✅ View logs
- ✅ Quit application
- ✅ System notifications

### 3. Main Launcher Script (`JARVIS.py`)

The main entry point that ties everything together.

## Installation

### Prerequisites

```bash
# Install required dependencies
pip install -r local_client/requirements.txt
```

Key dependencies:
- `pystray>=0.19.0` - System tray icon
- `psutil>=5.9.0` - Process management
- `Pillow>=10.0.0` - Image handling

## Usage

### Basic Usage

Start JARVIS with all components:

```bash
python JARVIS.py
```

### Command-Line Options

```bash
# Start without system tray
python JARVIS.py --no-tray

# Enable debug logging
python JARVIS.py --debug

# Start only a specific component (for testing)
python JARVIS.py --component backend
python JARVIS.py --component local_client
python JARVIS.py --component settings_ui

# Disable automatic restart on crash
python JARVIS.py --no-monitor

# Custom log file
python JARVIS.py --log-file /path/to/custom.log
```

### System Tray Menu

When running with system tray (default), right-click the tray icon to access:

- **Show Settings**: Open the Settings UI
- **Status**: View component status (Backend, Client, UI)
- **Restart All**: Restart all components
- **View Logs**: Open logs directory
- **Quit**: Gracefully shutdown JARVIS

## Architecture

### Component Startup Order

1. **Backend Server** starts first (port 5000)
2. **Local Client** starts after backend is ready
3. **Settings UI** starts last

Each component has a configurable startup delay to ensure proper initialization.

### Process Monitoring

The launcher continuously monitors all components:

- Checks process health every 2 seconds
- Detects crashed components immediately
- Automatically restarts crashed components (up to 3 attempts)
- Prevents restart loops (30-second cooldown)

### Crash Recovery

When a component crashes:

1. Launcher detects the crash
2. Logs the crash details
3. Waits for restart delay (default: 5 seconds)
4. Attempts to restart the component
5. If restart fails 3 times, stops monitoring

### Graceful Shutdown

When shutting down:

1. Components stop in reverse order (UI → Client → Backend)
2. Each component gets 10 seconds for graceful shutdown
3. Force kill if graceful shutdown fails
4. All processes cleaned up

## Configuration

### Component Configuration

Edit `application_launcher.py` to customize component behavior:

```python
ComponentConfig(
    name='Backend Server',
    script_path='backend/server.py',
    working_dir='backend',
    startup_delay=2.0,           # Wait time after start
    max_restart_attempts=3,      # Max restart attempts
    restart_delay=5.0            # Wait before restart
)
```

### Logging

Logs are stored in `data/logs/` with timestamps:

```
data/logs/launcher_20260209_143022.log
```

Log level can be set via command-line:
- Default: `INFO`
- Debug mode: `DEBUG` (use `--debug` flag)

## Testing

### Basic Tests

Run basic functionality tests:

```bash
python test_launcher_basic.py
```

This tests:
- ApplicationLauncher instantiation
- SystemTrayManager instantiation
- Component configuration
- Status reporting

### Manual Testing

1. Start the launcher:
   ```bash
   python JARVIS.py
   ```

2. Verify all components start:
   - Check console output for "✅ All components started successfully"
   - Check system tray icon appears
   - Check logs in `data/logs/`

3. Test crash recovery:
   - Kill a component process manually
   - Verify launcher detects and restarts it

4. Test graceful shutdown:
   - Press Ctrl+C or use tray menu "Quit"
   - Verify all components stop cleanly

## Troubleshooting

### Component Fails to Start

**Symptoms**: Component exits immediately after start

**Solutions**:
1. Check component logs in `data/logs/`
2. Verify script path is correct
3. Ensure all dependencies are installed
4. Check for port conflicts (backend uses port 5000)

### System Tray Icon Not Appearing

**Symptoms**: No tray icon visible

**Solutions**:
1. Verify `pystray` is installed: `pip install pystray`
2. Check if system tray is enabled in OS
3. Try running without tray: `python JARVIS.py --no-tray`

### Components Keep Crashing

**Symptoms**: Restart loop, components crash repeatedly

**Solutions**:
1. Check logs for error details
2. Verify configuration files exist
3. Check API keys are valid
4. Ensure required services are available (Firebase, etc.)

### High CPU Usage

**Symptoms**: Launcher uses excessive CPU

**Solutions**:
1. Check monitoring interval (default: 2 seconds)
2. Verify components aren't in crash loop
3. Check for resource leaks in components

## Development

### Adding New Components

1. Add component configuration in `_define_components()`:

```python
'new_component': ComponentConfig(
    name='New Component',
    script_path='path/to/script.py',
    working_dir='path/to/dir',
    startup_delay=1.0,
    max_restart_attempts=3,
    restart_delay=5.0
)
```

2. Add to startup order in `start()` method

3. Add to shutdown order in `shutdown()` method

### Customizing System Tray

Edit `system_tray_manager.py`:

- Change icon: Update `_create_icon_image()`
- Add menu items: Update `_create_icon()` menu
- Add callbacks: Add methods and wire to menu items

## Requirements Validation

This implementation satisfies the following requirements:

- ✅ **Req 1.5**: Settings UI launches automatically
- ✅ **Req 1.6**: Backend Server starts automatically
- ✅ **Req 1.7**: Local Client starts automatically
- ✅ **Req 1.8**: Synchronized state between components
- ✅ **Req 8.1**: Components start in correct order
- ✅ **Req 8.2**: Graceful shutdown
- ✅ **Req 8.3**: Error logging
- ✅ **Req 8.4**: Configuration restoration on restart
- ✅ **Req 8.5**: Pairing state restoration on restart
- ✅ **Req 8.6**: Minimize to system tray
- ✅ **Req 8.7**: Restore from system tray
- ✅ **Req 8.8**: Quit option in tray menu
- ✅ **Req 10.4**: Automatic component restart on crash
- ✅ **Req 10.5**: Crash detection and recovery

## Future Enhancements

Potential improvements:

1. **Web-based Dashboard**: Real-time component monitoring
2. **Remote Control**: Start/stop components remotely
3. **Health Checks**: Ping endpoints to verify component health
4. **Performance Metrics**: Track CPU, memory, response times
5. **Auto-update**: Check for and install updates
6. **Component Dependencies**: Define startup dependencies
7. **Custom Restart Policies**: Per-component restart strategies
8. **Notification System**: Alert on crashes or issues

## License

Part of the JARVIS project. See main LICENSE file for details.
