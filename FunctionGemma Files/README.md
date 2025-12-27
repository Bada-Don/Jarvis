# FunctionGemma Local Setup

A local function calling system using Google's FunctionGemma-270m model.

## Setup

### 1. Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```cmd
pip install -r requirements.txt
```

### 3. HuggingFace Authentication

The FunctionGemma model is gated and requires authentication:

1. Create a HuggingFace account at https://huggingface.co/join
2. Go to https://huggingface.co/settings/tokens
3. Create a **new token** with these settings:
   - Token type: **Read** (or Fine-grained with read access)
   - **IMPORTANT**: Enable "Access content in gated repos" permission
4. Copy the token
5. Login via CLI:

```cmd
huggingface-cli login
```

Paste your token when prompted.

6. Accept the model terms at https://huggingface.co/google/functiongemma-270m-it
   - Click "Agree and access repository"

### 4. Download the Model

```cmd
python download_functiongemma.py
```

This will download the model to `./local_models/functiongemma-270m-it`

**Note:** You must also accept the model terms at https://huggingface.co/google/functiongemma-270m-it before downloading.

## Usage

### Capability Testing (Recommended)

Test FunctionGemma's multi-step abilities with advanced functions:

```cmd
python test_capabilities.py
```

**Available Functions:**
- `open_app` - Open applications (notepad, calculator, chrome, word, etc.)
- `type_text` - Type text on keyboard
- `press_key` - Press keys (enter, ctrl+s, alt+f4, etc.)
- `save_file` - Save current file with name and location
- `create_folder` - Create folders on desktop/documents/downloads
- `search_web` - Search Google
- `take_screenshot` - Capture screen
- `wait_seconds` - Pause execution
- `close_app` - Close current application

**Example Commands to Test:**
- "Open notepad and write a shopping list"
- "Create a folder called Projects on desktop"
- "Open calculator and then take a screenshot"
- "Search for Python tutorials and then open notepad"
- "Open notepad, type Hello World, and save as test.txt"
- "Open word, write a letter, save as letter.docx to documents"

### Interactive Chat

For general interactive testing:

```cmd
python interactive_demo.py
```

## Available Functions

- `toggle_wifi(state)` - Turn WiFi on or off
- `open_app(app_name)` - Open an application
- `set_volume(level)` - Set system volume (0-100)

See `schemas.py` for function definitions and `functions.py` for implementations.
