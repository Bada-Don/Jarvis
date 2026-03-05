/**
 * Crypto polyfill for React Native
 * AWS SDK requires crypto.getRandomValues
 */

// Import react-native-get-random-values first
import 'react-native-get-random-values';

// Ensure crypto object exists
if (typeof global.crypto === 'undefined') {
  global.crypto = {};
}

// react-native-get-random-values should have already set getRandomValues
// but let's ensure it's there
if (typeof global.crypto.getRandomValues === 'undefined') {
  throw new Error('crypto.getRandomValues not available after polyfill');
}

// Add subtle crypto stub for AWS SDK v3
if (typeof global.crypto.subtle === 'undefined') {
  global.crypto.subtle = {};
}

export default global.crypto;
