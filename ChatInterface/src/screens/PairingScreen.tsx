/**
 * Pairing Screen for JARVIS Mobile App
 * Handles device pairing workflow with QR code scanning.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { QRScanner } from '../components/QRScanner';
import { PairingManager } from '../services/PairingManager';

interface PairingScreenProps {
  pairingManager: PairingManager;
  onPairingComplete: () => void;
  onCancel?: () => void;
}

export const PairingScreen: React.FC<PairingScreenProps> = ({
  pairingManager,
  onPairingComplete,
  onCancel,
}) => {
  const [showScanner, setShowScanner] = useState(false);
  const [manualToken, setManualToken] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPaired, setIsPaired] = useState(false);

  useEffect(() => {
    checkPairingStatus();
  }, []);

  const checkPairingStatus = async () => {
    try {
      const paired = await pairingManager.isPaired();
      setIsPaired(paired);

      if (paired) {
        const desktopId = await pairingManager.getPairedDesktopId();
        console.log(`Already paired with desktop: ${desktopId}`);
      }
    } catch (error) {
      console.error('Failed to check pairing status:', error);
    }
  };

  const handleQRScan = async (token: string) => {
    setIsProcessing(true);

    try {
      const result = await pairingManager.submitPairingToken(token);

      if (result.success) {
        Alert.alert(
          'Pairing Successful',
          'Your device has been paired with the desktop application.',
          [
            {
              text: 'OK',
              onPress: () => {
                setShowScanner(false);
                onPairingComplete();
              },
            },
          ]
        );
      } else {
        Alert.alert(
          'Pairing Failed',
          result.message || 'The pairing code is invalid or has expired. Please try again.',
          [
            {
              text: 'OK',
              onPress: () => {
                setShowScanner(false);
                setIsProcessing(false);
              },
            },
          ]
        );
      }
    } catch (error) {
      console.error('Pairing error:', error);
      Alert.alert(
        'Pairing Error',
        `An error occurred during pairing: ${(error as Error).message}`,
        [
          {
            text: 'OK',
            onPress: () => {
              setShowScanner(false);
              setIsProcessing(false);
            },
          },
        ]
      );
    }
  };

  const handleManualPairing = async () => {
    if (!manualToken.trim()) {
      Alert.alert('Invalid Token', 'Please enter a pairing token.');
      return;
    }

    if (!manualToken.startsWith('pair_')) {
      Alert.alert(
        'Invalid Token',
        'Pairing tokens should start with "pair_".'
      );
      return;
    }

    setIsProcessing(true);

    try {
      const result = await pairingManager.submitPairingToken(manualToken);

      if (result.success) {
        Alert.alert(
          'Pairing Successful',
          'Your device has been paired with the desktop application.',
          [
            {
              text: 'OK',
              onPress: () => {
                setManualToken('');
                onPairingComplete();
              },
            },
          ]
        );
      } else {
        Alert.alert(
          'Pairing Failed',
          result.message || 'The pairing code is invalid or has expired. Please try again.'
        );
      }
    } catch (error) {
      console.error('Pairing error:', error);
      Alert.alert(
        'Pairing Error',
        'An error occurred during pairing. Please try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUnpair = async () => {
    Alert.alert(
      'Unpair Device',
      'Are you sure you want to unpair this device? You will need to scan a new QR code to reconnect.',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Unpair',
          style: 'destructive',
          onPress: async () => {
            try {
              const success = await pairingManager.unpair();
              if (success) {
                setIsPaired(false);
                Alert.alert('Unpaired', 'Device has been unpaired successfully.');
              } else {
                Alert.alert('Error', 'Failed to unpair device.');
              }
            } catch (error) {
              console.error('Unpair error:', error);
              Alert.alert('Error', 'An error occurred while unpairing.');
            }
          },
        },
      ]
    );
  };

  if (showScanner) {
    return (
      <QRScanner
        onScan={handleQRScan}
        onCancel={() => {
          setShowScanner(false);
          setIsProcessing(false);
        }}
        isProcessing={isProcessing}
      />
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <Text style={styles.title}>Pair Your Device</Text>

          {isPaired ? (
            <View style={styles.pairedContainer}>
              <Text style={styles.pairedText}>✓ Device Paired</Text>
              <Text style={styles.pairedSubtext}>
                Your mobile device is connected to the desktop application.
              </Text>
              <TouchableOpacity
                style={[styles.button, styles.unpairButton]}
                onPress={handleUnpair}
              >
                <Text style={styles.buttonText}>Unpair Device</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <Text style={styles.subtitle}>
                Scan the QR code displayed on your desktop application to pair
                your device.
              </Text>

              <TouchableOpacity
                style={styles.button}
                onPress={() => setShowScanner(true)}
                disabled={isProcessing}
              >
                <Text style={styles.buttonText}>Scan QR Code</Text>
              </TouchableOpacity>

              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>OR</Text>
                <View style={styles.dividerLine} />
              </View>

              <Text style={styles.manualTitle}>Enter Pairing Code Manually</Text>
              <TextInput
                style={styles.input}
                placeholder="pair_xxxxxxxxxxxx"
                placeholderTextColor="#8E8E93"
                value={manualToken}
                onChangeText={setManualToken}
                autoCapitalize="none"
                autoCorrect={false}
                editable={!isProcessing}
              />

              <TouchableOpacity
                style={[styles.button, styles.manualButton]}
                onPress={handleManualPairing}
                disabled={isProcessing || !manualToken.trim()}
              >
                {isProcessing ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <Text style={styles.buttonText}>Pair with Code</Text>
                )}
              </TouchableOpacity>
            </>
          )}

          {onCancel && (
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onCancel}
              disabled={isProcessing}
            >
              <Text style={styles.buttonText}>
                {isPaired ? 'Continue' : 'Skip for Now'}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 40,
    lineHeight: 22,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 30,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#3A3A3C',
  },
  dividerText: {
    color: '#8E8E93',
    fontSize: 14,
    marginHorizontal: 16,
  },
  manualTitle: {
    fontSize: 18,
    color: '#FFFFFF',
    marginBottom: 12,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#1C1C1E',
    borderWidth: 1,
    borderColor: '#3A3A3C',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#FFFFFF',
    marginBottom: 16,
  },
  manualButton: {
    backgroundColor: '#5856D6',
  },
  cancelButton: {
    backgroundColor: '#3A3A3C',
    marginTop: 20,
  },
  pairedContainer: {
    alignItems: 'center',
    marginVertical: 40,
  },
  pairedText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#34C759',
    marginBottom: 10,
  },
  pairedSubtext: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 22,
  },
  unpairButton: {
    backgroundColor: '#FF3B30',
  },
});
