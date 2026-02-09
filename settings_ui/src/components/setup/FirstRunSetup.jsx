import { useState, useEffect } from 'react';
import {
  Modal,
  ModalBody,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
} from '../ui/AnimatedModal';
import ApiKeyStep from './ApiKeyStep';
import PathConfigStep from './PathConfigStep';
import PairingStep from './PairingStep';

const STEPS = {
  API_KEYS: 0,
  PATHS: 1,
  PAIRING: 2,
};

const STEP_TITLES = {
  [STEPS.API_KEYS]: 'API Configuration',
  [STEPS.PATHS]: 'System Paths',
  [STEPS.PAIRING]: 'Device Pairing',
};

const STEP_DESCRIPTIONS = {
  [STEPS.API_KEYS]: 'Configure your AI provider API keys to enable JARVIS functionality',
  [STEPS.PATHS]: 'Set up system paths for desktop, documents, and downloads folders',
  [STEPS.PAIRING]: 'Pair your mobile device to control JARVIS remotely',
};

/**
 * FirstRunSetup Component
 * 
 * Multi-step wizard for initial JARVIS configuration.
 * Guides users through API key setup, path configuration, and device pairing.
 * 
 * Requirements: 2.1, 2.2, 2.8, 2.9, 2.10
 */
export default function FirstRunSetup({ isOpen, onComplete, onSkip }) {
  const [currentStep, setCurrentStep] = useState(STEPS.API_KEYS);
  const [configuration, setConfiguration] = useState({
    apiKeys: {
      gemini: '',
      openai: '',
    },
    paths: {
      desktop: '',
      documents: '',
      downloads: '',
    },
    pairing: {
      completed: false,
      deviceId: null,
    },
  });
  const [stepValid, setStepValid] = useState(false);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setCurrentStep(STEPS.API_KEYS);
      setStepValid(false);
    }
  }, [isOpen]);

  const handleNext = () => {
    if (currentStep < STEPS.PAIRING) {
      setCurrentStep(currentStep + 1);
      setStepValid(false);
    } else {
      // Final step - complete setup
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > STEPS.API_KEYS) {
      setCurrentStep(currentStep - 1);
      setStepValid(false);
    }
  };

  const handleComplete = () => {
    // Mark first-run as complete and save configuration
    if (onComplete) {
      onComplete(configuration);
    }
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    }
  };

  const updateConfiguration = (section, data) => {
    setConfiguration((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        ...data,
      },
    }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case STEPS.API_KEYS:
        return (
          <ApiKeyStep
            apiKeys={configuration.apiKeys}
            onChange={(data) => updateConfiguration('apiKeys', data)}
            onValidationChange={setStepValid}
          />
        );
      case STEPS.PATHS:
        return (
          <PathConfigStep
            paths={configuration.paths}
            onChange={(data) => updateConfiguration('paths', data)}
            onValidationChange={setStepValid}
          />
        );
      case STEPS.PAIRING:
        return (
          <PairingStep
            onPairingComplete={(deviceId) => {
              updateConfiguration('pairing', { completed: true, deviceId });
              setStepValid(true);
            }}
            onSkip={() => setStepValid(true)}
          />
        );
      default:
        return null;
    }
  };

  const isLastStep = currentStep === STEPS.PAIRING;
  const isFirstStep = currentStep === STEPS.API_KEYS;

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative z-50 max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-2xl bg-white dark:bg-neutral-900 shadow-2xl">
        <div className="overflow-y-auto max-h-[90vh] p-8 md:p-10">
          {/* Header */}
          <div className="mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-neutral-100">
              {STEP_TITLES[currentStep]}
            </h2>
            <p className="mt-2 text-sm md:text-base text-neutral-600 dark:text-neutral-400">
              {STEP_DESCRIPTIONS[currentStep]}
            </p>
            
            {/* Step Indicator */}
            <div className="flex items-center justify-center gap-2 mt-6">
              {Object.values(STEPS).map((step) => (
                <div
                  key={step}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    step === currentStep
                      ? 'w-8 bg-primary'
                      : step < currentStep
                      ? 'w-2 bg-primary/50'
                      : 'w-2 bg-neutral-300 dark:bg-neutral-700'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="my-6">{renderStep()}</div>

          {/* Footer */}
          <div className="mt-8 flex flex-col sm:flex-row gap-3 sm:justify-end">
            {/* Skip Button (only on first step) */}
            {isFirstStep && (
              <button
                onClick={handleSkip}
                className="px-4 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100 transition-colors"
              >
                Skip Setup
              </button>
            )}

            <div className="flex gap-3 ml-auto">
              {/* Back Button */}
              {!isFirstStep && (
                <button
                  onClick={handleBack}
                  className="px-6 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
                >
                  Back
                </button>
              )}

              {/* Next/Complete Button */}
              <button
                onClick={handleNext}
                disabled={!stepValid}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  stepValid
                    ? 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/25'
                    : 'bg-neutral-300 dark:bg-neutral-700 text-neutral-500 dark:text-neutral-500 cursor-not-allowed'
                }`}
              >
                {isLastStep ? 'Complete Setup' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
