/**
 * AWS Service for JARVIS Mobile App
 * Handles real-time messaging, command sending, and status listening via AWS DynamoDB
 * Replaces FirebaseService for AWS-only architecture
 */

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  PutCommand,
  QueryCommand,
  UpdateCommand,
  DeleteCommand,
} from '@aws-sdk/lib-dynamodb';

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

export class AWSService {
  private client: DynamoDBClient;
  private docClient: DynamoDBDocumentClient;
  private deviceId: string | null = null;
  private pairedDesktopId: string | null = null;
  private tableName: string;
  private pollingInterval: NodeJS.Timeout | null = null;
  private isConnected: boolean = false;
  private lastStatusTimestamp: number = 0;
  private statusCallback: ((status: StatusMessage) => void) | null = null;

  /**
   * Initialize AWS Service
   * @param deviceId - Mobile device ID
   * @param pairedDesktopId - Paired desktop device ID (optional)
   * @param config - AWS configuration
   */
  constructor(
    deviceId: string,
    pairedDesktopId?: string,
    config?: {
      region?: string;
      accessKeyId?: string;
      secretAccessKey?: string;
      tableName?: string;
    }
  ) {
    if (!deviceId) {
      throw new Error('Device ID is required');
    }

    this.deviceId = deviceId;
    this.pairedDesktopId = pairedDesktopId || null;
    this.tableName = config?.tableName || 'JarvisState';

    // Initialize AWS DynamoDB client
    this.client = new DynamoDBClient({
      region: config?.region || 'us-east-1',
      credentials: config?.accessKeyId && config?.secretAccessKey
        ? {
          accessKeyId: config.accessKeyId,
          secretAccessKey: config.secretAccessKey,
        }
        : undefined, // Use default credentials if not provided
    });

    this.docClient = DynamoDBDocumentClient.from(this.client);

    console.log('☁️ AWSService initialized');
    console.log(`   Device ID: ${deviceId}`);
    console.log(`   Region: ${config?.region || 'us-east-1'}`);
    console.log(`   Table: ${this.tableName}`);
    if (pairedDesktopId) {
      console.log(`   Paired Desktop ID: ${pairedDesktopId}`);
    }
  }

  /**
   * Connect to AWS and register device
   */
  async connect(): Promise<void> {
    try {
      console.log('☁️ Connecting to AWS...');

      // Register device in DynamoDB
      await this._registerDevice();

      this.isConnected = true;

      console.log('✅ Connected to AWS');
    } catch (error) {
      console.error('❌ Failed to connect to AWS:', error);
      throw error;
    }
  }

  /**
   * Disconnect from AWS
   */
  disconnect(): void {
    console.log('☁️ Disconnecting from AWS...');

    // Stop polling
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }

