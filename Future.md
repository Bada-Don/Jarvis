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
   - Try Hardcoded voice replies. 

2. **Camera/Media access**
   - Read handwritten Nameplate content to write in FlexiSIGN
   - Import Documents sent from phone in FlexiSIGN and save.
   - Automatically detect what the number is, and what size...  

3. **Microphone access / Voice input**
   - Speech-to-text for commands
   - On device processing of Voice for better performance and transmission.

4. **Optimizing Prompts using Toon Data Structure**
   - Use Toon instead of JSON for lesser token consumption

5. **Verification Mechanism**
   - Ask the planner model to give a description of expected final state
   - Example: 
   -          "FlexiSIGN window with Harshit Singla written in it" 
              "Google docs opened and Hello World written in it" 
   - Take a screenshot of the final state and send that to the planner model
   - Compare the two and perform operations if needed

6. **Better icon detection**
   - Combine FastSAM with EasyOCR for text-based elements
   - Fine-tune confidence thresholds
   - Add fallback strategies when vision fails

7. **Multi-monitor support**
   - Detect which monitor to use
   - Handle different resolutions

8. **Task scheduling**
   - "Remind me to..." commands
   - Scheduled automation tasks

9. **Conversation memory**
   - Remember context from previous commands
   - "Do that again" / "Undo that"

10. **Error recovery**
   - Detect when clicks miss their target
   - Auto-retry with adjusted coordinates

## 💡 Ideas
- Browser extension for better web automation
- Custom hotkeys for common tasks in Mobile App
- Task recording (watch and learn, with Windows accessibility APIs)


## Sample Commands:
- "Open Gmail and compose a mail"
- "Open notepad, write hello world and save to desktop"
- "Make front iron number plate PB12W3998"
- "Open Google Docs and write a note"
- "Write Harshit Singla in Blackberry font and size 4 inch x 0.5 inch"
