# Firebase Quick Start Checklist

Use this checklist to quickly set up Firebase for JARVIS.

## ✅ Checklist

### 1. Create Firebase Project
- [ ] Go to [Firebase Console](https://console.firebase.google.com/)
- [ ] Click "Add project"
- [ ] Name: `jarvis-desktop-app`
- [ ] Click "Create project"

### 2. Enable Realtime Database
- [ ] Navigate to **Build** → **Realtime Database**
- [ ] Click "Create Database"
- [ ] Choose location (e.g., `us-central1`)
- [ ] Start in **Test mode**
- [ ] Click "Enable"
- [ ] Copy database URL: `https://PROJECT-ID-default-rtdb.firebaseio.com/`

### 3. Enable Anonymous Authentication
- [ ] Navigate to **Build** → **Authentication**
- [ ] Click "Get started"
- [ ] Go to **Sign-in method** tab
- [ ] Enable "Anonymous"
- [ ] Click "Save"

### 4. Download Service Account Credentials
- [ ] Navigate to **Project Settings** → **Service accounts**
- [ ] Click "Generate new private key"
- [ ] Save as `firebase-admin-credentials.json`
- [ ] Move file to `data/firebase-admin-credentials.json`
- [ ] **NEVER commit this file to git!**

### 5. Configure Security Rules
- [ ] Navigate to **Build** → **Realtime Database** → **Rules** tab
- [ ] Copy contents from `firebase-security-rules.json`
- [ ] Paste into Firebase console
- [ ] Click "Publish"

### 6. Update Environment Variables

#### Backend (.env)
- [ ] Copy `backend/.env.example` to `backend/.env`
- [ ] Set `FIREBASE_CREDENTIALS_PATH=../data/firebase-admin-credentials.json`
- [ ] Set `FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/`

#### Local Client (.env)
- [ ] Copy `local_client/.env.example` to `local_client/.env`
- [ ] Set `FIREBASE_CREDENTIALS_PATH=../data/firebase-admin-credentials.json`
- [ ] Set `FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/`

#### Mobile App (.env)
- [ ] Copy `ChatInterface/.env.example` to `ChatInterface/.env`
- [ ] Set `FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/`
- [ ] Set `FIREBASE_PROJECT_ID=your-project-id`

### 7. Configure Mobile Apps (Later)

**Note**: The mobile app uses Expo, so native configuration is simplified.

#### For Expo Development (Current)
- [ ] Update `ChatInterface/.env` with Firebase URL and Project ID
- [ ] No native config files needed yet

#### For Standalone Builds (Later - Task 13)

**Android**
- [ ] Register Android app in Firebase console
- [ ] Package name: `com.anonymous.ChatInterface` (from app.json)
- [ ] Download `google-services.json`
- [ ] Place in `ChatInterface/` root

**iOS**
- [ ] Register iOS app in Firebase console
- [ ] Bundle ID: `com.anonymous.ChatInterface`
- [ ] Download `GoogleService-Info.plist`
- [ ] Place in `ChatInterface/` root

### 8. Verify Setup
- [ ] Run test connection script (see FIREBASE_SETUP_GUIDE.md)
- [ ] Check Firebase console for test data

## 🔒 Security Reminders

- ✅ `firebase-admin-credentials.json` is in `.gitignore`
- ✅ Never share credentials publicly
- ✅ Use environment variables for sensitive data
- ✅ Security rules are configured (not in test mode)

## 📚 Next Steps

After completing this checklist:
1. Proceed to Task 2: Implement Firebase service module
2. See `docs/FIREBASE_SETUP_GUIDE.md` for detailed instructions
3. See `firebase-security-rules.json` for security rules explanation

## 🆘 Need Help?

- Full guide: `docs/FIREBASE_SETUP_GUIDE.md`
- Firebase docs: https://firebase.google.com/docs
- Security rules: https://firebase.google.com/docs/database/security
