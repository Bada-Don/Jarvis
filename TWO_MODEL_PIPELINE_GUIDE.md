# Two-Model Pipeline - Setup & Usage Guide

Automate FlexiSIGN number plate creation using voice/text commands from your mobile app.

## Architecture Overview

```
Mobile App  →  Backend Server  →  Local Client  →  FlexiSIGN
   (React Native)    (Flask)         (Python)       (Desktop App)
                       ↓                ↓
               Gemini Flash Lite   Gemini 2.0 Flash
               (Planner Model)    (Vision Mapper)
```

## Prerequisites

- Windows PC with FlexiSIGN installed
- Python 3.10+
- Gemini API Key (from Google AI Studio)
- Mobile device on same network as PC

## Setup Instructions

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the key for the next steps

### 2. Configure Backend Server

```bash
cd backend

# Create .env file
copy .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_api_key_here

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

Server runs on `http://0.0.0.0:5000`

### 3. Configure Local Client

```bash
cd local_client

# Create .env file
copy .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_api_key_here

# Install dependencies
pip install -r requirements.txt

# Start the client
python client.py
```

### 4. Configure FlexiSIGN Path (Optional)

Edit `local_client/flexisign_config.json` if FlexiSIGN is installed in a non-default location:

```json
{
  "exe_path": "C:\\Program Files\\FlexiSIGN-PRO\\FlexiSIGN-PRO.exe",
  "window_title": "FlexiSIGN-PRO"
}
```

### 5. Run Mobile App

```bash
cd ChatInterface

npm install
npx expo start
```

Scan QR code with Expo Go app on your phone.

## Usage

### Supported Commands

Send these commands from the mobile app:

| Command | Result |
|---------|--------|
| "Make iron number plate set for bike, PB12W3998" | Creates front (8x1.2) and back (10x1.5) plates |
| "Make glass number plate for bike, MH12AB1234" | Creates front (6x1.2) and back (10x1.5) plates |
| "Make car number plate, DL01CA0001" | Creates front (14x2.3) and back (14x2.4) plates |

### What Happens

1. Your command goes to the backend server
2. Gemini Flash Lite generates an execution plan
3. Plan is sent to local client via WebSocket
4. Local client:
   - Opens FlexiSIGN (if not already open)
   - Takes a screenshot
   - Detects UI elements using FastSAM
   - Gemini 2.0 Flash identifies which buttons to click
   - Executes keyboard actions and clicks
5. Progress updates appear on your mobile app

## Plate Dimensions Reference

| Plate Type | Front Size | Back Size |
|------------|------------|-----------|
| Bike Iron | 8 x 1.2 inches | 10 x 1.5 inches |
| Bike Glass | 6 x 1.2 inches | 10 x 1.5 inches |
| Car Normal | 14 x 2.3 inches | 14 x 2.4 inches |

## Troubleshooting

### "Vision Mapper not finding elements"
- Ensure FlexiSIGN is visible on screen (not minimized)
- Close any overlapping windows
- Try again - AI vision can vary

### "Connection failed"
- Check backend server is running on port 5000
- Ensure mobile and PC are on same network
- Check firewall isn't blocking port 5000

### "API key error"
- Verify GEMINI_API_KEY is set in both `.env` files
- Check the key is valid at Google AI Studio

### "FlexiSIGN not starting"
- Run local client as Administrator
- Check `flexisign_config.json` has correct exe path

## Running Tests

```bash
# Backend tests
python -m unittest backend.tests.test_integration_pipeline -v

# Local client tests  
cd local_client
python -m unittest tests.test_integration_local_client -v

# Full E2E test
python tests/test_e2e_pipeline.py
```

## File Structure

```
├── backend/
│   ├── server.py              # Flask server + WebSocket
│   ├── gemini_service.py      # Planner Model (Gemini Flash Lite)
│   └── .env                   # API key config
│
├── local_client/
│   ├── client.py              # WebSocket client + command handler
│   ├── vision_service.py      # Screenshot + SoM + Vision Mapper
│   ├── plan_executor.py       # Executes keyboard/mouse actions
│   ├── flexisign_manager.py   # Launches/manages FlexiSIGN
│   └── .env                   # API key config
│
├── ChatInterface/             # React Native mobile app
│
└── tests/                     # Integration tests
```
