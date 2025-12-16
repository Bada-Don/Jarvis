import { useState } from 'react';
import FormField from './FormField';

export default function SystemSettingsPanel({
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

  // Filter settings based on search query
  const matchesSearch = (text) => {
    if (!searchQuery) return true;
    return text.toLowerCase().includes(searchQuery.toLowerCase());
  };

  const showServerUrl = matchesSearch('Server URL') || matchesSearch('SERVER_URL') || matchesSearch(settings.SERVER_URL);
  const showUsername = matchesSearch('Windows Username') || matchesSearch('WINDOWS_USERNAME') || matchesSearch(settings.WINDOWS_USERNAME);

  const hasVisibleSettings = showServerUrl || showUsername;

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
        {showServerUrl && (
          <FormField
            label="Server URL"
            value={settings.SERVER_URL}
            type="text"
            onChange={(value) => onChange('SERVER_URL', value)}
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
            onReset={() => onReset('SERVER_URL')}
            highlight={searchQuery}
          />
        )}

        {showUsername && (
          <FormField
            label="Windows Username"
            value={settings.WINDOWS_USERNAME}
            type="text"
            onChange={(value) => onChange('WINDOWS_USERNAME', value)}
            validation={[
              {
                type: 'required',
                message: 'Windows username is required',
              },
            ]}
            helpText="Your Windows username, used for generating file paths (e.g., C:\Users\[username]\...)"
            placeholder="Enter your Windows username"
            onReset={() => onReset('WINDOWS_USERNAME')}
            highlight={searchQuery}
          />
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
