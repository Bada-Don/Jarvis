import socketio
import pyautogui
import time
import os
import subprocess
import psutil
import win32gui
import win32con
import sys

# Import configuration
try:
    from config import *
except ImportError:
    print("⚠️ Warning: config.py not found, using default settings")
    SERVER_URL = 'http://localhost:5000'
    STARTUP_MODAL_ENABLED = True
    STARTUP_MODAL_TITLE = "FlexiSIGN"
    STARTUP_MODAL_BUTTON = "OK"
    STARTUP_MODAL_TIMEOUT = 30
    MODAL_CHECK_INTERVAL = 1

# Import FlexiSign Manager
try:
    from flexisign_manager import FlexiSignManager
    FLEXISIGN_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: flexisign_manager.py not found, using legacy mode")
    FLEXISIGN_MANAGER_AVAILABLE = False

# Initialize SocketIO Client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to Server')

@sio.event
def disconnect():
    print('Disconnected from Server')

@sio.event
def command(data):
    print('Received command:', data)
    execute_command(data)

def send_status(message, status_type="info"):
    """Send status update to server."""
    try:
        sio.emit('status_update', {
            'message': message,
            'type': status_type,
            'timestamp': time.time()
        })
        print(f"📤 Status sent: {message}")
    except Exception as e:
        print(f"Failed to send status: {e}")

