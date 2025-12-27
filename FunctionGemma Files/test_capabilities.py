"""
FunctionGemma Capability Testing Script

Advanced multi-step function calling with file operations, app control, and more.
Test the model's ability to handle complex, real-world tasks.
"""

from transformers import AutoProcessor, AutoModelForCausalLM
import re
import pyautogui
import time
import subprocess
import os
import json
from pathlib import Path

# Disable pyautogui failsafe for smoother operation
pyautogui.FAILSAFE = False

LOCAL_DIR = "./local_models/functiongemma-270m-it"
MODEL_NAME = "google/functiongemma-270m-it"

print("🚀 Loading FunctionGemma model...")
processor = AutoProcessor.from_pretrained(MODEL_NAME, cache_dir=LOCAL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=LOCAL_DIR, device_map="auto")
print("✅ Model loaded successfully!\n")

# ============================================================================
# ADVANCED FUNCTION DEFINITIONS
# ============================================================================

def open_app(app_name: str):
    """
    Open an application by name with smart mapping.
    
    Args:
        app_name: Name of the application to open
    """
    app_name = app_name.strip().lower()
    
    # Comprehensive app mapping
    app_map = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'calc': 'calc.exe',
        'paint': 'mspaint.exe',
        'mspaint': 'mspaint.exe',
        'cmd': 'cmd.exe',
        'command prompt': 'cmd.exe',
        'terminal': 'cmd.exe',
        'chrome': 'chrome.exe',
        'browser': 'chrome.exe',
        'edge': 'msedge.exe',
        'explorer': 'explorer.exe',
        'file explorer': 'explorer.exe',
        'files': 'explorer.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'outlook': 'outlook.exe'
    }
    
    try:
        executable = app_map.get(app_name, app_name + '.exe')
        subprocess.Popen(executable, shell=True)
        return {"status": "success", "message": f"Opened {app_name}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open {app_name}: {str(e)}"}

def type_text(text: str):
    """
    Type text using keyboard automation with smart delays.
    
    Args:
        text: The text to type
    """
    try:
        time.sleep(0.8)  # Wait for window to be ready
        pyautogui.write(text, interval=0.03)  # Slightly faster typing
        return {"status": "success", "message": f"Typed: {text}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to type text: {str(e)}"}

def press_key(key: str):
    """
    Press keyboard keys including combinations.
    
    Args:
        key: Key name or combination (e.g., 'enter', 'ctrl+s', 'alt+f4')
    """
    try:
        time.sleep(0.3)
        key = key.strip().lower()
        
        if '+' in key:
            # Handle key combinations
            keys = [k.strip() for k in key.split('+')]
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        
        return {"status": "success", "message": f"Pressed: {key}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to press key: {str(e)}"}

def save_file(filename: str, location: str = "desktop"):
    """
    Save current file with Ctrl+S and handle save dialog.
    
    Args:
        filename: Name of the file to save
        location: Where to save (desktop, documents, downloads)
    """
    try:
        # Press Ctrl+S to open save dialog
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1.5)  # Wait for save dialog
        
        # Navigate to location if needed
        if location.lower() == "desktop":
            # Usually default, but we can type the path
            pass
        elif location.lower() == "documents":
            pyautogui.write(os.path.expanduser("~/Documents/"))
            time.sleep(0.5)
        
        # Type filename
        pyautogui.write(filename)
        time.sleep(0.5)
        
        # Press Enter to save
        pyautogui.press('enter')
        
        return {"status": "success", "message": f"Saved file as {filename} to {location}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save file: {str(e)}"}

