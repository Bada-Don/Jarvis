import React, { useState, useRef, useEffect } from 'react';
import {
    View,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    ActivityIndicator,
    Text,
    Alert
} from 'react-native';
import { Paperclip, Send, FileText, X, Camera, Mic } from 'lucide-react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as ImagePicker from 'expo-image-picker';
import { 
    useAudioRecorder, 
    RecordingPresets, 
    setAudioModeAsync, 
    useAudioRecorderState, 
    requestRecordingPermissionsAsync,
    RecordingOptions 
} from 'expo-audio';

interface ChatInputProps {
    onSend: (text: string, files: any[]) => void;
    isSending: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isSending }) => {
    const [input, setInput] = useState('');
    const [pendingFiles, setPendingFiles] = useState<any[]>([]);
    const inputRef = useRef<TextInput>(null);

    // Initialize audio recorder with custom settings for better compatibility
    const recordingOptions: RecordingOptions = {
        ...RecordingPresets.HIGH_QUALITY,
        android: {
            extension: '.m4a',
            sampleRate: 44100,
            outputFormat: 'mpeg4',
            audioEncoder: 'aac',
        },
        ios: {
            extension: '.m4a',
            audioQuality: 0x7F, // AVAudioQuality.max
            sampleRate: 44100,
            linearPCMBitDepth: 16,
            linearPCMIsBigEndian: false,
            linearPCMIsFloat: false,
        },
        web: {
            mimeType: 'audio/webm',
            bitsPerSecond: 128000,
        },
    };

    const audioRecorder = useAudioRecorder(recordingOptions);
    const recorderState = useAudioRecorderState(audioRecorder);

    // Set up audio mode on mount
    useEffect(() => {
        (async () => {
            try {
                await setAudioModeAsync({
                    playsInSilentMode: true,
                    allowsRecording: true,
                });
            } catch (err) {
                console.error('Failed to set audio mode:', err);
            }
        })();

        // Cleanup on unmount
        return () => {
            if (recorderState.isRecording) {
                audioRecorder.stop();
            }
        };
    }, []);

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

    const handleCameraPress = async () => {
        try {
            // Request camera permissions
            const { status } = await ImagePicker.requestCameraPermissionsAsync();

            if (status !== 'granted') {
                Alert.alert(
                    'Permission Required',
                    'Camera permission is required to take photos.',
                    [{ text: 'OK' }]
                );
                return;
            }

            // Show action sheet to choose between camera and gallery
            Alert.alert(
                'Select Image',
                'Choose an option',
                [
                    {
                        text: 'Take Photo',
                        onPress: async () => {
                            const result = await ImagePicker.launchCameraAsync({
                                mediaTypes: ['images'],
                                allowsEditing: true,
                                quality: 0.1,  // Reduced quality for smaller file size
                            });

                            if (!result.canceled && result.assets) {
                                setPendingFiles((prev) => [...prev, ...result.assets]);
                            }
                        }
                    },
                    {
                        text: 'Choose from Gallery',
                        onPress: async () => {
                            const { status: galleryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

                            if (galleryStatus !== 'granted') {
                                Alert.alert(
                                    'Permission Required',
                                    'Gallery permission is required to select photos.',
                                    [{ text: 'OK' }]
                                );
                                return;
                            }

                            const result = await ImagePicker.launchImageLibraryAsync({
                                mediaTypes: ['images'],
                                allowsEditing: true,
                                quality: 0.1,  // Reduced quality for consistency
                                allowsMultipleSelection: true,
                            });

                            if (!result.canceled && result.assets) {
                                setPendingFiles((prev) => [...prev, ...result.assets]);
                            }
                        }
                    },
                    {
                        text: 'Cancel',
                        style: 'cancel'
                    }
                ]
            );
        } catch (err) {
            console.error('Error accessing camera:', err);
            Alert.alert('Error', 'Failed to access camera');
        }
    };

    const handleVoicePress = async () => {
        try {
            if (recorderState.isRecording) {
                // Stop recording
                console.log('Stopping recording...');
                console.log('Recording duration:', recorderState.durationMillis, 'ms');
                await audioRecorder.stop();
                const uri = audioRecorder.uri;

                if (uri) {
                    console.log('Recording saved to:', uri);
                    
                    // Get file info
                    let fileSize = 0;
                    try {
                        const response = await fetch(uri);
                        const blob = await response.blob();
                        fileSize = blob.size;
                        console.log('Audio file size:', fileSize, 'bytes');
                        
                        if (fileSize < 1000) {
                            console.warn('⚠️ Warning: Audio file is very small, might be empty!');
                        }
                    } catch (e) {
                        console.log('Could not get file size:', e);
                    }

                    // Add audio file to pending files (skip transcription)
                    const audioFile = {
                        uri,
                        name: `voice_${Date.now()}.m4a`,
                        fileName: `voice_${Date.now()}.m4a`,
                        type: 'audio/m4a',
                        mimeType: 'audio/m4a',
                        size: fileSize,
                        fileSize: fileSize,
                    };

                    setPendingFiles((prev) => [...prev, audioFile]);
                    
                    if (fileSize > 0) {
                        Alert.alert('Voice Recorded', `Audio file added (${Math.round(fileSize / 1024)}KB). Ready to send!`);
                    } else {
                        Alert.alert('Warning', 'Recording saved but file size is 0. Check microphone permissions.');
                    }
                } else {
                    console.error('No URI returned from recorder');
                    Alert.alert('Error', 'Recording failed - no file created');
                }
            } else {
                // Request permission before starting
                const { granted } = await requestRecordingPermissionsAsync();

                if (!granted) {
                    Alert.alert(
                        'Permission Required',
                        'Microphone permission is required to record audio.',
                        [{ text: 'OK' }]
                    );
                    return;
                }

                // Prepare and start recording
                console.log('Preparing to record...');
                try {
                    await audioRecorder.prepareToRecordAsync();
                    console.log('Recorder prepared successfully');
                    console.log('Starting recording...');
                    audioRecorder.record();
                    console.log('Recording started');
                    Alert.alert('Recording', 'Tap the mic button again to stop recording');
                } catch (prepError) {
                    console.error('Failed to prepare recorder:', prepError);
                    throw new Error(`Preparation failed: ${prepError.message || prepError}`);
                }
            }
        } catch (err) {
            console.error('Failed to handle voice recording:', err);
            Alert.alert('Error', `Failed to record audio: ${err.message || err}`);
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

    const hasContent = input.trim().length > 0 || pendingFiles.length > 0;

    return (
        <View style={styles.container}>
            {(pendingFiles.length > 0 || recorderState.isRecording) && (
                <View style={styles.pendingFilesContainer}>
                    {recorderState.isRecording && (
                        <View style={[styles.pendingFileItem, styles.recordingIndicator]}>
                            <Mic size={12} color="#EF4444" />
                            <Text style={styles.recordingText}>
                                Recording... {Math.floor((recorderState.durationMillis || 0) / 1000)}s
                            </Text>
                        </View>
                    )}
                    {pendingFiles.map((file, index) => (
                        <View key={index} style={styles.pendingFileItem}>
                            {(file.type || file.mimeType || '').includes('audio') ? (
                                <Mic size={12} color="#007AFF" />
                            ) : (
                                <FileText size={12} color="#007AFF" />
                            )}
                            <Text style={styles.pendingFileName} numberOfLines={1}>
                                {file.name || file.fileName || 'File'}
                            </Text>
                            <TouchableOpacity onPress={() => removePendingFile(index)} style={styles.removeFileButton}>
                                <X size={12} color="#6B7280" />
                            </TouchableOpacity>
                        </View>
                    ))}
                </View>
            )}

            <View style={styles.inputWrapper}>
                <TextInput
                    ref={inputRef}
                    style={styles.input}
                    placeholder="Message..."
                    placeholderTextColor="#a1a1aa"
                    value={input}
                    onChangeText={setInput}
                    multiline
                />

                <View style={styles.actionsContainer}>
                    <TouchableOpacity onPress={handleCameraPress} style={styles.actionButton}>
                        <Camera size={22} color="#a1a1aa" />
                    </TouchableOpacity>

                    <TouchableOpacity onPress={handleFilePick} style={styles.actionButton}>
                        <Paperclip size={22} color="#a1a1aa" />
                    </TouchableOpacity>

                    {hasContent ? (
                        <TouchableOpacity
                            onPress={handleSendPress}
                            disabled={isSending}
                            style={[
                                styles.sendButton,
                                isSending && styles.sendButtonDisabled
                            ]}
                        >
                            {isSending ? (
                                <ActivityIndicator size="small" color="#fff" />
                            ) : (
                                <Send size={20} color="#022726" />
                            )}
                        </TouchableOpacity>
                    ) : (
                        <TouchableOpacity
                            onPress={handleVoicePress}
                            style={[
                                styles.actionButton,
                                recorderState.isRecording && styles.recordingButton
                            ]}
                        >
                            <Mic size={22} color={recorderState.isRecording ? "#fafafa" : "#a1a1aa"} />
                        </TouchableOpacity>
                    )}
                </View>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        width: '100%',
        backgroundColor: '#0a0a0a',
        borderTopWidth: 1,
        borderTopColor: '#18181b',
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
        backgroundColor: '#042f2e',
        paddingHorizontal: 10,
        paddingVertical: 6,
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#16e2d7',
    },
    pendingFileName: {
        color: '#5eead4',
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
    input: {
        flex: 1,
        minHeight: 40,
        maxHeight: 100,
        paddingVertical: 8,
        paddingHorizontal: 16,
        fontSize: 16,
        color: '#fafafa',
        backgroundColor: '#18181b',
        borderRadius: 12,
    },
    actionsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    actionButton: {
        width: 40,
        height: 40,
        borderRadius: 12,
        backgroundColor: '#18181b',
        alignItems: 'center',
        justifyContent: 'center',
    },
    recordingButton: {
        backgroundColor: '#7f1d1d',
    },
    sendButton: {
        width: 40,
        height: 40,
        borderRadius: 12,
        backgroundColor: '#16e2d7',
        alignItems: 'center',
        justifyContent: 'center',
    },
    sendButtonDisabled: {
        backgroundColor: '#18181b',
    },
    recordingIndicator: {
        backgroundColor: '#7f1d1d',
        borderColor: '#ef4444',
    },
    recordingText: {
        color: '#fafafa',
        fontSize: 12,
        fontWeight: '600',
    },
});