import { useState, useEffect, useRef } from 'react';
import { QrCode, RefreshCw, CheckCircle, AlertCircle, Smartphone, Clock } from 'lucide-react';
import { api } from '../../api';

/**
 * PairingStep Component
 * 
 * Step for pairing mobile device with desktop.
 * Displays QR code, pairing token, countdown timer, and handles pairing status.
 * 
 * Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7
 */
export default function PairingStep({ onPairingComplete, onSkip }) {
  const [pairingData, setPairingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPaired, setIsPaired] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(false);
  
  const statusCheckInterval = useRef(null);
  const countdownInterval = useRef(null);

  useEffect(() => {
    generatePairingCode();
    
    return () => {
      // Cleanup intervals on unmount
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
      if (countdownInterval.current) {
        clearInterval(countdownInterval.current);
      }
    };
  }, []);

  const generatePairingCode = async () => {
    setLoading(true);
    setError(null);
    setIsPaired(false);

    try {
      // Call backend to generate pairing token and QR code
      const response = await api.generatePairingCode();
      
      if (response && response.token) {
        setPairingData({
          token: response.token,
          qrCodeData: response.qrCodeData, // Base64 encoded image
          expiresAt: response.expiresAt,
        });

        // Calculate initial time remaining
        const remaining = Math.max(0, response.expiresAt - Math.floor(Date.now() / 1000));
        setTimeRemaining(remaining);

        // Start countdown timer
        startCountdown(response.expiresAt);

        // Start checking pairing status
        startStatusCheck(response.token);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('Failed to generate pairing code:', err);
      setError(err.message || 'Failed to generate pairing code');
    } finally {
      setLoading(false);
    }
  };

  const startCountdown = (expiresAt) => {
    // Clear existing interval
    if (countdownInterval.current) {
      clearInterval(countdownInterval.current);
    }

    // Update countdown every second
    countdownInterval.current = setInterval(() => {
      const remaining = Math.max(0, expiresAt - Math.floor(Date.now() / 1000));
      setTimeRemaining(remaining);

      // If expired, stop countdown and regenerate
      if (remaining === 0) {
        clearInterval(countdownInterval.current);
        // Auto-regenerate after expiration
        setTimeout(() => {
          if (!isPaired) {
            generatePairingCode();
          }
        }, 1000);
      }
    }, 1000);
  };

  const startStatusCheck = (token) => {
    // Clear existing interval
    if (statusCheckInterval.current) {
      clearInterval(statusCheckInterval.current);
    }

    // Check pairing status every 2 seconds
    statusCheckInterval.current = setInterval(async () => {
      await checkPairingStatus(token);
    }, 2000);
  };

  const checkPairingStatus = async (token) => {
    if (checkingStatus || isPaired) {
      return;
    }

    setCheckingStatus(true);

    try {
      const response = await api.checkPairingStatus(token);
      
      if (response && response.paired) {
        setIsPaired(true);
        
        // Clear intervals
        if (statusCheckInterval.current) {
          clearInterval(statusCheckInterval.current);
        }
        if (countdownInterval.current) {
          clearInterval(countdownInterval.current);
        }

        // Notify parent component
        if (onPairingComplete) {
          onPairingComplete(response.deviceId);
        }
      }
    } catch (err) {
      console.error('Failed to check pairing status:', err);
      // Don't show error for status checks, just log it
    } finally {
      setCheckingStatus(false);
    }
  };

  const handleRegenerate = () => {
    // Clear intervals
    if (statusCheckInterval.current) {
      clearInterval(statusCheckInterval.current);
    }
    if (countdownInterval.current) {
      clearInterval(countdownInterval.current);
    }

    // Generate new code
    generatePairingCode();
  };

  const handleSkip = () => {
    // Clear intervals
    if (statusCheckInterval.current) {
      clearInterval(statusCheckInterval.current);
    }
    if (countdownInterval.current) {
      clearInterval(countdownInterval.current);
    }

    if (onSkip) {
      onSkip();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <RefreshCw className="w-12 h-12 text-primary animate-spin mb-4" />
        <p className="text-neutral-600 dark:text-neutral-400">Generating pairing code...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-900 dark:text-yellow-100">
              <p className="font-medium mb-1">Firebase Not Configured</p>
              <p className="text-yellow-700 dark:text-yellow-300 mb-2">
                Mobile pairing requires Firebase to be configured. This is optional and can be set up later.
              </p>
              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                Error details: {error}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Smartphone className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900 dark:text-blue-100">
              <p className="font-medium mb-1">To Enable Mobile Pairing:</p>
              <ol className="list-decimal list-inside text-blue-700 dark:text-blue-300 space-y-1 mt-2">
                <li>Create a Firebase project at <a href="https://console.firebase.google.com" target="_blank" rel="noopener noreferrer" className="underline">Firebase Console</a></li>
                <li>Download the service account credentials JSON file</li>
                <li>Place it at: <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">data/firebase-admin-credentials.json</code></li>
                <li>Add your Firebase config to: <code className="bg-blue-100 dark:bg-blue-900 px-1 rounded">data/firebase_config.json</code></li>
              </ol>
            </div>
          </div>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleSkip}
            className="flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 bg-primary text-white hover:bg-primary/90"
          >
            <span>Skip and Continue</span>
          </button>
          <button
            onClick={generatePairingCode}
            className="px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  if (isPaired) {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/40 flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">
              Pairing Successful!
            </h3>
            <p className="text-green-700 dark:text-green-300">
              Your mobile device has been successfully paired with JARVIS. You can now control
              JARVIS remotely from your mobile app.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Smartphone className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900 dark:text-blue-100">
            <p className="font-medium mb-1">Pair Your Mobile Device</p>
            <p className="text-blue-700 dark:text-blue-300">
              Scan the QR code below with your JARVIS mobile app to pair your device. You can also
              skip this step and pair later from the settings.
            </p>
          </div>
        </div>
      </div>

      {/* QR Code Display */}
      <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-300 dark:border-neutral-700 p-6">
        <div className="flex flex-col items-center">
          {/* QR Code */}
          <div className="bg-white p-4 rounded-lg mb-4">
            {pairingData?.qrCodeData ? (
              <img
                src={`data:image/png;base64,${pairingData.qrCodeData}`}
                alt="Pairing QR Code"
                className="w-64 h-64"
              />
            ) : (
              <div className="w-64 h-64 bg-neutral-200 dark:bg-neutral-700 rounded-lg flex items-center justify-center">
                <QrCode className="w-24 h-24 text-neutral-400" />
              </div>
            )}
          </div>

          {/* Pairing Token */}
          <div className="text-center mb-4">
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-1">Pairing Code</p>
            <p className="text-2xl font-mono font-bold text-neutral-900 dark:text-neutral-100">
              {pairingData?.token || '---'}
            </p>
          </div>

          {/* Countdown Timer */}
          <div className="flex items-center gap-2 text-neutral-600 dark:text-neutral-400">
            <Clock className="w-4 h-4" />
            <span className="text-sm">
              Expires in: <span className="font-mono font-bold">{formatTime(timeRemaining)}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleRegenerate}
          className="flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-700 border border-neutral-300 dark:border-neutral-700"
        >
          <RefreshCw className="w-5 h-5" />
          <span>Regenerate Code</span>
        </button>
        <button
          onClick={handleSkip}
          className="flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/30"
        >
          <span>Skip for Now</span>
        </button>
      </div>

      {/* Status Indicator */}
      <div className="text-center">
        <p className="text-sm text-neutral-500 dark:text-neutral-400">
          {checkingStatus ? (
            <span className="flex items-center justify-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Waiting for mobile device...
            </span>
          ) : (
            'Scan the QR code with your mobile app'
          )}
        </p>
      </div>
    </div>
  );
}
