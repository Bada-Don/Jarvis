import React, { useState } from 'react';
import { View, StyleSheet, StatusBar } from 'react-native';
import { ChatHeader } from '../components/ChatHeader';
import { MessageList } from '../components/MessageList';
import { ChatInput } from '../components/ChatInput';
import { sendMessage, uploadFile } from '../services/api';

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

            // Simulate response (or get real response if backend supported it)
            const assistantId = createId();
            setMessages((prev) => [
                ...prev,
                {
                    id: assistantId,
                    role: 'assistant',
                    content: 'Message received and logged.',
                },
            ]);
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
