import { useState } from 'react';
import FormField from './FormField';

const timingConfigs = [
  {
    key: 'ACTION_DELAY',
    label: 'Action Delay',
    helpText: 'Default delay after each automation step. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 10.0,
    step: 0.1,
  },
  {
    key: 'APP_LAUNCH_WAIT',
    label: 'Application Launch Wait',
    helpText: 'Extended delay after launching an application to allow it to fully load. Recommended: 2.0-5.0 seconds',
    min: 0.5,
    recommendedMin: 2.0,
    max: 30.0,
    step: 0.5,
  },
  {
    key: 'HOTKEY_DELAY',
    label: 'Hotkey Delay',
    helpText: 'Delay after pressing hotkey combinations. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
  {
    key: 'PRE_TYPE_DELAY',
    label: 'Pre-Type Delay',
    helpText: 'Small delay before typing text to ensure focus is ready. Recommended: 0.1-0.5 seconds',
    min: 0.0,
    recommendedMin: 0.1,
    max: 2.0,
    step: 0.1,
  },
  {
    key: 'SCREENSHOT_DELAY',
    label: 'Screenshot Delay',
    helpText: 'Delay before taking screenshots for vision analysis. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
  {
    key: 'WINDOW_ACTIVATION_TIMEOUT',
    label: 'Window Activation Timeout',
    helpText: 'Maximum time to wait for a window to appear. Recommended: 5.0-15.0 seconds',
    min: 1.0,
    recommendedMin: 5.0,
    max: 60.0,
    step: 1.0,
  },
  {
    key: 'WINDOW_POLL_INTERVAL',
    label: 'Window Poll Interval',
    helpText: 'How often to check for window appearance. Recommended: 0.3-1.0 seconds',
    min: 0.1,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
];

export default function TimingSettingsPanel({
  settings,
  onChange,
  onSave,
  onReset,
  searchQuery = '',
}) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);
    try {
      await onSave();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const isBelowRecommended = (config) => {
    const value = settings[config.key];
    return typeof value === 'number' && value < config.recommendedMin;
  };

  const matchesSearch = (config) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      config.label.toLowerCase().includes(query) ||
      config.key.toLowerCase().includes(query) ||
      config.helpText.toLowerCase().includes(query) ||
      String(settings[config.key]).toLowerCase().includes(query)
    );
  };

  const filteredConfigs = timingConfigs.filter(matchesSearch);

  if (searchQuery && filteredConfigs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No settings match your search query.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-secondary-200 pb-4">
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Timing Configuration</h2>
        <p className="text-sm text-secondary-600 leading-relaxed">
          Adjust timing and delay settings to optimize automation speed for your system's performance.
        </p>
      </div>

      {saveError && (
        <div className="p-4 bg-danger-50 border border-danger-300 text-danger-800 rounded-lg flex items-start animate-fade-in">
          <svg className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="font-medium">Save Error</p>
            <p className="text-sm mt-1">{saveError}</p>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {filteredConfigs.map((config) => (
          <div key={config.key}>
            <FormField
              label={config.label}
              value={settings[config.key]}
              type="number"
              onChange={(value) => onChange(config.key, value)}
              validation={[
                {
                  type: 'required',
                  message: `${config.label} is required`,
                },
                {
                  type: 'min',
                  value: config.min,
                  message: `Must be at least ${config.min}`,
                },
                {
                  type: 'max',
                  value: config.max,
                  message: `Must be at most ${config.max}`,
                },
              ]}
              helpText={config.helpText}
              unit="seconds"
              min={config.min}
              max={config.max}
              step={config.step}
              onReset={() => onReset(config.key)}
              highlight={searchQuery}
            />
            {isBelowRecommended(config) && (
              <div className="mt-2 p-3 bg-warning-50 border border-warning-300 rounded-lg text-sm text-warning-800 flex items-start animate-fade-in">
                <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium">Below Recommended Value</p>
                  <p className="mt-1">This value is below the recommended minimum of {config.recommendedMin} seconds. Lower values may cause automation failures.</p>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end pt-6 border-t border-secondary-200">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary"
        >
          {isSaving ? (
            <span className="flex items-center">
              <span className="spinner w-4 h-4 mr-2"></span>
              Saving...
            </span>
          ) : (
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Save Changes
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
