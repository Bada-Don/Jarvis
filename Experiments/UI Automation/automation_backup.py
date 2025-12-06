"""
Sample FlexiSIGN Automation Script
Demonstrates: Text Tool -> Write Text -> Select Tool -> Resize

Flow:
1. Click Text Tool
2. Write a name in the center of the canvas
3. Click Select Tool
4. Set size to 5.0 width and 1.0 height
"""

import time
import pyautogui
from elements import (
    create_uia,
    list_processes,
    get_root_for_pid,
    get_text_tool,
    get_select_tool,
    get_scale_width_input,
    get_scale_height_input,
    get_proportional_checkbox,
    get_font_dropdown,
    get_character_tab_item,
    get_scale_tab_item,
    invoke,
    set_value,
    toggle_checkbox,
    get_bounding_rect,
)

# ============================================
# CONFIGURATION - Set your FlexiSIGN PID here
# ============================================
FLEXISIGN_PID = None  # Set to None for auto-detect, or enter PID manually (e.g., 14480)
# ============================================


def find_flexisign_process():
    """Find FlexiSIGN process from running processes."""
    procs = list_processes()
    flexisign_procs = []
    for pid, name in procs:
        if "flexi" in name.lower():
            flexisign_procs.append((pid, name))
    
    if not flexisign_procs:
        return None
    
    if len(flexisign_procs) == 1:
        return flexisign_procs[0][0]
    
    # Multiple FlexiSIGN processes found
    print("Multiple FlexiSIGN processes found:")
    for pid, name in flexisign_procs:
        print(f"  PID {pid}: {name}")
    return flexisign_procs[0][0]  # Return first one


def find_flexisign_pid_from_window():
    """Find FlexiSIGN PID by looking at window titles."""
    try:
        import pygetwindow as gw
        import win32process
        import win32gui
        
        for window in gw.getAllWindows():
            if "FlexiSIGN" in window.title or "flexi" in window.title.lower():
                hwnd = window._hWnd
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                return pid
    except:
        pass
    return None


def bring_window_to_foreground(pid):
    """Bring the FlexiSIGN window to foreground using pygetwindow."""
    try:
        import pygetwindow as gw
        import psutil
        
        # Get the actual PID from the window
        for window in gw.getAllWindows():
            # FlexiSIGN window title contains "FlexiSIGN"
            if "FlexiSIGN" in window.title or "flexi" in window.title.lower():
                print(f"Found window: {window.title}")
                
                # Try to get the actual PID from the window
                try:
                    import win32process
                    import win32gui
                    hwnd = window._hWnd
                    _, actual_pid = win32process.GetWindowThreadProcessId(hwnd)
                    print(f"Window PID: {actual_pid}")
                    if actual_pid != pid:
                        print(f"WARNING: Configured PID ({pid}) doesn't match window PID ({actual_pid})")
                        print(f"Please update FLEXISIGN_PID to {actual_pid}")
                except:
                    pass
                
                window.activate()
                time.sleep(0.5)  # Wait for window to come to foreground
                return True
        return False
    except Exception as e:
        print(f"Warning: Could not bring window to foreground: {e}")
        return False


def click_element_center(element):
    """Click the center of a UI element."""
    rect = get_bounding_rect(element)
    if rect:
        center_x = (rect[0] + rect[2]) / 2
        center_y = (rect[1] + rect[3]) / 2
        pyautogui.click(center_x, center_y)
        return True
    return False


