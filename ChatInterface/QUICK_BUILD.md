# Quick APK Build Reference

## TL;DR - Fast Track

```bash
# 1. Get Firebase Web API Key from Firebase Console
# Go to: https://console.firebase.google.com/ → jarvis-0009 → Settings → Web app

# 2. Run setup script
cd ChatInterface
npm run setup-build

# 3. Login to Expo (create free account if needed)
eas login

# 4. Build APK
npm run build:preview

# 5. Wait 5-15 minutes, download APK from link provided

# 6. Install on phone and test over mobile network!
```

## What You Need

1. **Firebase Web API Key** - Get from Firebase Console
2. **Expo Account** - Sign up free at expo.dev
3. **EAS CLI** - Install with: `npm install -g eas-cli`

## Build Commands

```bash
# Preview build (recommended for testing)
npm run build:preview

# Production build (optimized)
npm run build:production

# Development build (with dev tools)
npm run build:dev
```

## Testing Pairing Over Internet

1. **Desktop**: Run `python local_client/run_settings.py` → QR code appears
2. **Phone**: Disconnect WiFi, use mobile data
3. **Phone**: Open JARVIS app → Scan QR Code
4. **Result**: Pairing works over internet via Firebase! 🎉

## Common Issues

**"Missing Firebase config"**
→ Run `npm run setup-build` and enter your Firebase credentials

**"EAS CLI not found"**
→ Run `npm install -g eas-cli`

**"Build failed"**
→ Check you're logged in: `eas whoami`
→ Make sure .env has all Firebase values

**"APK won't install"**
→ Enable "Install unknown apps" in Android settings

## File Locations

- Configuration: `ChatInterface/.env`
- Build config: `ChatInterface/eas.json`
- Full guide: `ChatInterface/BUILD_APK_GUIDE.md`

## Build Time

- First build: 15-20 minutes
- Subsequent builds: 5-10 minutes
- APK size: ~50-80 MB

## Free Tier Limits

Expo free accounts get limited build minutes per month. If you run out, you can:
- Wait for next month
- Upgrade to paid plan
- Build locally (requires Android Studio)

## Next Steps After Build

1. ✅ Test QR pairing over mobile network
2. ✅ Test sending commands remotely
3. ✅ Test voice messages
4. ✅ Test file uploads
5. 🚀 Consider publishing to Play Store

---

**Need help?** See `BUILD_APK_GUIDE.md` for detailed instructions.
