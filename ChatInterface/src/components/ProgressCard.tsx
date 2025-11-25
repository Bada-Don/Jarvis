import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Animated, Easing } from 'react-native';
import { CheckCircle, XCircle, Loader } from 'lucide-react-native';

interface ProgressCardProps {
    title: string;
    progress: number; // 0-100
    status: 'running' | 'success' | 'error';
    errorMessage?: string;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({
    title,
    progress,
    status,
    errorMessage
}) => {
    // Animated values for smooth transitions
    const progressAnim = useRef(new Animated.Value(0)).current;
    const spinAnim = useRef(new Animated.Value(0)).current;
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const fadeAnim = useRef(new Animated.Value(0)).current;

    // Initial fade-in animation
    useEffect(() => {
        Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 200,
            useNativeDriver: true,
        }).start();
    }, []);

    // Smooth progress bar animation
    useEffect(() => {
        Animated.timing(progressAnim, {
            toValue: progress,
            duration: 400,
            easing: Easing.out(Easing.cubic),
            useNativeDriver: false,
        }).start();
    }, [progress]);

    // Spinning animation for loader icon when running
    useEffect(() => {
        if (status === 'running') {
            const spin = Animated.loop(
                Animated.timing(spinAnim, {
                    toValue: 1,
                    duration: 1500,
                    easing: Easing.linear,
                    useNativeDriver: true,
                })
            );
            spin.start();
            return () => spin.stop();
        } else {
            spinAnim.setValue(0);
        }
    }, [status]);

    // Pulse animation for success/error states
    useEffect(() => {
        if (status === 'success' || status === 'error') {
            Animated.sequence([
                Animated.timing(pulseAnim, {
                    toValue: 1.1,
                    duration: 150,
                    useNativeDriver: true,
                }),
                Animated.timing(pulseAnim, {
                    toValue: 1,
                    duration: 150,
                    useNativeDriver: true,
                }),
            ]).start();
        }
    }, [status]);

    const progressWidth = progressAnim.interpolate({
        inputRange: [0, 100],
        outputRange: ['0%', '100%'],
    });

    const spinRotation = spinAnim.interpolate({
        inputRange: [0, 1],
        outputRange: ['0deg', '360deg'],
    });

    const getStatusColor = () => {
        switch (status) {
            case 'success':
                return '#10B981';
            case 'error':
                return '#EF4444';
            default:
                return '#3B82F6';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'success':
                return (
                    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
                        <CheckCircle size={20} color="#10B981" />
                    </Animated.View>
                );
            case 'error':
                return (
                    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
                        <XCircle size={20} color="#EF4444" />
                    </Animated.View>
                );
            default:
                return (
                    <Animated.View style={{ transform: [{ rotate: spinRotation }] }}>
                        <Loader size={20} color="#3B82F6" />
                    </Animated.View>
                );
        }
    };

    const getBackgroundColor = () => {
        switch (status) {
            case 'success':
                return '#F0FDF4';
            case 'error':
                return '#FEF2F2';
            default:
                return '#F9FAFB';
        }
    };

    const getBorderColor = () => {
        switch (status) {
            case 'success':
                return '#BBF7D0';
            case 'error':
                return '#FECACA';
            default:
                return '#E5E7EB';
        }
    };

    return (
        <Animated.View 
            style={[
                styles.container, 
                { 
                    opacity: fadeAnim,
                    backgroundColor: getBackgroundColor(),
                    borderColor: getBorderColor(),
                }
            ]}
        >
            <View style={styles.header}>
                {getStatusIcon()}
                <Text 
                    style={[styles.title, { color: getStatusColor() }]}
                    numberOfLines={2}
                >
                    {title}
                </Text>
            </View>

            {/* Always show progress bar, but style differently based on status */}
            <View style={styles.progressContainer}>
                <View style={styles.progressBackground}>
                    <Animated.View
                        style={[
                            styles.progressBar,
                            {
                                width: progressWidth,
                                backgroundColor: getStatusColor(),
                            },
                        ]}
                    />
                </View>
                <Text style={[styles.progressText, { color: getStatusColor() }]}>
                    {Math.round(progress)}%
                </Text>
            </View>

            {status === 'success' && (
                <View style={styles.statusContainer}>
                    <View style={[styles.statusBadge, { backgroundColor: '#D1FAE5' }]}>
                        <Text style={[styles.statusText, { color: '#065F46' }]}>
                            ✓ Completed
                        </Text>
                    </View>
                </View>
            )}

            {status === 'error' && (
                <View style={styles.errorContainer}>
                    <Text style={styles.errorText}>
                        {errorMessage || 'An error occurred'}
                    </Text>
                </View>
            )}
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: '#F9FAFB',
        borderRadius: 12,
        padding: 16,
        marginVertical: 8,
        borderWidth: 1,
        borderColor: '#E5E7EB',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
        elevation: 2,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        marginBottom: 12,
    },
    title: {
        fontSize: 15,
        fontWeight: '600',
        flex: 1,
    },
    progressContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    progressBackground: {
        flex: 1,
        height: 8,
        backgroundColor: '#E5E7EB',
        borderRadius: 4,
        overflow: 'hidden',
    },
    progressBar: {
        height: '100%',
        borderRadius: 4,
    },
    progressText: {
        fontSize: 13,
        fontWeight: '600',
        color: '#6B7280',
        minWidth: 40,
        textAlign: 'right',
    },
    statusContainer: {
        marginTop: 4,
    },
    statusBadge: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 6,
        alignSelf: 'flex-start',
    },
    statusText: {
        fontSize: 13,
        fontWeight: '600',
    },
    errorContainer: {
        marginTop: 8,
        padding: 12,
        backgroundColor: '#FEE2E2',
        borderRadius: 8,
        borderLeftWidth: 3,
        borderLeftColor: '#EF4444',
    },
    errorText: {
        fontSize: 13,
        color: '#991B1B',
        lineHeight: 18,
    },
});
