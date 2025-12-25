import json
import re

def sanitize_json_llm(text: str) -> str:
    """
    Sanitizes JSON string with common LLM syntax errors.
    1. Fixes unescaped backslashes (e.g., Windows paths).
    2. Fixes unescaped double quotes inside string values.
    """
    # ------------------------------------------------------------------
    # Step 1: Fix unescaped backslashes globally
    # ------------------------------------------------------------------
    # This regex looks for a backslash '\' that is NOT followed by 
    # a valid escape character (", \, /, b, f, n, r, t, u).
    # We use a negative lookahead (?!...) to ensure we don't break valid escapes.
    text = re.sub(r'\\(?![\\/bfnrtu"])', r'\\\\', text)

    # ------------------------------------------------------------------
    # Step 2: Fix unescaped quotes inside values (Heuristic)
    # ------------------------------------------------------------------
    # LLMs often output: "key": "value with "inner quotes" inside"
    # We iterate and escape quotes that don't look like structural delimiters.
    result = []
    length = len(text)
    
    for i, char in enumerate(text):
        if char == '"':
            # If already escaped (preceded by backslash), keep as is
            if i > 0 and text[i-1] == '\\':
                result.append(char)
                continue

            # Check if this quote is "Structural" (part of JSON syntax)
            # A quote is structural if it is immediately adjacent to:
            #   - : (colon)
            #   - , (comma)
            #   - { } [ ] (brackets)
            #   (ignoring whitespace)
            
            is_structural = False
            
            # Look Behind
            j = i - 1
            while j >= 0 and text[j].isspace(): j -= 1
            if j >= 0 and text[j] in '{[:,': 
                is_structural = True

            # Look Ahead (only if not already found to be structural)
            if not is_structural:
                j = i + 1
                while j < length and text[j].isspace(): j += 1
                if j < length and text[j] in '}:],':
                    is_structural = True
            
            # If it's NOT structural, it's likely an inner quote -> Escape it
            if not is_structural:
                result.append('\\"')
            else:
                result.append(char)
        else:
            result.append(char)

    return ''.join(result)


def safe_json_loads(text: str) -> dict:
    """
    Parse JSON with automatic fix for LLM formatting issues.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to sanitize
        fixed = sanitize_json_llm(text)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            # If it still fails, raise the error with the fixed text for debugging
            raise json.JSONDecodeError(f"Failed to parse even after sanitization. Fixed text:\n{fixed}\nError: {str(e)}", fixed, 0)

# --- Test Case ---
if __name__ == "__main__":
    bad_json = r"""
    {
    "sequence": [
    {
    "order": 2,
    "type": "keyboard",
    "value": "cmd /c mkdir "C:\Users\harsh\OneDrive\Desktop\Practicals" && type nul > "C:\Users\harsh\OneDrive\Desktop\Practicals\P1.docx"",
    "desc": "Create the Practicals folder"
    }
    ]
    }
    """
    
    print("Original broken JSON loads:", False)
    data = safe_json_loads(bad_json)
    print("\nSuccessfully parsed!")
    print(f"Fixed Path: {data['sequence'][0]['value']}")