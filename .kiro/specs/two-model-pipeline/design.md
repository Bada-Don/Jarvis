# Design Document: Two-Model Pipeline

## Overview

The Two-Model Pipeline implements an intelligent automation system for FlexiSIGN number plate creation. It separates concerns between planning (what to do) and vision (where to click), using two specialized AI models:

1. **Planner Model (Backend)**: Gemini Flash Lite converts natural language commands into structured execution plans with keyboard actions and named visual targets
2. **Vision Mapper Model (Local Client)**: Gemini 2.0 Flash maps visual target names to Set-of-Mark element IDs from annotated screenshots

This architecture ensures consistent dimension calculations (no hallucination) while enabling accurate UI element identification through computer vision.

## Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────┐     ┌─────────────────────────────────┐
│   Mobile App    │     │          Backend Server             │     │         Local Client            │
│  (React Native) │     │            (Flask)                  │     │          (Python)               │
├─────────────────┤     ├─────────────────────────────────────┤     ├─────────────────────────────────┤
│                 │     │                                     │     │                                 │
│  User sends     │────▶│  /api/process                       │     │                                 │
│  command        │     │     │                               │     │                                 │
│                 │     │     ▼                               │     │                                 │
│                 │     │  ┌─────────────────┐                │     │                                 │
│                 │     │  │ Planner Model   │                │     │                                 │
│                 │     │  │ (Gemini Lite)   │                │     │                                 │
│                 │     │  └────────┬────────┘                │     │                                 │
│                 │     │           │                         │     │                                 │
│                 │     │           ▼                         │     │                                 │
│                 │     │  Execution Plan JSON                │     │                                 │
│                 │     │           │                         │     │                                 │
│                 │     │           │ WebSocket               │     │                                 │
│                 │◀────│───────────┼─────────────────────────│────▶│  Receive Plan                   │
│  Progress       │     │           │                         │     │     │                           │
│  Updates        │     │           │                         │     │     ▼                           │
│                 │     │           │                         │     │  Execute Ctrl+N (blind)         │
│                 │     │           │                         │     │     │                           │
│                 │     │           │                         │     │     ▼                           │
│                 │     │           │                         │     │  ┌─────────────────┐            │
│                 │     │           │                         │     │  │ Screenshot      │            │
│                 │     │           │                         │     │  │ (pyautogui)     │            │
│                 │     │           │                         │     │  └────────┬────────┘            │
│                 │     │           │                         │     │           │                     │
│                 │     │           │                         │     │           ▼                     │
│                 │     │           │                         │     │  ┌─────────────────┐            │
│                 │     │           │                         │     │  │ FastSAM SoM     │            │
│                 │     │           │                         │     │  │ (existing)      │            │
│                 │     │           │                         │     │  └────────┬────────┘            │
│                 │     │           │                         │     │           │                     │
│                 │     │           │                         │     │           ▼                     │
│                 │     │           │                         │     │  Annotated Image + Box Map      │
│                 │     │           │                         │     │           │                     │
│                 │     │           │                         │     │           ▼                     │
│                 │     │           │                         │     │  ┌─────────────────┐            │
│                 │     │           │                         │     │  │ Vision Mapper   │            │
│                 │     │           │                         │     │  │ (Gemini 2.0)    │            │
│                 │     │           │                         │     │  └────────┬────────┘            │
│                 │     │           │                         │     │           │                     │
│                 │     │           │                         │     │           ▼                     │
│                 │     │           │                         │     │  ID Map: {target: id}           │
│                 │     │           │                         │     │           │                     │
│                 │     │           │                         │     │           ▼                     │
│                 │     │           │                         │     │  Execute Steps (clicks/keys)    │
│                 │     │           │                         │     │                                 │
└─────────────────┘     └─────────────────────────────────────┘     └─────────────────────────────────┘
```

## Components and Interfaces

### 1. Backend Server Components

#### 1.1 Gemini Service (`backend/gemini_service.py`)

Handles communication with Gemini Flash Lite for plan generation.

```python
class GeminiPlannerService:
    def __init__(self, api_key: str)
    def generate_plan(self, user_command: str) -> dict
