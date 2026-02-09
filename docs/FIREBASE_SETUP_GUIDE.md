# Firebase Setup Guide for JARVIS Desktop Packaging

This guide walks you through setting up Firebase for JARVIS desktop-to-mobile communication.

## Prerequisites

- Google account
- Access to [Firebase Console](https://console.firebase.google.com/)

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or "Create a project"
3. Enter project name: `jarvis-desktop-app` (or your preferred name)
4. (Optional) Enable Google Analytics if desired
5. Click "Create project"
6. Wait for project creation to complete

## Step 2: Enable Realtime Database

1. In your Firebase project, navigate to **Build** → **Realtime Database**
2. Click "Create Database"
3. Select a location (choose closest to your users):
   - `us-central1` (United States)
   - `europe-west1` (Belgium)
   - `asia-southeast1` (Singapore)
4. Start in **Test mode** for now (we'll configure security rules later)
5. Click "Enable"
6. Note your database URL (format: `https://PROJECT-ID-default-rtdb.firebaseio.com/`)

## Step 3: Enable Authentication (Anonymous)

1. Navigate to **Build** → **Authentication**
2. Click "Get started"
3. Go to the **Sign-in method** tab
4. Click on "Anonymous"
5. Toggle "Enable" to ON
6. Click "Save"

## Step 4: Download Service Account Credentials

### For Desktop Application (Admin SDK)

1. Navigate to **Project Settings** (gear icon) → **Service accounts**
2. Click "Generate new private key"
3. Click "Generate key" in the confirmation dialog
4. Save the downloaded JSON file as `firebase-admin-credentials.json`
5. **IMPORTANT**: Keep this file secure and never commit it to version control

### For Mobile Application (Expo React Native)

**Note**: This app uses Expo, which simplifies Firebase setup. You'll configure Firebase using environment variables and the `@react-native-firebase` packages (to be installed in Task 13).

**For now, just note your Firebase configuration:**

1. Navigate to **Project Settings** (gear icon) → **General**
2. Scroll down to "Your apps" section
3. Note your **Project ID** (you'll need this for `.env` configuration)

**When you're ready to build standalone apps (later):**

#### For Android
1. Click the Android icon in "Your apps"
2. Register app with package name: `com.anonymous.ChatInterface` (from `app.json`)
3. Download `google-services.json`
4. Place in `ChatInterface/` root directory (Expo will handle it)

#### For iOS
1. Click the iOS icon in "Your apps"
2. Register app with bundle ID: `com.anonymous.ChatInterface`
3. Download `GoogleService-Info.plist`
4. Place in `ChatInterface/` root directory (Expo will handle it)

**For Expo development (recommended for now):**
- You don't need `google-services.json` or `GoogleService-Info.plist` yet
- Firebase will work through the JavaScript SDK with your database URL
- These files are only needed when building standalone/production apps

## Step 5: Configure Security Rules

1. Navigate to **Build** → **Realtime Database**
2. Click on the **Rules** tab
3. Replace the default rules with the security rules from `firebase-security-rules.json`
4. Click "Publish"

### Security Rules Explanation

The security rules ensure:
- Only authenticated users can access data
- Devices can only read/write their own data
- Pairing tokens have time-based expiration
- Rate limiting on pairing attempts
- Devices can only access paired device data

## Step 6: Configure Firebase in JARVIS

### Desktop Application

1. Place `firebase-admin-credentials.json` in the `data/` directory of your JARVIS installation
2. Update `backend/.env` with your Firebase configuration:
   ```
   FIREBASE_CREDENTIALS_PATH=../data/firebase-admin-credentials.json
   FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/
   ```

### Mobile Application

1. Place `google-services.json` (Android) in `ChatInterface/android/app/`
2. Place `GoogleService-Info.plist` (iOS) in `ChatInterface/ios/`
3. Update `ChatInterface/.env` with your Firebase configuration:
   ```
   FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/
   FIREBASE_PROJECT_ID=your-project-id
   ```

**Note for Expo users**: If using Expo managed workflow (development), you only need the `.env` configuration. The native config files (`google-services.json`, `GoogleService-Info.plist`) are only required when building standalone apps with `expo build` or EAS Build.

## Step 7: Verify Setup

### Test Desktop Connection

```bash
cd backend
python -c "
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('../data/firebase-admin-credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/'
})

ref = db.reference('test')
ref.set({'status': 'connected'})
print('Desktop Firebase connection successful!')
"
```

### Test Mobile Connection

For Expo development, the mobile app will connect using the JavaScript SDK. Full native Firebase integration will be implemented in Task 13.

**Quick test** (after Task 13 implementation):
```javascript
// In your React Native app
import { getDatabase, ref, set } from 'firebase/database';

const db = getDatabase();
const testRef = ref(db, 'test/mobile');
set(testRef, { status: 'connected', timestamp: Date.now() });
console.log('Mobile Firebase connection successful!');
```

## Security Best Practices

1. **Never commit credentials**: Add `firebase-admin-credentials.json` to `.gitignore`
2. **Use environment variables**: Store sensitive configuration in `.env` files
3. **Rotate keys regularly**: Generate new service account keys periodically
4. **Monitor usage**: Check Firebase console for unusual activity
5. **Enable billing alerts**: Set up budget alerts in Google Cloud Console
6. **Use production rules**: Replace test mode rules with the provided security rules

## Troubleshooting

### Connection Issues

- Verify database URL is correct
- Check that credentials file path is correct
- Ensure Firebase project has billing enabled (if using paid features)
- Check network connectivity and firewall settings

### Authentication Issues

- Verify Anonymous authentication is enabled
- Check that security rules allow anonymous access
- Ensure app is using correct Firebase configuration

### Permission Denied Errors

- Review security rules in Firebase console
- Check that device is properly authenticated
- Verify device ID matches the authenticated user ID

## Next Steps

After completing Firebase setup:
1. Implement Firebase service module (Task 2)
2. Implement device pairing system (Task 3)
3. Test end-to-end communication

## Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Realtime Database](https://firebase.google.com/docs/database)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [React Native Firebase](https://rnfirebase.io/)
