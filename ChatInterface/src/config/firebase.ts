import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

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

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

export { app, database };
