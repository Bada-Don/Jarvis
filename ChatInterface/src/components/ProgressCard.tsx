import React from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
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
    const progressAnim = React.useRef(new Animated.Value(progress)).current;

    React.useEffect(() => {
        Animated.timing(progressAnim, {
            toValue: progress,
            duration: 300,
            useNativeDriver: false,
        }).start();
    }, [progress]);

    const progressWidth = progressAnim.interpolate({
        inputRange: [0, 100],
        outputRange: ['0%', '100%'],
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
                return <CheckCircle size={20} color="#10B981" />;
            case 'error':
                return <XCircle size={20} color="#EF4444" />;
            default:
                return <Loader size={20} color="#3B82F6" />;
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                {getStatusIcon()}
                <Text style={[styles.title, { color: getStatusColor() }]}>
                    {title}
                </Text>
            </View>

            {status === 'running' && (
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
                    <Text style={styles.progressText}>{Math.round(progress)}%</Text>
                </View>
            )}

            {status === 'success' && (
                <View style={styles.statusContainer}>
                    <View style={[styles.statusBadge, { backgroundColor: '#D1FAE5' }]}>
                        <Text style={[styles.statusText, { color: '#065F46' }]}>
                            Completed
                        </Text>
                    </View>
                </View>
            )}

            {status === 'error' && errorMessage && (
                <View style={styles.errorContainer}>
                    <Text style={styles.errorText}>{errorMessage}</Text>
                </View>
            )}
        </View>
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
