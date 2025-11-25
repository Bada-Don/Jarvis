"""
Test script to help identify modal window titles
Run this while the modal is visible to see all window titles
"""
import win32gui
import time

def list_all_windows():
    """List all visible windows with their titles."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Only show windows with titles
                class_name = win32gui.GetClassName(hwnd)
                windows.append((window_text, class_name, hwnd))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def main():
    print("=" * 80)
    print("JARVIS Modal Detection Helper")
    print("=" * 80)
    print("\nThis script will list all visible windows every 2 seconds.")
    print("Start FlexiSIGN and watch for the modal window title.\n")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            windows = list_all_windows()
            
            print(f"\n[{time.strftime('%H:%M:%S')}] Found {len(windows)} visible windows:")
            print("-" * 80)
            
            for i, (title, class_name, hwnd) in enumerate(windows, 1):
                print(f"{i:3d}. Title: '{title}'")
                print(f"     Class: {class_name}")
                print(f"     HWND:  {hwnd}")
                print()
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nStopped. Use the window title you found in config.py")
        print("Example: STARTUP_MODAL_TITLE = 'FlexiSIGN'")

if __name__ == '__main__':
    main()
