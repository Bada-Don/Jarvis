import React, { useState, useEffect } from 'react';
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
    const [progressMessageId, setProgressMessageId] = useState<string | null>(null);

    // Connect to real-time status updates
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
            
            // Update or create progress message
            if (progressMessageId) {
                // Update existing progress message
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === progressMessageId
                            ? {
                                  ...msg,
                                  progress: progress,
                                  progressTitle: message,
                                  progressStatus: status === 'success' || status === 'error' ? status : 'running',
                                  errorMessage: error,
                              }
                            : msg
                    )
                );
            } else {
                // Create new progress message
                const newProgressId = createId();
                setProgressMessageId(newProgressId);
                
                setMessages((prev) => [
                    ...prev,
                    {
                        id: newProgressId,
                        role: 'assistant',
                        content: '',
                        isProgress: true,
                        progress: progress,
                        progressTitle: message,
                        progressStatus: status === 'success' || status === 'error' ? status : 'running',
                    },
                ]);
            }
            
            // Clear progress message ID when complete
            if (status === 'success' || status === 'error') {
                setTimeout(() => setProgressMessageId(null), 3000);
            }
        });

        return cleanup;
    }, [progressMessageId]);

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
