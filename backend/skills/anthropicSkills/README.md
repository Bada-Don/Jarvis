# Claude Skills Library

This is a collection of Markdown-based skills extracted from Anthropic's Claude platform. Each skill is a self-contained guide for your agent to follow when handling specific tasks.

## What Are Skills?

Skills are **Markdown files injected into the system prompt at runtime** when a relevant trigger is detected. They're the mechanism Claude uses to specialize behavior for specific domains (document creation, spreadsheets, frontend design, etc.).

You can fully replicate this pattern in your own agent system.

## Skills Included

### Document & Data Processing

- **docx.md** - Create, edit, read Word documents (.docx files)
- **pdf.md** - PDF processing: merge, split, extract, create, fill forms
- **pdf-reading.md** - Read and inspect PDFs: text extraction, visual inspection, embedded content
- **pptx.md** - Create, edit, read PowerPoint presentations (.pptx files)
- **xlsx.md** - Create, edit, read spreadsheets with formulas and formatting
- **file-reading.md** - Router skill: determines which tool to use for 15+ file types

### Design & Frontend

- **frontend-design.md** - Build production-grade web UIs and components
- **humanizer-pro.md** - Transform AI-generated text to sound human (5-pass system)

### Product Knowledge

- **product-self-knowledge.md** - Facts about Anthropic's Claude products (API, Claude Code, Claude.ai)

## How to Use These Skills

### 1. Skill Router Pattern

Implement a simple keyword matcher in your agent:

```python
def detect_skill(user_message: str) -> str | None:
    keywords = {
        "docx": ["word", "doc", "document"],
        "xlsx": ["spreadsheet", "excel", "csv"],
        "pdf": ["pdf", "merge", "extract"],
        "frontend-design": ["website", "ui", "component"],
        "humanizer-pro": ["humanize", "sound human"],
    }
    
    message_lower = user_message.lower()
    for skill, triggers in keywords.items():
        if any(trigger in message_lower for trigger in triggers):
            return skill
    return None
```

### 2. Load and Inject the Skill

```python
def inject_skill(skill_name: str, system_prompt: str) -> str:
    with open(f"skills/{skill_name}.md") as f:
        skill_content = f.read()
    return f"{system_prompt}\n\n## Skill: {skill_name}\n\n{skill_content}"
```

### 3. Call Your Agent with Enhanced Prompt

```python
detected_skill = detect_skill(user_message)
enhanced_prompt = system_prompt

if detected_skill:
    skill_file = f"skills/{detected_skill}.md"
    enhanced_prompt = inject_skill(skill_name=detected_skill, system_prompt=system_prompt)

response = agent.chat(
    system_prompt=enhanced_prompt,
    user_message=user_message
)
```

## Scaling to More Skills

As you build more specialized skills:

1. **Create `.md` files** following the format: YAML frontmatter + content
2. **Add to your router** with keyword triggers
3. **Version control** — keep skills in git for changes
4. **Test** — verify the skill content is accurate before injecting

## Architecture Insights

The key design principles Claude uses:

- **Separation of concerns**: Each skill handles one domain
- **Self-contained**: Skills don't depend on other skills
- **Triggering**: Keywords in user message determine which skill loads
- **Composability**: Agent system prompt + loaded skill = enhanced behavior
- **No hardcoding**: Skills are data (Markdown) injected at runtime, not code

## Dependencies for Running These Skills

### Document Skills
- `npm install -g docx` (docx creation)
- `npm install -g pptxgenjs` (pptx creation)
- `pip install openpyxl pandas` (spreadsheet handling)
- `pip install pypdf pdfplumber reportlab` (PDF processing)
- LibreOffice (PDF conversion, formula recalculation)
- Poppler (pdftoppm, pdftotext, pdfimages)

### Frontend Skills
- Node.js and npm for JavaScript-based tools
- CSS knowledge for frontend-design implementations

### Text Processing
- None (humanizer-pro is pure pattern matching)

## Contributing

Want to add more skills?

1. Create a new `.md` file in the `skills/` directory
2. Follow the YAML frontmatter format (name, description)
3. Write clear, actionable instructions
4. Test with your agent
5. Add to the router

## License

These skills are based on Anthropic's proprietary system but extracted here as educational reference material for your own agent architecture.

---

**Built with reference to Claude's actual skill system** — use these as inspiration for your own agent's specialized behaviors.
