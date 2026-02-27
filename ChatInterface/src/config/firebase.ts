import { initializeApp, getApps, getApp } from "firebase/app";
import { getDatabase } from "firebase/database";
import { getAuth, signInAnonymously } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBZmxVR5tdvdMg6SarCGsKSfFBgPfNpzjA",
  authDomain: "jarvis-0009.firebaseapp.com",
  databaseURL: "https://jarvis-0009-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "jarvis-0009",
  storageBucket: "jarvis-0009.firebasestorage.app",
  messagingSenderId: "59641107562",
  appId: "1:59641107562:web:52391cae70866bc47fa613",
  measurementId: "G-NX9C6HC0ZF"
};

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
const database = getDatabase(app);
const auth = getAuth(app);

export const isFirebaseConfigured = () => {
  return !!firebaseConfig.apiKey && firebaseConfig.apiKey !== "YOUR_API_KEY";
};

export const getFirebaseDatabase = () => database;

export const signInAnonymouslyToFirebase = async () => {
  try {
    return await signInAnonymously(auth);
  } catch (error) {
    console.error("Firebase anonymous sign-in error:", error);
    throw error;
  }
};

export { app, database, auth };