def create_folder(folder_name: str, location: str = "desktop"):
    """
    Create a new folder in specified location.
    
    Args:
        folder_name: Name of the folder to create
        location: Where to create it (desktop, documents, downloads)
    """
    try:
        # Handle Windows OneDrive Desktop vs Local Desktop
        if location.lower() == "desktop":
            # Try OneDrive Desktop first (common on Windows 10/11)
            onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
            local_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            
            if os.path.exists(onedrive_desktop):
                base_path = onedrive_desktop
                print(f"     📁 Using OneDrive Desktop: {base_path}")
            else:
                base_path = local_desktop
                print(f"     📁 Using Local Desktop: {base_path}")
        elif location.lower() == "documents":
            base_path = os.path.join(os.path.expanduser("~"), "Documents")
        elif location.lower() == "downloads":
            base_path = os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            base_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        folder_path = os.path.join(base_path, folder_name)
        print(f"     📁 Creating folder at: {folder_path}")
        
        os.makedirs(folder_path, exist_ok=True)
        
        # Verify folder was created
        if os.path.exists(folder_path):
            return {"status": "success", "message": f"Created folder '{folder_name}' at {folder_path}"}
        else:
            return {"status": "error", "message": f"Folder creation failed - path doesn't exist: {folder_path}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to create folder: {str(e)}"}

def search_web(query: str):
    """
    Search the web using default browser.
    
    Args:
        query: Search query
    """
    try:
        import webbrowser
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return {"status": "success", "message": f"Searching for: {query}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to search: {str(e)}"}

