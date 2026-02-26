import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, StatusBar, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { ChatHeader } from '../components/ChatHeader';
import { MessageList } from '../components/MessageList';
import { ChatInput } from '../components/ChatInput';
import { PermissionModal } from '../components/PermissionModal';
import { AbortButton } from '../components/AbortButton';
import { PairingScreen } from './PairingScreen';
import { 
    sendMessage, 
    uploadFile, 
    connectToStatusUpdates,
    connectToPermissionRequests,
    sendPermissionResponse,
    abortTask,
    PermissionRequest,
} from '../services/api';
import { FirebaseService } from '../services/FirebaseService';
import { PairingManager } from '../services/PairingManager';
import { isFirebaseConfigured } from '../config/firebase';

const createId = () => Math.random().toString(36).slice(2);

export default function ChatScreen() {
    const [messages, setMessages] = useState([
        {
            id: createId(),
            role: 'assistant',
            content: 'Hi, I am your AI assistant. Upload files and send me a message to get started.',
        },
    ]);

    const [isSending, setIsSending] = useState(false);
    const [isTaskRunning, setIsTaskRunning] = useState(false);
    const [permissionRequest, setPermissionRequest] = useState<PermissionRequest | null>(null);
    const [showPairingScreen, setShowPairingScreen] = useState(false);
    const [isPaired, setIsPaired] = useState(false);
    const [useFirebase, setUseFirebase] = useState(false);
    
    // Firebase and Pairing services
    const firebaseServiceRef = useRef<FirebaseService | null>(null);
    const pairingManagerRef = useRef<PairingManager | null>(null);
    
    // Use ref to track progress message ID to avoid re-creating the effect
    const progressMessageIdRef = useRef<string | null>(null);
    const clearTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Initialize Firebase and Pairing on mount
    useEffect(() => {
        initializeServices();
    }, []);

    const initializeServices = async () => {
        try {
            // Check if Firebase is configured
            const firebaseConfigured = isFirebaseConfigured();
            
            if (firebaseConfigured) {
                console.log('🔥 Firebase is configured, initializing services...');
                
                // Initialize PairingManager
                const pairingManager = new PairingManager();
                pairingManagerRef.current = pairingManager;
                
                // Check if already paired
                const paired = await pairingManager.isPaired();
                setIsPaired(paired);
                
                if (paired) {
                    // Get paired desktop ID
                    const desktopId = await pairingManager.getPairedDesktopId();
                    
                    if (desktopId) {
                        // Get device ID
                        const deviceId = await pairingManager.getDeviceId();
                        
                        if (deviceId) {
                            // Clean up existing Firebase service if any
                            if (firebaseServiceRef.current) {
                                firebaseServiceRef.current.disconnect();
                            }
                            
                            // Initialize Firebase service
                            const firebaseService = new FirebaseService(deviceId, desktopId);
                            firebaseServiceRef.current = firebaseService;
                            
                            // Connect to Firebase
                            await firebaseService.connect();
                            
                            // Clear old status messages to prevent showing stale errors
                            await firebaseService.clearMessages();
                            console.log('🧹 Cleared old status messages');
                            
                            // Set up status listener (this will remove any existing listener)
                            firebaseService.listenForStatus(handleFirebaseStatus);
                            
                            setUseFirebase(true);
                            console.log('✅ Firebase messaging enabled');
                        }
                    }
                } else {
                    console.log('⚠️ Device not paired. Showing pairing screen...');
                    setShowPairingScreen(true);
                }
            } else {
                console.log('⚠️ Firebase not configured. Using WebSocket only.');
                setUseFirebase(false);
            }
        } catch (error) {
            console.error('❌ Failed to initialize services:', error);
            Alert.alert(
                'Initialization Error',
                'Failed to initialize Firebase services. Using local connection only.'
            );
        }
    };

    const handleFirebaseStatus = (status: any) => {
        console.log('📱 Firebase status update:', status);
        
        // Extract progress info
        const progress = status.progress;
        const message = status.message;
        const statusType = status.status || status.type;
        
        // Update task running state
        if (progress !== undefined) {
            if (progress > 0 && progress < 100 && statusType !== 'success' && statusType !== 'error') {
                setIsTaskRunning(true);
            } else if (statusType === 'success' || statusType === 'error' || progress >= 100) {
                setIsTaskRunning(false);
            }
        }
        
        // Determine the final status
        const progressStatus = statusType === 'success' ? 'success' : statusType === 'error' ? 'error' : 'running';
        
        // Check if we have an existing progress message to update
        if (progressMessageIdRef.current) {
            // Update existing progress message
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === progressMessageIdRef.current
                        ? {
                              ...msg,
                              progress: progress,
                              progressTitle: message,
                              progressStatus: progressStatus,
                          }
                        : msg
                )
            );
        } else {
            // Create new progress message
            const newProgressId = createId();
            progressMessageIdRef.current = newProgressId;
            
            setMessages((prev) => [
                ...prev,
                {
                    id: newProgressId,
                    role: 'assistant',
                    content: '',
                    isProgress: true,
                    progress: progress,
                    progressTitle: message,
                    progressStatus: progressStatus,
                },
            ]);
        }
        
        // Only clear progress message ID when task is truly complete
        // Don't clear immediately to prevent creating duplicate progress cards
        if ((statusType === 'success' || statusType === 'error') && progress >= 100) {
            // Clear any existing timeout
            if (clearTimeoutRef.current) {
                clearTimeout(clearTimeoutRef.current);
            }
            // Set a longer delay to ensure no more updates arrive
            clearTimeoutRef.current = setTimeout(() => {
                progressMessageIdRef.current = null;
                clearTimeoutRef.current = null;
            }, 5000); // Increased from 3000 to 5000ms
        }
    };

    // Connect to WebSocket status updates (fallback)
    useEffect(() => {
        if (useFirebase) {
            // Skip WebSocket if using Firebase
            return;
        }
        
        const cleanup = connectToStatusUpdates((statusData) => {
            console.log('Status update received:', statusData);
            
            // Parse the data - handle nested message structure
            let progressData = statusData;
            
            // If message is an object with progress data, use that
            if (typeof statusData.message === 'object' && statusData.message.progress !== undefined) {
                progressData = statusData.message;
            }
            
            // Extract progress info
            const progress = progressData.progress;
            const message = progressData.message || statusData.message;
            const status = progressData.status || statusData.type;
            const error = progressData.error;
            
            // Only handle progress updates (not regular status messages)
            if (progress === undefined) {
                return;
            }
            
            // Update task running state based on progress
            if (progress > 0 && progress < 100 && status !== 'success' && status !== 'error') {
                setIsTaskRunning(true);
            } else if (status === 'success' || status === 'error' || progress >= 100) {
                setIsTaskRunning(false);
            }
            
            // Determine the final status
            const progressStatus = status === 'success' || status === 'error' ? status : 'running';
            
            // Check if we have an existing progress message to update
            if (progressMessageIdRef.current) {
                // Update existing progress message in-place
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === progressMessageIdRef.current
                            ? {
                                  ...msg,
                                  progress: progress,
                                  progressTitle: message,
                                  progressStatus: progressStatus,
                                  errorMessage: error,
                              }
                            : msg
                    )
                );
            } else {
                // Create new progress message
                const newProgressId = createId();
                progressMessageIdRef.current = newProgressId;
                
                setMessages((prev) => [
                    ...prev,
                    {
                        id: newProgressId,
                        role: 'assistant',
                        content: '',
                        isProgress: true,
                        progress: progress,
                        progressTitle: message,
                        progressStatus: progressStatus,
                        errorMessage: error,
                    },
                ]);
            }
            
            // Only clear progress message ID when task is truly complete
            // Don't clear immediately to prevent creating duplicate progress cards
            if ((status === 'success' || status === 'error') && progress >= 100) {
                // Clear any existing timeout
                if (clearTimeoutRef.current) {
                    clearTimeout(clearTimeoutRef.current);
                }
                // Set a longer delay to ensure no more updates arrive
                clearTimeoutRef.current = setTimeout(() => {
                    progressMessageIdRef.current = null;
                    clearTimeoutRef.current = null;
                }, 5000); // Increased from 3000 to 5000ms
            }
        });

        return () => {
            cleanup();
            // Clear any pending timeout on unmount
            if (clearTimeoutRef.current) {
                clearTimeout(clearTimeoutRef.current);
            }
        };
    }, [useFirebase]);

    // Connect to permission requests
    useEffect(() => {
        const cleanup = connectToPermissionRequests((request) => {
            setPermissionRequest(request);
        });

        return cleanup;
    }, []);

    // Cleanup Firebase on unmount
    useEffect(() => {
        return () => {
            if (firebaseServiceRef.current) {
                firebaseServiceRef.current.disconnect();
            }
        };
    }, []);

    const handlePairingComplete = async () => {
        setShowPairingScreen(false);
        setIsPaired(true);
        
        // Reinitialize services after pairing
        await initializeServices();
        
        Alert.alert(
            'Pairing Complete',
            'Your device is now paired with the desktop application. You can now send commands remotely!'
        );
    };

    const handlePermissionApprove = () => {
        if (permissionRequest) {
            sendPermissionResponse(permissionRequest.requestId, true);
            setPermissionRequest(null);
        }
    };

    const handlePermissionDeny = () => {
        if (permissionRequest) {
            sendPermissionResponse(permissionRequest.requestId, false);
            setPermissionRequest(null);
        }
    };

    const handleAbortTask = () => {
        abortTask();
        setIsTaskRunning(false);
        
        // Add abort message to chat
        setMessages((prev) => [
            ...prev,
            {
                id: createId(),
                role: 'assistant',
                content: '🛑 Task aborted by user.',
            },
        ]);
    };

    const handleUnpair = async () => {
        try {
            // Disconnect Firebase
            if (firebaseServiceRef.current) {
                firebaseServiceRef.current.disconnect();
                firebaseServiceRef.current = null;
            }

            // Unpair device
            if (pairingManagerRef.current) {
                await pairingManagerRef.current.unpair();
            }

            // Reset state
            setIsPaired(false);
            setUseFirebase(false);
            setShowPairingScreen(true);

            Alert.alert(
                'Device Unpaired',
                'Your device has been unpaired. You can pair again by scanning a QR code.'
            );
        } catch (error) {
            console.error('❌ Failed to unpair:', error);
            Alert.alert(
                'Unpair Failed',
                'Failed to unpair device. Please try again.'
            );
        }
    };

    const handleSend = async (text: string, files: any[]) => {
        setIsSending(true);

        const attachments = files.map((file) => ({
            id: createId(),
            name: file.name || file.fileName || `image_${Date.now()}.jpg`,
            size: file.size || file.fileSize || 0,
            uri: file.uri,
            type: file.mimeType || file.type || 'image/jpeg',
        }));

        const userMessage = {
            id: createId(),
            role: 'user',
            content: text,
            attachments,
        };

        setMessages((prev) => [...prev, userMessage]);

        try {
            // Upload files first (always use WebSocket for file uploads)
            for (const file of attachments) {
                await uploadFile(file.uri, file.name, file.type);
            }

            // Send message via Firebase or WebSocket
            if (text) {
                if (useFirebase && firebaseServiceRef.current) {
                    // Send via Firebase
                    await firebaseServiceRef.current.sendCommand(text);
                    console.log('✅ Command sent via Firebase');
                } else {
                    // Send via WebSocket
                    await sendMessage(text);
                    console.log('✅ Message sent via WebSocket');
                }
            }

            // Progress updates will come via Firebase or WebSocket
        } catch (error) {
            console.error('Error in handleSend:', error);
            setMessages((prev) => [
                ...prev,
                {
                    id: createId(),
                    role: 'assistant',
                    content: 'Error sending message or file.',
                },
            ]);
        } finally {
            setIsSending(false);
        }
    };

    // Show pairing screen if not paired and Firebase is configured
    if (showPairingScreen && pairingManagerRef.current) {
        return (
            <PairingScreen
                pairingManager={pairingManagerRef.current}
                onPairingComplete={handlePairingComplete}
                onCancel={() => {
                    setShowPairingScreen(false);
                    // Continue with WebSocket only
                    setUseFirebase(false);
                }}
            />
        );
    }

    return (
        <KeyboardAvoidingView 
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
        >
            <StatusBar barStyle="light-content" backgroundColor="#0a0a0a" />

            <ChatHeader
                title="Jarvis"
                subtitle={useFirebase ? 'Online · Firebase' : 'Online · Local'}
                onUnpair={isPaired ? handleUnpair : undefined}
            />

            <View style={styles.contentContainer}>
                <MessageList messages={messages} />
            </View>

            <AbortButton 
                visible={isTaskRunning} 
                onAbort={handleAbortTask} 
            />

            <ChatInput
                onSend={handleSend}
                isSending={isSending}
            />

            <PermissionModal
                visible={permissionRequest !== null}
                operation={permissionRequest?.operation || ''}
                details={permissionRequest?.details || ''}
                onApprove={handlePermissionApprove}
                onDeny={handlePermissionDeny}
            />
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0a0a0a',
    },
    contentContainer: {
        flex: 1,
        backgroundColor: '#0a0a0a',
    },
});
