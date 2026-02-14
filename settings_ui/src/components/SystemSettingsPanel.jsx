import { useState } from 'react';
import { AlertTriangle, Check } from 'lucide-react';
import Loader from './Loader';
import FormField from './FormField';

export default function SystemSettingsPanel({
  settings,
  windowManagerSettings,
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

  // Filter settings based on search query
  const matchesSearch = (text) => {
    if (!searchQuery) return true;
    return String(text || '').toLowerCase().includes(searchQuery.toLowerCase());
  };

  const showServerUrl = matchesSearch('Server URL') || matchesSearch('server_url') || matchesSearch(settings.server_url);
  const showUsername = matchesSearch('Windows Username') || matchesSearch('windows_username') || matchesSearch(settings.windows_username);

  const showActivationAttempts = matchesSearch('Activation Attempts') || matchesSearch('activation_attempts');
  const showVerbose = matchesSearch('Verbose Logging') || matchesSearch('verbose');

  const hasVisibleSettings = showServerUrl || showUsername || showActivationAttempts || showVerbose;

  if (searchQuery && !hasVisibleSettings) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No settings match your search query.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-secondary-200 pb-4">
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">System Settings</h2>
        <p className="text-sm text-secondary-600 leading-relaxed">
          Configure basic system settings for the JARVIS local client.
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

      <div className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-white border-b pb-2">Basic Configuration</h3>

          {showServerUrl && (
            <FormField
              label="Server URL"
              value={settings.server_url}
              type="text"
              onChange={(value) => onChange('system', 'server_url', value)}
              validation={[
                {
                  type: 'required',
                  message: 'Server URL is required',
                },
                {
                  type: 'pattern',
                  value: '^https?://.+',
                  message: 'Must be a valid URL starting with http:// or https://',
                },
              ]}
              helpText="The URL of the backend server that processes automation commands"
              placeholder="http://localhost:5000"
              onReset={() => onReset('system', 'server_url')}
              highlight={searchQuery}
            />
          )}

          {showUsername && (
            <FormField
              label="Windows Username"
              value={settings.windows_username}
              type="text"
              onChange={(value) => onChange('system', 'windows_username', value)}
              validation={[
                {
                  type: 'required',
                  message: 'Windows username is required',
                },
              ]}
              helpText="Your Windows username, used for generating file paths (e.g., C:\Users\[username]\...)"
              placeholder="Enter your Windows username"
              onReset={() => onReset('system', 'windows_username')}
              highlight={searchQuery}
            />
          )}
        </div>

        {(showActivationAttempts || showVerbose) && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white border-b pb-2">Window Management</h3>

            {showActivationAttempts && (
              <FormField
                label="Activation Attempts"
                value={windowManagerSettings.activation_attempts}
                type="number"
                onChange={(value) => onChange('window_manager', 'activation_attempts', value)}
                validation={[
                  {
                    type: 'min',
                    value: 1,
                    message: 'Must be at least 1',
                  },
                ]}
                helpText="Number of times to try activating a window before failing"
                min={1}
                max={10}
                onReset={() => onReset('window_manager', 'activation_attempts')}
                highlight={searchQuery}
              />
            )}

            {showVerbose && (
              <FormField
                label="Verbose Logging"
                value={windowManagerSettings.verbose}
                type="boolean"
                onChange={(value) => onChange('window_manager', 'verbose', value)}
                helpText="Enable detailed logging for window management operations"
                onReset={() => onReset('window_manager', 'verbose')}
                highlight={searchQuery}
              />
            )}
          </div>
        )}
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
