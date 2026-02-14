/**
 * Pairing Manager for JARVIS Mobile App
 * Handles QR code scanning, pairing token submission, and device pairing status.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Camera } from 'expo-camera';
import { getFirebaseDatabase, signInAnonymouslyToFirebase } from '../config/firebase';
import { ref, get, update, set } from 'firebase/database';

interface PairingToken {
  token: string;
  desktopId: string;
  expiresAt: number;
  used: boolean;
}

interface DeviceConfig {
  deviceId: string;
  pairedDesktopId?: string;
  lastUpdated: number;
}

export class PairingManager {
  private database: any; // Firebase database instance
  private deviceId: string | null = null;
  private readonly DEVICE_CONFIG_KEY = '@jarvis_device_config';

  /**
   * Initialize PairingManager.
   * Uses Firebase database directly for pairing operations.
   */
  constructor() {
    this._initializeDeviceId();
  }

  /**
   * Initialize device ID by loading from storage or generating new one.
   */
  private async _initializeDeviceId(): Promise<void> {
    try {
      const deviceId = await this._getOrCreateDeviceId();
      this.deviceId = deviceId;

      // Sign in anonymously to Firebase (required for security rules)
      await signInAnonymouslyToFirebase();

      // Initialize Firebase database
      this.database = getFirebaseDatabase();

      console.log('✅ PairingManager initialized');
      console.log(`   Device ID: ${deviceId}`);
    } catch (error) {
      console.error('❌ Failed to initialize device ID:', error);
      throw error;
    }
  }

  /**
   * Load existing device ID or generate a new one.
   * 
   * @returns Device ID string
   */
  private async _getOrCreateDeviceId(): Promise<string> {
    try {
      // Try to load existing device config
      const configJson = await AsyncStorage.getItem(this.DEVICE_CONFIG_KEY);

      if (configJson) {
        const config: DeviceConfig = JSON.parse(configJson);
        if (config.deviceId) {
          console.log(`📱 Loaded existing device ID: ${config.deviceId}`);
          return config.deviceId;
        }
      }
    } catch (error) {
      console.warn('⚠️ Failed to load device config:', error);
    }

    // Generate new device ID
    const deviceId = `mobile_${this._generateUUID().substring(0, 16)}`;

    // Save device config
    await this._saveDeviceConfig(deviceId);

    console.log(`🆕 Generated new device ID: ${deviceId}`);
    return deviceId;
  }

  /**
   * Generate a UUID v4.
   * 
   * @returns UUID string
   */
  private _generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Save device configuration to secure storage.
   * 
   * @param deviceId - Mobile device ID
   * @param pairedDesktopId - Desktop device ID (if paired)
   */
  private async _saveDeviceConfig(
    deviceId: string,
    pairedDesktopId?: string
  ): Promise<void> {
    try {
      const config: DeviceConfig = {
        deviceId,
        pairedDesktopId,
        lastUpdated: Date.now(),
      };

      await AsyncStorage.setItem(
        this.DEVICE_CONFIG_KEY,
        JSON.stringify(config)
      );

      console.log('💾 Device config saved');
    } catch (error) {
      console.error('❌ Failed to save device config:', error);
      throw error;
    }
  }

  /**
   * Request camera permissions.
   * 
   * @returns True if permission granted, false otherwise
   */
  async requestCameraPermission(): Promise<boolean> {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();

      if (status === 'granted') {
        console.log('✅ Camera permission granted');
        return true;
      } else {
        console.warn('⚠️ Camera permission denied');
        return false;
      }
    } catch (error) {
      console.error('❌ Failed to request camera permission:', error);
      return false;
    }
  }

  /**
   * Check if camera permission is granted.
   * 
   * @returns True if permission granted, false otherwise
   */
  async hasCameraPermission(): Promise<boolean> {
    try {
      const { status } = await Camera.getCameraPermissionsAsync();
      return status === 'granted';
    } catch (error) {
      console.error('❌ Failed to check camera permission:', error);
      return false;
    }
  }

  /**
   * Scan QR code and extract pairing token.
   * This method should be called from a component that renders the camera.
   * 
   * @param data - Scanned QR code data
   * @returns Pairing token if valid, null otherwise
   */
  extractTokenFromQRCode(data: string): string | null {
    try {
      // Validate token format (should start with "pair_")
      if (data && data.startsWith('pair_')) {
        console.log(`📷 QR code scanned: ${data}`);
        return data;
      } else {
        console.warn('⚠️ Invalid QR code format');
        return null;
      }
    } catch (error) {
      console.error('❌ Failed to extract token from QR code:', error);
      return null;
    }
  }

  /**
   * Submit pairing token to Firebase for verification.
   * 
   * @param token - Pairing token from QR code
   * @returns Object with success status and optional error message
   */
  async submitPairingToken(token: string): Promise<{ success: boolean; message?: string }> {
    try {
      if (!this.deviceId) {
        await this._initializeDeviceId();
      }

      if (!this.deviceId) {
        return { success: false, message: 'Device ID not initialized' };
      }

      // Ensure we are authenticated with Firebase
      try {
        await signInAnonymouslyToFirebase();
      } catch (authError) {
        console.warn('⚠️ Firebase auth may already be initialized:', authError);
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      console.log(`🔑 Submitting pairing token: ${token}`);

      // Get token data from Firebase
      const tokenRef = ref(this.database, `pairing/${token}`);
      const tokenSnapshot = await get(tokenRef);
      const tokenData = tokenSnapshot.val();

      if (!tokenData) {
        console.warn('⚠️ Token not found in Firebase');
        return { success: false, message: 'Invalid code: Token not found. Please regenerate the QR code.' };
      }

      // Check if token is expired
      const currentTime = Math.floor(Date.now() / 1000);

      // Check for clock skew (if token future time is unreasonably far)
      if (tokenData.createdAt && currentTime < tokenData.createdAt - 60) {
        console.warn(`⚠️ Clock skew detected. Device time (${currentTime}) is behind Token creation (${tokenData.createdAt})`);
      }

      if (currentTime > tokenData.expiresAt) {
        console.warn(`⚠️ Token expired. Current: ${currentTime}, Expires: ${tokenData.expiresAt}`);
        return { success: false, message: 'Pairing code has expired. Please regenerate the QR code.' };
      }

      // Check if token already used
      if (tokenData.used) {
        console.warn('⚠️ Token already used');
        return { success: false, message: 'This pairing code has already been used.' };
      }

      // Mark token as used and store mobile device ID
      await update(tokenRef, {
        used: true,
        mobileId: this.deviceId,
        usedAt: currentTime,
      });

      // Register mobile device in Firebase
      await this._registerDevice(tokenData.desktopId);

      // Save pairing info locally
      await this._saveDeviceConfig(this.deviceId, tokenData.desktopId);

      console.log(`✅ Pairing successful with desktop: ${tokenData.desktopId}`);
      return { success: true };

    } catch (error) {
      console.error('❌ Failed to submit pairing token:', error);
      return { success: false, message: `Pairing error: ${(error as Error).message}` };
    }
  }

  /**
   * Register this mobile device in Firebase.
   * 
   * @param desktopId - Desktop device ID to pair with
   */
  private async _registerDevice(desktopId: string): Promise<void> {
    try {
      if (!this.deviceId) {
        throw new Error('Device ID not initialized');
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      const deviceRef = ref(this.database, `devices/${this.deviceId}`);

      await set(deviceRef, {
        type: 'mobile',
        paired: true,
        pairedWith: desktopId,
        lastSeen: Math.floor(Date.now() / 1000),
        version: '1.0.0',
        registeredAt: Math.floor(Date.now() / 1000),
      });

      console.log(`✅ Mobile device registered: ${this.deviceId}`);
    } catch (error) {
      console.error('❌ Failed to register device:', error);
      throw error;
    }
  }

  /**
   * Check if this device is currently paired with a desktop.
   * 
   * @returns True if paired, false otherwise
   */
  async isPaired(): Promise<boolean> {
    try {
      if (!this.deviceId) {
        await this._initializeDeviceId();
      }

      if (!this.deviceId) {
        return false;
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      // Check Firebase device status
      const deviceRef = ref(this.database, `devices/${this.deviceId}`);
      const deviceSnapshot = await get(deviceRef);
      const deviceData = deviceSnapshot.val();

      if (deviceData) {
        return deviceData.paired === true;
      }

      return false;

    } catch (error) {
      console.error('❌ Failed to check paired status:', error);
      return false;
    }
  }

  /**
   * Get the ID of the paired desktop device.
   * 
   * @returns Desktop device ID if paired, null otherwise
   */
  async getPairedDesktopId(): Promise<string | null> {
    try {
      if (!this.deviceId) {
        await this._initializeDeviceId();
      }

      if (!this.deviceId) {
        return null;
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      // Check Firebase device status
      const deviceRef = ref(this.database, `devices/${this.deviceId}`);
      const deviceSnapshot = await get(deviceRef);
      const deviceData = deviceSnapshot.val();

      if (deviceData && deviceData.paired) {
        return deviceData.pairedWith || null;
      }

      return null;

    } catch (error) {
      console.error('❌ Failed to get paired desktop ID:', error);
      return null;
    }
  }

  /**
   * Get the current device ID.
   * 
   * @returns Device ID string
   */
  async getDeviceId(): Promise<string> {
    if (!this.deviceId) {
      await this._initializeDeviceId();
    }

    if (!this.deviceId) {
      throw new Error('Failed to initialize device ID');
    }

    return this.deviceId;
  }

  /**
   * Unpair this device from the desktop.
   * 
   * @returns True if unpair successful, false otherwise
   */
  async unpair(): Promise<boolean> {
    try {
      if (!this.deviceId) {
        await this._initializeDeviceId();
      }

      if (!this.deviceId) {
        return false;
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      // Update Firebase device status
      const deviceRef = ref(this.database, `devices/${this.deviceId}`);

      await update(deviceRef, {
        paired: false,
        pairedWith: null,
        unpairedAt: Math.floor(Date.now() / 1000),
      });

      // Update local config
      await this._saveDeviceConfig(this.deviceId);

      console.log('🔓 Device unpaired');
      return true;

    } catch (error) {
      console.error('❌ Failed to unpair device:', error);
      return false;
    }
  }

  /**
   * Update device presence in Firebase.
   */
  async updatePresence(): Promise<void> {
    try {
      if (!this.deviceId) {
        await this._initializeDeviceId();
      }

      if (!this.deviceId) {
        return;
      }

      if (!this.database) {
        this.database = getFirebaseDatabase();
      }

      const deviceRef = ref(this.database, `devices/${this.deviceId}`);

      await update(deviceRef, {
        lastSeen: Math.floor(Date.now() / 1000),
      });

    } catch (error) {
      console.error('❌ Failed to update presence:', error);
    }
  }
}
