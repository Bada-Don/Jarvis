import React, { useEffect } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';

interface SplashVideoProps {
    onFinish: () => void;
}

const { width } = Dimensions.get('window');

// Video source
const videoSource = require('../../assets/Jarvis_Animation.mp4');

export const SplashVideo: React.FC<SplashVideoProps> = ({ onFinish }) => {
    const player = useVideoPlayer(videoSource, (player) => {
        player.loop = false;
        player.play();
    });

    useEffect(() => {
        // Listen for playback end
        const subscription = player.addListener('playToEnd', () => {
            onFinish();
        });

        // Fallback timeout in case video fails
        const timeout = setTimeout(() => {
            onFinish();
        }, 10000);

        return () => {
            subscription.remove();
            clearTimeout(timeout);
        };
    }, [player, onFinish]);

    return (
        <View style={styles.container}>
            <VideoView
                player={player}
                style={styles.video}
                contentFit="contain"
                nativeControls={false}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000000ff',
        justifyContent: 'center',
        alignItems: 'center',
    },
    video: {
        width: width,
        aspectRatio: 16 / 9,
    },
});
