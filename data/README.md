# JARVIS Data Directory

This directory contains runtime data and configuration files for JARVIS.

## Firebase Credentials

### Required File: `firebase-admin-credentials.json`

This file contains your Firebase Admin SDK service account credentials. It is required for desktop-to-mobile communication.

**How to obtain:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your JARVIS project
3. Navigate to **Project Settings** → **Service accounts**
4. Click "Generate new private key"
5. Save the downloaded file as `firebase-admin-credentials.json` in this directory

**Security:**
- ⚠️ **NEVER commit this file to version control**
- ⚠️ **NEVER share this file publicly**
- ⚠️ This file is already in `.gitignore`
- ⚠️ Keep this file secure on your local machine

### Template File: `firebase-config-template.json`

This is a template showing the structure of the credentials file. Do NOT use this template directly - download the actual credentials from Firebase Console.

## Directory Structure

```
data/
├── README.md                           # This file
├── firebase-config-template.json      # Template (DO NOT USE)
├── firebase-admin-credentials.json    # Your actual credentials (NOT IN GIT)
├── config.py                          # User configuration (created on first run)
└── logs/                              # Application logs
```

## Setup Instructions

See the following guides for complete setup instructions:
- `docs/FIREBASE_SETUP_GUIDE.md` - Detailed Firebase setup guide
- `docs/FIREBASE_QUICK_START.md` - Quick start checklist

## Verification

After placing your credentials file, run the verification script:

```bash
python scripts/verify_firebase_setup.py
```

This will check that:
- Credentials file exists and is valid
- Environment variables are configured
- Firebase connection works
- Security rules are in place
