import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { FileText } from 'lucide-react-native';

interface Attachment {
    id: string;
    name: string;
    size: number;
    uri: string;
    type: string;
}

interface MessageItemProps {
    message: {
        id: string;
        role: string;
        content: string;
        attachments?: Attachment[];
    };
}

const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
    const isUser = message.role === 'user';

    const renderAttachments = (attachments?: Attachment[]) => {
        if (!attachments || attachments.length === 0) return null;

        return (
            <View style={styles.attachmentsContainer}>
                {attachments.map((att) => (
                    <View key={att.id} style={styles.attachmentItem}>
                        <View style={styles.attachmentIcon}>
                            <FileText size={16} color={isUser ? "#007AFF" : "#fff"} />
                        </View>
                        <View style={styles.attachmentInfo}>
                            <Text style={[styles.attachmentName, isUser ? styles.textUser : styles.textAssistant]} numberOfLines={1}>
                                {att.name}
                            </Text>
                            <Text style={[styles.attachmentSize, isUser ? styles.textUserSecondary : styles.textAssistantSecondary]}>
                                {formatFileSize(att.size)}
                            </Text>
                        </View>
                    </View>
                ))}
            </View>
        );
    };

    return (
        <View style={[styles.container, isUser ? styles.containerUser : styles.containerAssistant]}>
            {!isUser && <View style={styles.avatarAssistant} />}

            <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleAssistant]}>
                {message.content ? (
                    <Text style={[styles.text, isUser ? styles.textUser : styles.textAssistant]}>
                        {message.content}
                    </Text>
                ) : null}
                {renderAttachments(message.attachments)}
            </View>

            {isUser && <View style={styles.avatarUser} />}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        marginBottom: 12,
        width: '100%',
        gap: 8,
    },
    containerUser: {
        justifyContent: 'flex-end',
    },
    containerAssistant: {
        justifyContent: 'flex-start',
    },
    avatarAssistant: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: '#E0E0E0',
        marginTop: 4,
    },
    avatarUser: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: '#007AFF',
        marginTop: 4,
    },
    bubble: {
        maxWidth: '75%',
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
    },
    bubbleUser: {
        backgroundColor: '#007AFF',
        borderBottomRightRadius: 4,
    },
    bubbleAssistant: {
        backgroundColor: '#F3F4F6',
        borderTopLeftRadius: 4,
    },
    text: {
        fontSize: 15,
        lineHeight: 22,
    },
    textUser: {
        color: '#fff',
    },
    textUserSecondary: {
        color: 'rgba(255, 255, 255, 0.7)',
    },
    textAssistant: {
        color: '#1F2937',
    },
    textAssistantSecondary: {
        color: '#6B7280',
    },
    attachmentsContainer: {
        marginTop: 8,
        gap: 8,
    },
    attachmentItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        backgroundColor: 'rgba(255,255,255,0.2)',
        padding: 8,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
    },
    attachmentIcon: {
        width: 32,
        height: 32,
        borderRadius: 16,
        backgroundColor: 'rgba(255,255,255,0.9)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    attachmentInfo: {
        flex: 1,
    },
    attachmentName: {
        fontSize: 13,
        fontWeight: '500',
    },
    attachmentSize: {
        fontSize: 11,
    },
});