    this.isConnected = false;
    console.log('✅ Disconnected from AWS');
  }

  /**
   * Register device in DynamoDB
   */
  private async _registerDevice(): Promise<void> {
    if (!this.deviceId) return;

    try {
      const timestamp = Date.now();

      await this.docClient.send(
        new PutCommand({
          TableName: this.tableName,
          Item: {
            PK: `DEVICE#${this.deviceId}`,
            SK: 'METADATA',
            type: 'mobile',
            lastSeen: timestamp,
            online: true,
            pairedDesktopId: this.pairedDesktopId,
            registeredAt: timestamp,
          },
        })
      );

      console.log('✅ Device registered in AWS');
    } catch (error) {
      console.error('❌ Failed to register device:', error);
      throw error;
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
      throw new Error('Not connected to AWS. Please check your connection.');
    }

    try {
      console.log(`📤 Sending command: ${commandText}`);

      const messageId = `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const timestamp = Date.now();

      // Create command message in DynamoDB
      await this.docClient.send(
        new PutCommand({
          TableName: this.tableName,
          Item: {
            PK: `DEVICE#${this.pairedDesktopId}`,
            SK: `COMMAND#${timestamp}#${messageId}`,
            messageId,
            type: 'command',
            text: commandText,
            timestamp,
            processed: false,
            ttl: Math.floor(Date.now() / 1000) + 3600, // 1 hour TTL
          },
        })
      );

      console.log(`✅ Command sent with ID: ${messageId}`);
      // Don't log "Command sent via AWS" here - already logged in ChatScreen

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
      console.warn('⚠️ Not connected to AWS. Status updates may be delayed.');
    }

    console.log('👂 Listening for status updates...');

    this.statusCallback = callback;

    // Poll for status updates every 1 second (was 2s) for better responsiveness
    this.pollingInterval = setInterval(async () => {
      await this._pollStatusUpdates();
    }, 1000);

    // Do an immediate poll
    this._pollStatusUpdates();

    console.log('✅ AWS messaging enabled');

    // Return cleanup function
    return () => {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
      this.statusCallback = null;
      console.log('👂 Stopped listening for status updates');
    };
  }

  /**
   * Poll for new status updates from DynamoDB
   */
  private async _pollStatusUpdates(): Promise<void> {
    if (!this.deviceId || !this.statusCallback) return;

    try {
      // Query for status messages newer than last timestamp
      const result = await this.docClient.send(
        new QueryCommand({
          TableName: this.tableName,
          KeyConditionExpression: 'PK = :pk AND SK > :sk',
          ExpressionAttributeValues: {
            ':pk': `DEVICE#${this.deviceId}`,
            ':sk': `STATUS#${this.lastStatusTimestamp}`,
          },
          ScanIndexForward: true, // Sort by timestamp ascending
          Limit: 50,
        })
      );

      if (result.Items && result.Items.length > 0) {
        // Track processed items to avoid duplicates
        const processedItems = new Set<string>();

        // Process each status update
        for (const item of result.Items) {
          // Create unique key for deduplication (timestamp + message + progress)
          const uniqueKey = `${item.timestamp}_${item.message || item.text || ''}_${item.progress || 'none'}`;

          // Skip if already processed in this batch
          if (processedItems.has(uniqueKey)) {
            console.log('⏭️ Skipping duplicate status');
            continue;
          }

          processedItems.add(uniqueKey);

          const status: StatusMessage = {
            type: item.type || 'status',
            message: item.message || item.text || '',
            progress: item.progress,
            timestamp: item.timestamp,
          };

          // Only log once per unique status (moved AFTER deduplication)
          console.log('📱 Status update received:', status);
          this.statusCallback(status);

          // Update last timestamp
          if (item.timestamp > this.lastStatusTimestamp) {
            this.lastStatusTimestamp = item.timestamp;
          }
        }

        // Clean up old status messages (keep last 10)
        if (result.Items.length > 10) {
          await this._cleanupOldStatus(result.Items.slice(0, result.Items.length - 10));
        }
      }
    } catch (error) {
      console.error('❌ Failed to poll status updates:', error);
    }
  }

  /**
   * Clean up old status messages
   */
  private async _cleanupOldStatus(items: any[]): Promise<void> {
    if (!this.deviceId) return;

    try {
      console.log('🧹 Clearing old status messages');

      for (const item of items) {
        await this.docClient.send(
          new DeleteCommand({
            TableName: this.tableName,
            Key: {
              PK: item.PK,
              SK: item.SK,
            },
          })
        );
      }

      console.log('✅ Old status messages cleared');
    } catch (error) {
      console.error('❌ Failed to cleanup old status:', error);
    }
  }

  /**
   * Set paired desktop ID
   * @param desktopId - Desktop device ID
   */
  setPairedDesktopId(desktopId: string): void {
    this.pairedDesktopId = desktopId;
    console.log(`🔗 Paired desktop ID set: ${desktopId}`);

    // Update device metadata
    if (this.isConnected) {
      this._updateDeviceMetadata();
    }
  }

  /**
   * Update device metadata in DynamoDB
   */
  private async _updateDeviceMetadata(): Promise<void> {
    if (!this.deviceId) return;

    try {
      await this.docClient.send(
        new UpdateCommand({
          TableName: this.tableName,
          Key: {
            PK: `DEVICE#${this.deviceId}`,
            SK: 'METADATA',
          },
          UpdateExpression: 'SET pairedDesktopId = :desktopId, lastSeen = :timestamp',
          ExpressionAttributeValues: {
            ':desktopId': this.pairedDesktopId,
            ':timestamp': Date.now(),
          },
        })
      );
    } catch (error) {
      console.error('❌ Failed to update device metadata:', error);
    }
  }

  /**
   * Get paired desktop ID
   * @returns Desktop device ID or null
   */
  getPairedDesktopId(): string | null {
    return this.pairedDesktopId;
  }

  /**
   * Check if connected to AWS
   * @returns True if connected, false otherwise
   */
  isAWSConnected(): boolean {
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
    if (!this.deviceId) return;

    try {
      await this.docClient.send(
        new UpdateCommand({
          TableName: this.tableName,
          Key: {
            PK: `DEVICE#${this.deviceId}`,
            SK: 'METADATA',
          },
          UpdateExpression: 'SET lastSeen = :timestamp, online = :online',
          ExpressionAttributeValues: {
            ':timestamp': Date.now(),
            ':online': true,
          },
        })
      );
    } catch (error) {
      console.error('❌ Failed to update presence:', error);
    }
  }

  /**
   * Clear all messages for this device
   * Useful for cleanup
   */
  async clearMessages(): Promise<void> {
    if (!this.deviceId) return;

    try {
      // Query all messages for this device
      const result = await this.docClient.send(
        new QueryCommand({
          TableName: this.tableName,
          KeyConditionExpression: 'PK = :pk',
          ExpressionAttributeValues: {
            ':pk': `DEVICE#${this.deviceId}`,
          },
        })
      );

      if (result.Items) {
        // Delete each message
        for (const item of result.Items) {
          if (item.SK !== 'METADATA') {
            // Don't delete device metadata
            await this.docClient.send(
              new DeleteCommand({
                TableName: this.tableName,
                Key: {
                  PK: item.PK,
                  SK: item.SK,
                },
              })
            );
          }
        }
      }

      console.log('✅ Messages cleared');
    } catch (error) {
      console.error('❌ Failed to clear messages:', error);
    }
  }
}
