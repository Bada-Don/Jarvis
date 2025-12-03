# JARVIS - Future Improvements

## ✅ Completed
- [x] General computer automation (not just FlexiSIGN)
- [x] Auto-detect mode (general vs FlexiSIGN) based on command
- [x] Unified Two-Model Pipeline for all tasks
- [x] Improved Vision Mapper prompts for general UI elements

## 🔄 In Progress
- [ ] Improve icon detection accuracy (Gemini sometimes picks wrong elements)
- [ ] Make SoM more robust (FastSAM tuning)

## 📋 Planned
1. **Hot word for voice activation** ("Hey JARVIS")
   - Use Porcupine or similar wake word detection
   - Continuous listening mode

2. **Camera access**
   - Read handwritten notes
   - Scan documents/images for OCR

3. **Microphone access / Voice input**
   - Speech-to-text for commands
   - Look at Self-Operating Computer's `--voice` mode for reference

4. **Better icon detection**
   - Combine FastSAM with EasyOCR for text-based elements
   - Fine-tune confidence thresholds
   - Add fallback strategies when vision fails

5. **Multi-monitor support**
   - Detect which monitor to use
   - Handle different resolutions

6. **Task scheduling**
   - "Remind me to..." commands
   - Scheduled automation tasks

7. **Conversation memory**
   - Remember context from previous commands
   - "Do that again" / "Undo that"

8. **Error recovery**
   - Detect when clicks miss their target
   - Auto-retry with adjusted coordinates

## 💡 Ideas
- Browser extension for better web automation
- Integration with Windows accessibility APIs
- Custom hotkeys for common tasks
- Task recording (watch and learn)