def main():
    print("=== FlexiSIGN Automation Sample ===\n")
    
    # Step 1: Find FlexiSIGN process
    print("Step 1: Finding FlexiSIGN process...")
    
    if FLEXISIGN_PID is not None:
        pid = FLEXISIGN_PID
        print(f"Using manually configured PID: {pid}")
    else:
        # Try to find PID from window first (most reliable)
        pid = find_flexisign_pid_from_window()
        if pid:
            print(f"Auto-detected FlexiSIGN from window (PID: {pid})")
        else:
            # Fallback to process list
            pid = find_flexisign_process()
            if not pid:
                print("ERROR: FlexiSIGN process not found.")
                print("\nTo find the PID, run: python elements.py")
                print("Then set FLEXISIGN_PID at the top of this script.")
                return
            print(f"Auto-detected FlexiSIGN from process list (PID: {pid})")
    print()
    
    # Step 2: Bring FlexiSIGN window to foreground
    print("Step 2: Bringing FlexiSIGN window to foreground...")
    if bring_window_to_foreground(pid):
        print("FlexiSIGN window activated\n")
    else:
        print("WARNING: Could not automatically activate window. Please click on FlexiSIGN window manually.")
        print("Waiting 5 seconds for you to click on FlexiSIGN...")
        time.sleep(5)
    
    # Step 3: Initialize UI Automation
    print("Step 3: Initializing UI Automation...")
    uia = create_uia()
    root = get_root_for_pid(uia, pid)
    if not root:
        print("ERROR: Could not get root element for FlexiSIGN")
        return
    print("UI Automation initialized\n")
    
    # Step 4: Click Text Tool
    print("Step 4: Clicking Text Tool...")
    text_tool = get_text_tool(uia, root)
    if not text_tool:
        print("ERROR: Text Tool not found")
        return
    
    if click_element_center(text_tool):
        print("Text Tool clicked successfully")
    else:
        print("ERROR: Could not click Text Tool")
        return
    time.sleep(0.8)
    
    # Step 5: Click center of canvas and type text
    print("\nStep 5: Writing text in center of canvas...")
    # Get canvas area (you may need to adjust these coordinates based on your screen)
    # For now, we'll click at a relative position
    print("Clicking canvas center...")
    # Move to center of screen (adjust as needed for your canvas position)
    screen_width, screen_height = pyautogui.size()
    canvas_x = screen_width // 2
    canvas_y = screen_height // 2
    
    pyautogui.click(canvas_x, canvas_y)
    time.sleep(0.5)
    
    # Type the text
    text_to_write = "John Doe"
    print(f"Typing: '{text_to_write}'")
    pyautogui.write(text_to_write, interval=0.08)
    time.sleep(0.8)
    
    # Step 6: Click Select Tool to select the text
    print("\nStep 6: Clicking Select Tool to select text...")
    select_tool = get_select_tool(uia, root)
    if not select_tool:
        print("ERROR: Select Tool not found")
        return
    
    if click_element_center(select_tool):
        print("Select Tool clicked successfully")
    else:
        print("ERROR: Could not click Select Tool")
        return
    time.sleep(0.8)
    
    # Step 7: Change font to Blackberry
    print("\nStep 7: Changing font to Blackberry...")
    
    # First, click the text to select it
    print("Clicking text to select it...")
    pyautogui.click(canvas_x, canvas_y)
    time.sleep(0.5)
    
    # FlexiSIGN quirk: Must switch away from Character tab first, then back to it
    # This auto-focuses the font dropdown
    print("Switching to Scale tab first...")
    scale_tab = get_scale_tab_item(uia, root)
    if scale_tab:
        click_element_center(scale_tab)
        time.sleep(0.5)
    
    print("Switching to Character tab...")
    char_tab = get_character_tab_item(uia, root)
    if char_tab:
        if click_element_center(char_tab):
            print("Character tab clicked - font dropdown is now auto-focused")
            time.sleep(0.5)
            
            # Type font name directly (font dropdown is already focused)
            pyautogui.hotkey('ctrl', 'a')  # Select all existing text
            time.sleep(0.2)
            pyautogui.write('Blackberry', interval=0.08)
            time.sleep(0.3)
            
            # Press left then right arrow to apply changes (FlexiSIGN quirk)
            print("Applying font change (left-right arrow trick)...")
            pyautogui.press('left')
            time.sleep(0.2)
            pyautogui.press('right')
            time.sleep(0.5)
            
            print("Font changed to Blackberry")
        else:
            print("WARNING: Could not click Character tab")
    
    # Step 8: Set dimensions (5.0 width, 1.0 height)
    print("\nStep 8: Setting dimensions...")
    
    # Switch back to Scale tab
    print("Switching to Scale tab...")
    scale_tab = get_scale_tab_item(uia, root)
    if scale_tab:
        click_element_center(scale_tab)
        time.sleep(0.5)
    
    # First, disable proportional scaling
    print("Disabling proportional scaling...")
    proportional_cb = get_proportional_checkbox(uia, root, ensure_tab_active=False)
    if proportional_cb:
        toggle_checkbox(proportional_cb, target_on=False)
        print("Proportional scaling disabled")
        time.sleep(0.4)
    else:
        print("WARNING: Could not find proportional checkbox")
    
    # Set width to 5.0
    print("Setting width to 5.0...")
    width_input = get_scale_width_input(uia, root, ensure_tab_active=False)  # Already on Scale tab
    if width_input:
        if set_value(width_input, "5.0"):
            print("Width set to 5.0")
            pyautogui.press('enter')  # Confirm the value
            time.sleep(0.4)
        else:
            print("WARNING: Could not set width value")
    else:
        print("ERROR: Width input not found")
    
    # Set height to 1.0
    print("Setting height to 1.0...")
    height_input = get_scale_height_input(uia, root, ensure_tab_active=False)
    if height_input:
        if set_value(height_input, "1.0"):
            print("Height set to 1.0")
            pyautogui.press('enter')  # Confirm the value
            time.sleep(0.4)
        else:
            print("WARNING: Could not set height value")
    else:
        print("ERROR: Height input not found")
    
    print("\n=== Automation Complete! ===")
    print("Text object created with dimensions 5.0 x 1.0")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
