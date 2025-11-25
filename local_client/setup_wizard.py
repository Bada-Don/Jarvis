"""
FlexiSign Configuration Wizard
Helps you set up flexisign_config.json with the correct paths and settings
"""
import json
import os
import psutil
import win32gui
import time
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text):
    """Print a section header."""
    print(f"\n--- {text} ---\n")


def list_running_processes():
    """List all running processes."""
    processes = set()
    for proc in psutil.process_iter(['name']):
        try:
            processes.add(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(processes)


def list_visible_windows():
    """List all visible windows."""
    windows = []
    
    def callback(hwnd, window_list):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                window_list.append(title)
        return True
    
    win32gui.EnumWindows(callback, windows)
    return sorted(windows)


def find_process_by_keyword(keyword):
    """Find processes matching a keyword."""
    matches = []
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if keyword.lower() in proc.info['name'].lower():
                matches.append({
                    'name': proc.info['name'],
                    'path': proc.info['exe']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return matches


def get_user_input(prompt, default=None):
    """Get user input with optional default."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def yes_no_question(prompt, default=True):
    """Ask a yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes']


def browse_for_file(prompt):
    """Ask user to browse for a file."""
    print(f"\n{prompt}")
    print("Please enter the full path to the file:")
    path = input("> ").strip().strip('"')
    
    if os.path.exists(path):
        return path
    else:
        print(f"⚠️  Warning: File not found: {path}")
        if yes_no_question("Use this path anyway?", False):
            return path
        return None


def main():
    """Run the configuration wizard."""
    print_header("FlexiSign Configuration Wizard")
    print("This wizard will help you configure FlexiSign automation.")
    print("Make sure FlexiSign and its loader/patcher are running before starting.")
    
    if not yes_no_question("\nAre FlexiSign and the loader/patcher currently running?", False):
        print("\n⚠️  Please start them first, then run this wizard again.")
        print("This helps us detect the correct process names and window titles.")
        return
    
    config = {
        "loader_patcher": {},
        "flexisign_pro": {},
        "timing": {
            "process_check_interval": 0.5,
            "window_check_interval": 1,
            "modal_check_interval": 0.5,
            "window_close_wait": 2
        },
        "debug": {
            "verbose_logging": True,
            "list_all_windows": False
        }
    }
    
    # Step 1: Loader/Patcher Configuration
    print_header("Step 1: Loader/Patcher Configuration")
    print("The loader/patcher is the small utility that removes FlexiSign restrictions.")
    
    print_section("Detecting Running Processes")
    processes = list_running_processes()
    
    print("Enter a keyword to search for the loader/patcher process:")
    print("(e.g., 'scanner', 'loader', 'patcher', 'protection')")
    keyword = get_user_input("Search keyword", "scanner")
    
    matches = find_process_by_keyword(keyword)
    
    if matches:
        print(f"\nFound {len(matches)} matching process(es):")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['name']}")
            print(f"   Path: {match['path']}")
        
        choice = int(get_user_input(f"\nSelect loader/patcher (1-{len(matches)})", "1")) - 1
        if 0 <= choice < len(matches):
            config['loader_patcher']['process_name'] = matches[choice]['name']
            config['loader_patcher']['exe_path'] = matches[choice]['path']
            print(f"\n✓ Selected: {matches[choice]['name']}")
    else:
        print("\n⚠️  No matching processes found.")
        config['loader_patcher']['process_name'] = get_user_input("Enter loader process name")
        config['loader_patcher']['exe_path'] = browse_for_file("Enter loader executable path")
    
    # Modal configuration
    print_section("Loader Startup Modal")
    print("Does the loader show a modal dialog when it first starts?")
    has_modal = yes_no_question("(Usually has an 'OK' button)", True)
    
    config['loader_patcher']['startup_modal'] = {
        "enabled": has_modal,
        "title": get_user_input("Modal window title", "FlexiSIGN") if has_modal else "",
        "button": "OK",
        "timeout": 15
    }
    
    config['loader_patcher']['wait_after_start'] = int(get_user_input(
        "Seconds to wait after starting loader", "3"
    ))
    
    # Step 2: FlexiSign Pro Configuration
    print_header("Step 2: FlexiSign Pro Configuration")
    
    print_section("Detecting FlexiSign Process")
    keyword = get_user_input("Search keyword for FlexiSign", "flexi")
    matches = find_process_by_keyword(keyword)
    
    if matches:
        print(f"\nFound {len(matches)} matching process(es):")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['name']}")
            print(f"   Path: {match['path']}")
        
        choice = int(get_user_input(f"\nSelect FlexiSign (1-{len(matches)})", "1")) - 1
        if 0 <= choice < len(matches):
            config['flexisign_pro']['process_names'] = [matches[choice]['name']]
            config['flexisign_pro']['exe_path'] = matches[choice]['path']
            print(f"\n✓ Selected: {matches[choice]['name']}")
    else:
        print("\n⚠️  No matching processes found.")
        config['flexisign_pro']['process_names'] = [get_user_input("Enter FlexiSign process name")]
        config['flexisign_pro']['exe_path'] = browse_for_file("Enter FlexiSign executable path")
    
    # Window titles
    print_section("Detecting FlexiSign Windows")
    windows = list_visible_windows()
    flexi_windows = [w for w in windows if 'flexi' in w.lower()]
    
    if flexi_windows:
        print("Found FlexiSign window(s):")
        for i, window in enumerate(flexi_windows, 1):
            print(f"{i}. {window}")
        
        config['flexisign_pro']['window_titles'] = flexi_windows
        print(f"\n✓ Using {len(flexi_windows)} window title(s)")
    else:
        print("\n⚠️  No FlexiSign windows detected.")
        titles = get_user_input("Enter window title(s) (comma-separated)", "FlexiSIGN-PRO")
        config['flexisign_pro']['window_titles'] = [t.strip() for t in titles.split(',')]
    
    config['flexisign_pro']['demo_mode_indicators'] = ["trial", "demo", "evaluation", "restricted"]
    config['flexisign_pro']['wait_after_start'] = int(get_user_input(
        "Seconds to wait after starting FlexiSign", "8"
    ))
    
    # Step 3: Save Configuration
    print_header("Step 3: Save Configuration")
    
    config_path = "flexisign_config.json"
    
    # Show preview
    print("Configuration preview:")
    print(json.dumps(config, indent=2))
    
    if yes_no_question(f"\nSave configuration to {config_path}?", True):
        # Backup existing config
        if os.path.exists(config_path):
            backup_path = f"{config_path}.backup"
            os.rename(config_path, backup_path)
            print(f"✓ Backed up existing config to {backup_path}")
        
        # Save new config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Configuration saved to {config_path}")
        
        # Test the configuration
        print_header("Step 4: Test Configuration")
        if yes_no_question("Would you like to test the configuration now?", True):
            print("\nTesting FlexiSign Manager...")
            try:
                from flexisign_manager import FlexiSignManager
                manager = FlexiSignManager(config_path)
                success = manager.ensure_proper_state()
                
                if success:
                    print("\n✅ SUCCESS! FlexiSign automation is working correctly.")
                else:
                    print("\n❌ Test failed. Check the logs above for errors.")
            except Exception as e:
                print(f"\n❌ Error during test: {e}")
        
        print_header("Setup Complete!")
        print("Your FlexiSign automation is now configured.")
        print("\nNext steps:")
        print("1. Review flexisign_config.json and adjust if needed")
        print("2. Run 'python flexisign_manager.py' to test standalone")
        print("3. Start the JARVIS client with 'python client.py'")
        print("\nFor help, see FLEXISIGN_SETUP.md")
    else:
        print("\nConfiguration not saved.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
