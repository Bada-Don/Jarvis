import socketio
import pyautogui
import time
import os
import subprocess
import psutil
import win32gui
import win32con
import sys

# Initialize SocketIO Client
sio = socketio.Client()

SERVER_URL = 'http://localhost:5000'

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


def find_window_by_title(title):
    """Find a window by its title (partial match)."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Only check non-empty titles
                # Debug: print all visible windows
                # print(f"DEBUG: Found window: '{window_text}'")
                if title.lower() in window_text.lower():
                    print(f"✓ MATCH FOUND: '{window_text}'")
                    windows.append(hwnd)
        return True
    
    windows = []
    print(f"Searching for window containing: '{title}'")
    win32gui.EnumWindows(callback, windows)
    
    if windows:
        print(f"Found {len(windows)} matching window(s)")
    else:
        print(f"No windows found matching '{title}'")
    
    return windows[0] if windows else None

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
                
                print(f"Checking if process '{process_name}' is running...")
                if not is_process_running(process_name):
                    print(f"Process not found. Starting: {exe_path}")
                    send_status(f"Starting {process_name}...", "info")
                    try:
                        subprocess.Popen([exe_path])
                        print("Waiting for process to start...")
                        time.sleep(5)  # Wait for the process to initialize
                    except Exception as e:
                        print(f"Error starting process: {e}")
                else:
                    print(f"Process '{process_name}' is already running.")
                    send_status(f"{process_name} is ready", "success")
            
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
