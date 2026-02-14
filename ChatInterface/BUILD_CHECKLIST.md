# APK Build Checklist

Use this checklist to ensure everything is ready before building.

## Pre-Build Checklist

### 1. Firebase Configuration ✓

- [ ] Firebase project exists (`jarvis-0009`)
- [ ] Firebase Realtime Database is enabled
- [ ] Firebase Web app is created in project
- [ ] You have the Firebase Web API Key
- [ ] You have all Firebase config values:
  - [ ] API Key (AIza...)
  - [ ] Auth Domain (jarvis-0009.firebaseapp.com)
  - [ ] Database URL (https://jarvis-0009-default-rtdb...)
  - [ ] Project ID (jarvis-0009)
  - [ ] Storage Bucket
  - [ ] Messaging Sender ID
  - [ ] App ID

### 2. Local Configuration ✓

- [ ] `.env` file exists in `ChatInterface/` directory
- [ ] `.env` contains all `EXPO_PUBLIC_FIREBASE_*` variables
- [ ] `app.json` has Firebase config in `extra` section (optional but recommended)
- [ ] `eas.json` exists (created automatically)

### 3. Expo Setup ✓

- [ ] Expo account created (free at expo.dev)
- [ ] EAS CLI installed globally: `npm install -g eas-cli`
- [ ] Logged into EAS: `eas login`
- [ ] Can run: `eas whoami` (shows your username)

### 4. Dependencies ✓

- [ ] Node.js installed (v18 or higher)
- [ ] npm or yarn installed
- [ ] All packages installed: `npm install` in ChatInterface directory
- [ ] No errors in `npm install` output

### 5. Code Verification ✓

- [ ] App runs in Expo Go: `npm start`
- [ ] No critical errors in console
- [ ] Firebase connection works (check logs)
- [ ] QR Scanner component exists
- [ ] Pairing screen exists

## Build Process Checklist

### 1. Pre-Build Steps

- [ ] All changes committed to git (optional but recommended)
- [ ] Terminal is in `ChatInterface` directory
- [ ] Internet connection is stable

### 2. Start Build

Choose one:
- [ ] Preview build: `npm run build:preview` (recommended)
- [ ] Production build: `npm run build:production`
- [ ] Development build: `npm run build:dev`

### 3. During Build

- [ ] EAS asks about Android keystore → Select "Yes, generate new"
- [ ] Build is queued successfully
- [ ] Build link is provided
- [ ] Can track build at: https://expo.dev/accounts/[username]/projects/ChatInterface/builds

### 4. Build Completion

- [ ] Build status shows "Finished"
- [ ] Download link is available
- [ ] APK file downloaded (50-80 MB)
- [ ] APK filename: `build-[id].apk`

## Installation Checklist

### 1. Transfer APK to Phone

Choose one method:
- [ ] Direct download on phone from EAS link
- [ ] USB transfer from computer
- [ ] Email/cloud storage link
- [ ] QR code from EAS build page

### 2. Install on Android

- [ ] APK file opened on phone
- [ ] "Install unknown apps" permission granted
- [ ] Installation completed successfully
- [ ] App icon appears in app drawer

### 3. First Launch

- [ ] App opens without crashing
- [ ] Splash screen plays
- [ ] No immediate errors
- [ ] Permissions requested (camera, microphone)

## Testing Checklist

### 1. Basic Functionality

- [ ] App launches successfully
- [ ] UI loads correctly
- [ ] No crash on startup
- [ ] Can navigate through app

### 2. Permissions

- [ ] Camera permission requested
- [ ] Camera permission granted
- [ ] Microphone permission requested
- [ ] Microphone permission granted

### 3. Firebase Connection

- [ ] App connects to Firebase
- [ ] No Firebase errors in logs
- [ ] Device ID generated
- [ ] Device registered in Firebase

### 4. Pairing Test (Main Goal!)

#### Desktop Setup:
- [ ] Desktop app running
- [ ] Settings UI opened: `python local_client/run_settings.py`
- [ ] QR code generated and visible
- [ ] Token shows in logs (pair_...)

#### Mobile Setup:
- [ ] Phone disconnected from WiFi
- [ ] Using mobile data only
- [ ] JARVIS app opened
- [ ] Pairing screen appears

#### Pairing Process:
- [ ] "Scan QR Code" button tapped
- [ ] Camera opens
- [ ] QR code scanned successfully
- [ ] "Processing pairing..." message appears
- [ ] "Pairing Successful" alert shows
- [ ] Chat screen appears
- [ ] Device shows as paired

#### Verification:
- [ ] Check Firebase Console → Realtime Database → devices → [mobile_id]
- [ ] `paired: true` in database
- [ ] `pairedWith` shows desktop ID
- [ ] Desktop logs show mobile device connected

### 5. Remote Communication

- [ ] Send test message from mobile
- [ ] Message appears on desktop
- [ ] Desktop can respond
- [ ] Response appears on mobile
- [ ] Real-time sync works

### 6. Additional Features

- [ ] Voice message recording works
- [ ] File upload works
- [ ] Task execution works
- [ ] Abort button works
- [ ] App doesn't crash during use

## Troubleshooting Checklist

### Build Issues

If build fails:
- [ ] Check EAS build logs for errors
- [ ] Verify all Firebase config in .env
- [ ] Ensure EAS CLI is latest: `npm install -g eas-cli@latest`
- [ ] Try clearing cache: `eas build:clear-cache`
- [ ] Check Expo status: https://status.expo.dev/

### Installation Issues

If APK won't install:
- [ ] Enable "Install unknown apps" in Settings
- [ ] Check phone has enough storage (100+ MB free)
- [ ] Try downloading APK again
- [ ] Verify APK is not corrupted (check file size)

### Pairing Issues

If pairing fails:
- [ ] Check both devices have internet
- [ ] Verify Firebase Realtime Database is accessible
- [ ] Check Firebase security rules allow read/write
- [ ] Ensure QR code is not expired (5 min limit)
- [ ] Try manual token entry as fallback
- [ ] Check Firebase Console for error logs

### Runtime Issues

If app crashes:
- [ ] Check for missing permissions
- [ ] Verify Firebase config is correct
- [ ] Look for errors in device logs (adb logcat)
- [ ] Try uninstalling and reinstalling
- [ ] Build development version for better error messages

## Success Criteria ✅

Your build is successful when:

1. ✅ APK installs without errors
2. ✅ App launches and runs smoothly
3. ✅ QR code scanning works
4. ✅ Pairing completes over mobile network (not same WiFi)
5. ✅ Can send commands from mobile to desktop
6. ✅ Real-time communication works via Firebase

## Post-Success Steps

After successful testing:

- [ ] Document any issues encountered
- [ ] Note build time and APK size
- [ ] Save APK file for future reference
- [ ] Consider publishing to Play Store
- [ ] Share APK with other testers
- [ ] Update documentation with findings

---

**Ready to build?** Run: `npm run setup-build` then `npm run build:preview`
