# Extensibility: MCP & Skills

Both Warp and Jarvis have moved toward a modular "Skills" architecture using Markdown files. However, Warp's implementation provides a more mature framework for discovery, scoping, and external protocol integration.

## 1. Local Skills (Comparing Warp vs. Jarvis)

### **Jarvis's Current State**
*   **Storage:** Skills are stored as `.md` files in `backend/skills/`.
*   **Discovery:** Uses a central `manifest.json` to map triggers (keywords) to specific skill files.
*   **Metadata:** Uses YAML front matter for basic `name` and `description`.
*   **Workflow:** Instructions guide the LLM through tool usage (e.g., Read → Analyze → Edit).

### **Warp's Implementation**
*   **Storage:** Scans multiple directories: `~/.agents/skills/` (global) and `./repo/.agents/skills/` (project-local).
*   **Dynamic Discovery:** No central `manifest.json` is required for discovery; Warp automatically parses all `.md` files in the skill directories.
*   **Scoped Precedence:** Warp implements a `provider_rank`. If a project has a local `read_file` skill, it can override the global one for that specific repo.
*   **Bundled Skills:** Core functionalities (like `add-mcp-server`) are "Bundled" and read-only, ensuring system integrity while allowing user expansion.

## 2. Model Context Protocol (MCP)

This is the largest gap between Warp and Jarvis. Warp is an early adopter of MCP, a standardized protocol for connecting AI models to data sources.

### **How it works in Warp:**
*   **Unified Client:** Warp has a `TemplatableMCPServerManager` that acts as a generic MCP client.
*   **Dynamic Tooling:** Instead of writing an `.md` file for every new tool (like Slack, GitHub, or Postgres), Warp simply connects to an MCP server. The server "advertises" its tools, and Warp's agent automatically adopts them.
*   **Authentication (OAuth):** Warp handles the complex OAuth flows for third-party integrations natively. If a skill requires Slack access, Warp manages the browser-based login and token storage safely.

## 3. Why this matters for Jarvis

While Jarvis's transition to `.md` files is a great step forward, it still requires manual "wiring" via `manifest.json` and custom Python code for every new integration.

**Refined Implementation Plan for Jarvis:**
1.  **Dynamic Discovery:** Eliminate the need for `manifest.json` by auto-scanning `backend/skills/*.md` on startup. This makes it easier to add/remove skills.
2.  **Native MCP Integration:** Build a Python-based MCP client. This would allow Jarvis to use the [vast ecosystem of MCP servers](https://github.com/modelcontextprotocol/servers) (e.g., for Google Drive, Brave Search, or SQLite) without any custom code.
3.  **Project-Local Skills:** Allow Jarvis to look for a `.jarvis/skills/` directory in the current working directory. This lets users define repo-specific tools that follow the project.
4.  **Credential Management:** Implement a secure way to handle API keys for these skills (similar to Warp's `ManagedSecretManager`), rather than relying on `.env` files.

## 🔗 References
*   `warp-master/app/src/ai/mcp/templatable_manager.rs` (MCP lifecycle)
*   `warp-master/app/src/ai/skills/skill_manager.rs` (Local skill management)
*   `backend/skills/manifest.json` (Jarvis's current implementation)

