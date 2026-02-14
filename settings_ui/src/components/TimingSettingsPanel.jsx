import { useState } from 'react';
import { AlertTriangle, Check } from 'lucide-react';
import Loader from './Loader';
import FormField from './FormField';

const timingConfigs = [
  {
    key: 'action_delay',
    label: 'Action Delay',
    helpText: 'Default delay after each automation step. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 10.0,
    step: 0.1,
  },
  {
    key: 'app_launch_wait',
    label: 'Application Launch Wait',
    helpText: 'Extended delay after launching an application to allow it to fully load. Recommended: 2.0-5.0 seconds',
    min: 0.5,
    recommendedMin: 2.0,
    max: 30.0,
    step: 0.5,
  },
  {
    key: 'hotkey_delay',
    label: 'Hotkey Delay',
    helpText: 'Delay after pressing hotkey combinations. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
  {
    key: 'pre_type_delay',
    label: 'Pre-Type Delay',
    helpText: 'Small delay before typing text to ensure focus is ready. Recommended: 0.1-0.5 seconds',
    min: 0.0,
    recommendedMin: 0.1,
    max: 2.0,
    step: 0.1,
  },
  {
    key: 'screenshot_delay',
    label: 'Screenshot Delay',
    helpText: 'Delay before taking screenshots for vision analysis. Recommended: 0.3-1.0 seconds',
    min: 0.0,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
  {
    key: 'window_activation_timeout',
    label: 'Window Activation Timeout',
    helpText: 'Maximum time to wait for a window to appear. Recommended: 5.0-15.0 seconds',
    min: 1.0,
    recommendedMin: 5.0,
    max: 60.0,
    step: 1.0,
  },
  {
    key: 'window_poll_interval',
    label: 'Window Poll Interval',
    helpText: 'How often to check for window appearance. Recommended: 0.3-1.0 seconds',
    min: 0.1,
    recommendedMin: 0.3,
    max: 5.0,
    step: 0.1,
  },
  {
    key: 'retry_delay',
    label: 'Retry Delay',
    helpText: 'Delay before retrying after a verification failure. Recommended: 1.0-3.0 seconds',
    min: 0.5,
    recommendedMin: 1.0,
    max: 30.0,
    step: 0.5,
  },
  {
    key: 'verification_delay',
    label: 'Verification Delay',
    helpText: 'Delay before starting verification after task execution. Recommended: 0.5-2.0 seconds',
    min: 0.0,
    recommendedMin: 0.5,
    max: 10.0,
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
          <AlertTriangle className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
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
                <AlertTriangle className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
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
              <Loader variant="spinner" size="sm" className="mr-2" />
              Saving...
            </span>
          ) : (
            <span className="flex items-center">
              <Check className="w-4 h-4 mr-2" />
              Save Changes
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
