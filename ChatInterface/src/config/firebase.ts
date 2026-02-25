/**
 * Firebase Configuration for JARVIS Mobile App
 * Initializes Firebase with environment variables
 */

import { initializeApp, FirebaseApp } from 'firebase/app';
import { getDatabase, Database } from 'firebase/database';
import { initializeAuth, getReactNativePersistence, getAuth, Auth, signInAnonymously } from 'firebase/auth';
import ReactNativeAsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

// Firebase configuration from environment variables
const firebaseConfig = {
  databaseURL: process.env.EXPO_PUBLIC_FIREBASE_DATABASE_URL || Constants.expoConfig?.extra?.firebaseDatabaseUrl,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID || Constants.expoConfig?.extra?.firebaseProjectId,
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY || Constants.expoConfig?.extra?.firebaseApiKey,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN || Constants.expoConfig?.extra?.firebaseAuthDomain,
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET || Constants.expoConfig?.extra?.firebaseStorageBucket,
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || Constants.expoConfig?.extra?.firebaseMessagingSenderId,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID || Constants.expoConfig?.extra?.firebaseAppId,
};

let app: FirebaseApp | null = null;
let database: Database | null = null;
let auth: Auth | null = null;

/**
 * Initialize Firebase app
 * @returns Firebase app instance
 */
export const initializeFirebase = (): FirebaseApp => {
  if (app) {
    return app;
  }

  try {
    // Validate required configuration
    if (!firebaseConfig.databaseURL) {
      throw new Error('Firebase Database URL is required');
    }

    if (!firebaseConfig.projectId) {
      throw new Error('Firebase Project ID is required');
    }

    console.log('🔥 Initializing Firebase...');
    console.log(`   Project ID: ${firebaseConfig.projectId}`);
    console.log(`   Database URL: ${firebaseConfig.databaseURL}`);

    app = initializeApp(firebaseConfig);
    console.log('✅ Firebase initialized successfully');

    return app;
  } catch (error) {
    console.error('❌ Failed to initialize Firebase:', error);
    throw error;
  }
};

/**
 * Get Firebase Realtime Database instance
 * @returns Database instance
 */
export const getFirebaseDatabase = (): Database => {
  if (!database) {
    const firebaseApp = initializeFirebase();
    database = getDatabase(firebaseApp);
    console.log('✅ Firebase Database initialized');
  }
  return database;
};

/**
 * Get Firebase Auth instance with AsyncStorage persistence
 * @returns Auth instance
 */
export const getFirebaseAuth = (): Auth => {
  if (!auth) {
    const firebaseApp = initializeFirebase();
    // Initialize Auth with AsyncStorage persistence to maintain session
    auth = initializeAuth(firebaseApp, {
      persistence: getReactNativePersistence(ReactNativeAsyncStorage)
    });
    console.log('✅ Firebase Auth initialized with AsyncStorage persistence');
  }
  return auth;
};

/**
 * Sign in anonymously to Firebase
 * Required for Firebase security rules
 * @returns User credential
 */
export const signInAnonymouslyToFirebase = async () => {
  try {
    const firebaseAuth = getFirebaseAuth();
    const userCredential = await signInAnonymously(firebaseAuth);
    console.log('✅ Signed in anonymously to Firebase');
    console.log(`   User ID: ${userCredential.user.uid}`);
    return userCredential;
  } catch (error) {
    console.error('❌ Failed to sign in anonymously:', error);
    throw error;
  }
};

/**
 * Check if Firebase is configured
 * @returns True if Firebase is configured, false otherwise
 */
export const isFirebaseConfigured = (): boolean => {
  return !!(firebaseConfig.databaseURL && firebaseConfig.projectId);
};

export { firebaseConfig };
