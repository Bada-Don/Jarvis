# JARVIS Local Client - Modal Handling Guide

## Overview
The local client now supports automatic handling of modal dialogs that appear when FlexiSIGN starts up.

## Configuration

Edit `config.py` to customize the modal handling:

```python
# Enable/disable modal handling
STARTUP_MODAL_ENABLED = True

# Modal window title (can be partial match)
STARTUP_MODAL_TITLE = "FlexiSIGN"

# Button text to click
STARTUP_MODAL_BUTTON = "OK"

# How long to wait for modal (seconds)
STARTUP_MODAL_TIMEOUT = 30
```

## How It Works

1. **Process Check**: When the client checks if FlexiSIGN is running
2. **Process Start**: If not running, it starts the process
3. **Modal Detection**: If `wait_for_modal` is enabled, it waits for the modal
4. **Auto-Click**: When modal appears, it automatically clicks the button

## Finding the Modal Title

If you don't know the exact modal title:

1. Run the client with debug mode
2. Start FlexiSIGN manually
3. Check the console output for window titles
4. Update `STARTUP_MODAL_TITLE` in `config.py`

## Modal Handling Methods

The client tries two methods to close the modal:

1. **Press Enter** - Works for most OK buttons
2. **Click Center** - Fallback if Enter doesn't work

## Troubleshooting

### Modal not detected
- Check the modal title is correct (case-insensitive, partial match)
- Increase `STARTUP_MODAL_TIMEOUT` if FlexiSIGN takes longer to show modal
- Check console logs for window detection messages

### Modal detected but not closed
- Try changing `STARTUP_MODAL_BUTTON` to match the actual button text
- The client will try pressing Enter first, then clicking center
- Check if the modal requires a different key (Tab, Space, etc.)

### Process starts but modal never appears
- Set `STARTUP_MODAL_ENABLED = False` if no modal is needed
- The modal might have a different title - check console logs

## Advanced Usage

You can also add standalone modal handling steps in workflows:

```python
{
    "type": "wait_for_modal",
    "modal_title": "License Agreement",
    "button_text": "Accept",
    "timeout": 20
}
```

## Example Workflow

```python
{
    "action": "flexisign_workflow",
    "steps": [
        {
            "type": "check_process",
            "process_name": "FlexiSIGN",
            "exe_path": "C:\\Program Files\\FlexiSIGN\\flexisign.exe",
            "wait_for_modal": True,
            "modal_title": "FlexiSIGN Startup",
            "modal_button": "OK",
            "modal_timeout": 30
        },
        {
            "type": "check_window",
            "window_title": "FlexiSIGN-PRO"
        }
    ]
}
```