```

#### 1.2 Updated Server Endpoint (`backend/server.py`)

Modified `/api/process` endpoint to use the Planner Model.

```python
@app.route('/api/process', methods=['POST'])
def process_instruction():
    # 1. Get user command
    # 2. Call GeminiPlannerService.generate_plan()
    # 3. Send plan to local client via WebSocket
    # 4. Return acknowledgment to mobile app
```

### 2. Local Client Components

#### 2.1 Vision Service (`local_client/vision_service.py`)

Handles screenshot capture, SoM detection, and Vision Mapper model.

```python
class VisionService:
    def __init__(self, api_key: str, som_model_path: str)
    def capture_screenshot(self) -> np.ndarray
    def run_som_detection(self, image: np.ndarray) -> tuple[np.ndarray, dict]
    def map_targets_to_ids(self, annotated_image: np.ndarray, targets: list[str]) -> dict
```

#### 2.2 Plan Executor (`local_client/plan_executor.py`)

Executes the plan using keyboard/mouse actions.

```python
class PlanExecutor:
    def __init__(self, vision_service: VisionService, status_callback: callable)
    def execute_plan(self, plan: dict) -> bool
    def execute_keyboard_step(self, step: dict) -> None
    def execute_visual_click(self, target_name: str, id_map: dict, box_map: dict) -> None
```

#### 2.3 Updated Client (`local_client/client.py`)

New action handler for `two_model_workflow`.

```python
def execute_command(command_data):
    if action == 'two_model_workflow':
        executor = PlanExecutor(vision_service, send_status)
        executor.execute_plan(command_data['plan'])
```

### 3. Shared Components

#### 3.1 SoM Module (Reuse existing `backend/SoM.py`)

The existing SoM implementation will be extracted into reusable functions:

```python
# Keep existing configuration exactly as-is
def run_som_on_image(image: np.ndarray, model: FastSAM) -> tuple[np.ndarray, dict]:
    """
    Run SoM detection on an image.
    Returns: (annotated_image, box_map)
    Uses existing filter_boxes() and draw_annotations() with current config.
    """
```

## Data Models

### Execution Plan Schema

```json
{
  "sequence": [
    {
      "order": 1,
      "type": "keyboard",
      "value": "ctrl+n",
      "desc": "New Page"
    },
    {
      "order": 2,
      "type": "visual_click",
      "target_name": "text_tool",
      "desc": "Click Text Tool"
    },
    {
      "order": 3,
      "type": "keyboard",
      "value": "PB12W3998",
      "desc": "Type Number"
    },
    {
      "order": 4,
      "type": "keyboard",
      "value": "shift+up",
      "repeats": 10,
      "desc": "Move Up"
    }
  ]
}
```

### Box Map Schema

```json
{
  "1": [100.0, 200.0, 150.0, 250.0],
  "2": [300.0, 50.0, 400.0, 80.0]
}
```

### ID Map Schema (Vision Mapper Output)

```json
{
  "text_tool": 45,
  "select_tool": 12,
  "canvas_center": 78,
  "width_input": 88,
  "height_input": 92
}
```

### WebSocket Command Schema

```json
{
  "action": "two_model_workflow",
  "plan": { "sequence": [...] },
  "user_command": "Make iron number plate set for bike, PB12W3998"
}
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Execution Plan Structure Validity

*For any* valid user command string, the Planner Model output SHALL be valid JSON containing a "sequence" array where each element has an "order" field, a "type" field (either "keyboard" or "visual_click"), and the appropriate type-specific fields ("value" for keyboard, "target_name" for visual_click).

**Validates: Requirements 2.4, 2.5, 2.6**

### Property 2: SoM Annotation Consistency

*For any* set of N filtered bounding boxes, the draw_annotations function SHALL produce an annotated image and a box_map dictionary containing exactly N entries, where each entry maps an integer ID (1 to N) to a coordinate array [x1, y1, x2, y2].

