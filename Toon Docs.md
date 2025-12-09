Here is a detailed Markdown document defining the TOON data format specification. You can save this as `TOON_SPEC.md` for your AI IDE's knowledge base.

***

# TOON (Token-Oriented Object Notation) Specification v1.0

**Status:** Stable  
**File Extension:** `.toon`  
**MIME Type:** `application/toon`  
**Encoding:** UTF-8 (Required)

## 1. Abstract
TOON is a minimal, schema-aware data serialization format designed specifically to minimize token usage for Large Language Models (LLMs) while maintaining human readability. It combines **YAML-like indentation** for nested structures with **CSV-style tabular headers** for uniform arrays.

**Primary Goal:** Reduce token count by 30-60% compared to JSON by removing redundant syntax (braces, repeated keys, quotes) while preserving strict typing and structural integrity.

***

## 2. Core Syntax & Grammar

### 2.1 Document Structure
A TOON document is a collection of key-value pairs, nested objects, and tabular arrays. It relies on **significant whitespace** (indentation) to define hierarchy.

- **Indentation:** Strictly **2 spaces** per level. Tabs are forbidden.
- **Separators:** Newlines separate properties; colons (`:`) separate keys from values.
- **Comments:** Lines starting with `#` are comments.

### 2.2 Scalars (Primitives)
TOON minimizes the use of quotes. Values are typed by inference unless quoted.

| Type | Syntax Rule | Examples |
| :--- | :--- | :--- |
| **String** | Unquoted by default. Quoted if containing special chars (`:`, `#`, `[`, `{`, `|`), delimiters, or leading/trailing whitespace. | `hello world`, `"123"` (force string), `"key:value"` |
| **Integer** | Standard decimal notation. | `42`, `-100` |
| **Float** | Decimal or scientific notation. | `3.14`, `-0.05`, `1.2e-5` |
| **Boolean** | Lowercase only. | `true`, `false` |
| **Null** | Lowercase literal. | `null` |

### 2.3 Objects
Objects use indentation to define children. Keys must be unquoted valid identifiers (alphanumeric + `_`, `.`). Complex keys containing spaces or special characters must be quoted.

```toon
user:
  id: 101
  name: Alice
  preferences:
    theme: dark
    notifications: true
```

### 2.4 Arrays
TOON supports two array formats: **Inline** (for short lists) and **Tabular** (for lists of objects).

#### A. Inline Arrays (Primitive Lists)
Used for simple lists of scalars.
```toon
tags[3]: react, typescript, ai
scores[4]: 10, 20, 30, 40
```
*Note: The `[N]` length indicator is optional for parsers but recommended for LLM generation to prevent hallucinations.*

#### B. Tabular Arrays (The "TOON" Speciality)
Used for arrays of uniform objects. This is where TOON saves the most tokens.
- **Header:** `key[count]{col1,col2,col3}:`
- **Rows:** CSV-style values indented by 2 spaces.

**JSON Equivalent:**
```json
"users": [
  {"id": 1, "name": "Alice", "role": "admin"},
  {"id": 2, "name": "Bob", "role": "user"}
]
```

**TOON Format:**
```toon
users[2]{id,name,role}:
  1,Alice,admin
  2,Bob,user
```

### 2.5 Key Folding (Dot Notation)
To further save tokens, nested singleton objects can be flattened using dot notation.

**Standard:**
```toon
server:
  config:
    port: 8080
```
**Folded (Valid TOON):**
```toon
server.config.port: 8080
```

***

## 3. Implementation Details for AI IDE

If you are building an IDE or parser to read TOON, implement the following logic.

### 3.1 Parsing Algorithm (State Machine)

1.  **Tokenizer:** Split document by newlines.
2.  **Indentation Check:** Measure leading spaces. If `indent % 2 != 0`, throw `SyntaxError`.
3.  **Line Type Detection:**
    *   **Comment:** Starts with `#` → Skip.
    *   **Header (Tabular):** Matches regex `^(\w+)\[(\d+)\]\{(.+)\}:\s*$`
        *   *Action:* Create array property. Parse `{...}` as column keys. Switch state to `READ_ROWS`.
    *   **Key-Value:** Matches `^([\w\.]+):\s*(.+)$`
        *   *Action:* Assign scalar value.
    *   **Parent Key:** Matches `^([\w\.]+):\s*$`
        *   *Action:* Create object. Push current context to stack. Increase expected indent.
    *   **Array Row (in READ_ROWS state):** Matches indentation level of parent array.
        *   *Action:* Split by comma (respecting quotes). Map values to column keys from Header.

### 3.2 Type Inference Rules
When parsing a scalar string `S`:
1.  If `S` is `"null"`, return `null`.
2.  If `S` is `"true"` or `"false"`, return `boolean`.
3.  If `S` matches `^-?\d+$`, return `int`.
4.  If `S` matches `^-?\d*\.\d+$` or scientific notation, return `float`.
5.  If `S` is wrapped in double quotes `""`, return string content (strip quotes).
6.  Else, return `S` as string.

### 3.3 Delimiter Handling
While comma `,` is the default delimiter, TOON supports explicit delimiters in headers for robustness.
*   **Pipe Delimiter:** `users[2|]{id|name}:` -> Row: `1|Alice`
*   **Tab Delimiter:** `users[2\t]{id\tname}:` -> Row: `1\tAlice`

### 3.4 Tokenization Strategy (For LLM Context)
When feeding TOON to an LLM, do not strip newlines or indentation; they are semantically significant.
*   **Tip:** Inject the schema header `users[N]{cols...}:` into the system prompt to force the model to output valid TOON tables.

***

## 4. Comparison: JSON vs. TOON

### Example Data
```json
{
  "employees": [
    { "id": 1, "name": "John Doe", "email": "john@example.com" },
    { "id": 2, "name": "Jane Smith", "email": "jane@example.com" },
    { "id": 3, "name": "Bob Jones", "email": "bob@example.com" }
  ]
}
```

### JSON (Tokens: ~65)
*Verbose. Repeated keys ("id", "name", "email") consume context window.*

### TOON (Tokens: ~35)
```toon
employees[3]{id,name,email}:
  1,John Doe,john@example.com
  2,Jane Smith,jane@example.com
  3,Bob Jones,bob@example.com
```
*Compact. Schema is defined once. Zero redundancy.*

***

## 5. IDE Features Checklist
To fully support TOON in your AI IDE, implement:

*   [ ] **Syntax Highlighting:**
    *   Keywords: `true`, `false`, `null` (Blue)
    *   Headers: `key[N]{...}:` (Purple/Bold)
    *   Strings: Quoted values (Green)
    *   Comments: (Grey)
*   [ ] **Folding/Unfolding:** Allow collapsing indentation levels and tabular array blocks.
*   [ ] **Schema Validation:** Warn if the number of items in a row doesn't match the columns defined in `{...}`.
*   [ ] **Auto-Conversion:** "Paste JSON as TOON" command (automatic flattening of arrays).
