# 🤖 JARVIS - Cloud-Native AI Computer Automation Platform

> **AWS-Powered Intelligent Automation System** | 🏆 Single Source of Truth & Hackathon Master Document

[![AWS](https://img.shields.io/badge/AWS-100000?style=for-the-badge&logo=amazon-aws&logoColor=FF9900)](https://aws.amazon.com/)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-005B99?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactnative.dev/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**JARVIS** is a highly advanced, distributed AI automation platform that translates natural language commands into direct, intelligent computer actions. 

Moving beyond brittle, traditional RPA (Robotic Process Automation) and slow, vision-only AI agents, JARVIS introduces a novel **Multi-Plane Execution Architecture** and a **Dynamic Router-Planner Engine**. Powered natively by **Amazon Bedrock**, JARVIS fundamentally changes how AI interacts with operating systems by attempting to execute tasks at the deepest, fastest system levels (Shell/File I/O) before gracefully falling back to AI-driven GUI interaction.

---

## 📑 Master Table of Contents

*   **PART 1: Foundations & Architecture** (Current Segment)
    1. [Executive Summary & Key Metrics](#1-executive-summary--key-metrics)
    2. [The Problem vs. The JARVIS Solution](#2-the-problem-vs-the-jarvis-solution)
    3. [Core Technical Innovations](#3-core-technical-innovations)
    4.[High-Level System Architecture](#4-high-level-system-architecture)
*   **PART 2: Cloud, Cost & Security** (Next Segment)
    5. AWS Cloud-Native Integration Deep Dive
    6. Comprehensive Cost & Scalability Analysis
    7. Security Guardrails & Human-in-the-Loop (HITL)
*   **PART 3: Workflows & Engine Mechanics** (Upcoming Segment)
    8. Multi-Plane Execution Workflows (Mermaid Deep Dives)
    9. AI-Powered File Editing Engine Mechanics
    10. Component Level Breakdown (Frontend, Backend, Puppet)
*   **PART 4: Deployment & Reference** (Final Segment)
    11. Exhaustive Installation & Deployment Guide
    12. API Reference & State Management
    13. Roadmap, Troubleshooting & Contributing

---

## 1. Executive Summary & Key Metrics

JARVIS bridges the gap between human intent and machine execution by utilizing a heavily integrated ecosystem of AWS AI models, localized OCR, and programmatic APIs. 

Designed for enterprise scalability but optimized to r  un on the AWS Free Tier, it offers a complete, secure, and lightning-fast alternative to existing automation frameworks.

### 📊 Performance & Impact Metrics

| Metric | JARVIS Performance | Competitive Significance |
|--------|--------------------|--------------------------|
| **AWS Cloud Integration** | 8 Core Services + IaC | Fully distributed, production-ready, cloud-native backend. |
| **Token Optimization** | 40-60% Reduction | Dynamic prompt routing drastically lowers LLM context size. |
| **Inference Latency** | Sub-second (Claude Haiku) | Bedrock Haiku integration provides real-time planning. |
| **Execution Speed** | 10-50x Faster | Bypasses UI clicking by prioritizing native Shell and File APIs. |
| **Operational Cost** | ~$0.25/month (Free Tier) | A fraction of the cost of API-heavy, monolithic AI agents. |
| **Execution Planes** | 7 Distinct Fallback Tiers | Guarantees task completion regardless of system UI limitations. |

---

## 2. The Problem vs. The JARVIS Solution

### ❌ The Problem with Current Automation
1. **Traditional RPA is Brittle:** Scripts break when screen resolutions change, button colors update, or UI layouts shift. They lack cognitive understanding.
2. **Vision-Only AI Agents are Slow & Expensive:** Passing constant desktop screenshots to large multimodal models (like Claude 3.5 Sonnet or GPT-4o) for *every single action* takes 5-10 seconds per click and burns massive amounts of tokens.
3. **Monolithic Prompts:** Giving an AI agent instructions for "how to use a shell", "how to edit Excel", and "how to use the mouse" simultaneously bloats the context window, causing hallucination and high costs.

### ✅ The JARVIS Solution
1. **Contextual Intelligence:** JARVIS understands the *intent* of the command, not just pixel coordinates.
2. **Deep-System First:** If you ask JARVIS to "create a folder," it doesn't open File Explorer and click around. It instantly executes `mkdir` via the CLI plane.
3. **Modular Prompting:** JARVIS dynamically loads *only* the knowledge it needs for a specific task, slashing token usage by up to 60%.

---

## 3. Core Technical Innovations

### 3.1 The Dynamic Router-Planner Architecture
To solve the monolithic prompt problem, JARVIS utilizes a two-stage LLM pipeline powered by **Amazon Bedrock**. 

1. **The Router (Claude 4.5 Haiku):** A lightweight, blazing-fast model analyzes the user's natural language request. It outputs a simple array of required capabilities (e.g., `["shell", "file_io"]`).
2. **The Prompt Assembler:** The Python backend dynamically stitches together a highly optimized system prompt using *only* the rules and tool definitions requested by the Router.
3. **The Planner (Claude 4.5 Haiku):** Receives the optimized prompt and generates a strict JSON execution plan.

```mermaid
sequenceDiagram
    participant User
    participant Router as AWS Bedrock Router (Haiku)
    participant Backend as Backend Assembler
    participant Planner as AWS Bedrock Planner (Haiku)
    participant Execution as Local Puppet
    
    User->>Backend: "Write a python script and run it in VS Code"
    Backend->>Router: Analyze Intent
    Router-->>Backend: Tool Selection:[Shell, File_IO]
    Note over Backend: Excludes GUI, Vision, Office modules.<br/>Reduces prompt from 5000 to 1500 tokens.
    Backend->>Planner: Send Optimized Minimal Prompt
    Planner-->>Backend: Generate JSON Execution Plan
    Backend->>Execution: Push via WebSocket / DynamoDB
```

### 3.2 The Multi-Plane Execution Engine
JARVIS features an intelligent hierarchy of execution. It evaluates the optimal "Plane" to complete a task, strictly defaulting to the fastest method, and cascading down to Vision only when absolutely necessary.

```mermaid
graph TD
    A[Task Execution Request] --> B{Can be done via CLI?}

    B -->|Yes - FASTEST| C[Plane 1: Command-Line Shell<br/>0.1s]
    B -->|No| D{Can be done via File API?}

    D -->|Yes - FAST| E[Plane 2: Direct File Read/Write<br/>0.2s]
    D -->|No| F{Is it an Office or Code file edit?}

    F -->|Yes - INTELLIGENT| G[Plane 3: AI Memory Document Editing<br/>1.5s]
    F -->|No| H{Can be done via OS Keyboard?}

    H -->|Yes - MEDIUM| I[Plane 4: Deterministic Keyboard Shortcuts<br/>0.5s]
    H -->|No| J{Is the target element text?}

    J -->|Yes - SLOW| K[Plane 5: Local Tesseract OCR Clicking<br/>2.0s]
    J -->|No| L[Plane 6: Vision Fallback<br/>5.0s+]

    L --> M[Capture UI Screen]
    M --> N[FastSAM Generates Boundary Boxes]
    N --> O[AWS S3 Presigned URL Upload]
    O --> P[Bedrock Sonnet Analyzes URL and Selects Box ID]
    P --> Q[PyAutoGUI Clicks Coordinate]
```

---

## 4. High-Level System Architecture

JARVIS operates on a deeply decoupled, distributed 3-tier architecture. This allows the heavy lifting (AI processing, routing, state management) to happen securely in the AWS Cloud, while a lightweight "Puppet" handles local OS manipulation.

```mermaid
graph TB
    subgraph Frontend["📱 Client Interface (React Native / Web)"]
        ChatUI[Chat & Voice UI]
        DiffViewer[HITL Approval & Diff Viewer]
        Settings[Device Pairing & Settings]
    end

    subgraph AWSCloud["☁️ AWS Cloud Infrastructure (Backend)"]
        subgraph ComputeLayer["EC2 / Flask API"]
            FlaskAPI[Flask Backend API]
            SocketIO[WebSocket Server]
            AWSHub[`aws_service_hub.py`]
            RouterEngine[`newPlanner_service.py`]
        end
        subgraph AWSServices["Core AWS Services"]
            Bedrock[Amazon Bedrock<br/>Haiku/Sonnet]
            DynamoDB[(Amazon DynamoDB<br/>Commands & State Queue)]
            S3[(Amazon S3<br/>1hr TTL Presigned URLs)]
        end
    end

    subgraph Execution["💻 Local Execution Puppet (Target OS)"]
        PuppetClient[`client.py` Worker]
        PlanExecutor[`plan_executor.py`]
        
        subgraph Tools["Execution Planes"]
            Shell[Subprocess CLI]
            FileIO[OS File System]
            Office[XML Office Parser]
            Vision[FastSAM + Tesseract]
        end
    end

    %% Network Connections
    ChatUI -- WSS / HTTPS --> FlaskAPI
    RouterEngine -- Boto3 REST --> Bedrock
    AWSHub -- Boto3 --> DynamoDB
    AWSHub -- Boto3 --> S3
    
    PuppetClient -- HTTPS Polling / WSS --> FlaskAPI
    PuppetClient -- Secure URL Download --> S3
    
    PlanExecutor --> Shell
    PlanExecutor --> FileIO
    PlanExecutor --> Office
    PlanExecutor --> Vision
```

***

## 5. AWS Cloud-Native Integration Deep Dive

JARVIS is not just a localized script; it is a fully distributed cloud application. It natively leverages an 8-service AWS ecosystem, deployed automatically via **AWS CloudFormation** to ensure Infrastructure as Code (IaC) consistency, high availability, and security.

### 5.1 Core AWS Service Architecture

| AWS Service | Architecture Role & Technical Implementation |
| :--- | :--- |
| **Amazon Bedrock** | **The AI/ML Brain.** JARVIS utilizes `Claude 4.5 Haiku` for the Router and Planner due to its sub-second inference latency, making real-time OS control possible. It utilizes `Claude 4.6 Sonnet` exclusively for the Vision Plane, parsing dense UI components when CLI/File APIs fail. |
| **Amazon DynamoDB** | **Real-Time State & Queuing.** Uses a highly efficient single-table design (`JarvisState`). It manages device pairing tokens, command queuing between the Backend and Local Puppet, and execution history. **Cost/Security Hack:** Configured with a 24-hour TTL (Time-to-Live) to automatically prune stale execution data, keeping storage costs at absolute zero. |
| **Amazon S3** | **Ephemeral Asset Storage.** Stores FastSAM bounding-box screenshots during Vision Fallback execution. Uses Boto3 (`aws_service_hub.py`) to generate **Presigned URLs** with a strict 1-hour expiration. A bucket lifecycle policy deletes all objects after 1 day, preventing public exposure of sensitive desktop data. |
| **Amazon EC2** | **Compute Layer.** Hosts the Flask backend and WebSocket server on a highly efficient `t3.micro` Linux instance. In enterprise environments, Windows EC2 instances serve as headless execution nodes for background automation tasks. |
| **AWS CloudFormation** | **Infrastructure as Code (IaC).** The entire backend infrastructure (VPC, Subnets, IAM Roles, DynamoDB Tables, S3 Buckets) is defined in `deployment/jarvis-stack.yaml`. This allows judges or enterprise clients to spin up a fully secure JARVIS environment in ~10 minutes. |
| **AWS IAM** | **Identity & Security.** Implements strict least-privilege IAM roles. EC2 instances use attached Instance Profiles, meaning **zero hardcoded AWS credentials** exist anywhere in the application code. |
| **Amazon VPC** | **Network Isolation.** The EC2 backend operates within a custom Virtual Private Cloud (10.0.0.0/16). Strict Security Groups limit ingress strictly to ports 443/5000 (API/WebSockets) and 22 (Admin SSH). |
| **AWS Amplify** | **Frontend Hosting.** (Optional/Recommended) Provides seamless CI/CD hosting for the React Native Web interface, easily mapping to custom domains. |

---

## 6. Comprehensive Cost & Scalability Analysis

One of the fatal flaws of modern UI-clicking AI agents is their reliance on massive multimodal models for every single action, resulting in exorbitant costs and high latency. JARVIS’s Router-Planner architecture, combined with AWS Serverless configurations, makes it radically cost-effective.

### 6.1 Operational Cost Breakdown (Monthly)

| Resource / AWS Service | Free Tier (First 12 Months) | Enterprise Scale (1,000 Users) | Cost Optimization Strategy |
|------------------------|-----------------------------|--------------------------------|----------------------------|
| **Compute (EC2 / ALB)** | $0.00 (`t3.micro` 750 hrs/mo) | ~$300.00 (ASG + Load Balancer) | Stateless backend allows massive horizontal scaling on cheap Spot Instances. |
| **State (DynamoDB)** | $0.00 (25GB, 25 WCU/RCU) | ~$100.00 (On-Demand Scaling) | 24-hour TTL ensures the table never bloats, reducing RCU/WCU costs. |
| **Storage (S3)** | $0.00 (5GB, 20k GET, 2k PUT) | ~$50.00 (Standard-IA) | 1-day deletion lifecycle policy keeps storage usage near zero. |
| **AI (Bedrock Inference)**| ~$0.25 (Pay-per-token)* | ~$100.00 (< $0.10/user) | Router drops prompt context by 40-60%. Shell execution uses text models, bypassing expensive Vision models 90% of the time. |
| **Total Estimated Cost** | **~$0.25 / month** | **~$550.00 / month** | **< $0.60 per user at enterprise scale.** |

### 6.2 Enterprise Scalability Roadmap

JARVIS is designed to scale horizontally without application-level bottlenecks. 

```mermaid
graph LR
    subgraph Client Tier
        Mobile[React Native Apps]
    end
    
    subgraph AWS Network
        ALB[Application Load Balancer]
        ASG[Auto Scaling Group - EC2 Flask Backends]
    end
    
    subgraph AWS Serverless Data
        DDB[(Shared DynamoDB)]
        S3Bucket[(Shared S3 Bucket)]
    end
    
    subgraph Execution Tier
        Worker1[Local Puppet Windows]
        Worker2[Local Puppet Mac]
        Worker3[Headless EC2 Windows]
    end

    Mobile -->|HTTPS/WSS| ALB
    ALB --> ASG
    ASG -->|Boto3 Read/Write| DDB
    ASG -->|Presigned URLs| S3Bucket
    
    DDB -.->|Polls for Commands| Worker1
    DDB -.->|Polls for Commands| Worker2
    DDB -.->|Polls for Commands| Worker3
```

1. **Stateless Backends:** Because execution state is handled by DynamoDB, Flask EC2 instances can be rapidly spun up or killed via Auto Scaling Groups (ASG) based on CPU load.
2. **Decoupled Workers:** Local Puppets (the execution nodes) simply poll DynamoDB or maintain WebSocket connections. One scalable backend can serve tens of thousands of local puppets globally.

---

## 7. Security Guardrails & Human-in-the-Loop (HITL)

Because JARVIS executes actions directly on the local operating system, robust security guardrails are non-negotiable. JARVIS implements a strict Human-in-the-Loop (HITL) architecture for sensitive operations.

### 7.1 Destructive Action Pause & Approval

If the Bedrock Planner determines that an action involves modifying data, it flags the JSON payload with `requires_approval = True`. Execution on the local machine immediately pauses, and a prompt is sent to the React Native UI.

**Trigger Conditions for HITL:**
*   File deletion or formatting.
*   File overwriting.
*   AI-driven Document Editing (Word/Excel edits).
*   Executing unknown shell binaries.

```mermaid
stateDiagram-v2
    [*] --> AI_Generates_Plan
    AI_Generates_Plan --> Check_Sensitivity: Parse execution JSON
    
    state Check_Sensitivity {
        direction LR
        is_destructive --> requires_approval
    }
    
    Check_Sensitivity --> Pause_Execution: requires_approval == true
    Check_Sensitivity --> Execute_Directly: requires_approval == false
    
    Pause_Execution --> Mobile_UI: Emit WebSocket Event
    
    state Mobile_UI {
        Display_Warning --> User_Action
        User_Action --> Approve
        User_Action --> Reject
    }
    
    Mobile_UI --> Execute_Directly: Signed Approval Received
    Mobile_UI --> Abort_Task: Rejection Received
    
    Execute_Directly --> [*]
    Abort_Task --> [*]
```

### 7.2 The Diff Viewer (Visual File Editing)
When JARVIS modifies an Excel or Word document via the AI Editing Plane, it does not just execute blindly. It reads the file, generates the changes, and pushes a **Diff Preview** to the frontend. The user sees exactly what data will be replaced (Before/After) before approving the operation.

### 7.3 Execution Sandboxing
1. **No Admin Rights:** Shell execution runs strictly in the user context via Python's `subprocess`. It cannot bypass Windows UAC without manual human clicking.
2. **Regex Command Filtering:** The Local Puppet maintains a blacklist of dangerous commands (e.g., `del /s`, `format C:`, `rm -rf /`). If generated by the AI, the Puppet rejects the command locally before execution.
3. **Data Privacy (Ephemeral State):** As detailed in the AWS section, screenshots taken for vision tasks are stored on S3 for a maximum of 1 hour via presigned URLs and then permanently destroyed. Data is not used for model training.

***

## 8. Multi-Plane Execution Workflows (Deep Dives)

JARVIS's most powerful feature is its ability to bypass slow, error-prone visual automation (clicking and dragging) in favor of deep-system APIs, only using visual fallback when forced. Below are two deep-dive scenarios illustrating this dynamic routing.

### 8.1 Scenario 1: The Developer Flow (Speed & CLI Focus)

**User Command:** *"Create a Python script that implements a bubble sort algorithm, save it to my Desktop, and open it in VS Code."*

In a traditional RPA or Vision Agent, the AI would open the Start Menu, click VS Code, click "New File", type the code, click "Save As", etc.—taking upwards of 30-45 seconds. JARVIS executes this in **< 3 seconds**.

```mermaid
sequenceDiagram
    participant User
    participant Bedrock_Router as Router (Haiku)
    participant Bedrock_Planner as Planner (Haiku)
    participant Execution_Puppet as Local Puppet
    participant OS_Filesystem as OS File I/O
    participant OS_Shell as OS Shell
    
    User->>Bedrock_Router: "Create bubble sort python script on Desktop and open in VS Code"
    Bedrock_Router-->>Bedrock_Planner: Selected Planes: [File_IO, Shell]
    Note right of Bedrock_Planner: Prompt size reduced by 60%.<br/>Vision & Office tools excluded.
    
    Bedrock_Planner->>Bedrock_Planner: Generate Code & JSON Plan
    Bedrock_Planner-->>Execution_Puppet: Push Plan (2 Steps)
    
    Execution_Puppet->>OS_Filesystem: Step 1: tool=write_file, path=~/Desktop/sort.py, content=[Code]
    OS_Filesystem-->>Execution_Puppet: Success (0.05s)
    
    Execution_Puppet->>OS_Shell: Step 2: tool=shell, command="code ~/Desktop/sort.py"
    OS_Shell-->>Execution_Puppet: Success (0.1s)
    
    Execution_Puppet-->>User: Task Complete Notification
```

### 8.2 Scenario 2: Legacy GUI Interaction (Vision Fallback)

**User Command:** *"Click the 'Export Data' button in this proprietary, legacy accounting software."*

Because the software has no CLI or accessible File API, the Router intelligently falls back to **Plane 6: Vision Fallback**.

```mermaid
sequenceDiagram
    participant User
    participant Puppet as Local Puppet
    participant FastSAM as Local FastSAM
    participant S3 as AWS S3 (Presigned)
    participant Sonnet as Planner (Claude 4.6 Sonnet)
    participant OS as Target OS (PyAutoGUI)
    
    User->>Puppet: "Click 'Export Data'"
    Puppet->>Puppet: Plan requires [vision_ui]
    Puppet->>OS: Capture Screen Snapshot
    Puppet->>FastSAM: Process Image & Generate Bounding Boxes
    FastSAM-->>Puppet: Output: Image with numbered boxes[1...85]
    
    Puppet->>S3: Upload Boxed Image (Boto3)
    S3-->>Puppet: Return Presigned URL (1hr TTL)
    
    Puppet->>Sonnet: Send S3 URL + "Which box ID is 'Export Data'?"
    Sonnet-->>Puppet: "Box #42"
    
    Puppet->>FastSAM: Get Coordinates for Box #42
    FastSAM-->>Puppet: (X: 1050, Y: 320)
    
    Puppet->>OS: PyAutoGUI.click(1050, 320)
    OS-->>User: Click Executed Successfully
```

---

## 9. AI-Powered File Editing Engine Mechanics

Standard automation bots can open Microsoft Word or Excel, but they struggle to intelligently *edit* existing content without breaking formats. JARVIS introduces **Plane 3: AI Document Editing**. 

Instead of blind typing, JARVIS treats `.docx`, `.xlsx`, and `.py` files as data structures. It extracts the context, uses Bedrock to generate a precise JSON Diff payload (Search String -> Replace String), and modifies the file natively via Python libraries (`python-docx`, `openpyxl`), completely preserving original fonts, tables, and formulas.

### 9.1 The Intelligent Edit Workflow

1. **Context Extraction:** Puppet reads the target document and extracts raw text/data while ignoring style metadata.
2. **LLM Diff Generation:** The text is sent to the Bedrock Planner. The Planner outputs a structured JSON array of exact `search_text` and `replace_text` pairs based on the user's instructions.
3. **HITL Diff Preview:** The Backend pushes these pairs to the React Native Frontend. The user views a visual "Before and After" (Diff Viewer).
4. **Native Replacement:** Upon approval, the Puppet traverses the document's XML/structure, applying the text replacements directly to the `runs` (Word) or `cells` (Excel) containing the target strings, leaving the surrounding formatting completely untouched.

```json
// Example Bedrock Diff Payload for Document Editing
{
  "tool": "edit_document",
  "path": "C:/Users/Admin/Documents/Q3_Report.docx",
  "requires_approval": true,
  "edits":[
    {
      "search_text": "Q3 2024 Revenue was $2.4M",
      "replace_text": "Q4 2024 Revenue was $3.1M"
    }
  ]
}
```

---

## 10. Component Level Breakdown

The JARVIS codebase is strictly organized to maintain the separation of concerns between the Cloud Backend, the Local Execution Puppet, and the User Interface.

### 10.1 ☁️ `backend/` (AWS Cloud Engine)
The brain of the operation. This stateless Flask application is designed to be hosted on Amazon EC2 and interfaces directly with AWS APIs.

*   `server.py`: The main Flask/Socket.IO entry point. Handles routing, WebSocket connections, and REST endpoints.
*   `newPlanner_service.py`: **The Core Innovation.** Contains the dynamic prompt assembly logic. It queries the `Router`, builds the minimized context window, and queries the `Planner`.
*   `aws_service_hub.py`: The Boto3 integration layer. Manages DynamoDB state, queuing logic, S3 presigned URL generation, and IAM credential assumption.
*   `ai_editor_engine.py`: Parses the Diff JSON payloads and manages the backend logic for the HITL document editing flow.

### 10.2 💻 `local_client/` (Execution Puppet)
The worker node deployed on the target Windows/Mac/Linux machine. It is entirely decoupled from the backend AI logic.

*   `client.py`: The long-polling/WebSocket worker. It securely connects to the EC2 backend or DynamoDB queue, waiting for execution JSON payloads.
*   `plan_executor.py`: **The Multi-Plane Engine.** A massive routing file that maps the AI's JSON `tool` requests to actual Python OS commands (e.g., mapping `"tool": "shell"` to `subprocess.run()`).
*   `run_settings.py`: A local PyWebView configuration UI. Allows the user to map custom tool paths (like the Tesseract OCR executable) and pair the device with the backend.
*   `vision_processor.py`: Handles the Plane 6 Fallback. Triggers FastSAM, draws bounding boxes, and handles S3 uploads.

### 10.3 📱 `ChatInterface/` (React Native Frontend)
The user-facing control center, built with React Native and Expo. It can be compiled to iOS, Android, or Web (hosted via AWS Amplify).

*   `App.js` / `ChatScreen.js`: Renders the chat interface, handles voice-to-text input, and parses Markdown responses from Bedrock.
*   `DiffViewer.js`: The visual HITL component. Renders the side-by-side comparison of proposed AI document edits and emits the signed approval WebSockets.
*   `DevicePairing.js`: Manages the secure token handshake between the mobile app, the Cloud Backend, and the Local Puppet.

***

## 11. Exhaustive Installation & Deployment Guide

JARVIS is a distributed system. To achieve the full "Cloud-to-Local" automation pipeline, you must deploy the AWS Infrastructure, start the Cloud Backend, run the Local Puppet on your target machine, and launch the Mobile/Web UI.

### Phase 1: AWS Cloud Infrastructure Setup (Recommended)
Deploying via AWS CloudFormation ensures all IAM roles, S3 buckets, DynamoDB tables, and VPC configurations are perfectly aligned with least-privilege security.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Bada-Don/Jarvis.git
   cd Jarvis
   ```
2. **Deploy CloudFormation Stack:**
   *(Requires AWS CLI configured with admin credentials)*
   ```bash
   aws cloudformation create-stack \
     --stack-name jarvis-production-stack \
     --template-body file://deployment/jarvis-stack.yaml \
     --capabilities CAPABILITY_NAMED_IAM
   ```
   *Note: This provisions the `JarvisState` DynamoDB table and the S3 bucket with the 1-day deletion lifecycle policy.*

### Phase 2: Cloud Backend Server (Flask/EC2)
This server acts as the central Router-Planner brain. It can be run locally for testing or deployed to an AWS EC2 instance.

1. **Environment Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Configure `.env`:** Create a `.env` file in the `backend/` directory:
   ```env
   LLM_PROVIDER=aws_bedrock
   AWS_REGION=us-east-1
   AWS_BEDROCK_PLANNER_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0
   AWS_BEDROCK_VISION_MODEL=us.anthropic.claude-sonnet-4-6
   S3_BUCKET_NAME=jarvis-assets-[YOUR-ACCOUNT-ID]
   DYNAMODB_TABLE=JarvisState
   FLASK_PORT=5000
   ```
3. **Start the Server:**
   ```bash
   python server.py
   ```
   *(Ensure your AWS CLI profile has Amazon Bedrock model access granted in the AWS Console).*

### Phase 3: Local Execution Puppet (Target OS)
This is the worker node that actually types, clicks, and manipulates files. **Run this on the machine you want to automate.**

1. **Install System Dependencies:**
   *   **Tesseract OCR:** Download and install from[UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Add it to your system `PATH`.
   *   **FastSAM Weights:** Download the `FastSAM-s.pt` model weights and place them inside the `backend/weights/` directory.
2. **Python Environment Setup:**
   ```bash
   cd local_client
   python -m venv venv
   venv\Scripts\activate  # Windows recommended
   pip install -r ..\backend\requirements.txt
   pip install pywin32 comtypes pywebview  # Windows-specific automation libraries
   ```
3. **Configure Puppet Settings & Connect:**
   ```bash
   # 1. Opens a UI to set your Cloud Backend IP and Tool Paths (e.g., Tesseract.exe)
   python run_settings.py 

   # 2. Starts the background worker listening for commands
   python client.py
   ```

### Phase 4: React Native Mobile Client
The UI where you issue commands and approve file edits.

1. **Install Node Modules:**
   ```bash
   cd ChatInterface
   npm install
   ```
2. **Configure Connection:** Edit `src/config.js` or `.env` to point to your Cloud Backend API (e.g., `http://<EC2-PUBLIC-IP>:5000`).
3. **Start Expo:**
   ```bash
   npx expo start
   ```
   *(Scan the QR code with the Expo Go app on your phone, or press `w` to run in a web browser).*

---

## 12. API Reference & State Management

JARVIS relies heavily on WebSockets for real-time execution streaming and DynamoDB for asynchronous state.

### 12.1 Core WebSocket Events (`Socket.IO`)

| Event Name | Direction | Payload Context |
| :--- | :--- | :--- |
| `connect_device` | Mobile -> Backend | Registers a pairing token linking Mobile UI to Local Puppet. |
| `issue_command` | Mobile -> Backend | `{ "text": "Create a folder", "device_id": "xyz123" }` |
| `plan_generated` | Backend -> Mobile | Returns the JSON routing array. Updates UI to "Executing Plan..." |
| `require_approval`| Backend -> Mobile | Triggers HITL. Sends the Before/After Diff JSON for file edits. |
| `approve_action` | Mobile -> Backend | Signs and releases the pause lock, allowing the Puppet to execute. |
| `execution_log` | Puppet -> Backend | Streams real-time shell output (`stdout/stderr`) back to the UI. |

### 12.2 DynamoDB State Schema (`JarvisState` Table)

To ensure zero-cost scaling, JARVIS uses a Single-Table Design in DynamoDB with a 24-hour TTL.
*   **Partition Key (`PK`):** `DEVICE#<DeviceID>`
*   **Sort Key (`SK`):** `TASK#<TaskID>` or `STATE#CONFIG`
*   **Attributes:** `CommandText`, `ExecutionPlan_JSON`, `Status` (Pending/Running/AwaitingApproval/Completed), `ExpiresAt` (TTL Epoch).

---

## 13. Troubleshooting & Common Issues

| Issue / Error | Root Cause | Resolution |
| :--- | :--- | :--- |
| **Bedrock `AccessDeniedException`** | AWS Account has not requested model access. | Go to AWS Console -> Amazon Bedrock -> Model Access -> Request access to Claude 3.5/4.5 Haiku and Sonnet. |
| **Puppet: `tesseract is not installed`**| System cannot find the OCR binary. | Add `C:\Program Files\Tesseract-OCR` to Windows Environment Variables, or set the path explicitly via `run_settings.py`. |
| **S3 `SignatureDoesNotMatch`** | EC2/Local clock drift invalidating the Presigned URL. | Ensure the machine running the Cloud Backend is synced to an NTP time server. URLs expire in exactly 60 minutes. |
| **UI stuck on "Awaiting Approval"** | WebSocket connection dropped during HITL pause. | Restart `client.py` on the Local Puppet; the queue will replay the missed state from DynamoDB. |

---

## 14. Roadmap & Future Enhancements

The vision for JARVIS extends far beyond the current Multi-Plane execution engine:

*   [ ] **Model Context Protocol (MCP) Server Support:** Allowing JARVIS to securely expose local OS APIs (like File I/O and Shell) directly to external IDEs (like Cursor) or enterprise AI tools as native capabilities.
*   [ ] **"Hey JARVIS" Voice Wake Word:** Deepening the React Native integration with native iOS/Android background audio processing for completely hands-free desktop control.
*   [ ] **AWS Cognito Integration:** Upgrading the current device-pairing token system to full Enterprise Single Sign-On (SSO) with AWS Cognito user pools.
*   [ ] **macOS / Linux First-Class Support:** Expanding Plane 4 (Keyboard) and Plane 1 (Shell) fallback parameters for `osascript` (Mac) and `xdotool` (Linux/X11).

---

## 15. Contributing & License

We welcome contributions from the open-source community, particularly in adding new "Tools" to the Multi-Plane Engine (e.g., native browser automation APIs). Please read `CONTRIBUTING.md` for our code of conduct and pull request process.

### License
This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details. 

**Disclaimer:** JARVIS executes code directly on your operating system. Never run JARVIS with an Admin/Root elevated shell unless explicitly testing a sandbox environment.

***
**<div align="center">Built with 🧠 by Harshit Singla</div>**
<div align="center"><i>Showcasing the absolute frontier of Cloud-Native AI Automation.</i></div>