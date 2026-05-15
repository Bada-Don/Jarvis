# Structured Agent Interaction & Terminal Mastery

Warp excels at providing high-fidelity feedback loop mechanisms, especially for user clarification and terminal-based workflows.

## 1. Structured Interaction: `AskUserQuestion`

Instead of relying on the user to interpret a text-based question and reply with the "correct" string, Warp uses a structured tool to guide the interaction.

### **Features:**
*   **Question IDs:** Each question is tracked with a unique ID, allowing the agent to correlate specific answers to specific internal tasks.
*   **Types:** Supports `MultipleChoice` (with `is_multiselect` support).
*   **Recommendations:** The agent can mark certain options as `recommended: true`. The UI can then highlight these (e.g., a "Primary" button), making the agent's intent clear.
*   **"Other" Fallback:** A `supports_other` flag allows for a free-form text input if none of the provided options fit.

**Benefit:** This reduces ambiguity and prevents the agent from getting stuck when a user provides a slightly different answer than expected.

## 2. Terminal Mastery: Snapshots & LRC

Because Warp is a terminal emulator, it treats shell commands as first-class citizens with deep introspection.

### **Terminal Snapshots** (`LongRunningCommandSnapshot`)
When a command is long-running (LRC), Warp doesn't just wait for it to finish. It can take a "Snapshot" of the active terminal:
*   **`grid_contents`**: The actual characters visible on the screen.
*   **`cursor`**: The (x, y) position of the cursor.
*   **`is_alt_screen_active`**: Detects if the user is in a TUI like `vim`, `htop`, or `less`.

**Why it's cool:** This allows the agent to "see" what's happening in real-time. If an agent runs a dev server and it's waiting for input, the snapshot tells the agent exactly what's on the screen so it can provide the right input.

### **PTY Write Modes** (`AIAgentPtyWriteMode`)
Warp provides different ways for an agent to "type" into a running terminal:
*   **`Raw`**: Sends bytes exactly as-is.
*   **`Line`**: Sends the text followed by a newline (the "Enter" key).
*   **`Block`**: Uses **Bracketed Paste** mode (`\x1b[200~ ... \x1b[201~`). This is critical for pasting large blocks of code into REPLs or TUIs without triggering auto-indentation or other "typing" side-effects.

## 3. Why this matters for Jarvis

Jarvis's current interaction is limited to standard Python `input()` or chat-based text. Its terminal support is limited to captured stdout/stderr after the command finishes.

**Implementation Plan for Jarvis:**
1.  **Structured `ask_user`:** Update the `ask_user` tool to accept an `options` list. The Chat UI can then render these as selectable chips/buttons.
2.  **LRC Visibility:** For long-running shell commands, implement a "Snapshot" capability that reads the tail of the log or uses a PTY capture to give the agent a "live look" at the process.
3.  **Bracketed Paste:** When Jarvis uses `keyboard` or `shell_command` to write code, it should detect if the target supports bracketed paste to ensure the code remains perfectly formatted.

## 🔗 References
*   `warp-master/crates/ai/src/agent/action/mod.rs` (Action definitions)
*   `warp-master/crates/ai/src/agent/action_result/mod.rs` (Snapshot definitions)
*   `warp-master/app/src/ai/agent/conversation.rs` (Command block info & PWD management)
