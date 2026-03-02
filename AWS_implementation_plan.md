# JARVIS AWS-Native Migration Plan

This plan outlines the migration of JARVIS from its current Google/Firebase stack to an AWS-native architecture for the AI for Bharat Hackathon.

## Finalized Architecture

### 1. LLM Migration (Amazon Bedrock)
Using `boto3` to communicate with Amazon Bedrock.

| Current Model | Bedrock Model | Rationale | Cost (approx.) |
| :--- | :--- | :--- | :--- |
| **Planner** | **Claude 3.5 Haiku** | Fast, reliable JSON generator. | $0.25/$1.25 per 1M tokens |
| **Vision Mapper** | **Claude 3.5 Sonnet** | Pinpoint visual accuracy for SoM. | $3.00/$15.00 per 1M tokens |

### 2. Backend Hosting (EC2 Relay)
**Platform: Amazon EC2 (Free Tier t3.micro)**
*   **Networking:** The EC2 instance will have a Public IP and act as a **Relay**. Both the Local PC and the Mobile App will connect to this IP, bypassing NAT/Router constraints.
*   **Latency:** Confirmed 1-2s lag is acceptable. The persistent SocketIO connection on EC2 will maintain the relay.

### 3. Database & State (DynamoDB)
**Table: `JarvisState`**
*   **Pairing:** Stores `DeviceID` <=> `PairedMobileID` mappings.
*   **History:** Stores the last **10 tasks** (with TTL) for debugging and auditing.
*   **Status:** Real-time state syncing to replace Firebase Realtime Database.

### 4. Storage (S3)
**Bucket: `jarvis-automation-assets`**
*   **Screenshots:** Current screenshots will be uploaded to S3 with a short TTL (1 hour).
*   **Bedrock Access:** Input images for Vision Mapper will be read directly from S3 or via presigned URLs.

### 5. Authentication (Cognito)
**Service: Amazon Cognito Identity Pools**
*   **Anonymous Access:** Replaces Firebase Anonymous Auth. Allows the mobile app to securely interact with S3 and DynamoDB without hardcoded credentials.

### 6. Deployment (One-Click)
**Method: AWS CloudFormation**
*   A single YAML template will provision: VPC, Security Groups (Ports 5000/80), EC2 instance with User Data (auto-installs Python/Flask), IAM Roles, DynamoDB Table, and S3 Bucket.

---

## Part 3: Progress Bar & UI Improvements
The user indicated that the current progress bar is not correctly implemented.
*   **Improvement:** Revamp [send_status_dual](file:///d:/Documents/Codes/Jarvis/backend/server.py#185-215) in [server.py](file:///d:/Documents/Codes/Jarvis/backend/server.py) to ensure granular progress steps (e.g., 20% Plan, 40% Vision, 60% Execution, etc.) are correctly broadcasted and received.

---

## Proposed Changes

### [Component] LLM & Cloud Services
*   **[NEW]** `backend/aws_service_hub.py`: Centralized boto3 client for Bedrock, S3, and DynamoDB.
*   **[MODIFY]** [backend/planner_service.py](file:///d:/Documents/Codes/Jarvis/backend/planner_service.py): Integrate Bedrock provider.
*   **[DELETE]** [backend/firebase_service.py](file:///d:/Documents/Codes/Jarvis/backend/firebase_service.py) (To be moved to [legacy/](file:///d:/Documents/Codes/Jarvis/local_client/client.py#565-600)).

### [Component] Backend Core
*   **[MODIFY]** [backend/server.py](file:///d:/Documents/Codes/Jarvis/backend/server.py): Update SocketIO logic to work behind AWS ALB (optional) or direct EC2.
*   **[NEW]** `deployment/jarvis-stack.yaml`: The CloudFormation template.

## Verification Plan

### Automated Tests
*   `test_bedrock_integration.py`: Verify model invocation.
*   `test_dynamodb_history.py`: Verify last 10 tasks logic.

### Manual Verification
1.  **CloudFormation Run:** Trigger the stack and verify all resources are green.
2.  **NAT Test:** Verify Local PC connects to EC2 without manual port forwarding.
3.  **End-to-End:** "JARVIS, write a hello world and run it" triggered from Mobile.
