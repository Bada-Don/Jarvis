import React, { useEffect, useRef, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TouchableOpacity,
    Animated,
    Easing,
    ScrollView,
    TextInput,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { HelpCircle } from 'lucide-react-native';

export interface ClarificationOption {
    label?: string;
    value?: string;
}

interface ClarificationModalProps {
    visible: boolean;
    question: string;
    options?: Array<ClarificationOption | string>;
    isMultiselect?: boolean;
    onSubmit: (answer: string) => void;
    onSkip: () => void;
}

function normalizeOption(opt: ClarificationOption | string): { label: string; value: string } {
    if (typeof opt === 'string') {
        return { label: opt, value: opt };
    }
    const v = opt.value ?? opt.label ?? '';
    const l = opt.label ?? opt.value ?? '';
    return { label: l || v, value: v || l };
}

export const ClarificationModal: React.FC<ClarificationModalProps> = ({
    visible,
    question,
    options,
    isMultiselect,
    onSubmit,
    onSkip,
}) => {
    const scaleAnim = useRef(new Animated.Value(0.8)).current;
    const opacityAnim = useRef(new Animated.Value(0)).current;
    const [answer, setAnswer] = useState('');
    const [selectedMulti, setSelectedMulti] = useState<string[]>([]);

    useEffect(() => {
        if (visible) {
            setAnswer('');
            setSelectedMulti([]);
            Animated.parallel([
                Animated.spring(scaleAnim, {
                    toValue: 1,
                    friction: 8,
                    tension: 100,
                    useNativeDriver: true,
                }),
                Animated.timing(opacityAnim, {
                    toValue: 1,
                    duration: 200,
                    easing: Easing.out(Easing.ease),
                    useNativeDriver: true,
                }),
            ]).start();
        } else {
            scaleAnim.setValue(0.8);
            opacityAnim.setValue(0);
        }
    }, [visible]);

    const normalized = (options ?? []).map(normalizeOption).filter((o) => o.value || o.label);

    const toggleMulti = (value: string) => {
        setSelectedMulti((prev) =>
            prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
        );
    };

    const applyChipPress = (value: string) => {
        if (isMultiselect) {
            toggleMulti(value);
            return;
        }
        onSubmit(value);
    };

    const handleSubmit = () => {
        const trimmed = answer.trim();
        if (trimmed) {
            onSubmit(trimmed);
            return;
        }
        if (isMultiselect && selectedMulti.length > 0) {
            onSubmit(selectedMulti.join(', '));
        }
    };

    return (
        <Modal
            visible={visible}
            transparent
            animationType="none"
            statusBarTranslucent
        >
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                style={styles.keyboardRoot}
            >
                <Animated.View style={[styles.overlay, { opacity: opacityAnim }]}>
                    <Animated.View
                        style={[
                            styles.modalContainer,
                            { transform: [{ scale: scaleAnim }] },
                        ]}
                    >
                        <View style={styles.iconContainer}>
                            <HelpCircle size={32} color="#22d3ee" />
                        </View>

                        <Text style={styles.title}>Jarvis needs input</Text>

                        <ScrollView
                            style={styles.scrollContainer}
                            contentContainerStyle={styles.scrollContent}
                            keyboardShouldPersistTaps="handled"
                            showsVerticalScrollIndicator
                        >
                            <Text style={styles.question}>{question}</Text>

                            {normalized.length > 0 ? (
                                <View style={styles.chipsWrap}>
                                    {normalized.map((o, idx) => {
                                        const selected =
                                            isMultiselect && selectedMulti.includes(o.value);
                                        return (
                                            <TouchableOpacity
                                                key={`${o.value}-${idx}`}
                                                style={[styles.chip, selected && styles.chipSelected]}
                                                onPress={() => applyChipPress(o.value)}
                                                activeOpacity={0.85}
                                            >
                                                <Text
                                                    style={[
                                                        styles.chipText,
                                                        selected && styles.chipTextSelected,
                                                    ]}
                                                >
                                                    {o.label}
                                                </Text>
                                            </TouchableOpacity>
                                        );
                                    })}
                                </View>
                            ) : null}

                            <Text style={styles.inputLabel}>Your reply</Text>
                            <TextInput
                                style={styles.input}
                                placeholder="Type an answer…"
                                placeholderTextColor="#71717a"
                                value={answer}
                                onChangeText={setAnswer}
                                multiline
                                editable={true}
                            />
                            {isMultiselect && normalized.length > 0 ? (
                                <Text style={styles.hint}>
                                    Tap chips to toggle selections; Submit sends your text if filled, otherwise selected chips.
                                </Text>
                            ) : null}
                        </ScrollView>

                        <View style={styles.buttonContainer}>
                            <TouchableOpacity
                                style={[styles.button, styles.skipButton]}
                                onPress={onSkip}
                                activeOpacity={0.8}
                            >
                                <Text style={styles.skipButtonText}>Skip</Text>
                            </TouchableOpacity>

                            <TouchableOpacity
                                style={[styles.button, styles.submitButton]}
                                onPress={handleSubmit}
                                activeOpacity={0.8}
                            >
                                <Text style={styles.submitButtonText}>Submit</Text>
                            </TouchableOpacity>
                        </View>
                    </Animated.View>
                </Animated.View>
            </KeyboardAvoidingView>
        </Modal>
    );
};

const styles = StyleSheet.create({
    keyboardRoot: {
        flex: 1,
    },
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.82)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    modalContainer: {
        backgroundColor: '#18181b',
        borderRadius: 16,
        padding: 24,
        width: '100%',
        maxWidth: 360,
        maxHeight: '85%',
        alignItems: 'stretch',
        borderWidth: 1,
        borderColor: '#27272a',
    },
    scrollContainer: {
        width: '100%',
        maxHeight: 340,
        marginBottom: 12,
    },
    scrollContent: {
        paddingVertical: 4,
    },
    iconContainer: {
        width: 56,
        height: 56,
        borderRadius: 28,
        backgroundColor: '#164e63',
        justifyContent: 'center',
        alignItems: 'center',
        alignSelf: 'center',
        marginBottom: 12,
    },
    title: {
        fontSize: 18,
        fontWeight: '700',
        color: '#fafafa',
        marginBottom: 12,
        textAlign: 'center',
    },
    question: {
        fontSize: 15,
        color: '#e4e4e7',
        lineHeight: 22,
        marginBottom: 14,
    },
    chipsWrap: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 14,
    },
    chip: {
        marginRight: 8,
        marginBottom: 8,
        paddingHorizontal: 12,
        paddingVertical: 8,
        borderRadius: 999,
        backgroundColor: '#27272a',
        borderWidth: 1,
        borderColor: '#3f3f46',
    },
    chipSelected: {
        borderColor: '#22d3ee',
        backgroundColor: '#0e7490',
    },
    chipText: {
        fontSize: 13,
        color: '#e4e4e7',
        fontWeight: '500',
    },
    chipTextSelected: {
        color: '#ecfeff',
    },
    inputLabel: {
        fontSize: 12,
        fontWeight: '600',
        color: '#a1a1aa',
        marginBottom: 6,
    },
    input: {
        minHeight: 88,
        borderWidth: 1,
        borderColor: '#3f3f46',
        borderRadius: 12,
        padding: 12,
        fontSize: 15,
        color: '#fafafa',
        backgroundColor: '#09090b',
        textAlignVertical: 'top',
    },
    hint: {
        fontSize: 12,
        color: '#71717a',
        marginTop: 8,
        lineHeight: 17,
    },
    buttonContainer: {
        flexDirection: 'row',
        gap: 12,
        width: '100%',
        marginTop: 4,
    },
    button: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 14,
        borderRadius: 12,
    },
    skipButton: {
        backgroundColor: '#27272a',
        borderWidth: 1,
        borderColor: '#3f3f46',
    },
    skipButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fafafa',
    },
    submitButton: {
        backgroundColor: '#16e2d7',
    },
    submitButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#022726',
    },
});
