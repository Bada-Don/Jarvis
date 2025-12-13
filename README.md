# JARVIS - AI Computer Automation Assistant

A voice/text-controlled AI assistant that can automate tasks on your Windows PC. Uses a Two-Model Pipeline architecture for intelligent task planning and visual UI interaction.

## Features

- **General Computer Automation**: Open apps, browse the web, type text, click buttons
- **FlexiSIGN Integration**: Specialized number plate creation workflow
- **Mobile App Control**: Send commands from your phone via React Native app
- **Voice Input**: Record voice messages with on-device speech-to-text (Whisper)
- **Visual UI Detection**: Uses FastSAM + Gemini Vision to identify and click UI elements
- **Real-time Progress**: See step-by-step execution status on your phone

## Architecture

```
Mobile App  →  Backend Server  →  Local Client  →  Your PC
   (React Native)    (Flask)         (Python)       (Windows)
                       ↓                ↓
               Gemini Flash Lite   Gemini 2.0 Flash
               (Planner Model)    (Vision Mapper)
```

### Two-Model Pipeline

1. **Planner Model** (Gemini Flash Lite): Converts natural language to execution steps
2. **Vision Mapper** (Gemini 2.0 Flash): Identifies UI elements on screen for clicking

## Example Commands

### General Tasks
- "Open Notepad and type Hello World"
- "Open Chrome and go to google.com"
- "Open Calculator"
- "Take a screenshot" (coming soon)

### FlexiSIGN Tasks
- "Make iron number plate set for bike, PB12W3998"
- "Make glass number plate for bike, MH12AB1234"
- "Make car number plate, DL01CA0001"

## Quick Start

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Copy it for the next steps

### 2. Setup Backend Server

```bash
cd backend
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

pip install -r requirements.txt
python server.py
```

### 3. Setup Local Client

```bash
cd local_client
copy .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

pip install -r requirements.txt
python client.py
```

### 4. Setup Mobile App (Optional)

```bash
cd ChatInterface
npm install
npx expo start
```

Scan QR code with Expo Go app.

## How It Works

1. You send a command: "Open Notepad and type Hello"
2. **Planner Model** creates a step-by-step plan:
   - Press Win key
   - Type "notepad"
   - Press Enter
   - Type "Hello"
3. **Local Client** executes keyboard steps immediately
4. For visual clicks, it takes a screenshot
5. **FastSAM** detects all UI elements and numbers them
6. **Vision Mapper** identifies which numbered box matches the target
7. Client clicks at the center of that box

## Project Structure

```
├── backend/
│   ├── server.py           # Flask + WebSocket server
│   ├── gemini_service.py   # Planner Model (general + FlexiSIGN)
│   └── .env                # API key
│
├── local_client/
│   ├── client.py           # WebSocket client + command handler
│   ├── vision_service.py   # Screenshot + SoM + Vision Mapper
│   ├── plan_executor.py    # Executes keyboard/mouse actions
│   ├── flexisign_manager.py # FlexiSIGN app lifecycle
│   └── .env                # API key
│
├── ChatInterface/          # React Native mobile app
│
└── debug_logs/             # Execution logs for troubleshooting
```

## Debug Logs

Each execution creates a debug folder:

```
debug_logs/2024-12-01_16-39-33/
├── session_info.json       # Command and timestamps
├── planner_output.json     # Execution plan
├── screenshot.png          # Original screenshot
├── annotated.png           # SoM annotated image
├── box_map.json            # Element coordinates
├── vision_mapper_output.json # Target to ID mapping
└── execution_log.txt       # Step-by-step log
```

## Troubleshooting

### "Vision Mapper not finding elements"
- Make sure the target window is visible (not minimized)
- Close overlapping windows
- Try the command again

### "Connection failed"
- Check backend server is running on port 5000
- Ensure PC and phone are on same network

### "API key error"
- Verify GEMINI_API_KEY in both .env files
- Check key validity at Google AI Studio

## Requirements

- Windows 10/11
- Python 3.10+
- Gemini API Key
- FastSAM weights (auto-downloaded)

## Recent Updates

### Voice Recording & Speech-to-Text (NEW!)
- ✅ Voice recording with microphone button
- ✅ On-device speech-to-text using OpenAI's Whisper
- ✅ Automatic text insertion after transcription
- ✅ Support for 99+ languages
- ✅ Smart fallback to audio file attachment

See [ChatInterface/QUICK_START_VOICE.md](ChatInterface/QUICK_START_VOICE.md) for setup.

## Future Plans

- [ ] Hot word voice activation ("Hey JARVIS")
- [ ] Real-time voice transcription (streaming)
- [ ] Camera access for visual input
- [ ] Improved icon detection accuracy
- [ ] Multi-monitor support
- [ ] Task scheduling
