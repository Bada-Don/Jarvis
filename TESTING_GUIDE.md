# JARVIS Testing Guide

## Overview
This guide explains how to test JARVIS after making code changes, especially to the mobile app (ChatInterface).

---

## 🎯 Quick Answer

**For the changes we just made:**

### Backend Changes (Python)
✅ **No rebuild needed** - Just restart JARVIS.py
- Python is interpreted, changes take effect immediately on restart

### Mobile App Changes (React Native/TypeScript)
⚠️ **Depends on your current setup:**

1. **If using Expo Go app** → Changes apply automatically (hot reload)
2. **If using preview build (APK)** → Need to rebuild
3. **If using development build** → Need to rebuild

---

## 📱 Mobile App Testing Options

### Option 1: Expo Go (Fastest for Development) ⚡

**Best for:** Quick testing, development, frequent changes

**Setup:**
```bash
cd ChatInterface
npm start
# or
npx expo start
```

**On your phone:**
1. Install Expo Go from Play Store
2. Scan the QR code from terminal
3. Changes hot-reload automatically

**Pros:**
- ✅ Instant updates (hot reload)
- ✅ No build time
- ✅ Perfect for testing our fixes

**Cons:**
- ❌ Can't test native modules fully
- ❌ Some features may behave differently

**Recommended for:** Testing the fixes we just made (Firebase, progress bar, etc.)

---

### Option 2: Development Build (Best Balance) 🔧

**Best for:** Testing with native features, closer to production

**Build once:**
```bash
cd ChatInterface
npx expo run:android
# or
npm run android
```

**Then for testing:**
```bash
npm start
```

**Pros:**
- ✅ Hot reload still works
- ✅ Full native module support
- ✅ Closer to production behavior

**Cons:**
- ⚠️ Initial build takes 5-10 minutes
- ⚠️ Need to rebuild if native dependencies change

**Recommended for:** Testing Firebase integration, camera, audio

---

### Option 3: Preview Build (Production-like) 📦

**Best for:** Final testing before release

**Build:**
```bash
cd ChatInterface
npm run build:preview
# or
eas build --platform android --profile preview
```

**Pros:**
- ✅ Exactly like production
- ✅ Can share APK for testing

**Cons:**
- ❌ Takes 10-20 minutes to build
- ❌ No hot reload
- ❌ Need to rebuild for every change

**Recommended for:** Final validation before release

---

## 🧪 Recommended Testing Workflow

### For Our Recent Changes

Since we modified:
- Firebase Auth persistence
- Progress bar logic
- Duplicate listener prevention
- Backend error logging

**Recommended approach:**

#### Step 1: Test Backend Changes
```bash
# Stop JARVIS if running
# Then restart
python JARVIS.py
```

**What to test:**
- Send a command that might fail
- Check logs in `data/logs/` for detailed error traces
- Verify error messages are more informative

---

#### Step 2: Test Mobile App (Choose One)

**Option A: Quick Test with Expo Go (Recommended)**
```bash
cd ChatInterface
npm start
```
Then scan QR code with Expo Go app

**Option B: Development Build (If you have time)**
```bash
cd ChatInterface
npx expo run:android
```
Wait for build, then test

**What to test:**
1. **Firebase Auth Persistence:**
   - Close and reopen app
   - Should stay logged in ✅

2. **Progress Bar:**
   - Send a command
   - Watch progress bar go to 100%
   - Verify it doesn't restart ✅
   - Send another command immediately
   - Should work without issues ✅

3. **Duplicate Listeners:**
   - Check logs (adb logcat or Expo logs)
   - Should see each status update only ONCE ✅
   - No more 4-8x duplicates

---

## 🔍 Testing Checklist

### Backend Testing
- [ ] JARVIS.py starts without errors
- [ ] Backend server responds on http://localhost:5000
- [ ] Error logs show full tracebacks
- [ ] Commands execute successfully

### Mobile App Testing
- [ ] App connects to backend
- [ ] Firebase authentication works
- [ ] User stays logged in after app restart
- [ ] Progress bar completes without restarting
- [ ] No duplicate status messages in logs
- [ ] Can send multiple commands in sequence
- [ ] QR code pairing works (if testing Firebase)

