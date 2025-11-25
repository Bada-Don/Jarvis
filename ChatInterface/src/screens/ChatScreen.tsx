import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, StatusBar } from 'react-native';
import { ChatHeader } from '../components/ChatHeader';
import { MessageList } from '../components/MessageList';
import { ChatInput } from '../components/ChatInput';
import { sendMessage, uploadFile, connectToStatusUpdates } from '../services/api';

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
    
    // Use ref to track progress message ID to avoid re-creating the effect
    const progressMessageIdRef = useRef<string | null>(null);
    const clearTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Connect to real-time status updates - only run once on mount
    useEffect(() => {
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
            
            // Clear any pending timeout that would reset the progress ID
            if (clearTimeoutRef.current) {
                clearTimeout(clearTimeoutRef.current);
                clearTimeoutRef.current = null;
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
            
            // Clear progress message ID when complete (after a delay to allow for final display)
            if (status === 'success' || status === 'error') {
                clearTimeoutRef.current = setTimeout(() => {
                    progressMessageIdRef.current = null;
                    clearTimeoutRef.current = null;
                }, 3000);
            }
        });

        return () => {
            cleanup();
            // Clear any pending timeout on unmount
            if (clearTimeoutRef.current) {
                clearTimeout(clearTimeoutRef.current);
            }
        };
    }, []); // Empty dependency array - only run once on mount

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
            // Upload files first
            for (const file of attachments) {
                await uploadFile(file.uri, file.name, file.type);
            }

            // Send message
            if (text) {
                await sendMessage(text);
            }

            // Progress updates will come via WebSocket
            // No need to add a static response message
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

    return (
        <View style={styles.container}>
            <StatusBar barStyle="dark-content" backgroundColor="#fff" />

            <ChatHeader
                title="Jarvis"
                subtitle="Online · Realtime"
            />

            <View style={styles.contentContainer}>
                <MessageList messages={messages} />
            </View>

            <ChatInput
                onSend={handleSend}
                isSending={isSending}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    contentContainer: {
        flex: 1,
        backgroundColor: '#F9FAFB',
    },
});
