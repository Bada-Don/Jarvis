# Warp Architecture & Tool Patterns: Executive Summary

This directory contains a detailed breakdown of the architectural patterns and tool implementation strategies extracted from the [Warp](https://github.com/warpdotdev/warp) codebase. The goal is to adapt these patterns to make Jarvis's agentic operations more "smooth and reliable."

## 📂 Documentation Index

1.  **[Core Architecture: Task-Exchange Model](./01_core_architecture.md)**
    *   Breakdown of the `Task`, `Exchange`, and `Transaction` system.
    *   How Warp manages conversation state and context pruning.
2.  **[Smart File Editing: Fuzzy-Matching Diffs](./02_smart_editing.md)**
    *   Deep dive into the `V4A` diff format and the `fuzzy_match_v4a_diffs` algorithm.
    *   Strategies for handling LLM hallucinations in code edits.
3.  **[Robust File I/O: Budgets & Metadata](./03_file_io.md)**
    *   Analysis of `TextFileAccumulator` and byte-budgeted reading.
    *   Binary detection and ranged reads.
4.  **[Structured Agent Interaction](./04_agent_interaction.md)**
    *   The `AskUserQuestion` tool: Multi-choice, recommendations, and structured feedback.
    *   Terminal grid snapshots for long-running/interactive processes.
5.  **[Extensibility: MCP & Skills](./05_mcp_and_skills.md)**
    *   How Warp integrates Model Context Protocol (MCP) and `.agents/skills`.

## 🚀 Key Takeaways for Jarvis

*   **Move away from full-file rewrites:** Implement context-aware diffs with fuzzy matching.
*   **Prevent Context Overflow:** Implement byte budgets for file reads.
*   **Improve Clarity:** Use structured selection cards instead of open-ended text questions where possible.
*   **Handle Interactivity:** Capture terminal snapshots for REPLs and watchers.

---
*Reference: Research conducted May 2026. Source: `warp-master/` repository.*
