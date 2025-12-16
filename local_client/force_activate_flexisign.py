"""
Force Activate FlexiSIGN Window

A focused script that uses the most reliable method to bring FlexiSIGN
to the foreground, even when another window is active.

This uses a combination of:
1. Thread input attachment
2. Window restoration
3. Multiple activation calls
4. Physical click as fallback

Usage:
    python force_activate_flexisign.py
"""

import sys
import time
import ctypes

try:
    import pygetwindow as gw
    import win32gui
    import win32con
    import win32process
    import pyautogui
except ImportError as e:
    print(f"❌ Error: Missing required module: {e}")
    print("Install with: pip install pygetwindow pywin32 pyautogui")
    sys.exit(1)


def find_flexisign_window():
    """
    Detect FlexiSIGN window by window title containing 'FlexiSIGN'.
    
    Returns:
        pygetwindow Window object if found, None otherwise.
    """
    try:
        for window in gw.getAllWindows():
            # Only match windows with "FlexiSIGN" (not just "flexi")
            # This avoids matching IDE windows with flexisign files open
            title_lower = window.title.lower()
            if "flexisign-pro" in title_lower:
                print(f"Found FlexiSIGN window: {window.title}")
                return window
    except Exception as e:
        print(f"Error finding window: {e}")
    return None


def get_pid_from_window(window):
    """
    Retrieve process ID (PID) from window handle.
    
    Args:
        window: pygetwindow Window object
        
    Returns:
        Process ID if successful, None otherwise.
    """
    try:
        hwnd = window._hWnd
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception:
        return None


def method_1_thread_attach(window, verbose=True):
    """
    Method 1: AttachThreadInput technique (most reliable).
    
    This method attaches the input processing of the foreground window's thread
    to the target window's thread, allowing us to change the foreground window.
    
    Args:
        window: pygetwindow Window object
        verbose: Print status messages
        
    Returns:
        True if window was successfully activated, False otherwise
    """
    if verbose:
        print("  Method 1: AttachThreadInput")
    
    hwnd = window._hWnd
    
    try:
        # Restore if minimized
        if window.isMinimized:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
        
        # Check if already active
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd == hwnd:
            if verbose:
                print("    ✓ Already active")
            return True
        
        # Get thread IDs
        foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
        
        # Attach threads if different
        threads_attached = False
        if foreground_thread != target_thread:
            try:
                ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, True)
                threads_attached = True
            except Exception as e:
                if verbose:
                    print(f"    ⚠️ Thread attach failed: {e}")
                return False
        
        # Activate window
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.05)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        time.sleep(0.05)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        # Try to set focus
        try:
            win32gui.SetFocus(hwnd)
        except:
            pass
        
        # Detach threads
        if threads_attached:
            try:
                ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, False)
            except:
                pass
        
        # Verify
        time.sleep(0.2)
        current_foreground = win32gui.GetForegroundWindow()
        
        if current_foreground == hwnd:
            if verbose:
                print("    ✓ Success")
            return True
        else:
            if verbose:
                print("    ❌ Failed")
            return False
            
    except Exception as e:
        if verbose:
            print(f"    ❌ Error: {e}")
        return False


def method_2_click_window(window, verbose=True):
    """
    Method 2: Click window center (reliable fallback).
    
    This method physically clicks the center of the window to activate it.
    Works even when thread attachment fails.
    
    Args:
        window: pygetwindow Window object
        verbose: Print status messages
        
    Returns:
        True if window was successfully activated, False otherwise
    """
    if verbose:
        print("  Method 2: Click Window Center")
    
    hwnd = window._hWnd
    
    try:
        # Restore if minimized
        if window.isMinimized:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        
        # Bring to top first
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.1)
        except:
            pass
        
        # Calculate center
        center_x = window.left + (window.width // 2)
        center_y = window.top + (window.height // 2)
        
        if verbose:
            print(f"    Clicking at ({center_x}, {center_y})")
        
        # Click the window
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)
        
        # Verify
        current_foreground = win32gui.GetForegroundWindow()
        if current_foreground == hwnd:
            if verbose:
                print("    ✓ Success")
            return True
        else:
            if verbose:
                print("    ❌ Failed")
            return False
            
    except Exception as e:
        if verbose:
            print(f"    ❌ Error: {e}")
        return False


def force_activate_window(window, verbose=True):
    """
    Force activate a window using two-method approach with fallback.
    
    Primary Method: AttachThreadInput (most reliable for cross-thread activation)
    Fallback Method: Click Window Center (works when thread attach fails)
    
    Args:
        window: pygetwindow Window object
        verbose: Print status messages
        
    Returns:
        True if window was successfully activated, False otherwise
    """
    if verbose:
        print(f"Attempting to activate: {window.title}")
    
    # Check if already active
    if window.isActive:
        if verbose:
            print("  ✓ Window already active")
        return True
    
    # Try Method 1: AttachThreadInput
    if method_1_thread_attach(window, verbose):
        return True
    
    # Fallback to Method 2: Click Window
    if verbose:
        print("  Primary method failed, trying fallback...")
    
    if method_2_click_window(window, verbose):
        return True
    
    # Both methods failed
    if verbose:
        print("  ❌ All activation methods failed")
    return False


def main():
    print("=" * 60)
    print("FORCE ACTIVATE FLEXISIGN")
    print("=" * 60)
    
    # Find FlexiSIGN
    print("\n1. Finding FlexiSIGN window...")
    window = find_flexisign_window()
    
    if window is None:
        print("❌ FlexiSIGN window not found")
        print("   Please ensure FlexiSIGN is running")
        sys.exit(1)
    
    print(f"✓ Found: {window.title}")
    
    # Check current state
    print("\n2. Checking current state...")
    if window.isActive:
        print("✓ FlexiSIGN is already active")
        print("\n💡 To test activation, switch to another window first")
        sys.exit(0)
    else:
        print("⚠️ FlexiSIGN is NOT active")
        
        # Show current foreground window
        try:
            foreground_hwnd = win32gui.GetForegroundWindow()
            foreground_title = win32gui.GetWindowText(foreground_hwnd)
            print(f"   Current foreground: {foreground_title}")
        except:
            pass
    
    # Activate FlexiSIGN
    print("\n3. Activating FlexiSIGN with two-method approach...")
    print("-" * 60)
    
    success = force_activate_window(window, verbose=True)
    
    # Results
    print("\n" + "=" * 60)
    if success:
        print("✓ SUCCESS: FlexiSIGN is now active")
        print("=" * 60)
        print("\n💡 Two-Method Approach:")
        print("   Primary: AttachThreadInput (cross-thread activation)")
        print("   Fallback: Click Window Center (physical click)")
        print("\n✓ This has been integrated into flexisign_uia.py")
        return 0
    else:
        print("❌ FAILED: Could not activate FlexiSIGN")
        print("=" * 60)
        print("\nBoth methods failed:")
        print("  - Method 1: AttachThreadInput")
        print("  - Method 2: Click Window Center")
        print("\nTroubleshooting:")
        print("  1. Try running as Administrator")
        print("  2. Check if FlexiSIGN is responding")
        print("  3. Close other applications that might block activation")
        print("  4. Try the comprehensive test: python test_window_activation.py")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
