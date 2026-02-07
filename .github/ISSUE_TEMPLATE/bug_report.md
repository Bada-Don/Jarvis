---
name: Bug Report
about: Report a bug to help us improve JARVIS
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Start JARVIS components (backend, local client, mobile app)
2. Send command: "..."
3. Observe behavior: "..."
4. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Screenshots / Videos

If applicable, add screenshots or screen recordings to help explain the problem.

## Debug Logs

Please attach relevant files from your `debug_logs/` folder:

- [ ] `session_info.json`
- [ ] `planner_output.json`
- [ ] `execution_log.txt`
- [ ] `screenshot.png` (if vision-related)
- [ ] `annotated.png` (if vision-related)
- [ ] `vision_mapper_output.json` (if vision-related)

**Paste relevant log excerpts here:**
```
[Paste logs here]
```

## System Information

**Operating System:**
- [ ] Windows 10
- [ ] Windows 11
- Version: [e.g., 22H2]

**Python Version:**
```
[Output of: python --version]
```

**Node.js Version:**
```
[Output of: node --version]
```

**JARVIS Components:**
- Backend Server: [Running/Not Running]
- Local Client: [Running/Not Running]
- Mobile App: [Connected/Disconnected]

**LLM Provider:**
- [ ] Gemini (Flash Lite / 2.5 Flash)
- [ ] OpenAI (GPT-4 / GPT-3.5)

**Dependencies:**
- Tesseract OCR: [Installed/Not Installed]
- FastSAM weights: [Present/Missing]

## Additional Context

**Which execution plane failed?**
- [ ] Shell command execution
- [ ] File operations
- [ ] Keyboard actions
- [ ] Vision pipeline (FastSAM/Vision Mapper)
- [ ] Other: ___________

**Error messages:**
```
[Paste any error messages here]
```

**Frequency:**
- [ ] Always happens
- [ ] Happens sometimes
- [ ] Happened once

**Impact:**
- [ ] Blocks all functionality
- [ ] Blocks specific features
- [ ] Minor inconvenience

## Attempted Solutions

What have you tried to fix this?

- [ ] Restarted JARVIS components
- [ ] Checked API keys
- [ ] Verified file paths in config.py
- [ ] Reinstalled dependencies
- [ ] Checked debug logs
- [ ] Other: ___________

## Related Issues

Are there any related issues? Link them here.

---

**Checklist before submitting:**
- [ ] I've searched existing issues to avoid duplicates
- [ ] I've included debug logs
- [ ] I've provided system information
- [ ] I've described steps to reproduce
- [ ] I've attached screenshots (if applicable)
