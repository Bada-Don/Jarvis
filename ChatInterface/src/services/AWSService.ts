/**
 * AWS Service for JARVIS Mobile App (Migrated to Firebase)
 * Handles real-time messaging, command sending, and status listening via Firebase
 * Replaces AWS DynamoDB logic with Firebase Realtime Database patterns
 */

import {
  getFirebaseDatabase,
  signInAnonymouslyToFirebase,
  isFirebaseConfigured,
} from '../config/firebase';
import {
  ref,
  push,
  set,
  onValue,
  off,
  update,
  remove,
  serverTimestamp,
  DatabaseReference,
  Unsubscribe,
} from 'firebase/database';

interface StatusMessage {
  type: 'status' | 'progress' | 'error' | 'completion';
  message: string;
  progress?: number;
  timestamp: number;
}

export class AWSService {
  private database: any;
  private deviceId: string | null = null;
  private pairedDesktopId: string | null = null;
  private isConnected: boolean = false;
  private statusCallback: ((status: StatusMessage) => void) | null = null;
  private statusUnsubscribe: Unsubscribe | null = null;

  /**
   * Initialize AWS Service (Firebase-backed)
   * @param deviceId - Mobile device ID
   * @param pairedDesktopId - Paired desktop device ID (optional)
   * @param config - Not used in Firebase version but kept for interface compatibility
   */
  constructor(
    deviceId: string,
    pairedDesktopId?: string,
    config?: any
  ) {
    if (!deviceId) {
      throw new Error('Device ID is required');
    }

    this.deviceId = deviceId;
    this.pairedDesktopId = pairedDesktopId || null;

    console.log('☁️ AWSService (Firebase-backed) initialized');
    console.log(`   Device ID: ${deviceId}`);
    if (pairedDesktopId) {
      console.log(`   Paired Desktop ID: ${pairedDesktopId}`);
    }
  }

  /**
   * Connect to Firebase and authenticate
   */
  async connect(): Promise<void> {
    try {
      if (!isFirebaseConfigured()) {
        throw new Error('Firebase is not configured. Please check environment variables.');
      }

      console.log('☁️ Connecting to Firebase (via AWSService)...');

      // Task 1: Replace Cognito with Firebase Auth
      await signInAnonymouslyToFirebase();

      // Get database instance
      this.database = getFirebaseDatabase();

      // Update device presence
      await this._updatePresence();

      this.isConnected = true;
      console.log('✅ Connected to Firebase');
    } catch (error) {
      console.error('❌ Failed to connect to Firebase:', error);
      throw error;
    }
  }

  /**
   * Update device presence in Firebase
   */
  private async _updatePresence(): Promise<void> {
    if (!this.deviceId) return;

    try {
      const deviceRef = ref(this.database, `devices/${this.deviceId}`);
      await update(deviceRef, {
        lastSeen: serverTimestamp(),
        online: true,
        type: 'mobile',
      });
    } catch (error) {
      console.error('❌ Failed to update presence:', error);
    }
  }

  /**
   * Disconnect from Firebase
   */
  disconnect(): void {
    console.log('☁️ Disconnecting from Firebase...');
    
    if (this.statusUnsubscribe) {
      this.statusUnsubscribe();
      this.statusUnsubscribe = null;
    }

    this.isConnected = false;
    console.log('✅ Disconnected');
  }

  /**
   * Send command to paired desktop
   * @param commandText - Command text to send
   * @returns Message ID
   */
  async sendCommand(commandText: string): Promise<string> {
    if (!this.pairedDesktopId) {
      throw new Error('No paired desktop. Please pair with a desktop first.');
    }

    if (!this.isConnected) {
      throw new Error('Not connected. Please check your connection.');
    }

    try {
      console.log(`📤 Sending command: ${commandText}`);

      const timestamp = Date.now();
      
      // Push to desktop's command queue (matching original Firebase pattern)
      const commandsRef = ref(this.database, `messages/${this.pairedDesktopId}/commands`);
      const newCommandRef = push(commandsRef);
      
      await set(newCommandRef, {
        type: 'command',
        text: commandText,
        timestamp,
        processed: false,
      });

      const messageId = newCommandRef.key!;
      console.log(`✅ Command sent with ID: ${messageId}`);

      return messageId;
    } catch (error) {
      console.error('❌ Failed to send command:', error);
      throw error;
    }
  }

  /**
   * Listen for status updates from paired desktop
   * @param callback - Callback function to handle status updates
   * @returns Unsubscribe function
   */
  listenForStatus(callback: (status: StatusMessage) => void): () => void {
    if (!this.deviceId) {
      throw new Error('Device ID not set');
    }

    console.log('👂 Listening for status updates via Firebase...');

    this.statusCallback = callback;
    const statusRef = ref(this.database, `messages/${this.deviceId}/status`);

    // Track processed message IDs to prevent duplicates
    const processedMessageIds = new Set<string>();

    this.statusUnsubscribe = onValue(statusRef, (snapshot) => {
      const statusData = snapshot.val();

      if (statusData) {
        // Sort keys by timestamp
        const sortedKeys = Object.keys(statusData).sort((a, b) => {
          return (statusData[a].timestamp || 0) - (statusData[b].timestamp || 0);
        });

        for (const key of sortedKeys) {
          if (!processedMessageIds.has(key)) {
            processedMessageIds.add(key);
            const status = statusData[key];
            console.log('📱 Status update received:', status);
            this.statusCallback?.(status);
          }
        }
        
        // Cleanup old messages if needed
        if (sortedKeys.length > 10) {
            // Keep last 10
            const oldKeys = sortedKeys.slice(0, sortedKeys.length - 10);
            oldKeys.forEach(async (key) => {
                const oldStatusRef = ref(this.database, `messages/${this.deviceId}/status/${key}`);
                await remove(oldStatusRef);
                processedMessageIds.delete(key);
            });
        }
      }
    });

    return () => {
      if (this.statusUnsubscribe) {
        this.statusUnsubscribe();
        this.statusUnsubscribe = null;
      }
      this.statusCallback = null;
    };
  }

  /**
   * Set paired desktop ID
   */
  setPairedDesktopId(desktopId: string): void {
    this.pairedDesktopId = desktopId;
    console.log(`🔗 Paired desktop ID set: ${desktopId}`);
  }

  /**
   * Clear all messages for this device
   */
  async clearMessages(): Promise<void> {
    if (!this.deviceId) return;

    try {
      const messagesRef = ref(this.database, `messages/${this.deviceId}`);
      await remove(messagesRef);
      console.log('✅ Messages cleared');
    } catch (error) {
      console.error('❌ Failed to clear messages:', error);
    }
  }

  /**
   * Update device presence
   */
  async updatePresence(): Promise<void> {
    await this._updatePresence();
  }

  /**
   * Helper methods for compatibility with aws-migration branch interface
   */
  isAWSConnected(): boolean {
    return this.isConnected;
  }

  getDeviceId(): string | null {
    return this.deviceId;
  }

  getPairedDesktopId(): string | null {
    return this.pairedDesktopId;
  }
}
