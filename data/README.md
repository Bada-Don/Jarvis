# Data Directory

This directory contains Firebase configuration and credentials.

## Required Files

### 1. firebase-admin-credentials.json (Required)

Download from Firebase Console:
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the downloaded file as `firebase-admin-credentials.json` in this directory

**⚠️ NEVER commit this file to git!** It contains sensitive credentials.

### 2. firebase_config.json (Optional but Recommended)

If your Firebase database is in a non-US region, create this file:

```json
{
  "project_id": "your-project-id",
  "database_url": "https://your-project-id-default-rtdb.asia-southeast1.firebasedatabase.app",
  "region": "asia-southeast1"
}
```

**Common regions:**
- `us-central1` (United States) - Default
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

**To auto-generate this file:**
```bash
python fix_firebase_region.py
```

### 3. device_config.json (Auto-generated)

This file is automatically created when you run the pairing manager. It stores your device ID.

**⚠️ Do not commit this file** - it's device-specific.

## Files in This Directory

```
data/
├── firebase-admin-credentials.json    # Your Firebase credentials (REQUIRED, DO NOT COMMIT)
├── firebase_config.json               # Database URL config (optional, DO NOT COMMIT)
├── device_config.json                 # Device ID (auto-generated, DO NOT COMMIT)
├── firebase_config.json.example       # Template for firebase_config.json
└── README.md                          # This file
```

## Security Notes

- ✅ `.gitignore` is configured to exclude sensitive files
- ✅ Only commit `.example` files
- ✅ Never share credentials publicly
- ✅ Rotate credentials if accidentally exposed
