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
                return '#16e2d7';
            case 'error':
                return '#ef4444';
            default:
                return '#16e2d7';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'success':
                return (
                    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
                        <CheckCircle size={20} color="#16e2d7" />
                    </Animated.View>
                );
            case 'error':
                return (
                    <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
                        <XCircle size={20} color="#ef4444" />
                    </Animated.View>
                );
            default:
                return (
                    <Animated.View style={{ transform: [{ rotate: spinRotation }] }}>
                        <Loader size={20} color="#16e2d7" />
                    </Animated.View>
                );
        }
    };

    const getBackgroundColor = () => {
        switch (status) {
            case 'success':
                return '#042f2e';
            case 'error':
                return '#7f1d1d';
            default:
                return '#18181b';
        }
    };

    const getBorderColor = () => {
        switch (status) {
            case 'success':
                return '#16e2d7';
            case 'error':
                return '#ef4444';
            default:
                return '#18181b';
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
                    <View style={[styles.statusBadge, { backgroundColor: '#042f2e' }]}>
                        <Text style={[styles.statusText, { color: '#5eead4' }]}>
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
        backgroundColor: '#18181b',
        borderRadius: 12,
        padding: 16,
        marginVertical: 8,
        borderWidth: 1,
        borderColor: '#18181b',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.08,
        shadowRadius: 8,
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
        backgroundColor: '#0a0a0a',
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
        color: '#a1a1aa',
        minWidth: 40,
        textAlign: 'right',
    },
    statusContainer: {
        marginTop: 8,
    },
    statusBadge: {
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 9999,
        alignSelf: 'flex-start',
    },
    statusText: {
        fontSize: 13,
        fontWeight: '600',
    },
    errorContainer: {
        marginTop: 8,
        padding: 12,
        backgroundColor: '#7f1d1d',
        borderRadius: 12,
        borderLeftWidth: 3,
        borderLeftColor: '#ef4444',
    },
    errorText: {
        fontSize: 13,
        color: '#fafafa',
        lineHeight: 18,
    },
});
