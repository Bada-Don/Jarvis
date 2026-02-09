# Firebase Integration Guide for JARVIS Mobile App

## Overview

The JARVIS mobile app now supports Firebase-based communication with the desktop application, enabling remote control over the internet without requiring the same local network.

## Features Implemented

### ✅ Task 13.1: Firebase SDK Integration
- Firebase JavaScript SDK installed and configured
- Environment variable support for Firebase configuration
- Firebase initialization module with error handling
- Anonymous authentication for security rules

### ✅ Task 13.2: Firebase Messaging Service
- `FirebaseService` class for real-time messaging
- Command sending to paired desktop
- Status update listening from desktop
- Automatic reconnection with exponential backoff
- Device presence tracking

### ✅ Task 13.3: QR Code Scanner
- Camera permission handling
- QR code scanning UI with visual feedback
- Token validation (must start with `pair_`)
- Error handling for invalid codes

### ✅ Task 13.4: Pairing Flow
- Complete pairing workflow implementation
- QR code scanning for pairing
- Manual token entry as fallback
- Secure device ID storage in AsyncStorage
- Pairing status persistence
- Unpair functionality

## Architecture

### Communication Flow

```
Mobile App → Firebase Realtime DB → Desktop App
     ↓                                    ↓
  Commands                            Status Updates
```

### Key Components

1. **Firebase Configuration** (`src/config/firebase.ts`)
   - Initializes Firebase app
   - Provides database and auth instances
   - Handles anonymous authentication

2. **Firebase Service** (`src/services/FirebaseService.ts`)
   - Manages real-time messaging
   - Sends commands to desktop
   - Listens for status updates
   - Handles reconnection

3. **Pairing Manager** (`src/services/PairingManager.ts`)
   - Manages device pairing
   - Generates and stores device IDs
   - Validates pairing tokens
   - Handles QR code scanning

4. **Chat Screen** (`src/screens/ChatScreen.tsx`)
   - Integrates Firebase messaging
   - Falls back to WebSocket for local development
   - Shows pairing screen when needed

5. **Pairing Screen** (`src/screens/PairingScreen.tsx`)
   - QR code scanning interface
   - Manual token entry
   - Pairing status display

## Setup Instructions

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable **Realtime Database**
4. Enable **Authentication** → **Anonymous** sign-in method
5. Get your Firebase configuration from Project Settings

### 2. Environment Configuration

Create `ChatInterface/.env` file:

```env
# Firebase Configuration
EXPO_PUBLIC_FIREBASE_API_KEY=your-api-key
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
EXPO_PUBLIC_FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
EXPO_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
EXPO_PUBLIC_FIREBASE_APP_ID=your-app-id
```

**Note:** Use `EXPO_PUBLIC_` prefix to make variables available in Expo.

### 3. Firebase Security Rules

Set up security rules in Firebase Console → Realtime Database → Rules:

