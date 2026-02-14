#!/usr/bin/env node

/**
 * Setup script for JARVIS Mobile APK build
 * Helps configure Firebase credentials before building
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function main() {
  console.log('\n🚀 JARVIS Mobile APK Build Setup\n');
  console.log('This script will help you configure Firebase credentials for building the APK.\n');
  
  // Check if .env exists
  const envPath = path.join(__dirname, '.env');
  let existingEnv = '';
  
  if (fs.existsSync(envPath)) {
    existingEnv = fs.readFileSync(envPath, 'utf8');
    console.log('✅ Found existing .env file\n');
  } else {
    console.log('📝 Creating new .env file\n');
  }
  
  console.log('Please provide your Firebase configuration.');
  console.log('You can find these values in Firebase Console → Project Settings → Your apps → Web app\n');
  
  // Get Firebase credentials
  const apiKey = await question('Firebase API Key (AIza...): ');
  const authDomain = await question('Auth Domain (jarvis-0009.firebaseapp.com): ') || 'jarvis-0009.firebaseapp.com';
  const databaseUrl = await question('Database URL: ') || 'https://jarvis-0009-default-rtdb.asia-southeast1.firebasedatabase.app';
  const projectId = await question('Project ID: ') || 'jarvis-0009';
  const storageBucket = await question('Storage Bucket: ') || 'jarvis-0009.firebasestorage.app';
  const messagingSenderId = await question('Messaging Sender ID: ');
  const appId = await question('App ID (1:...:web:...): ');
  
  // Create .env content
  const envContent = `# Firebase Configuration for APK Build
EXPO_PUBLIC_FIREBASE_API_KEY=${apiKey}
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=${authDomain}
EXPO_PUBLIC_FIREBASE_DATABASE_URL=${databaseUrl}
EXPO_PUBLIC_FIREBASE_PROJECT_ID=${projectId}
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=${storageBucket}
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=${messagingSenderId}
EXPO_PUBLIC_FIREBASE_APP_ID=${appId}
`;
  
  // Write .env file
  fs.writeFileSync(envPath, envContent);
  console.log('\n✅ Configuration saved to .env\n');
  
  // Update app.json
  const appJsonPath = path.join(__dirname, 'app.json');
  const appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'));
  
  appJson.expo.extra = {
    firebaseApiKey: apiKey,
    firebaseAuthDomain: authDomain,
    firebaseDatabaseUrl: databaseUrl,
    firebaseProjectId: projectId,
    firebaseStorageBucket: storageBucket,
    firebaseMessagingSenderId: messagingSenderId,
    firebaseAppId: appId
  };
  
  fs.writeFileSync(appJsonPath, JSON.stringify(appJson, null, 2));
  console.log('✅ Updated app.json with Firebase config\n');
  
  // Check if EAS CLI is installed
  console.log('Checking for EAS CLI...');
  const { execSync } = require('child_process');
  
  try {
    execSync('eas --version', { stdio: 'ignore' });
    console.log('✅ EAS CLI is installed\n');
  } catch (error) {
    console.log('⚠️  EAS CLI not found. Installing...\n');
    console.log('Run: npm install -g eas-cli\n');
  }
  
  console.log('🎉 Setup complete!\n');
  console.log('Next steps:');
  console.log('1. Login to Expo: eas login');
  console.log('2. Build APK: eas build --platform android --profile preview');
  console.log('3. Download and install APK on your phone');
  console.log('\nSee BUILD_APK_GUIDE.md for detailed instructions.\n');
  
  rl.close();
}

main().catch(error => {
  console.error('❌ Error:', error.message);
  rl.close();
  process.exit(1);
});
