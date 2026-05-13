---
name: ui_os
description: "Use this skill whenever the user needs to interact with the operating system UI: opening applications, typing text, pressing keys or shortcuts, clicking on UI elements by text or visually, browsing websites, or navigating menus. Triggers include: 'open app', 'type', 'press', 'click', 'shortcut', 'browse', 'navigate to URL', 'go to website', 'send message in WhatsApp', or any request involving keyboard input, mouse clicks, or application window control. Do NOT use for shell commands (use shell skill), file editing (use file_editing skill), or FlexiSIGN operations (use flexisign skill)."
---

For keyboard steps, include:
- "value": the key or text to type
  - For shortcuts: "ctrl+c", "alt+tab", "win+r", "ctrl+shift+esc"
  - For special keys: "enter", "tab", "escape", "backspace", "delete", "up", "down", "left", "right", "f1"-"f12"
  - For text: just the text string like "Hello World" or "notepad"
  - **CRITICAL: NEVER use {curly braces} inside a text string (e.g., "Hello{enter}World"). This is FORBIDDEN. Use separate steps for special keys or use "write_file" for multi-line text.**
- "repeats": (optional) number of times to repeat

For click_text_fast steps, include:
- "window_title": partial or full title of the window containing the text
- "text": the exact text to find and click on (use full name for contacts to avoid ambiguity)
- Use this for: buttons with text, menu items, contact names, file names, any readable text
- Fuzzy matching enabled: will match partial words (e.g., "Harshit Singla" matches "Harshit" or "Singla")
- Examples: clicking "Harshit Singla" in WhatsApp, "Send" button, "File" menu

For visual_click steps (SLOW - use only when text is not available), include:
- "target_name": descriptive name of the UI element to click
  - Be specific: "chrome_address_bar", "start_menu_button", "file_menu", "save_button", "close_button_x"
  - For text/buttons: "button_OK", "button_Cancel", "menu_File", "tab_Settings", "button_Compose"
  - For icons: "icon_chrome", "icon_folder", "taskbar_chrome"
  - Gmail's "Compose" button MUST always be clicked using visual_click. Use the exact identifier: button_Compose.

## Common Patterns:

### Opening Applications:
- Press Win key, type app name, press Enter
- Or use Win+R for Run dialog

### Clicking on Text Elements (FAST METHOD - ALWAYS PREFER THIS):
- Use click_text_fast to click on any visible text: buttons, menu items, contact names, file names
- Example: Click on "Harshit" contact in WhatsApp
{
  "sequence":[
    {"order": 1, "type": "click_text_fast", "window_title": "WhatsApp", "text": "Harshit", "desc": "Click on Harshit contact"}
  ]
}
- Example: Click "Send" button
{
  "sequence":[
    {"order": 1, "type": "click_text_fast", "window_title": "Inbox", "text": "Compose", "desc": "Click Compose button"}
  ]
}

### Web Browsing:
- To navigate to a URL: Ctrl+L (focus address bar), type URL with a SPACE at the end, press Enter
- IMPORTANT: Always add a trailing space after URLs (e.g., "youtube.com ") to prevent browser autocomplete
- To search on a website: Use the website's search shortcut (e.g., "/" on YouTube) or click_text_fast on search box
- YouTube shortcuts: "/" focuses the search bar, then type query and press Enter
- Google shortcuts: Just type in the search box (auto-focused on google.com)
- DO NOT use the browser address bar to search within a website - use the website's own search feature

### Text Editing:
- Click to position cursor
- Type text
- Use Ctrl+A (select all), Ctrl+C (copy), Ctrl+V (paste)

## Example - Open Notepad and type:
{
  "sequence":[
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "notepad", "desc": "Type notepad"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Notepad"},
    {"order": 4, "type": "keyboard", "value": "Hello World!", "desc": "Type the message"}
  ],
  "expected_final_state": "Notepad window open with 'Hello World!' typed in the text area"
}

## Example - Open Chrome and go to Google:
{
  "sequence":[
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "chrome", "desc": "Search for Chrome"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch Chrome"},
    {"order": 4, "type": "keyboard", "value": "ctrl+l", "desc": "Focus address bar"},
    {"order": 5, "type": "keyboard", "value": "google.com ", "desc": "Type URL with trailing space to prevent autocomplete"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Navigate to site"}
  ],
  "expected_final_state": "Chrome browser open showing Google homepage with search box visible"
}

## Example - Send message to contact in WhatsApp (FAST METHOD):
{
  "sequence":[
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "whatsapp", "desc": "Search for WhatsApp"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch WhatsApp"},
    {"order": 4, "type": "click_text_fast", "window_title": "WhatsApp", "text": "Harshit", "desc": "Click on Harshit contact"},
    {"order": 5, "type": "keyboard", "value": "Hello!", "desc": "Type message"},
    {"order": 6, "type": "keyboard", "value": "enter", "desc": "Send message"}
  ],
  "expected_final_state": "WhatsApp showing chat with Harshit with 'Hello!' message sent"
}

## Example - Click on icon without text (SLOW - only when necessary):
{
  "sequence":[
    {"order": 1, "type": "visual_click", "target_name": "button_submit", "desc": "Click Submit button"},
    {"order": 2, "type": "visual_click", "target_name": "dropdown_options", "desc": "Open dropdown menu"}
  ],
  "expected_final_state": "Form submitted with dropdown menu expanded showing options"
}