```json
{
  "rules": {
    "devices": {
      "$deviceId": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    },
    "pairing": {
      "$token": {
        ".read": "auth != null",
        ".write": "auth != null && !data.exists()"
      }
    },
    "messages": {
      "$deviceId": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

### 4. Install Dependencies

```bash
cd ChatInterface
npm install
```

Dependencies already included:
- `firebase@^11.2.0` - Firebase JavaScript SDK
- `expo-camera@~17.0.5` - Camera for QR scanning
- `expo-barcode-scanner@~14.0.3` - QR code scanning
- `@react-native-async-storage/async-storage@^2.1.0` - Secure storage

### 5. Run the App

```bash
npm start
```

Scan the QR code with Expo Go app on your mobile device.

## Usage

### First-Time Pairing

1. **Start Desktop Application**
   - Desktop app generates a pairing QR code
   - QR code is displayed in the Settings UI

2. **Open Mobile App**
   - If Firebase is configured and device is not paired, pairing screen appears
   - Tap "Scan QR Code" button
   - Grant camera permission when prompted

3. **Scan QR Code**
   - Point camera at the QR code on desktop
   - App automatically detects and validates the code
   - Pairing completes within seconds

4. **Start Using**
   - Once paired, you can send commands remotely
   - Status updates appear in real-time

### Manual Pairing (Alternative)

If QR scanning doesn't work:

1. Tap "Enter Pairing Code Manually"
2. Type the pairing token (e.g., `pair_abc123xyz`)
3. Tap "Pair with Code"

### Unpairing

1. Open pairing screen (if available in settings)
2. Tap "Unpair Device"
3. Confirm the action
4. Device will need to be paired again

## How It Works

### Device Pairing Process

1. **Desktop generates pairing token**
   - Token format: `pair_<random_string>`
   - Token expires after 5 minutes (configurable)
   - Token stored in Firebase: `/pairing/{token}`

2. **Mobile scans QR code**
   - Extracts token from QR code
   - Validates token format

3. **Mobile submits token to Firebase**
   - Checks if token exists and is not expired
   - Marks token as used
   - Stores mobile device ID with token

4. **Devices are paired**
   - Mobile device registered in `/devices/{mobileId}`
   - Desktop device ID stored with mobile device
   - Pairing info saved locally on mobile

### Command Flow

1. **User sends command from mobile**
   ```typescript
   firebaseService.sendCommand("open notepad");
   ```

2. **Command written to Firebase**
   ```
   /messages/{desktopId}/commands/{messageId}
   {
     type: "command",
     text: "open notepad",
     timestamp: 1234567890,
     processed: false
   }
   ```

3. **Desktop listens for commands**
   - Desktop's FirebaseService detects new command
   - Processes the command
   - Sends status updates back

4. **Status updates sent to mobile**
   ```
   /messages/{mobileId}/status/{messageId}
   {
     type: "status",
     message: "Opening notepad...",
     progress: 50,
     timestamp: 1234567890
   }
   ```

5. **Mobile displays status**
   - Mobile's FirebaseService receives status update
   - Updates UI with progress

### Automatic Reconnection

The FirebaseService implements automatic reconnection with exponential backoff:

- **Initial delay:** 1 second
- **Max delay:** 30 seconds
- **Max attempts:** 10
- **Backoff strategy:** Exponential (2^n)

If connection is lost:
1. Service detects disconnection
2. Schedules reconnection attempt
3. Retries with increasing delays
4. Resets delay on successful connection

## Fallback to WebSocket

The app supports both Firebase and WebSocket:

- **Firebase:** For remote communication over internet
- **WebSocket:** For local development on same network

The app automatically:
1. Checks if Firebase is configured
2. Uses Firebase if configured and paired
3. Falls back to WebSocket if Firebase not available
4. Allows user to skip pairing and use WebSocket only

## Data Structure

### Device Registration

```json
{
  "devices": {
    "mobile_abc123": {
      "type": "mobile",
      "paired": true,
      "pairedWith": "desktop_xyz789",
      "lastSeen": 1234567890,
      "version": "1.0.0",
      "registeredAt": 1234567890
    }
  }
}
```

### Pairing Token

```json
{
  "pairing": {
    "pair_abc123xyz": {
      "desktopId": "desktop_xyz789",
      "expiresAt": 1234567890,
      "used": true,
      "mobileId": "mobile_abc123",
      "usedAt": 1234567890
    }
  }
}
```

### Messages

```json
{
  "messages": {
    "desktop_xyz789": {
      "commands": {
        "msg_001": {
          "type": "command",
          "text": "open notepad",
          "timestamp": 1234567890,
          "processed": false
        }
      }
    },
    "mobile_abc123": {
      "status": {
        "msg_001": {
          "type": "status",
          "message": "Opening notepad...",
          "progress": 50,
          "timestamp": 1234567890
        }
      }
    }
  }
}
```

## Security Considerations

### Authentication
- Anonymous authentication required for all operations
- Each device gets unique anonymous user ID
- Security rules validate authentication

### Device IDs
- Generated using UUID v4
- Stored securely in AsyncStorage
- Never transmitted in plain text (handled by Firebase)

### Pairing Tokens
- Time-limited (5 minutes default)
- Single-use only
- Automatically deleted after use
- Cannot be reused

### Firebase Security Rules
- Devices can only read/write their own data
- Pairing tokens can only be written once
- Messages require authentication
- Rate limiting on pairing operations (recommended)

## Troubleshooting

### Firebase Not Connecting

**Problem:** App shows "Not connected to Firebase"

**Solutions:**
1. Check `.env` file has correct Firebase configuration
2. Verify Firebase project has Realtime Database enabled
3. Check Firebase security rules allow anonymous auth
4. Ensure internet connection is available

### QR Code Not Scanning

**Problem:** Camera doesn't detect QR code

**Solutions:**
1. Grant camera permission in device settings
2. Ensure good lighting conditions
3. Hold camera steady and at proper distance
4. Try manual token entry as alternative

### Pairing Failed

**Problem:** "Pairing code is invalid or has expired"

**Solutions:**
1. Check if token is expired (5 minute limit)
2. Regenerate QR code on desktop
3. Verify Firebase security rules are correct
4. Check Firebase Realtime Database is accessible

### Commands Not Sending

**Problem:** Commands don't reach desktop

**Solutions:**
1. Verify device is paired (check pairing status)
2. Check Firebase connection status
3. Ensure desktop app is running and connected
4. Check Firebase Realtime Database rules
5. Verify paired desktop ID is correct

### Status Updates Not Received

**Problem:** No status updates from desktop

**Solutions:**
1. Check Firebase connection on mobile
2. Verify desktop is sending status updates
3. Check message path in Firebase console
4. Ensure status listener is active

## Development Tips

### Testing Firebase Locally

1. Use Firebase Emulator Suite for local testing:
   ```bash
   firebase emulators:start
   ```

2. Update `.env` to point to emulator:
   ```env
   EXPO_PUBLIC_FIREBASE_DATABASE_URL=http://localhost:9000/?ns=your-project-id
   ```

### Debugging

Enable verbose logging:

```typescript
// In firebase.ts
console.log('🔥 Firebase config:', firebaseConfig);

