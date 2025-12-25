import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { FileText } from 'lucide-react-native';
import { ProgressCard } from './ProgressCard';
import JarvisLogo from './JarvisLogo';

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
        isProgress?: boolean;
        progress?: number;
        progressTitle?: string;
        progressStatus?: 'running' | 'success' | 'error';
        errorMessage?: string;
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

    // Render progress card for progress messages
    if (message.isProgress) {
        return (
            <View style={[styles.container, styles.containerAssistant]}>
                <View style={styles.avatarAssistant}>
                    <JarvisLogo style={styles.logo} />
                </View>
                <View style={{ maxWidth: '75%', flex: 1 }}>
                    <ProgressCard
                        title={message.progressTitle || 'Processing...'}
                        progress={message.progress || 0}
                        status={message.progressStatus || 'running'}
                        errorMessage={message.errorMessage}
                    />
                </View>
            </View>
        );
    }

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
            {!isUser && (
                <View style={styles.avatarAssistant}>
                    <JarvisLogo style={styles.logo} />
                </View>
            )}

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
        backgroundColor: '#18181b',
        marginTop: 4,
        alignItems: 'center',
        justifyContent: 'center',
    },
    logo: {
        width: 20,
        height: 20,
        color: '#16e2d7',
    },
    avatarUser: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: '#16e2d7',
        marginTop: 4,
    },
    bubble: {
        maxWidth: '75%',
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 12,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08,
        shadowRadius: 8,
        elevation: 2,
    },
    bubbleUser: {
        backgroundColor: '#16e2d7',
        borderBottomRightRadius: 4,
    },
    bubbleAssistant: {
        backgroundColor: '#18181b',
        borderTopLeftRadius: 4,
    },
    text: {
        fontSize: 15,
        lineHeight: 22,
    },
    textUser: {
        color: '#022726',
    },
    textUserSecondary: {
        color: 'rgba(2, 39, 38, 0.7)',
    },
    textAssistant: {
        color: '#fafafa',
    },
    textAssistantSecondary: {
        color: '#a1a1aa',
    },
    attachmentsContainer: {
        marginTop: 8,
        gap: 8,
    },
    attachmentItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        backgroundColor: 'rgba(0,0,0,0.2)',
        padding: 8,
        borderRadius: 12,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
    },
    attachmentIcon: {
        width: 32,
        height: 32,
        borderRadius: 12,
        backgroundColor: 'rgba(255,255,255,0.1)',
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