---

## 🛠️ Development Commands Reference

### Backend (Python)
```bash
# Start JARVIS
python JARVIS.py

# Start with debug logging
python JARVIS.py --debug

# Start only backend (for testing)
python JARVIS.py --component backend

# View logs
tail -f data/logs/backend_stdout_*.log
tail -f data/logs/backend_stderr_*.log
```

### Mobile App (React Native)
```bash
cd ChatInterface

# Start Expo development server
npm start
# or
npx expo start

# Start with specific options
npx expo start --clear  # Clear cache
npx expo start --tunnel # Use tunnel for remote testing

# Run on Android (development build)
npm run android
# or
npx expo run:android

# Build preview APK
npm run build:preview

# Build development APK
npm run build:dev

# Check for TypeScript errors
npx tsc --noEmit
```

---

## 📊 Monitoring & Debugging

### Backend Logs
```bash
# Real-time backend logs
tail -f data/logs/backend_stdout_*.log

# Real-time error logs
tail -f data/logs/backend_stderr_*.log

# All launcher logs
tail -f data/logs/launcher_*.log
```

### Mobile App Logs

**Using Expo:**
```bash
cd ChatInterface
npm start
# Logs appear in terminal automatically
```

**Using Android Debug Bridge:**
```bash
# View all logs
adb logcat

# Filter for React Native
adb logcat | grep ReactNative

# Filter for your app
adb logcat | grep ChatInterface

# Clear logs
adb logcat -c
```

---

## 🚀 Quick Start for Testing Our Changes

### Fastest Method (5 minutes):

1. **Terminal 1 - Backend:**
   ```bash
   python JARVIS.py
   ```

2. **Terminal 2 - Mobile App:**
   ```bash
   cd ChatInterface
   npm start
   ```

3. **Phone:**
   - Open Expo Go
   - Scan QR code
   - Test the fixes!

### What You Should See:

✅ **Progress bar completes properly**
- Goes from 0% → 100%
- Shows "Completed" status
- Doesn't restart

✅ **No duplicate logs**
- Each status update appears once
- No 4-8x repetition

✅ **Auth persists**
- Close and reopen app
- Still logged in

✅ **Better error messages**
- Backend logs show full stack traces
- Error types included in responses

---

## 💡 Pro Tips

### For Rapid Development:
1. Use Expo Go for mobile testing (hot reload)
2. Keep JARVIS.py running in one terminal
3. Keep `npm start` running in another
4. Changes to TypeScript/React files reload automatically
5. Only restart JARVIS.py when changing Python files

### For Production Testing:
1. Build preview APK once
2. Install on device
3. Test all features thoroughly
4. Rebuild only when ready to release

### For Debugging:
1. Enable debug mode: `python JARVIS.py --debug`
2. Use `console.log()` in React Native (appears in Expo terminal)
3. Check both backend and mobile logs
4. Use React Native Debugger for advanced debugging

---

## 🐛 Common Issues

### "Metro bundler not starting"
```bash
cd ChatInterface
npx expo start --clear
```

### "Can't connect to backend"
- Check JARVIS.py is running
- Verify backend is on http://localhost:5000
- Check firewall settings

### "Changes not appearing"
- Shake device → Reload
- Or press 'r' in Expo terminal
- Or `npx expo start --clear`

### "Build failed"
```bash
cd ChatInterface
rm -rf node_modules
npm install
npx expo start --clear
```

---

## 📝 Summary

**For the changes we made today:**

1. **Backend:** Just restart `python JARVIS.py` ✅
2. **Mobile App:** Use `npm start` with Expo Go for fastest testing ✅
3. **Full Testing:** Use development build if you need native features
4. **Production:** Build preview APK only for final validation

**Recommended workflow:**
```bash
# Terminal 1
python JARVIS.py

# Terminal 2
cd ChatInterface && npm start

# Phone: Scan QR with Expo Go
```

This gives you hot reload for mobile changes and easy restart for backend changes!

---

**Need help?** Check the logs:
- Backend: `data/logs/`
- Mobile: Expo terminal or `adb logcat`