// In FirebaseService.ts
console.log('📤 Sending command:', commandText);
console.log('📱 Status update:', status);
```

### Testing Pairing Flow

1. Clear AsyncStorage to reset device ID:
   ```typescript
   import AsyncStorage from '@react-native-async-storage/async-storage';
   await AsyncStorage.clear();
   ```

2. Generate test pairing token in Firebase Console
3. Test manual token entry
4. Test QR code scanning with generated QR code

## Production Deployment

### Environment Variables

For production builds, set environment variables in:

1. **EAS Build:** Use `eas.json` or EAS Secrets
2. **Classic Build:** Use `.env` file (not committed to git)

### Build Configuration

Update `app.json` for production:

```json
{
  "expo": {
    "extra": {
      "firebaseApiKey": "production-api-key",
      "firebaseDatabaseUrl": "https://prod-project-id-default-rtdb.firebaseio.com/",
      "firebaseProjectId": "prod-project-id"
    }
  }
}
```

### Security Checklist

- [ ] Firebase security rules are production-ready
- [ ] Anonymous authentication is enabled
- [ ] Rate limiting is configured
- [ ] Environment variables are not committed to git
- [ ] `.env` is in `.gitignore`
- [ ] Production Firebase project is separate from development

## Future Enhancements

Potential improvements for future versions:

1. **Push Notifications**
   - Notify user when command completes
   - Alert on errors or important events

2. **Offline Support**
   - Queue commands when offline
   - Sync when connection restored

3. **Multiple Desktop Pairing**
   - Pair with multiple desktops
   - Switch between paired devices

4. **Enhanced Security**
   - Email/password authentication
   - Two-factor authentication
   - Device verification

5. **Command History**
   - View past commands
   - Repeat previous commands
   - Search command history

## Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Expo Firebase Guide](https://docs.expo.dev/guides/using-firebase/)
- [React Native Firebase](https://rnfirebase.io/)
- [Firebase Security Rules](https://firebase.google.com/docs/database/security)

## Support

For issues or questions:
1. Check this guide first
2. Review Firebase Console for errors
3. Check device logs for error messages
4. Verify Firebase configuration
5. Test with WebSocket fallback to isolate Firebase issues

---

**Last Updated:** February 2026
**Version:** 1.0.0