def take_screenshot(filename: str = None):
    """
    Take a screenshot and save it.
    
    Args:
        filename: Optional filename for the screenshot
    """
    try:
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        screenshot_path = os.path.join(os.path.expanduser("~/Desktop"), filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        return {"status": "success", "message": f"Screenshot saved as {filename}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to take screenshot: {str(e)}"}

def wait_seconds(seconds: int):
    """
    Wait for specified number of seconds.
    
    Args:
        seconds: Number of seconds to wait
    """
    try:
        time.sleep(seconds)
        return {"status": "success", "message": f"Waited {seconds} seconds"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to wait: {str(e)}"}

def close_app():
    """
    Close the current application using Alt+F4.
    """
    try:
        pyautogui.hotkey('alt', 'f4')
        return {"status": "success", "message": "Closed current application"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to close app: {str(e)}"}

def task_complete():
    """
    Indicate that the task is finished.
    """
    return {"status": "complete", "message": "Task completed successfully"}

# ============================================================================
# FUNCTION REGISTRY AND SCHEMAS
# ============================================================================

AVAILABLE_FUNCTIONS = {
    'open_app': open_app,
    'type_text': type_text,
    'press_key': press_key,
    'save_file': save_file,
    'create_folder': create_folder,
    'search_web': search_web,
    'take_screenshot': take_screenshot,
    'wait_seconds': wait_seconds,
    'close_app': close_app,
    'task_complete': task_complete,
    'debug_paths': debug_paths
}

# Function schemas for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open an application by name (notepad, calculator, chrome, word, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text using the keyboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press keyboard keys or key combinations (enter, ctrl+s, alt+f4, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key or key combination to press"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_file",
            "description": "Save the current file with a specific name and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file to save"},
                    "location": {"type": "string", "description": "Location to save (desktop, documents, downloads)", "enum": ["desktop", "documents", "downloads"]}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a new folder in specified location",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"},
                    "location": {"type": "string", "description": "Where to create folder", "enum": ["desktop", "documents", "downloads"]}
                },
                "required": ["folder_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web using Google",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot and save it",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Optional filename for screenshot"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_seconds",
            "description": "Wait for a specified number of seconds",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Number of seconds to wait"}
                },
                "required": ["seconds"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_app",
            "description": "Close the current application",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_complete",
            "description": "Indicate that the task is finished",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
# ============================================================================
# FUNCTION CALL PARSING AND EXECUTION
# ============================================================================

def extract_tool_calls(text):
    """Extract function calls from model output (official Google pattern)"""
    def cast(v):
        try: return int(v)
        except:
            try: return float(v)
            except: return {'true': True, 'false': False}.get(v.lower(), v.strip("'\""))

    return [{
        "name": name,
        "arguments": {
            k: cast((v1 or v2).strip())
            for k, v1, v2 in re.findall(r"(\w+):(?:<escape>(.*?)<escape>|([^,}]*))", args)
        }
    } for name, args in re.findall(
        r"<start_function_call>call:(\w+)\{(.*?)\}<end_function_call>",
        text,
        re.DOTALL
    )]

def execute_task(user_command, max_turns=15):
    """
    Execute a potentially complex multi-step task.
    
    Args:
        user_command: Natural language command from user
        max_turns: Maximum number of conversation turns
    """
    print(f"\n{'='*80}")
    print(f"🎯 TASK: {user_command}")
    print(f"{'='*80}")
    
    # Initialize conversation
    messages = [
        {
            "role": "developer",
            "content": "You are a model that can do function calling with the following functions. Execute the user's task step by step. Call task_complete when finished."
        },
        {
            "role": "user",
            "content": user_command
        }
    ]
    
    for turn in range(1, max_turns + 1):
        print(f"\n🔄 Turn {turn}:")
        
        # Generate model response
        inputs = processor.apply_chat_template(
            messages,
            tools=tools,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt"
        )
        
        outputs = model.generate(
            **inputs.to(model.device),
            pad_token_id=processor.eos_token_id,
            max_new_tokens=256,
            temperature=0.1  # Slightly more deterministic
        )
        
        generated_tokens = outputs[0][len(inputs["input_ids"][0]):]
        output = processor.decode(generated_tokens, skip_special_tokens=True)
        
        print(f"  🤖 Model: {output}")
        
        # Check if model is just responding (no function call)
        if "<start_function_call>" not in output:
            print(f"  💬 Final response: {output}")
            break
        
        # Extract function calls
        calls = extract_tool_calls(output)
        
        if not calls:
            print("  ❌ No valid function calls detected")
            break
        
        # Add assistant's tool calls to conversation
        messages.append({
            "role": "assistant",
            "tool_calls": [{"type": "function", "function": call} for call in calls]
        })
        
        # Execute each function call
        results = []
        task_completed = False
        
        for call in calls:
            func_name = call['name']
            func_args = call['arguments']
            
            print(f"  ⚙️  Executing: {func_name}({func_args})")
            
            if func_name in AVAILABLE_FUNCTIONS:
                result = AVAILABLE_FUNCTIONS[func_name](**func_args)
                results.append({"name": func_name, "response": result})
                
                # Print result with appropriate emoji
                status = result.get("status", "unknown")
                if status == "success":
                    print(f"     ✅ {result['message']}")
                elif status == "complete":
                    print(f"     🎉 {result['message']}")
                    task_completed = True
                else:
                    print(f"     ❌ {result['message']}")
            else:
                error_result = {"status": "error", "message": f"Unknown function: {func_name}"}
                results.append({"name": func_name, "response": error_result})
                print(f"     ❌ Unknown function: {func_name}")
        
        # Add tool results to conversation
        messages.append({
            "role": "tool",
            "content": results
        })
        
        # Check if task is complete
        if task_completed:
            print(f"\n🎉 Task completed successfully!")
            break
        
        # Small delay between turns
        time.sleep(0.5)
    
    print(f"\n{'='*80}\n")

# ============================================================================
# MAIN TESTING INTERFACE
# ============================================================================

def main():
    """Main testing interface"""
    print("🧪 FunctionGemma Capability Testing")
    print("="*50)
    print("\n📋 Available Functions:")
    print("  • open_app - Open applications (notepad, calculator, chrome, word, etc.)")
    print("  • type_text - Type text on keyboard")
    print("  • press_key - Press keys (enter, ctrl+s, alt+f4, etc.)")
    print("  • save_file - Save current file with name and location")
    print("  • create_folder - Create folders on desktop/documents/downloads")
    print("  • search_web - Search Google")
    print("  • take_screenshot - Capture screen")
    print("  • wait_seconds - Pause execution")
    print("  • close_app - Close current application")
    
    print("\n🎯 Example Commands to Test:")
    print("  'Open notepad and write a shopping list'")
    print("  'Create a folder called Projects on desktop'")
    print("  'Open calculator and then take a screenshot'")
    print("  'Search for Python tutorials and then open notepad'")
    print("  'Open notepad, type Hello World, and save as test.txt'")
    print("  'Open word, write a letter, save as letter.docx to documents'")
    
    print(f"\n{'='*50}")
    print("Type your command or 'quit' to exit")
    print(f"{'='*50}\n")
    
    while True:
        try:
            user_input = input("🎤 Your command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Testing session ended. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Execute the task
            execute_task(user_input)
            
        except KeyboardInterrupt:
            print("\n\n👋 Testing interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    main()