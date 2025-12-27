from transformers import AutoProcessor, AutoModelForCausalLM
import re
import pyautogui
import time
import subprocess
import os

LOCAL_DIR = "./local_models/functiongemma-270m-it"
MODEL_NAME = "google/functiongemma-270m-it"

# Load model
print("Loading model...")
processor = AutoProcessor.from_pretrained(MODEL_NAME, cache_dir=LOCAL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=LOCAL_DIR, device_map="auto")
print("Model loaded!\n")

# Define expanded function schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open an application by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application (e.g., notepad, chrome, calculator)"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text using keyboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a keyboard key or key combination",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key name (e.g., enter, ctrl+s, alt+f4)"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_mouse",
            "description": "Click the mouse at current position or coordinates",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate (optional)"},
                    "y": {"type": "integer", "description": "Y coordinate (optional)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set system volume level",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume level 0-100"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
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
            "name": "search_web",
            "description": "Search the web for a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]

# Function implementations
def open_app(app_name):
    """Open an application"""
    app_name = app_name.strip()  # Remove leading/trailing spaces
    app_lower = app_name.lower()
    
    try:
        # Map common app names to executables
        app_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'mspaint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'chrome': 'chrome.exe',
            'edge': 'msedge.exe',
            'explorer': 'explorer.exe',
            'file explorer': 'explorer.exe'
        }
        
        executable = app_map.get(app_lower, app_name)
        subprocess.Popen(executable)
        return f"✓ Opened {app_name}"
    except Exception as e:
        return f"✗ Failed to open {app_name}: {str(e)}"

def type_text(text):
    """Type text using keyboard"""
    time.sleep(0.5)  # Small delay to ensure window is focused
    pyautogui.write(text, interval=0.05)
    return f"✓ Typed: {text}"

def press_key(key):
    """Press a keyboard key"""
    time.sleep(0.3)
    if '+' in key:
        # Handle key combinations like ctrl+s
        keys = key.split('+')
        pyautogui.hotkey(*keys)
    else:
        pyautogui.press(key)
    return f"✓ Pressed: {key}"

def click_mouse(x=None, y=None):
    """Click the mouse"""
    if x is not None and y is not None:
        pyautogui.click(x, y)
        return f"✓ Clicked at ({x}, {y})"
    else:
        pyautogui.click()
        return "✓ Clicked at current position"

def set_volume(level):
    """Set volume (simulated)"""
    return f"✓ Volume set to {level}%"

def wait(seconds):
    """Wait for specified seconds"""
    time.sleep(seconds)
    return f"✓ Waited {seconds} seconds"

def search_web(query):
    """Search the web"""
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"✓ Searching for: {query}"

# Dispatcher
def execute_function(func_name, args):
    """Execute the function"""
    functions = {
        'open_app': open_app,
        'type_text': type_text,
        'press_key': press_key,
        'click_mouse': click_mouse,
        'set_volume': set_volume,
        'wait': wait,
        'search_web': search_web
    }
    
    if func_name in functions:
        return functions[func_name](**args)
    else:
        return f"✗ Unknown function: {func_name}"

def parse_function_call(output):
    """Parse FunctionGemma output"""
    match = re.search(r'call:(\w+)\{(.+?)\}', output)
    if not match:
        return None, None
    
    func_name = match.group(1)
    args_str = match.group(2)
    args = {}
    
    # Parse escaped strings
    escaped_pattern = r'(\w+):<escape>([^<]+)<escape>'
    for arg_match in re.finditer(escaped_pattern, args_str):
        key = arg_match.group(1)
        value = arg_match.group(2).strip()  # Strip whitespace
        args[key] = value
    
    # Parse direct numbers
    direct_pattern = r'(\w+):(\d+)'
    for arg_match in re.finditer(direct_pattern, args_str):
        key = arg_match.group(1)
        if key not in args:
            args[key] = int(arg_match.group(2))
    
    return func_name, args

def process_command(user_input, conversation_history):
    """Process a command and return function call"""
    messages = [
        {"role": "developer", "content": "You are a model that can do function calling with the following functions"}
    ]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current user input
    messages.append({"role": "user", "content": user_input})
    
    inputs = processor.apply_chat_template(
        messages, tools=tools, add_generation_prompt=True,
        return_dict=True, return_tensors="pt"
    )
    
    outputs = model.generate(
        **inputs.to(model.device),
        pad_token_id=processor.eos_token_id,
        max_new_tokens=128
    )
    
    response = processor.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
    return response

# Main interactive loop
print("=" * 60)
print("  INTERACTIVE FUNCTION CALLING DEMO")
print("=" * 60)
print("\nAvailable functions:")
print("  • open_app - Open applications (notepad, calculator, etc.)")
print("  • type_text - Type text on keyboard")
print("  • press_key - Press keys (enter, ctrl+s, etc.)")
print("  • click_mouse - Click the mouse")
print("  • set_volume - Set system volume")
print("  • wait - Wait for seconds")
print("  • search_web - Search Google")
print("\nExamples:")
print("  'Open notepad'")
print("  'Type Hello World'")
print("  'Press enter'")
print("  'Search for Python tutorials'")
print("  'Set volume to 50'")
print("\nType 'quit' to exit\n")
print("=" * 60)

conversation_history = []

while True:
    user_input = input("\n🎤 You: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!")
        break
    
    if not user_input:
        continue
    
    print("🤖 Processing...")
    
    # Get model response
    response = process_command(user_input, conversation_history)
    print(f"   Model output: {response}")
    
    # Parse and execute
    func_name, args = parse_function_call(response)
    
    if func_name:
        print(f"   Calling: {func_name}({args})")
        result = execute_function(func_name, args)
        print(f"   {result}")
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})
    else:
        print("   ✗ No function call detected")
