# Firebase & Device Pairing

> 40 nodes · cohesion 0.09

## Key Concepts

- **PairingManager** (17 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **FirebaseService** (16 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **._initializeDeviceId()** (11 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **getFirebaseDatabase()** (10 connections) — `Jarvis-aws-migration\ChatInterface\src\config\firebase.ts`
- **.connect()** (8 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **.submitPairingToken()** (7 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **signInAnonymouslyToFirebase()** (5 connections) — `Jarvis-aws-migration\ChatInterface\src\config\firebase.ts`
- **._getOrCreateDeviceId()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **._saveDeviceConfig()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **._registerDevice()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **.isPaired()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **.getPairedDesktopId()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **.unpair()** (4 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **firebase.ts** (3 connections) — `ChatInterface\src\config\firebase.ts`
- **isFirebaseConfigured()** (3 connections) — `Jarvis-aws-migration\ChatInterface\src\config\firebase.ts`
- **.updatePresence()** (3 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **firebase.ts** (3 connections) — `Jarvis-aws-migration\ChatInterface\src\config\firebase.ts`
- **._setupConnectionMonitoring()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **._setupDisconnectHandler()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **._scheduleReconnect()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **._updatePresence()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **.sendCommand()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- **.constructor()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **._generateUUID()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- **.getDeviceId()** (2 connections) — `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`
- *... and 15 more nodes in this community*

## Relationships

- [[Configuration & Settings Management]] (5 shared connections)

## Source Files

- `ChatInterface\src\config\firebase.ts`
- `ChatInterface\src\services\FirebaseService.ts`
- `ChatInterface\src\services\PairingManager.ts`
- `Jarvis-aws-migration\ChatInterface\src\config\firebase.ts`
- `Jarvis-aws-migration\ChatInterface\src\services\FirebaseService.ts`
- `Jarvis-aws-migration\ChatInterface\src\services\PairingManager.ts`

## Audit Trail

- EXTRACTED: 112 (79%)
- INFERRED: 29 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*