**Validates: Requirements 3.3, 3.4**

### Property 3: Vision Mapper Output Structure

*For any* annotated image and list of target names, the Vision Mapper Model output SHALL be valid JSON where each key is a string from the input target list and each value is either an integer ID or null.

**Validates: Requirements 4.2**

### Property 4: Coordinate Lookup Correctness

*For any* valid ID map and box map where an ID exists in both, the coordinate lookup SHALL return the center point (cx, cy) where cx = (x1 + x2) / 2 and cy = (y1 + y2) / 2 from the corresponding box map entry.

**Validates: Requirements 4.4**

## Error Handling

### Backend Server Errors

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Missing Gemini API key | Log error, return 500 with message "Gemini API key not configured" |
| Planner Model API failure | Log error, return 500 with message "Failed to generate plan" |
| Invalid JSON from Planner | Log error, return 500 with message "Invalid plan format" |
| WebSocket client not connected | Log warning, return 200 with message "No local client connected" |

### Local Client Errors

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Missing Gemini API key | Log error, send status "error", skip vision mapping |
| Screenshot capture failure | Log error, send status "error", abort execution |
| FastSAM model load failure | Log error, send status "error", abort execution |
| Vision Mapper API failure | Log error, send status "error", abort execution |
| Target not found in ID map | Log warning, skip that click step, continue execution |
| ID not found in box map | Log warning, skip that click step, continue execution |

### Graceful Degradation

- If Vision Mapper fails, the system should report the error but not crash
- If a single step fails, subsequent steps should still attempt execution
- All errors should be reported to the mobile app via status updates

## Testing Strategy

### Unit Testing

Unit tests will cover:
- JSON parsing and validation for execution plans
- Coordinate calculation from bounding boxes
- Environment variable loading
- Step type detection and routing

### Property-Based Testing

Property-based tests will use the `hypothesis` library (Python) to verify:

1. **Plan Structure Property**: Generate random user commands, call Planner Model, verify output structure
2. **SoM Consistency Property**: Generate random bounding box arrays, run annotation, verify box_map integrity
3. **Vision Mapper Output Property**: Generate random target lists, verify output structure
4. **Coordinate Lookup Property**: Generate random box maps and IDs, verify center calculation

Each property-based test will:
- Run a minimum of 100 iterations
- Be tagged with the corresponding correctness property reference
- Use format: `**Feature: two-model-pipeline, Property {number}: {property_text}**`

### Integration Testing

Integration tests will verify:
- WebSocket communication between backend and local client
- End-to-end flow from mobile app command to FlexiSIGN automation
- Status update propagation to mobile app

## File Structure

```
backend/
├── .env.example              # NEW: Environment variable template
├── gemini_service.py         # NEW: Planner Model integration
├── server.py                 # MODIFIED: Add two_model_workflow
├── SoM.py                    # EXISTING: Keep current config
├── requirements.txt          # MODIFIED: Add google-generativeai

local_client/
├── .env.example              # NEW: Environment variable template
├── vision_service.py         # NEW: Screenshot + SoM + Vision Mapper
├── plan_executor.py          # NEW: Execute plans with keyboard/mouse
├── client.py                 # MODIFIED: Add two_model_workflow handler
├── requirements.txt          # MODIFIED: Add google-generativeai

ChatInterface/                # EXISTING: Minimal changes only
├── src/services/api.ts       # NO CHANGES: Already handles status updates
├── src/screens/ChatScreen.tsx # NO CHANGES: Already displays progress
```

## Mobile App Integration Notes

The existing ChatInterface already supports:
- Sending text commands via `sendMessage()` → `/api/process`
- Receiving real-time status updates via WebSocket `jarvis_status` events
- Displaying progress updates with percentage completion

**No changes required to the mobile app.** The backend will use the existing `/api/process` endpoint and emit status updates in the same format the app already expects.
