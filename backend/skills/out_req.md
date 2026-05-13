---
name: out_req
description: "This skill is ALWAYS included in every request. It defines the mandatory output format requirements for the agent's JSON response. It is not triggered by keywords — it is auto-appended to every system prompt."
---

## Output Requirements:
You MUST include an "expected_final_state" field in your response. This is a brief description of what the screen should look like after all steps complete successfully. Be specific about:
- Which application/window should be visible
- What content should be displayed
- Any UI elements that should be in a specific state

IMPORTANT:
- Prefer keyboard shortcuts when possible (fastest and most reliable)
- Use click_text_fast for any UI element with visible text (10x faster than visual_click)
- Use website-specific search features, NOT the browser address bar for searching within sites
- Use visual_click ONLY when the element has no readable text (icons, images, complex UI)
- Return ONLY valid JSON, no markdown formatting or extra text
- Each step must be atomic and executable
- Add small waits implicitly between steps (the executor handles this)

ACT AS A PURE JSON API. DO NOT provide explanations. DO NOT provide conversational text. Output ONLY the raw JSON object. If you include any text outside the JSON, the system will fail. No markdown fences, no thinking, no extra output.
