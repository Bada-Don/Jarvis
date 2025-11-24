import React, { useState, useRef } from 'react';
import {
    View,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    Text,
    Platform,
    KeyboardAvoidingView
} from 'react-native';
import { Paperclip, Send, FileText, X } from 'lucide-react-native';
import * as DocumentPicker from 'expo-document-picker';

interface ChatInputProps {
    onSend: (text: string, files: any[]) => void;
    isSending: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isSending }) => {
    const [input, setInput] = useState('');
    const [pendingFiles, setPendingFiles] = useState<any[]>([]);
    const inputRef = useRef<TextInput>(null);

    const handleFilePick = async () => {
        try {
            if (inputRef.current) {
                inputRef.current.blur();
            }

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

    const removePendingFile = (index: number) => {
        setPendingFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const handleSendPress = () => {
        const trimmed = input.trim();
        if (!trimmed && pendingFiles.length === 0) return;

        onSend(trimmed, pendingFiles);
        setInput('');
        setPendingFiles([]);
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
            style={styles.container}
        >
            {pendingFiles.length > 0 && (
                <View style={styles.pendingFilesContainer}>
                    {pendingFiles.map((file, index) => (
                        <View key={index} style={styles.pendingFileItem}>
                            <FileText size={12} color="#007AFF" />
                            <Text style={styles.pendingFileName} numberOfLines={1}>{file.name}</Text>
                            <TouchableOpacity onPress={() => removePendingFile(index)} style={styles.removeFileButton}>
                                <X size={12} color="#6B7280" />
                            </TouchableOpacity>
                        </View>
                    ))}
                </View>
            )}

            <View style={styles.inputWrapper}>
                <TouchableOpacity onPress={handleFilePick} style={styles.attachButton}>
                    <Paperclip size={22} color="#6B7280" />
                </TouchableOpacity>

                <TextInput
                    ref={inputRef}
                    style={styles.input}
                    placeholder="Message..."
                    placeholderTextColor="#9CA3AF"
                    value={input}
                    onChangeText={setInput}
                    multiline
                />

                <TouchableOpacity
                    onPress={handleSendPress}
                    disabled={isSending || (!input.trim() && pendingFiles.length === 0)}
                    style={[
                        styles.sendButton,
                        (isSending || (!input.trim() && pendingFiles.length === 0)) && styles.sendButtonDisabled
                    ]}
                >
                    {isSending ? (
                        <ActivityIndicator size="small" color="#fff" />
                    ) : (
                        <Send size={20} color="#fff" />
                    )}
                </TouchableOpacity>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        width: '100%',
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: '#E5E7EB',
    },
    pendingFilesContainer: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        paddingHorizontal: 16,
        paddingTop: 12,
    },
    pendingFileItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
        backgroundColor: '#EFF6FF',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#DBEAFE',
    },
    pendingFileName: {
        color: '#1E40AF',
        fontSize: 12,
        maxWidth: 120,
    },
    removeFileButton: {
        padding: 2,
    },
    inputWrapper: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
        padding: 12,
        paddingHorizontal: 16,
    },
    attachButton: {
        padding: 8,
        borderRadius: 20,
        backgroundColor: '#F3F4F6',
    },
    input: {
        flex: 1,
        minHeight: 40,
        maxHeight: 100,
        paddingVertical: 8,
        paddingHorizontal: 16,
        fontSize: 16,
        color: '#111827',
        backgroundColor: '#F3F4F6',
        borderRadius: 20,
    },
    sendButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#007AFF',
        alignItems: 'center',
        justifyContent: 'center',
    },
    sendButtonDisabled: {
        backgroundColor: '#E5E7EB',
    },
});
