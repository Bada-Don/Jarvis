/**
 * Firebase Service for JARVIS Mobile App
 * Handles real-time messaging, command sending, and status listening
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
  onDisconnect,
  DatabaseReference,
  Unsubscribe,
} from 'firebase/database';

interface Message {
  id: string;
  type: 'command' | 'status' | 'progress' | 'error' | 'completion';
  content: any;
  timestamp: number;
  processed: boolean;
}

interface CommandMessage {
  type: 'command';
  text: string;
  timestamp: number;
  processed: boolean;
}

interface StatusMessage {
  type: 'status' | 'progress' | 'error' | 'completion';
  message: string;
  progress?: number;
  timestamp: number;
}

export class FirebaseService {
  private database: any;
  private deviceId: string | null = null;
  private pairedDesktopId: string | null = null;
  private listeners: Map<string, Unsubscribe> = new Map();
  private reconnectInterval: NodeJS.Timeout | null = null;
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectDelay: number = 1000; // Start with 1 second
  private maxReconnectDelay: number = 30000; // Max 30 seconds

  /**
   * Initialize Firebase Service
   * @param deviceId - Mobile device ID
   * @param pairedDesktopId - Paired desktop device ID (optional)
   */
  constructor(deviceId: string, pairedDesktopId?: string) {
    if (!deviceId) {
      throw new Error('Device ID is required');
    }

    this.deviceId = deviceId;
    this.pairedDesktopId = pairedDesktopId || null;

    console.log('🔥 FirebaseService initialized');
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

      console.log('🔥 Connecting to Firebase...');

      // Sign in anonymously
      await signInAnonymouslyToFirebase();

      // Get database instance
      this.database = getFirebaseDatabase();

      // Set up connection monitoring
      this._setupConnectionMonitoring();

      // Update device presence
      await this._updatePresence();

      // Set up disconnect handler
      this._setupDisconnectHandler();

      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;

      console.log('✅ Connected to Firebase');
    } catch (error) {
      console.error('❌ Failed to connect to Firebase:', error);
      this._scheduleReconnect();
      throw error;
    }
  }

  /**
   * Disconnect from Firebase
   */
  disconnect(): void {
    console.log('🔥 Disconnecting from Firebase...');

    // Remove all listeners
    this.listeners.forEach((unsubscribe, key) => {
      unsubscribe();
      console.log(`   Removed listener: ${key}`);
    });
    this.listeners.clear();

    // Clear reconnect interval
    if (this.reconnectInterval) {
      clearTimeout(this.reconnectInterval);
      this.reconnectInterval = null;
    }

    this.isConnected = false;
    console.log('✅ Disconnected from Firebase');
  }

  /**
   * Set up connection monitoring
   */
  private _setupConnectionMonitoring(): void {
    const connectedRef = ref(this.database, '.info/connected');

    const unsubscribe = onValue(connectedRef, (snapshot) => {
      const connected = snapshot.val();

      if (connected) {
        console.log('✅ Firebase connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      } else {
        console.log('❌ Firebase connection lost');
        this.isConnected = false;
        this._scheduleReconnect();
      }
    });

    this.listeners.set('connection', unsubscribe);
  }

  /**
   * Set up disconnect handler to update presence
   */
  private _setupDisconnectHandler(): void {
    if (!this.deviceId) return;

    const deviceRef = ref(this.database, `devices/${this.deviceId}`);

    onDisconnect(deviceRef).update({
      lastSeen: serverTimestamp(),
      online: false,
    });
  }

  /**
   * Schedule automatic reconnection with exponential backoff
   */
  private _scheduleReconnect(): void {
    if (this.reconnectInterval) {
      return; // Already scheduled
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`🔄 Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);

    this.reconnectInterval = setTimeout(async () => {
      this.reconnectInterval = null;
      try {
        await this.connect();
      } catch (error) {
        console.error('❌ Reconnection failed:', error);
      }
    }, delay);
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

      console.log('✅ Device presence updated');
    } catch (error) {
      console.error('❌ Failed to update presence:', error);
    }
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
      throw new Error('Not connected to Firebase. Please check your connection.');
    }

    try {
      console.log(`📤 Sending command: ${commandText}`);

      // Create command message
      const commandMessage: CommandMessage = {
        type: 'command',
        text: commandText,
        timestamp: Date.now(),
        processed: false,
      };

      // Push to desktop's command queue
      const commandsRef = ref(
        this.database,
        `messages/${this.pairedDesktopId}/commands`
      );
      const newCommandRef = push(commandsRef);
      await set(newCommandRef, commandMessage);

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

    if (!this.isConnected) {
      console.warn('⚠️ Not connected to Firebase. Status updates may be delayed.');
    }

    // Remove existing listener if any to prevent duplicates
    const existingListener = this.listeners.get('status');
    if (existingListener) {
      console.log('⚠️ Removing existing status listener to prevent duplicates');
      existingListener();
      this.listeners.delete('status');
    }

    console.log('👂 Listening for status updates...');

    // Listen to status updates for this mobile device
    const statusRef = ref(this.database, `messages/${this.deviceId}/status`);

    // Track processed message IDs to prevent duplicates
    const processedMessageIds = new Set<string>();

    const unsubscribe = onValue(statusRef, (snapshot) => {
      const statusData = snapshot.val();

      if (statusData) {
        // Sort keys by timestamp chronologically
        const statusKeys = Object.keys(statusData);
        const sortedKeys = statusKeys.sort((a, b) => {
          return (statusData[a].timestamp || 0) - (statusData[b].timestamp || 0);
        });

        let hasNewMessages = false;

        // Process all NEW messages in chronological order
        for (const key of sortedKeys) {
          if (!processedMessageIds.has(key)) {
            processedMessageIds.add(key);
            const status = statusData[key];
            console.log('📱 Status update received:', status);
            callback(status);
            hasNewMessages = true;
          }
        }

        // Only clean up if we got new messages
        if (hasNewMessages && statusKeys.length > 10) {
          const oldKeys = statusKeys.slice(0, statusKeys.length - 10);
          oldKeys.forEach(async (key) => {
            const oldStatusRef = ref(
              this.database,
              `messages/${this.deviceId}/status/${key}`
            );
            await remove(oldStatusRef);
            // Remove from processed set
            processedMessageIds.delete(key);
          });
        }

        // Limit processed IDs set size to prevent memory leak
        if (processedMessageIds.size > 50) {
          const idsArray = Array.from(processedMessageIds);
          const toRemove = idsArray.slice(0, idsArray.length - 50);
          toRemove.forEach(id => processedMessageIds.delete(id));
        }
      }
    });

    this.listeners.set('status', unsubscribe);

    // Return cleanup function
    return () => {
      unsubscribe();
      this.listeners.delete('status');
      console.log('👂 Stopped listening for status updates');
    };
  }

  /**
   * Set paired desktop ID
   * @param desktopId - Desktop device ID
   */
  setPairedDesktopId(desktopId: string): void {
    this.pairedDesktopId = desktopId;
    console.log(`🔗 Paired desktop ID set: ${desktopId}`);
  }

  /**
   * Get paired desktop ID
   * @returns Desktop device ID or null
   */
  getPairedDesktopId(): string | null {
    return this.pairedDesktopId;
  }

  /**
   * Check if connected to Firebase
   * @returns True if connected, false otherwise
   */
  isFirebaseConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Get device ID
   * @returns Device ID
   */
  getDeviceId(): string | null {
    return this.deviceId;
  }

  /**
   * Update device presence periodically
   * Call this method every 30 seconds to keep presence updated
   */
  async updatePresence(): Promise<void> {
    await this._updatePresence();
  }

  /**
   * Clear all messages for this device
   * Useful for cleanup
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
}
