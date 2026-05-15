# Core Architecture: Task-Exchange Model

Warp organizes AI agent activity into a three-tier hierarchy that provides robustness, transactional integrity, and better context management.

## 1. The Hierarchy

### **Task** (`TaskId`)
*   **Definition:** A high-level goal or a discrete sub-goal (e.g., "Fix the login bug").
*   **Role:** Acts as a container for multiple exchanges. Tasks can be nested (hierarchical), allowing for sub-agents to operate on specific task nodes.
*   **Reference:** `app/src/ai/agent/task.rs`

### **Exchange** (`AIAgentExchangeId`)
*   **Definition:** A single "turn" in the conversation.
*   **Structure:**
    1.  **Input:** User query or system trigger.
    2.  **Output:** LLM reasoning and requested `AIAgentAction`s (tools).
    3.  **Result:** The outcome of the tool execution (`AIAgentActionResultType`).
*   **Reference:** `app/src/ai/agent/mod.rs` (definition of `AIAgentExchange`)

### **Transaction**
*   **Definition:** A mechanism to ensure that updates to the conversation state are atomic.
*   **Role:** When an agent produces output or a tool returns a result, the `Transaction` ensures the `TaskStore` is updated safely, preventing partial or corrupted history states.
*   **Reference:** `app/src/ai/agent/task/transaction.rs`

## 2. Key Components

### **TaskStore**
*   **Role:** A centralized repository for all tasks and exchanges in a session.
*   **Linearization:** It maintains a "linearized" index of exchanges for quick access to the most recent turn, even when the underlying structure is hierarchical.
*   **Reference:** `app/src/ai/agent/task_store.rs`

### **AIConversation**
*   **Role:** The top-level entity representing a full Agentic session.
*   **Metadata:** Tracks usage (tokens, credits), summarization status, and "autonomy level" (whether to ask for permission before tools).
*   **Reference:** `app/src/ai/agent/conversation.rs`

## 3. Why this matters for Jarvis

Jarvis currently implements a **Role-Based History** (roles like `thought`, `action`, `observation`, `user`). While this provides some structure, it remains a "flat" list of messages within a session. Adopting Warp's **Task-Exchange** model would elevate this:

1.  **Context Pruning:** We can "collapse" completed tasks in the LLM's context window. Instead of sending every line of debug output from a previous sub-goal, we can send only the final summary of that task.
2.  **Transaction Safety:** Jarvis's state updates are currently immediate. Warp's "Transaction" pattern would allow Jarvis to verify an entire sequence of tool results before "committing" them to the persistent history, making it easier to recover from failures or cancellations.
3.  **Sub-Agent Orchestration:** It provides a native way for a "Master Planner" to spawn "Sub-Agents" on specific `TaskId` nodes, keeping their context isolated and preventing "prompt drift."

## 🔗 References
*   `warp-master/app/src/ai/agent/conversation.rs`
*   `warp-master/app/src/ai/agent/task.rs`
*   `warp-master/app/src/ai/agent/task_store.rs`
