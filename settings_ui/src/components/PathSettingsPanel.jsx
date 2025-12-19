import { useState } from 'react';
import { AlertTriangle, Check } from 'lucide-react';
import Loader from './Loader';
import FormField from './FormField';

const pathConfigs = [
  {
    key: 'DOWNLOADS_PATH',
    label: 'Downloads Folder',
    helpText: 'Path to your Downloads folder',
    pathType: 'folder',
    required: false,
  },
  {
    key: 'DESKTOP_PATH',
    label: 'Desktop Folder',
    helpText: 'Path to your Desktop folder',
    pathType: 'folder',
    required: false,
  },
  {
    key: 'DOCUMENTS_PATH',
    label: 'Documents Folder',
    helpText: 'Path to your Documents folder',
    pathType: 'folder',
    required: false,
  },
];

export default function PathSettingsPanel({
  settings,
  onChange,
  onSave,
  onReset,
  searchQuery = '',
}) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

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

  const handlePathChange = (key, value) => {
    onChange(key, value);
    if (validationErrors[key]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
  };

  const matchesSearch = (config) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      config.label.toLowerCase().includes(query) ||
      config.key.toLowerCase().includes(query) ||
      config.helpText.toLowerCase().includes(query) ||
      String(settings[config.key] || '').toLowerCase().includes(query)
    );
  };

  const matchesSearchDynamic = (key) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
    return (
      label.toLowerCase().includes(query) ||
      key.toLowerCase().includes(query) ||
      String(settings[key] || '').toLowerCase().includes(query)
    );
  };

  const filteredConfigs = pathConfigs.filter(matchesSearch);
  const dynamicKeys = Object.keys(settings)
    .filter((key) => !pathConfigs.find((c) => c.key === key))
    .filter(matchesSearchDynamic);

  const allPathKeys = [
    ...pathConfigs.map((c) => c.key),
    ...Object.keys(settings).filter((key) => !pathConfigs.find((c) => c.key === key)),
  ];

  const hasVisibleSettings = filteredConfigs.length > 0 || dynamicKeys.length > 0;

  if (searchQuery && !hasVisibleSettings) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No settings match your search query.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">Path Management</h2>
        <p className="text-sm text-gray-600">
          Configure file paths and directories used by the automation system.
        </p>
      </div>

      {saveError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {saveError}
        </div>
      )}

      <div className="space-y-4">
        {filteredConfigs.map((config) => (
          <div key={config.key}>
            <FormField
              label={config.label}
              value={settings[config.key] || ''}
              type="path"
              onChange={(value) => handlePathChange(config.key, value)}
              validation={
                config.required
                  ? [
                      {
                        type: 'required',
                        message: `${config.label} is required`,
                      },
                    ]
                  : []
              }
              helpText={config.helpText}
              pathType={config.pathType}
              fileTypes={config.fileTypes}
              placeholder={`Select ${config.pathType === 'folder' ? 'folder' : 'file'} path...`}
              onReset={() => onReset(config.key)}
              highlight={searchQuery}
            />
            {validationErrors[config.key] && (
              <div className="mt-1 p-2 bg-red-50 border border-red-300 rounded text-sm text-red-700">
                {validationErrors[config.key]}
              </div>
            )}
          </div>
        ))}

        {dynamicKeys.map((key) => (
          <div key={key}>
            <FormField
              label={key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              value={settings[key] || ''}
              type="path"
              onChange={(value) => handlePathChange(key, value)}
              helpText={`Custom path setting: ${key}`}
              pathType="folder"
              placeholder="Select path..."
              onReset={() => onReset(key)}
              highlight={searchQuery}
            />
          </div>
        ))}

        {!searchQuery && allPathKeys.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No path settings configured.</p>
            <p className="text-sm mt-2">Path settings will appear here when defined in config.py</p>
          </div>
        )}
      </div>

      <div className="flex justify-end pt-4 border-t border-gray-200">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`
            px-6 py-2 rounded-md font-medium transition-colors flex items-center
            ${
              isSaving
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
          `}
        >
          {isSaving ? (
            <>
              <Loader variant="spinner" size="sm" className="mr-2" />
              Saving...
            </>
          ) : (
            <>
              <Check className="w-4 h-4 mr-2" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );
}
