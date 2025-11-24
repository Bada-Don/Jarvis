import socketio
import pyautogui
import time
import os
import subprocess

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

def execute_command(command_data):
    """
    Executes the command received from the server.
    """
    action = command_data.get('action')
    
    if action == 'sequence':
        steps = command_data.get('steps', [])
        for step in steps:
            step_type = step.get('type')
            
            if step_type == 'notification':
                print(f"NOTIFICATION: {step.get('message')}")
            
            elif step_type == 'open_app':
                app_path = step.get('path')
                print(f"Opening app: {app_path}")
                # For safety in this demo, we only actually open Notepad if explicitly requested
                # or just print it.
                if "notepad" in app_path.lower():
                    subprocess.Popen(['notepad.exe'])
                    time.sleep(1) # Wait for it to open
            
            elif step_type == 'type_text':
                text = step.get('text')
                print(f"Typing text: {text}")
                # Safety: Only type if we are sure (e.g., user focused the window)
                # For this demo, we will just print what we would type.
                # pyautogui.write(text, interval=0.05) 
                print(f"[MOCK ACTION] pyautogui.write('{text}')")

            time.sleep(0.5)

def main():
    try:
        sio.connect(SERVER_URL)
        sio.wait()
    except Exception as e:
        print(f"Connection failed: {e}")
        time.sleep(5)
        main()

if __name__ == '__main__':
    main()