def is_process_running(process_name):
    """Check if a process is running by name."""
    for proc in psutil.process_iter(['name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def find_window_by_title(title, exact_match=False):
    """Find a window by its title (partial or exact match)."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Only check non-empty titles
                # Debug: print all visible windows
                # print(f"DEBUG: Found window: '{window_text}'")
                if exact_match:
                    if window_text.lower() == title.lower():
                        print(f"✓ EXACT MATCH FOUND: '{window_text}'")
                        windows.append(hwnd)
                else:
                    if title.lower() in window_text.lower():
                        print(f"✓ MATCH FOUND: '{window_text}'")
                        windows.append(hwnd)
        return True
    
    windows = []
    print(f"Searching for window containing: '{title}' (exact={exact_match})")
    win32gui.EnumWindows(callback, windows)
    
    if windows:
        print(f"Found {len(windows)} matching window(s)")
    else:
        print(f"No windows found matching '{title}'")
    
    return windows[0] if windows else None

def wait_for_modal_and_click(modal_title, button_text="OK", timeout=30, check_interval=None):
    """
    Wait for a modal dialog to appear and click a button on it.
    
    Args:
        modal_title: The title of the modal window to look for
        button_text: The text of the button to click (default: "OK")
        timeout: Maximum time to wait in seconds
        check_interval: How often to check for the modal in seconds
    
    Returns:
        True if modal was found and clicked, False if timeout
    """
    if check_interval is None:
        check_interval = MODAL_CHECK_INTERVAL if 'MODAL_CHECK_INTERVAL' in globals() else 1
    
    print(f"Waiting for modal: '{modal_title}' (timeout: {timeout}s)...")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        # Look for the modal window
        modal_hwnd = find_window_by_title(modal_title, exact_match=False)
        
        if modal_hwnd:
            print(f"✓ Modal found: '{modal_title}'")
            send_status(f"Modal detected, clicking {button_text}...", "info")
            
            # Bring modal to front
            bring_window_to_front(modal_hwnd)
            time.sleep(0.5)
            
            # Try to find the button by text using pyautogui
            try:
                # Take a screenshot and look for the button
                # For now, we'll use a simple approach: press Enter or click center
                # You can enhance this with OCR or image recognition
                
                # Method 1: Press Enter (works for most OK buttons)
                print(f"Pressing Enter to click {button_text}...")
                pyautogui.press('enter')
                time.sleep(0.5)
                
                # Verify modal is gone
                if not find_window_by_title(modal_title, exact_match=False):
                    print(f"✓ Modal closed successfully")
                    send_status(f"Modal handled successfully", "success")
                    return True
                else:
                    # Method 2: Try clicking center of modal
                    print(f"Enter didn't work, trying to click center...")
                    rect = win32gui.GetWindowRect(modal_hwnd)
                    center_x = (rect[0] + rect[2]) // 2
                    center_y = (rect[1] + rect[3]) // 2
                    pyautogui.click(center_x, center_y)
                    time.sleep(0.5)
                    return True
                    
            except Exception as e:
                print(f"Error clicking modal button: {e}")
                return False
        
        # Wait before checking again
        time.sleep(check_interval)
    
    print(f"⚠️ Timeout: Modal '{modal_title}' not found within {timeout}s")
    return False

def bring_window_to_front(hwnd):
    """Bring a window to the front."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

def get_screen_center():
    """Get the center coordinates of the screen."""
    screen_width, screen_height = pyautogui.size()
    return screen_width // 2, screen_height // 2

def execute_command(command_data):
    """
    Executes the command received from the server.
    """
    action = command_data.get('action')
    
    if action == 'flexisign_workflow':
        # Use new FlexiSign Manager if available
        if FLEXISIGN_MANAGER_AVAILABLE:
            try:
                send_status("Starting FlexiSign automation (new manager)...", "info")
                manager = FlexiSignManager()
                success = manager.ensure_proper_state()
                
                if success:
                    send_status("FlexiSign Pro is ready!", "success")
                    
                    # Execute remaining workflow steps (after FlexiSign is ready)
                    steps = command_data.get('steps', [])
                    for step in steps:
                        step_type = step.get('type')
                        
                        # Skip process/window checks (already handled by manager)
                        if step_type in ['check_process', 'check_window', 'wait_for_modal']:
                            continue
                        
                        # Execute other steps
                        if step_type == 'notification':
                            message = step.get('message')
                            print(f"NOTIFICATION: {message}")
                            send_status(message, "info")
                        
                        elif step_type == 'press_key':
                            key = step.get('key')
                            print(f"Pressing key: {key}")
                            pyautogui.press(key)
                        
                        elif step_type == 'click_center':
                            print("Clicking at screen center...")
                            center_x, center_y = get_screen_center()
                            pyautogui.click(center_x, center_y)
                        
                        elif step_type == 'type_text':
                            text = step.get('text')
                            print(f"Typing text: {text}")
                            pyautogui.write(text, interval=0.05)
                        
                        time.sleep(0.5)
                else:
                    send_status("Failed to start FlexiSign Pro", "error")
                
                return  # Exit after using new manager
                
            except Exception as e:
                print(f"Error using FlexiSign Manager: {e}")
                send_status(f"Manager error: {e}, falling back to legacy mode", "warning")
                # Fall through to legacy mode
        
        # Legacy mode (original implementation)
        steps = command_data.get('steps', [])
        for step in steps:
            step_type = step.get('type')
            
            if step_type == 'notification':
                message = step.get('message')
                print(f"NOTIFICATION: {message}")
                send_status(message, "info")
            
            elif step_type == 'check_process':
                process_name = step.get('process_name')
                exe_path = step.get('exe_path')
                wait_for_modal = step.get('wait_for_modal', False)
                modal_title = step.get('modal_title', '')
                modal_button = step.get('modal_button', 'OK')
                
                print(f"Checking if process '{process_name}' is running...")
                process_was_started = False
                
                if not is_process_running(process_name):
                    print(f"Process not found. Starting: {exe_path}")
                    send_status(f"Starting {process_name}...", "info")
                    try:
                        subprocess.Popen([exe_path])
                        process_was_started = True
                        print("Waiting for process to start...")
                        time.sleep(5)  # Wait for the process to initialize
                    except Exception as e:
                        print(f"Error starting process: {e}")
                        send_status(f"Error starting process: {e}", "error")
                else:
                    print(f"Process '{process_name}' is already running.")
                    send_status(f"{process_name} is ready", "success")
                
                # If we just started the process and need to handle a modal
                if process_was_started and wait_for_modal and modal_title:
                    print(f"Process was just started, waiting for modal...")
                    modal_timeout = step.get('modal_timeout', 30)
                    if wait_for_modal_and_click(modal_title, modal_button, timeout=modal_timeout):
                        print(f"✓ Modal handled successfully")
                    else:
                        print(f"⚠️ Modal not found or couldn't be handled")
                        send_status(f"Warning: Expected modal not found", "warning")
            
            elif step_type == 'check_window':
                window_title = step.get('window_title')
                
                print(f"Checking for window: '{window_title}'...")
                hwnd = find_window_by_title(window_title)
                
                if hwnd:
                    print(f"Window found. Bringing to front...")
                    send_status(f"Found {window_title}, switching to it...", "success")
                    bring_window_to_front(hwnd)
                    time.sleep(1)  # Wait for window to come to front
                else:
                    print(f"Window '{window_title}' not found. Opening via Windows search...")
                    send_status(f"Opening {window_title}...", "info")
                    
                    # Press Windows key
                    pyautogui.press('win')
                    time.sleep(1)
                    
                    # Type the program name (extract first part of window title)
                    search_term = window_title.split()[0]  # e.g., "FlexiSIGN-PRO" -> "FlexiSIGN-PRO"
                    pyautogui.write(search_term, interval=0.05)
                    time.sleep(2)
                    
                    # Press Enter to open
                    pyautogui.press('enter')
                    print(f"Waiting for '{window_title}' to open...")
                    time.sleep(30)  # Wait for FlexiSIGN to load (takes ~20 seconds)
                    
                    # Try to find the window again
                    hwnd = find_window_by_title(window_title)
                    if hwnd:
                        print(f"Window opened successfully. Bringing to front...")
                        send_status(f"{window_title} opened successfully!", "success")
                        bring_window_to_front(hwnd)
                        time.sleep(1)
                    else:
                        print(f"Warning: Could not find window after opening. Continuing anyway...")
            
            elif step_type == 'press_key':
                key = step.get('key')
                print(f"Pressing key: {key}")
                pyautogui.press(key)
            
            elif step_type == 'click_center':
                print("Clicking at screen center...")
                center_x, center_y = get_screen_center()
                pyautogui.click(center_x, center_y)
            
            elif step_type == 'type_text':
                text = step.get('text')
                print(f"Typing text: {text}")
                pyautogui.write(text, interval=0.05)
            
            elif step_type == 'wait_for_modal':
                modal_title = step.get('modal_title')
                button_text = step.get('button_text', 'OK')
                timeout = step.get('timeout', 30)
                print(f"Waiting for modal: '{modal_title}'...")
                send_status(f"Waiting for modal: {modal_title}...", "info")
                if wait_for_modal_and_click(modal_title, button_text, timeout):
                    print(f"✓ Modal handled")
                else:
                    print(f"⚠️ Modal timeout")
            
            time.sleep(0.5)
    
    elif action == 'sequence':
        # Legacy support for old sequence commands
        steps = command_data.get('steps', [])
        for step in steps:
            step_type = step.get('type')
            
            if step_type == 'notification':
                print(f"NOTIFICATION: {step.get('message')}")
            
            elif step_type == 'open_app':
                app_path = step.get('path')
                print(f"Opening app: {app_path}")
                if "notepad" in app_path.lower():
                    subprocess.Popen(['notepad.exe'])
                    time.sleep(1)
            
            elif step_type == 'type_text':
                text = step.get('text')
                print(f"Typing text: {text}")
                pyautogui.write(text, interval=0.05)

            time.sleep(0.5)

def main():
    print("Starting Jarvis Local Client...")
    print("Auto-reload enabled. Edit this file and save to reload.")
    
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sio.disconnect()
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)
        main()

if __name__ == '__main__':
    main()
