"""
FlexiSIGN Window Activation Test Script

This script tests various methods to bring FlexiSIGN window to the foreground,
even when another window is currently active.

Tests multiple activation techniques:
1. pygetwindow activate()
2. win32gui SetForegroundWindow
3. win32gui ShowWindow + SetForegroundWindow
4. Alt+Tab simulation
5. Minimize all + restore target
6. Force activation with keyboard input

Usage:
    python test_window_activation.py
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


def print_separator():
    """Print a visual separator."""
    print("=" * 70)


def find_flexisign_window():
    """Find FlexiSIGN window."""
    print("\n🔍 Searching for FlexiSIGN window...")
    
    for window in gw.getAllWindows():
        title_lower = window.title.lower()
        if "flexisign-pro" in title_lower:
            print(f"✓ Found: {window.title}")
            print(f"  Handle: {window._hWnd}")
            print(f"  Position: ({window.left}, {window.top})")
            print(f"  Size: {window.width}x{window.height}")
            print(f"  Minimized: {window.isMinimized}")
            print(f"  Maximized: {window.isMaximized}")
            print(f"  Active: {window.isActive}")
            return window
    
    print("❌ FlexiSIGN window not found")
    return None


def get_foreground_window_info():
    """Get info about currently active window."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        title = win32gui.GetWindowText(hwnd)
        return hwnd, title
    return None, None


