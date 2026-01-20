# JARVIS - AI Computer Automation Assistant

## Problem Understanding

Modern computer automation faces a fundamental challenge: bridging the gap between natural language commands and precise UI interactions. Traditional automation tools require explicit scripting with exact coordinates or element identifiers, making them brittle and inaccessible to non-technical users.

Key challenges addressed:
- **Natural Language Ambiguity**: Users express tasks in varied, informal ways ("open notepad and type hello")
- **Dynamic UI Elements**: Screen layouts change based on resolution, themes, and application state
- **Visual Element Identification**: Clicking the right button requires understanding visual context
- **Cross-Application Automation**: Different apps have different UI patterns and interaction models

## Solution Approach

JARVIS implements a **Two-Model Pipeline** architecture that separates task planning from visual execution:

```mermaid
flowchart LR
    A[User Command] --> B[Planner Model]
    B --> C[Execution Plan]
    C --> D[Local Client]
    D --> E{Step Type?}
    E -->|Keyboard| F[Direct Execution]
    E -->|Visual Click| G[Vision Pipeline]
    G --> H[Screenshot + FastSAM]
    H --> I[Vision Mapper]
    I --> J[Click Coordinates]
    F --> K[Task Complete]
    J --> K
```

The solution decouples:
1. **Understanding WHAT to do** (Planner Model) from
2. **Understanding WHERE to click** (Vision Mapper)

This separation allows each model to specialize, improving accuracy and maintainability.

## Technical Methodology

### Two-Model Pipeline Architecture

```mermaid
sequenceDiagram
    participant User
    participant Backend
    participant Planner as Planner Model<br/>(Gemini Flash Lite)
    participant Client as Local Client
    participant Vision as Vision Mapper<br/>(Gemini 2.0 Flash)
    participant PC as Windows PC

    User->>Backend: "Open Chrome and go to google.com"
    Backend->>Planner: Generate execution plan
    Planner-->>Backend: JSON sequence of steps
    Backend->>Client: WebSocket: execute_plan
    
    loop For each step
        alt Keyboard Step
            Client->>PC: pyautogui keyboard action
        else Visual Click Step
            Client->>Client: Screenshot + FastSAM SoM
            Client->>Vision: Annotated image + targets
            Vision-->>Client: Target → Element ID mapping
            Client->>PC: Click at element center
        end
    end
    
    Client-->>User: Task complete
```

### Model 1: Planner (Gemini Flash Lite)

Converts natural language into structured execution plans. Supports two modes:

| Mode | Use Case | Knowledge |
|------|----------|-----------|
| General | Any computer task | Common UI patterns, keyboard shortcuts |
| FlexiSIGN | Designing/Professional Task | Plate dimensions, workflow sequences |

**Output Format:**
```json
{
  "mode": "general",
  "sequence": [
    {"order": 1, "type": "keyboard", "value": "win", "desc": "Open Start menu"},
    {"order": 2, "type": "keyboard", "value": "chrome", "desc": "Type app name"},
    {"order": 3, "type": "keyboard", "value": "enter", "desc": "Launch"},
    {"order": 4, "type": "visual_click", "target_name": "address_bar", "desc": "Click URL bar"}
  ]
}
```

### Model 2: Vision Mapper (Gemini 2.5 Flash)

Identifies UI elements in annotated screenshots. Uses Set-of-Mark (SoM) technique:

1. **FastSAM** detects all UI elements and draws numbered red boxes
2. **Vision Mapper** receives the annotated image + target list
3. Returns mapping: `{"address_bar": 45, "submit_button": 12}`

### Single-Pass Vision Architecture

For efficiency, the vision pipeline runs once per plan:

```mermaid
flowchart TD
    A[Plan Received] --> B{Has Visual Clicks?}
    B -->|No| C[Execute Keyboard Steps]
    B -->|Yes| D[Collect All Visual Targets]
    D --> E[Take Screenshot]
    E --> F[Run FastSAM SoM]
    F --> G[Call Vision Mapper Once]
    G --> H[Cache ID Map + Box Map]
    H --> I[Execute All Steps]
    I --> J{Step Type}
    J -->|Keyboard| K[pyautogui.press/write]
    J -->|Visual Click| L[Lookup cached coordinates]
    L --> M[pyautogui.click]
```

## Tools, Models & Architecture

### Technology Stack

