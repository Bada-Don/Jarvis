import React, { useEffect, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TouchableOpacity,
    Animated,
    Easing,
    ScrollView,
} from 'react-native';
import { AlertTriangle, Check, X } from 'lucide-react-native';

interface PermissionModalProps {
    visible: boolean;
    operation: string;
    details: string;
    onApprove: () => void;
    onDeny: () => void;
}

export const PermissionModal: React.FC<PermissionModalProps> = ({
    visible,
    operation,
    details,
    onApprove,
    onDeny,
}) => {
    const scaleAnim = useRef(new Animated.Value(0.8)).current;
    const opacityAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        if (visible) {
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

    return (
        <Modal
            visible={visible}
            transparent
            animationType="none"
            statusBarTranslucent
        >
            <Animated.View style={[styles.overlay, { opacity: opacityAnim }]}>
                <Animated.View
                    style={[
                        styles.modalContainer,
                        { transform: [{ scale: scaleAnim }] },
                    ]}
                >
                    <View style={styles.iconContainer}>
                        <AlertTriangle size={32} color="#f59e0b" />
                    </View>

                    <Text style={styles.title}>Permission Required</Text>
                    
                    <View style={styles.operationBadge}>
                        <Text style={styles.operationText}>{operation}</Text>
                    </View>

                    <ScrollView 
                        style={styles.scrollContainer}
                        contentContainerStyle={styles.scrollContent}
                        showsVerticalScrollIndicator={true}
                        persistentScrollbar={true}
                    >
                        <Text style={styles.details}>{details}</Text>

                        <Text style={styles.warning}>
                            This action requires your approval to proceed.
                        </Text>
                    </ScrollView>

                    <View style={styles.buttonContainer}>
                        <TouchableOpacity
                            style={[styles.button, styles.denyButton]}
                            onPress={onDeny}
                            activeOpacity={0.8}
                        >
                            <X size={20} color="#fafafa" />
                            <Text style={styles.denyButtonText}>Deny</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[styles.button, styles.approveButton]}
                            onPress={onApprove}
                            activeOpacity={0.8}
                        >
                            <Check size={20} color="#022726" />
                            <Text style={styles.approveButtonText}>Approve</Text>
                        </TouchableOpacity>
                    </View>
                </Animated.View>
            </Animated.View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    modalContainer: {
        backgroundColor: '#18181b',
        borderRadius: 16,
        padding: 24,
        width: '100%',
        maxWidth: 340,
        maxHeight: '80%',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: '#27272a',
    },
    scrollContainer: {
        width: '100%',
        maxHeight: 300,
        marginBottom: 16,
    },
    scrollContent: {
        paddingVertical: 4,
    },
    iconContainer: {
        width: 64,
        height: 64,
        borderRadius: 32,
        backgroundColor: '#422006',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    title: {
        fontSize: 20,
        fontWeight: '700',
        color: '#fafafa',
        marginBottom: 12,
    },
    operationBadge: {
        backgroundColor: '#7f1d1d',
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 8,
        marginBottom: 12,
    },
    operationText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#fca5a5',
        textTransform: 'uppercase',
    },
    details: {
        fontSize: 15,
        color: '#a1a1aa',
        textAlign: 'center',
        lineHeight: 22,
        marginBottom: 12,
    },
    warning: {
        fontSize: 13,
        color: '#f59e0b',
        textAlign: 'center',
        marginTop: 12,
    },
    buttonContainer: {
        flexDirection: 'row',
        gap: 12,
        width: '100%',
    },
    button: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 14,
        borderRadius: 12,
        gap: 8,
    },
    denyButton: {
        backgroundColor: '#27272a',
        borderWidth: 1,
        borderColor: '#3f3f46',
    },
    denyButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fafafa',
    },
    approveButton: {
        backgroundColor: '#16e2d7',
    },
    approveButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#022726',
    },
});
