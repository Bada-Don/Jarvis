import React, { useRef, useEffect } from 'react';
import {
    TouchableOpacity,
    Text,
    StyleSheet,
    Animated,
    Easing,
    Alert,
} from 'react-native';
import { StopCircle } from 'lucide-react-native';

interface AbortButtonProps {
    visible: boolean;
    onAbort: () => void;
}

export const AbortButton: React.FC<AbortButtonProps> = ({ visible, onAbort }) => {
    const slideAnim = useRef(new Animated.Value(100)).current;
    const pulseAnim = useRef(new Animated.Value(1)).current;

    useEffect(() => {
        if (visible) {
            // Slide in animation
            Animated.spring(slideAnim, {
                toValue: 0,
                friction: 8,
                tension: 80,
                useNativeDriver: true,
            }).start();

            // Pulse animation
            const pulse = Animated.loop(
                Animated.sequence([
                    Animated.timing(pulseAnim, {
                        toValue: 1.05,
                        duration: 800,
                        easing: Easing.inOut(Easing.ease),
                        useNativeDriver: true,
                    }),
                    Animated.timing(pulseAnim, {
                        toValue: 1,
                        duration: 800,
                        easing: Easing.inOut(Easing.ease),
                        useNativeDriver: true,
                    }),
                ])
            );
            pulse.start();

            return () => pulse.stop();
        } else {
            // Slide out animation
            Animated.timing(slideAnim, {
                toValue: 100,
                duration: 200,
                easing: Easing.in(Easing.ease),
                useNativeDriver: true,
            }).start();
        }
    }, [visible]);

    const handlePress = () => {
        Alert.alert(
            'Abort Task',
            'Are you sure you want to abort the current task? This action cannot be undone.',
            [
                {
                    text: 'Cancel',
                    style: 'cancel',
                },
                {
                    text: 'Abort',
                    style: 'destructive',
                    onPress: onAbort,
                },
            ]
        );
    };

    if (!visible) return null;

    return (
        <Animated.View
            style={[
                styles.container,
                {
                    transform: [
                        { translateY: slideAnim },
                        { scale: pulseAnim },
                    ],
                },
            ]}
        >
            <TouchableOpacity
                style={styles.button}
                onPress={handlePress}
                activeOpacity={0.8}
            >
                <StopCircle size={20} color="#fafafa" />
                <Text style={styles.buttonText}>Abort Task</Text>
            </TouchableOpacity>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        bottom: 100,
        alignSelf: 'center',
        zIndex: 1000,
    },
    button: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
        backgroundColor: '#dc2626',
        paddingHorizontal: 20,
        paddingVertical: 12,
        borderRadius: 24,
        shadowColor: '#dc2626',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.4,
        shadowRadius: 8,
        elevation: 8,
    },
    buttonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fafafa',
    },
});
