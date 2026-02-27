import { useState, useEffect } from 'react';
import { Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { api } from '../../api';

/**
 * ApiKeyStep Component
 * 
 * Step for configuring API keys (Gemini and OpenAI).
 * Validates API keys before allowing progression.
 * 
 * Requirements: 2.3, 2.4, 2.6, 10.1
 */
export default function ApiKeyStep({ apiKeys, onChange, onValidationChange }) {
  const [showGemini, setShowGemini] = useState(false);
  const [showOpenAI, setShowOpenAI] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationSuccess, setValidationSuccess] = useState(false);
  const [errors, setErrors] = useState({
    gemini: null,
    openai: null,
  });
  const [touched, setTouched] = useState({
    gemini: false,
    openai: false,
  });

  // Validate API keys whenever they change
  useEffect(() => {
    validateApiKeys();
  }, [apiKeys.gemini, apiKeys.openai]);

  const validateApiKeys = async () => {
    const newErrors = {
      gemini: null,
      openai: null,
    };

    // Gemini is required
    if (!apiKeys.gemini || apiKeys.gemini.trim() === '') {
      newErrors.gemini = 'Gemini API key is required';
      onValidationChange(false);
      setErrors(newErrors);
      return;
    }

    // Basic format validation for Gemini
    if (apiKeys.gemini.length < 20) {
      newErrors.gemini = 'API key appears to be too short';
      onValidationChange(false);
      setErrors(newErrors);
      return;
    }

    // OpenAI is optional, but validate if provided
    if (apiKeys.openai && apiKeys.openai.trim() !== '') {
      if (apiKeys.openai.length < 20) {
        newErrors.openai = 'API key appears to be too short';
        onValidationChange(false);
        setErrors(newErrors);
        return;
      }
    }

    // If we get here, basic validation passed
    setErrors(newErrors);
    onValidationChange(true);
  };

  const handleGeminiChange = (e) => {
    const value = e.target.value;
    onChange({ gemini: value });
    setTouched((prev) => ({ ...prev, gemini: true }));
    setValidationSuccess(false); // Reset validation success when key changes
  };

  const handleOpenAIChange = (e) => {
    const value = e.target.value;
    onChange({ openai: value });
    setTouched((prev) => ({ ...prev, openai: true }));
    setValidationSuccess(false); // Reset validation success when key changes
  };

  const handleTestConnection = async () => {
    setValidating(true);
    setValidationSuccess(false);
    setErrors({ gemini: null, openai: null });

    try {
      // Note: We're doing basic validation only since actual API testing
      // requires making real API calls which may fail due to network issues
      // The keys will be validated when actually used

      // Basic format validation for Gemini
      if (apiKeys.gemini) {
        if (apiKeys.gemini.length < 20) {
          setErrors((prev) => ({ ...prev, gemini: 'API key appears to be too short' }));
          onValidationChange(false);
          setValidating(false);
          return;
        }

        // Check if it looks like a valid Gemini key (starts with expected prefix)
        if (!apiKeys.gemini.startsWith('AIza')) {
          setErrors((prev) => ({
            ...prev,
            gemini: 'Gemini API keys typically start with "AIza". Please verify your key.'
          }));
          onValidationChange(false);
          setValidating(false);
          return;
        }
      }

      // Basic format validation for OpenAI if provided
      if (apiKeys.openai) {
        if (apiKeys.openai.length < 20) {
          setErrors((prev) => ({ ...prev, openai: 'API key appears to be too short' }));
          onValidationChange(false);
          setValidating(false);
          return;
        }

        // Check if it looks like a valid OpenAI key (starts with expected prefix)
        if (!apiKeys.openai.startsWith('sk-')) {
          setErrors((prev) => ({
            ...prev,
            openai: 'OpenAI API keys typically start with "sk-". Please verify your key.'
          }));
          onValidationChange(false);
          setValidating(false);
          return;
        }
      }

      // Basic validations passed
      setValidationSuccess(true);
      onValidationChange(true);

      // Show success message
      setErrors({
        gemini: null,
        openai: null,
      });
    } catch (error) {
      console.error('API key validation error:', error);
      setErrors({
        gemini: 'Failed to validate API keys. Please check your input.',
        openai: null,
      });
      onValidationChange(false);
    } finally {
      setValidating(false);
    }
  };

  const hasGeminiError = touched.gemini && errors.gemini;
  const hasOpenAIError = touched.openai && errors.openai;

  return (
    <div className="space-y-6">
      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900 dark:text-blue-100">
            <p className="font-medium mb-1">Gemini API Key Required</p>
            <p className="text-blue-700 dark:text-blue-300">
              JARVIS uses Google Gemini as its default intelligence provider. Please provide your Gemini API key to continue.
            </p>
          </div>
        </div>
      </div>

      {/* Gemini API Key */}
      <div>
        <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
          Gemini API Key <span className="text-red-500">*</span>
        </label>
        <div className="relative">
          <input
            type={showGemini ? 'text' : 'password'}
            value={apiKeys.gemini}
            onChange={handleGeminiChange}
            placeholder="Enter your Gemini API key"
            className={`w-full px-4 py-3 pr-12 rounded-lg border ${hasGeminiError
                ? 'border-red-500 focus:ring-red-500'
                : 'border-neutral-300 dark:border-neutral-700 focus:ring-primary'
              } bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:ring-2 transition-colors`}
          />
          <button
            type="button"
            onClick={() => setShowGemini(!showGemini)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors"
          >
            {showGemini ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
        {hasGeminiError && (
          <div className="flex items-center gap-2 mt-2 text-sm text-red-600 dark:text-red-400">
            <AlertCircle className="w-4 h-4" />
            <span>{errors.gemini}</span>
          </div>
        )}
        <p className="mt-2 text-xs text-neutral-500 dark:text-neutral-400">
          Get your API key from{' '}
          <a
            href="https://aistudio.google.com/app/apikey"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            Google AI Studio
          </a>
        </p>
      </div>

      {/* OpenAI API Key */}
      <div className="pt-4 border-t border-neutral-200 dark:border-neutral-800">
        <details className="group">
          <summary className="flex items-center justify-between cursor-pointer list-none">
            <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400 group-open:text-neutral-900 dark:group-open:text-neutral-100 transition-colors">
              Advanced: Use OpenAI (Optional)
            </span>
            <span className="text-xs text-neutral-400 transition-transform group-open:rotate-180">▼</span>
          </summary>
          <div className="mt-4 space-y-4">
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
              OpenAI API Key
            </label>
            <div className="relative">
              <input
                type={showOpenAI ? 'text' : 'password'}
                value={apiKeys.openai}
                onChange={handleOpenAIChange}
                placeholder="Enter your OpenAI API key (optional)"
                className={`w-full px-4 py-3 pr-12 rounded-lg border ${hasOpenAIError
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-neutral-300 dark:border-neutral-700 focus:ring-primary'
                  } bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:ring-2 transition-colors`}
              />
              <button
                type="button"
                onClick={() => setShowOpenAI(!showOpenAI)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 transition-colors"
              >
                {showOpenAI ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {hasOpenAIError && (
              <div className="flex items-center gap-2 mt-2 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span>{errors.openai}</span>
              </div>
            )}
          </div>
        </details>
      </div>

      {/* Test Connection Button */}
      <button
        onClick={handleTestConnection}
        disabled={validating || !apiKeys.gemini}
        className={`w-full px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${validationSuccess
            ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/50'
            : validating || !apiKeys.gemini
              ? 'bg-neutral-300 dark:bg-neutral-700 text-neutral-500 cursor-not-allowed'
              : 'bg-primary/10 text-primary hover:bg-primary/20 border border-primary/30'
          }`}
      >
        {validating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Validating Format...</span>
          </>
        ) : validationSuccess ? (
          <>
            <CheckCircle className="w-5 h-5" />
            <span>Format Valid ✓</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-5 h-5" />
            <span>Validate Format</span>
          </>
        )}
      </button>

      {/* Success Message */}
      {validationSuccess && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 animate-fade-in">
          <div className="flex items-start gap-2">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-green-900 dark:text-green-100">
              <p className="font-medium">API Keys Look Good!</p>
              <p className="text-green-700 dark:text-green-300 text-xs mt-1">
                Format validation passed. Keys will be tested when you use JARVIS.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