```mermaid
graph TB
    subgraph Frontend
        A[React Native Mobile App]
    end
    
    subgraph Backend Server
        B[Flask + SocketIO]
        C[Gemini Flash Lite<br/>Planner Model]
    end
    
    subgraph Local Client
        D[Python WebSocket Client]
        E[FastSAM<br/>UI Detection]
        F[Gemini 2.5 Flash<br/>Vision Mapper]
        G[pyautogui<br/>Mouse/Keyboard]
    end
    
    A <-->|HTTP/WebSocket| B
    B --> C
    B <-->|WebSocket| D
    D --> E
    D --> F
    D --> G
```

### Component Details

| Component | Technology | Purpose |
|-----------|------------|---------|
| Mobile App | React Native + Expo | User interface for commands |
| Backend Server | Flask + Flask-SocketIO | API gateway, plan generation |
| Planner Model | Gemini 2.5 Flash Lite | NL → Execution plan |
| Vision Mapper | Gemini 2.5 Flash | Image → Element IDs |
| SoM Detection | FastSAM (Ultralytics) | UI element segmentation |
| Automation | pyautogui + pywin32 | Mouse/keyboard control |
| Communication | WebSocket | Real-time bidirectional |

### Key Files Structure

```
├── backend/
│   ├── server.py           # Flask API + WebSocket hub
│   ├── gemini_service.py   # Planner Model integration
│   └── SoM.py              # FastSAM annotation logic
│
├── local_client/
│   ├── client.py           # WebSocket client, command router
│   ├── vision_service.py   # Screenshot, SoM, Vision Mapper
│   ├── plan_executor.py    # Step execution engine
│   └── flexisign_uia.py    # FlexiSIGN-specific automation
│
└── ChatInterface/          # React Native mobile app
```

### Execution Modes

The system supports two execution strategies:

```mermaid
flowchart LR
    A[Execution Plan] --> B{Mode?}
    B -->|Vision| C[Screenshot-based]
    B -->|Direct| D[UIA-based]
    
    C --> E[FastSAM + Gemini Vision]
    C --> F[Click by coordinates]
    
    D --> G[Windows UI Automation]
    D --> H[Direct element access]
```

| Mode | When Used | Advantages |
|------|-----------|------------|
| Vision | General tasks, unknown UIs | Works with any application |
| Direct | FlexiSIGN, known UIs | Faster, more reliable |

## Expected Impact

### Immediate Benefits

- **Accessibility**: Non-technical users can automate complex tasks via natural language
- **Flexibility**: Works across any Windows application without pre-configuration
- **Reliability**: Two-model separation reduces hallucination and improves accuracy
- **Debuggability**: Comprehensive logging captures screenshots, plans, and mappings

### Use Cases

| Domain | Example Commands |
|--------|------------------|
| General Automation | "Open Notepad and write an essay on Automation" |
| Web Browsing | "Open Chrome and go to youtube.com" |
| FlexiSIGN | "Make iron number plate set for bike, PB12W3998" |
| File Operations | "Go to Desktop and create a new folder named Hackathon" |

### Performance Characteristics

- **Plan Generation**: ~1-2 seconds (Gemini Flash Lite)
- **Vision Pass**: ~3-5 seconds (Screenshot + FastSAM + Vision Mapper)
- **Step Execution**: ~0.3-0.5 seconds per step
- **Total Latency**: Typically 5-15 seconds for multi-step tasks

### Future Roadmap

```mermaid
timeline
    title JARVIS Development Roadmap
    
    Completed : General automation
             : Auto-detect mode
             : Two-Model Pipeline
             : Debug logging
    
    In Progress : Icon detection accuracy
                : FastSAM tuning
    
    Planned : Voice activation ("Hey JARVIS")
           : Camera/OCR input
           : Multi-monitor support
           : Task scheduling
           : Conversation memory
           : Query Optimization
```

### Debug & Troubleshooting

Each execution creates a debug folder with full traceability:

```
debug_logs/2024-12-01_16-39-33/
├── session_info.json       # Command, timestamps
├── planner_output.json     # Execution plan
├── screenshot.png          # Original capture
├── annotated.png           # SoM-marked image
├── box_map.json            # Element coordinates
├── vision_mapper_output.json # Target mappings
└── execution_log.txt       # Step-by-step log
```

This enables rapid diagnosis of:
- Planner misinterpretation
- FastSAM detection failures
- Vision Mapper misidentification
- Coordinate calculation errors
