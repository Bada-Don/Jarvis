import React, { useState } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { View, StyleSheet } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';
import ChatScreen from './src/screens/ChatScreen';
import { SplashVideo } from './src/components/SplashVideo';

// Prevent the splash screen from auto-hiding
SplashScreen.preventAutoHideAsync();

export default function App() {
  const [showSplash, setShowSplash] = useState(true);

  React.useEffect(() => {
    // Hide native splash screen immediately
    SplashScreen.hideAsync();
  }, []);

  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  if (showSplash) {
    return (
      <View style={styles.container}>
        <SplashVideo onFinish={handleSplashFinish} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <SafeAreaProvider>
        <ChatScreen />
      </SafeAreaProvider>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
});
