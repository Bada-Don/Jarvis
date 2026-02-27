import os
import difflib
import subprocess
import platform
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 1. Define the Structured Output Schema ---
# This ensures the LLM ALWAYS replies in this exact format.
class EditCommand(BaseModel):
    search_text: str
    replace_text: str

class FileEdits(BaseModel):
    edits: list[EditCommand]

# --- 2. Core Functions ---
def get_ai_edits(file_content: str, prompt: str) -> FileEdits:
    """Sends the file and prompt to the LLM and gets structured edits back."""
    system_prompt = """
    You are an expert coding assistant and file editor. 
    Your task is to modify the provided file content based on the user's prompt.
    You must output a list of search and replace operations.
    CRITICAL RULES:
    1. 'search_text' must be an EXACT match of the text currently in the file. Include exact whitespace and indentation.
    2. 'replace_text' is the new text that will replace 'search_text'.
    3. Make the 'search_text' uniquely identifiable (include a few lines above/below if necessary to ensure it only matches one place).
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o", # Use gpt-4o for high reliability
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"File Content:\n```\n{file_content}\n```\n\nUser Request: {prompt}"}
        ],
        response_format=FileEdits,
    )

    return completion.choices[0].message.parsed

def apply_edits(original_content: str, edits: list[EditCommand]) -> str:
    """Applies the search/replace edits to the content in memory."""
    new_content = original_content
    for edit in edits:
        if edit.search_text in new_content:
            new_content = new_content.replace(edit.search_text, edit.replace_text)
        else:
            print(f"\n[WARNING] Could not find the following exact text to replace:\n'''{edit.search_text}'''\n")
    return new_content

def show_diff(original_content: str, new_content: str, filepath: str):
    """Generates and prints a unified diff in the console."""
    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{os.path.basename(filepath)}",
        tofile=f"b/{os.path.basename(filepath)}",
        n=3 # Number of context lines
    )
    diff_text = "".join(diff)
    if not diff_text:
        print("No changes made.")
    else:
        print("\n--- PROPOSED CHANGES (DIFF) ---")
        print(diff_text)
        print("-------------------------------\n")

def open_file_in_editor(filepath: str):
    """Opens the file using the default OS viewer/editor."""
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # Linux variants
        subprocess.call(('xdg-open', filepath))

# --- 3. Main Workflow ---
def main():
    print("🤖 AI File Editor Agent")
    
    # Step 1: Get File Path
    filepath = input("1. Enter the absolute or relative path to the txt file: ").strip()
    
    if not os.path.isfile(filepath):
        print(f"Error: File not found at '{filepath}'.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Step 2: Get User Prompt
    prompt = input('2. What would you like to do? (e.g., "Replace placeholders with my name..."): \n> ').strip()

    print("\nThinking and generating edits...")
    
    # Step 3: Get Edits from AI and Create Diff
    try:
        parsed_edits = get_ai_edits(original_content, prompt)
    except Exception as e:
        print(f"Failed to communicate with AI: {e}")
        return

    new_content = apply_edits(original_content, parsed_edits.edits)
    
    if new_content == original_content:
        print("The AI didn't suggest any valid changes. Exiting.")
        return

    # Show Diffs
    show_diff(original_content, new_content, filepath)

    # Step 4: Confirm and Apply Changes
    confirm = input("4. Apply these changes and save? (y/n): ").strip().lower()
    if confirm == 'y':
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Success! Changes saved to {filepath}.")
        
        # Step 5: Open the file
        print("5. Opening file...")
        open_file_in_editor(filepath)
    else:
        print("Changes discarded.")

if __name__ == "__main__":
    main()
