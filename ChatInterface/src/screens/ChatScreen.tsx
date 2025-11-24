import React, { useState, useRef, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    FlatList,
    StyleSheet,
    SafeAreaView,
    StatusBar,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
} from 'react-native';
import { Paperclip, Send, FileText, Loader2 } from 'lucide-react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as DocumentPicker from 'expo-document-picker';
import { sendMessage, uploadFile } from '../services/api';

const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};

const createId = () => Math.random().toString(36).slice(2);

export default function ChatScreen() {
    const [messages, setMessages] = useState([
        {
            id: createId(),
            role: 'assistant',
            content: 'Hi, I am your AI assistant. Upload files and send me a message to get started.',
        },
    ]);

    const [input, setInput] = useState('');
    const [pendingFiles, setPendingFiles] = useState([]);
    const [isSending, setIsSending] = useState(false);
    const flatListRef = useRef(null);

    useEffect(() => {
        if (flatListRef.current && messages.length > 0) {
            setTimeout(() => {
                flatListRef.current.scrollToEnd({ animated: true });
            }, 100);
        }
    }, [messages]);

    const handleFilePick = async () => {
        try {
            const result = await DocumentPicker.getDocumentAsync({
                type: '*/*',
                copyToCacheDirectory: true,
                multiple: true
            });

            if (!result.canceled && result.assets) {
                setPendingFiles((prev) => [...prev, ...result.assets]);
            }
        } catch (err) {
            console.error('Error picking file:', err);
        }
    };

    const removePendingFile = (index) => {
        setPendingFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSend = async () => {
        const trimmed = input.trim();
        if (!trimmed && pendingFiles.length === 0) return;

        setIsSending(true);

        const attachments = pendingFiles.map((file) => ({
            id: createId(),
            name: file.name,
            size: file.size,
            uri: file.uri,
            type: file.mimeType,
        }));

        const userMessage = {
            id: createId(),
            role: 'user',
            content: trimmed,
            attachments,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setPendingFiles([]);

        try {
            // Upload files first
            for (const file of attachments) {
                await uploadFile(file.uri, file.name, file.type);
            }

            // Send message
            if (trimmed) {
                await sendMessage(trimmed);
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

    const renderAttachments = (attachments) => {
        if (!attachments || attachments.length === 0) return null;

        return (
            <View style={styles.attachmentsContainer}>
                {attachments.map((att) => (
                    <View key={att.id} style={styles.attachmentItem}>
                        <View style={styles.attachmentIcon}>
                            <FileText size={16} color="#fff" />
                        </View>
                        <View style={styles.attachmentInfo}>
                            <Text style={styles.attachmentName} numberOfLines={1}>
                                {att.name}
                            </Text>
                            <Text style={styles.attachmentSize}>{formatFileSize(att.size)}</Text>
                        </View>
                    </View>
                ))}
            </View>
        );
    };

    const renderMessage = ({ item }) => {
        const isUser = item.role === 'user';

        return (
            <View style={[styles.messageRow, isUser ? styles.messageRowUser : styles.messageRowAssistant]}>
                {!isUser && <View style={styles.avatarAssistant} />}

                <View style={[styles.messageBubble, isUser ? styles.messageBubbleUser : styles.messageBubbleAssistant]}>
                    {item.content ? <Text style={isUser ? styles.messageTextUser : styles.messageTextAssistant}>{item.content}</Text> : null}
                    {renderAttachments(item.attachments)}
                </View>

                {isUser && <View style={styles.avatarUser} />}
            </View>
        );
    };

    return (
        <LinearGradient colors={['#f1f5f9', '#e2e8f0']} style={styles.container}>
            <SafeAreaView style={styles.safeArea}>
                <StatusBar barStyle="dark-content" />

                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.headerLeft}>
                        <View style={styles.headerAvatar} />
                        <View>
                            <Text style={styles.headerTitle}>Aurora AI</Text>
                            <Text style={styles.headerSubtitle}>Online · Realtime</Text>
                        </View>
                    </View>
                </View>

                {/* Messages */}
                <FlatList
                    ref={flatListRef}
                    data={messages}
                    renderItem={renderMessage}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={styles.messagesList}
                    showsVerticalScrollIndicator={false}
                />

                {/* Pending Files */}
                {pendingFiles.length > 0 && (
                    <View style={styles.pendingFilesContainer}>
                        {pendingFiles.map((file, index) => (
                            <View key={index} style={styles.pendingFileItem}>
                                <FileText size={12} color="#fff" />
                                <Text style={styles.pendingFileName} numberOfLines={1}>{file.name}</Text>
                                <TouchableOpacity onPress={() => removePendingFile(index)}>
                                    <Text style={styles.removeFileText}>×</Text>
                                </TouchableOpacity>
                            </View>
                        ))}
                    </View>
                )}

                {/* Input Area */}
                <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
                    <View style={styles.inputContainer}>
                        <TouchableOpacity onPress={handleFilePick} style={styles.attachButton}>
                            <Paperclip size={20} color="#64748b" />
                        </TouchableOpacity>

                        <TextInput
                            style={styles.input}
                            placeholder="Send a message..."
                            placeholderTextColor="#94a3b8"
                            value={input}
                            onChangeText={setInput}
                            multiline
                        />

                        <TouchableOpacity
                            onPress={handleSend}
                            disabled={isSending || (!input.trim() && pendingFiles.length === 0)}
                            style={[styles.sendButton, (isSending || (!input.trim() && pendingFiles.length === 0)) && styles.sendButtonDisabled]}
                        >
                            {isSending ? <ActivityIndicator size="small" color="#fff" /> : <Send size={18} color="#fff" />}
                        </TouchableOpacity>
                    </View>
                </KeyboardAvoidingView>
            </SafeAreaView>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    safeArea: {
        flex: 1,
    },
    header: {
        paddingHorizontal: 16,
        paddingVertical: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'transparent',
    },
    headerLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    headerAvatar: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: '#fff',
        opacity: 0.9,
    },
    headerTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: '#1e293b',
    },
    headerSubtitle: {
        fontSize: 12,
        color: '#10b981',
    },
    messagesList: {
        padding: 16,
        gap: 12,
    },
    messageRow: {
        flexDirection: 'row',
        gap: 8,
        marginBottom: 12,
        width: '100%',
    },
    messageRowUser: {
        justifyContent: 'flex-end',
    },
    messageRowAssistant: {
        justifyContent: 'flex-start',
    },
    avatarAssistant: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: 'rgba(255,255,255,0.5)',
        marginTop: 4,
    },
    avatarUser: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: '#fff',
        marginTop: 4,
    },
    messageBubble: {
        maxWidth: '80%',
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 2,
    },
    messageBubbleUser: {
        backgroundColor: '#fff',
        borderBottomRightRadius: 4,
    },
    messageBubbleAssistant: {
        backgroundColor: '#7b5cff',
        borderTopLeftRadius: 4,
    },
    messageTextUser: {
        color: '#0f172a',
        fontSize: 14,
        lineHeight: 20,
    },
    messageTextAssistant: {
        color: '#fff',
        fontSize: 14,
        lineHeight: 20,
    },
    attachmentsContainer: {
        marginTop: 8,
        gap: 8,
    },
    attachmentItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        backgroundColor: 'rgba(255,255,255,0.15)',
        padding: 8,
        borderRadius: 12,
    },
    attachmentIcon: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: 'rgba(255,255,255,0.2)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    attachmentInfo: {
        flex: 1,
    },
    attachmentName: {
        color: 'rgba(255,255,255,0.9)',
        fontSize: 12,
        fontWeight: '500',
    },
    attachmentSize: {
        color: 'rgba(255,255,255,0.7)',
        fontSize: 10,
    },
    pendingFilesContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        paddingHorizontal: 16,
        marginBottom: 8,
    },
    pendingFileItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
        backgroundColor: '#7b5cff',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 12,
    },
    pendingFileName: {
        color: '#fff',
        fontSize: 11,
        maxWidth: 100,
    },
    removeFileText: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 14,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        padding: 12,
        backgroundColor: '#fff',
        margin: 16,
        marginTop: 0,
        borderRadius: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 4,
    },
    attachButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: '#f1f5f9',
        alignItems: 'center',
        justifyContent: 'center',
    },
    input: {
        flex: 1,
        maxHeight: 100,
        paddingVertical: 8,
        paddingHorizontal: 4,
        fontSize: 14,
        color: '#0f172a',
    },
    sendButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: '#7b5cff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    sendButtonDisabled: {
        backgroundColor: '#cbd5e1',
    },
});