def method_1_pygetwindow(window):
    """Method 1: Use pygetwindow activate()."""
    print("\n📌 Method 1: pygetwindow.activate()")
    print("-" * 70)
    
    try:
        window.activate()
        time.sleep(0.5)
        
        if window.isActive:
            print("✓ SUCCESS: Window is now active")
            return True
        else:
            print("❌ FAILED: Window not active after activate()")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_2_setforeground(window):
    """Method 2: Use win32gui SetForegroundWindow."""
    print("\n📌 Method 2: win32gui.SetForegroundWindow()")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground after SetForegroundWindow()")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_3_show_and_setforeground(window):
    """Method 3: ShowWindow + SetForegroundWindow."""
    print("\n📌 Method 3: ShowWindow(SW_RESTORE) + SetForegroundWindow()")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        
        # First restore if minimized
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.2)
        
        # Then bring to foreground
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_4_alttab_simulation(window):
    """Method 4: Simulate Alt+Tab to switch to window."""
    print("\n📌 Method 4: Alt+Tab Simulation")
    print("-" * 70)
    print("⚠️ This will cycle through windows - watch carefully!")
    
    try:
        hwnd = window._hWnd
        
        # Get current foreground window
        initial_hwnd, initial_title = get_foreground_window_info()
        print(f"Current window: {initial_title}")
        
        # Try Alt+Tab multiple times to find FlexiSIGN
        max_attempts = 10
        for i in range(max_attempts):
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.3)
            
            current_hwnd, current_title = get_foreground_window_info()
            print(f"  Attempt {i+1}: {current_title}")
            
            if current_hwnd == hwnd:
                print("✓ SUCCESS: Found FlexiSIGN via Alt+Tab")
                return True
        
        print(f"❌ FAILED: Didn't find FlexiSIGN in {max_attempts} attempts")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_5_force_with_input(window):
    """Method 5: Force activation by simulating input to the window."""
    print("\n📌 Method 5: Force with BringWindowToTop + SetFocus")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        
        # Multiple aggressive techniques
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.1)
        
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        time.sleep(0.1)
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        # Try to set focus
        try:
            win32gui.SetFocus(hwnd)
        except:
            pass
        
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_6_attach_thread_input(window):
    """Method 6: Attach thread input and force foreground."""
    print("\n📌 Method 6: AttachThreadInput + SetForegroundWindow")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        
        # Get current foreground window thread
        foreground_hwnd = win32gui.GetForegroundWindow()
        foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
        
        # Get target window thread
        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
        
        if foreground_thread != target_thread:
            # Attach input threads
            ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, True)
            
            # Bring to foreground
            win32gui.BringWindowToTop(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(hwnd)
            
            # Detach threads
            ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, False)
        else:
            # Same thread, just set foreground
            win32gui.SetForegroundWindow(hwnd)
        
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_7_click_window(window):
    """Method 7: Click on the window to activate it."""
    print("\n📌 Method 7: Click Window Center")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        
        # Restore if minimized
        if window.isMinimized:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        
        # Calculate center of window
        center_x = window.left + (window.width // 2)
        center_y = window.top + (window.height // 2)
        
        print(f"Clicking at ({center_x}, {center_y})")
        
        # Click the window
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground after click")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def method_8_combined_aggressive(window):
    """Method 8: Combined aggressive approach."""
    print("\n📌 Method 8: Combined Aggressive Activation")
    print("-" * 70)
    
    try:
        hwnd = window._hWnd
        
        print("Step 1: Restore window if minimized...")
        if window.isMinimized:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
        
        print("Step 2: Attach thread input...")
        foreground_hwnd = win32gui.GetForegroundWindow()
        foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
        
        if foreground_thread != target_thread:
            ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, True)
        
        print("Step 3: Bring to top...")
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.1)
        
        print("Step 4: Show window...")
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        time.sleep(0.1)
        
        print("Step 5: Set foreground...")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        print("Step 6: Set focus...")
        try:
            win32gui.SetFocus(hwnd)
        except:
            pass
        
        if foreground_thread != target_thread:
            print("Step 7: Detach thread input...")
            ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, False)
        
        print("Step 8: Click window center...")
        center_x = window.left + (window.width // 2)
        center_y = window.top + (window.height // 2)
        pyautogui.click(center_x, center_y)
        
        time.sleep(0.5)
        
        current_hwnd, _ = get_foreground_window_info()
        if current_hwnd == hwnd:
            print("✓ SUCCESS: Window is now foreground")
            return True
        else:
            print("❌ FAILED: Window not foreground after all attempts")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    print_separator()
    print("FLEXISIGN WINDOW ACTIVATION TEST")
    print_separator()
    
    # Find FlexiSIGN window
    window = find_flexisign_window()
    if window is None:
        print("\n❌ Cannot proceed without FlexiSIGN window")
        print("Please start FlexiSIGN and try again")
        sys.exit(1)
    
    # Show current foreground window
    print("\n📋 Current State:")
    print_separator()
    current_hwnd, current_title = get_foreground_window_info()
    print(f"Foreground window: {current_title}")
    print(f"FlexiSIGN active: {window.isActive}")
    
    if window.isActive:
        print("\n⚠️ FlexiSIGN is already active!")
        print("Please switch to another window and run this script again.")
        sys.exit(0)
    
    # Test each method
    print("\n" + "=" * 70)
    print("TESTING ACTIVATION METHODS")
    print("=" * 70)
    
    methods = [
        ("pygetwindow activate()", method_1_pygetwindow),
        ("SetForegroundWindow", method_2_setforeground),
        ("ShowWindow + SetForegroundWindow", method_3_show_and_setforeground),
        ("Alt+Tab Simulation", method_4_alttab_simulation),
        ("Force with BringWindowToTop", method_5_force_with_input),
        ("AttachThreadInput", method_6_attach_thread_input),
        ("Click Window", method_7_click_window),
        ("Combined Aggressive", method_8_combined_aggressive),
    ]
    
    results = {}
    
    for method_name, method_func in methods:
        # Switch away from FlexiSIGN before each test
        if window.isActive:
            print(f"\n⚠️ Switching away from FlexiSIGN before testing {method_name}...")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
        
        # Test the method
        success = method_func(window)
        results[method_name] = success
        
        # Wait between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    successful_methods = []
    failed_methods = []
    
    for method_name, success in results.items():
        status = "✓ PASS" if success else "❌ FAIL"
        print(f"{status}: {method_name}")
        
        if success:
            successful_methods.append(method_name)
        else:
            failed_methods.append(method_name)
    
    print("\n" + "=" * 70)
    print(f"Successful: {len(successful_methods)}/{len(methods)}")
    print("=" * 70)
    
    if successful_methods:
        print("\n✓ Working methods:")
        for method in successful_methods:
            print(f"  - {method}")
        
        print("\n💡 Recommendation:")
        print(f"   Use: {successful_methods[0]}")
    else:
        print("\n❌ No methods worked!")
        print("\nPossible issues:")
        print("  - Windows security restrictions")
        print("  - FlexiSIGN running with different privileges")
        print("  - Another application blocking activation")
        print("\nTry:")
        print("  - Run this script as Administrator")
        print("  - Close other applications")
        print("  - Restart FlexiSIGN")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
