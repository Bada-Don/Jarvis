# Building JARVIS Mobile APK

This guide will help you build a standalone APK that you can install on your phone and test over mobile network (not requiring same WiFi as PC).

## Prerequisites

1. **Expo Account** (Free)
   - Sign up at: https://expo.dev/signup
   - You'll need this for EAS Build service

2. **EAS CLI** (Install globally)
   ```bash
   npm install -g eas-cli
   ```

## Step 1: Get Firebase Web API Key

You need to add the Firebase Web API key to your app configuration.

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project: `jarvis-0009`
3. Click the gear icon (⚙️) → Project Settings
4. Scroll down to "Your apps" section
5. If you don't have a web app, click "Add app" → Web (</>) icon
6. Copy the `apiKey` value from the config

The config will look like:
```javascript
const firebaseConfig = {
  apiKey: "AIza....", // ← Copy this
  authDomain: "jarvis-0009.firebaseapp.com",
  databaseURL: "https://jarvis-0009-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "jarvis-0009",
  storageBucket: "jarvis-0009.firebasestorage.app",
  messagingSenderId: "...",
  appId: "..."
};
```

## Step 2: Update Configuration Files

### Update `.env` file

Edit `ChatInterface/.env` and add all Firebase credentials:

```env
# Firebase Configuration
EXPO_PUBLIC_FIREBASE_API_KEY=AIza....  # ← Add this from Firebase Console
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=jarvis-0009.firebaseapp.com
EXPO_PUBLIC_FIREBASE_DATABASE_URL=https://jarvis-0009-default-rtdb.asia-southeast1.firebasedatabase.app
EXPO_PUBLIC_FIREBASE_PROJECT_ID=jarvis-0009
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=jarvis-0009.firebasestorage.app
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...  # ← Add from Firebase Console
EXPO_PUBLIC_FIREBASE_APP_ID=...  # ← Add from Firebase Console
```

### Update `app.json` (Optional - for extra security)

You can also add these to `app.json` under `extra` section:

```json
{
  "expo": {
    "extra": {
      "firebaseApiKey": "AIza....",
      "firebaseAuthDomain": "jarvis-0009.firebaseapp.com",
      "firebaseDatabaseUrl": "https://jarvis-0009-default-rtdb.asia-southeast1.firebasedatabase.app",
      "firebaseProjectId": "jarvis-0009",
      "firebaseStorageBucket": "jarvis-0009.firebasestorage.app",
      "firebaseMessagingSenderId": "...",
      "firebaseAppId": "..."
    }
  }
}
```

## Step 3: Login to Expo

Open terminal in the `ChatInterface` directory:

```bash
cd ChatInterface
eas login
```

Enter your Expo account credentials.

## Step 4: Configure EAS Build

Initialize EAS configuration (if not already done):

```bash
eas build:configure
```

This will create/update `eas.json` file.

## Step 5: Build the APK

### Option A: Preview Build (Recommended for Testing)

This creates an APK you can install directly:

```bash
eas build --platform android --profile preview
```

### Option B: Production Build

For a production-ready APK:

```bash
eas build --platform android --profile production
```

### What Happens During Build:

1. EAS will ask if you want to generate a new Android keystore → Select **Yes**
2. Build will be queued on Expo's servers (takes 5-15 minutes)
3. You'll get a link to track build progress
4. Once complete, you'll get a download link for the APK

## Step 6: Download and Install APK

1. **Download APK**
   - Click the download link from EAS build output
   - Or visit: https://expo.dev/accounts/[your-username]/projects/ChatInterface/builds
   - Download the APK file to your phone

2. **Install on Android Phone**
   - Transfer APK to your phone (via USB, email, or direct download)
   - Open the APK file
   - Android will ask "Install unknown apps" → Allow
   - Tap "Install"

## Step 7: Test Pairing Over Mobile Network

Now you can test the real pairing flow:

1. **On Desktop:**
   - Run the settings UI: `python local_client/run_settings.py`
   - QR code will be generated

2. **On Phone:**
   - Disconnect from WiFi (use mobile data)
   - Open JARVIS app
   - Tap "Scan QR Code"
   - Scan the QR code from desktop
   - Pairing should complete over internet via Firebase!

## Troubleshooting

### Build Fails

**Error: Missing credentials**
- Make sure you've added all Firebase config to `.env`
- Check that `.env` file is in `ChatInterface` directory

**Error: Android keystore**
- Let EAS generate a new keystore when prompted
- Don't worry about losing it for testing builds

### APK Won't Install

**"App not installed"**
- Enable "Install unknown apps" in Android settings
- Make sure you have enough storage space

**"Parse error"**
- APK might be corrupted, download again
- Make sure APK is for Android (not iOS)

### Pairing Doesn't Work

**QR code not scanning**
- Grant camera permission when prompted
- Ensure good lighting
- Try manual token entry as fallback

**"Token expired"**
- QR codes expire after 5 minutes
- Generate a new one on desktop

**"Pairing failed"**
- Check internet connection on both devices
- Verify Firebase is accessible (not blocked by firewall)
- Check Firebase Realtime Database rules allow read/write

## Build Variants

### Development Build (with Dev Tools)
```bash
eas build --platform android --profile development
```
- Includes React Native dev tools
- Larger file size
- Good for debugging

### Preview Build (Recommended)
```bash
eas build --platform android --profile preview
```
- Optimized but not production
- Smaller than development
- Good for testing

### Production Build
```bash
eas build --platform android --profile production
```
- Fully optimized
- Smallest file size
- Ready for Play Store

## Alternative: Local Build (Advanced)

If you want to build locally without EAS:

```bash
# Install Android Studio and SDK first
npx expo prebuild
cd android
./gradlew assembleRelease
```

APK will be in: `android/app/build/outputs/apk/release/app-release.apk`

## Notes

- **First build takes longer** (15-20 minutes) as EAS sets up everything
- **Subsequent builds are faster** (5-10 minutes)
- **Free Expo accounts** get limited build minutes per month
- **APK size** will be around 50-80 MB
- **Updates**: To update the app, build a new APK and reinstall

## Next Steps

After successful pairing test:

1. Test sending commands from mobile over internet
2. Test voice messages
3. Test file uploads
4. Verify Firebase real-time sync works
5. Consider publishing to Google Play Store for easier distribution

## Resources

- EAS Build Documentation: https://docs.expo.dev/build/introduction/
- Expo Application Services: https://expo.dev/eas
- Firebase Console: https://console.firebase.google.com/
