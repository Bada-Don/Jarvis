import { useState } from 'react';
import { api } from '../api';

export default function ConfigurationProfilesPanel({ onImportComplete }) {
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [message, setMessage] = useState(null);
  const [warnings, setWarnings] = useState([]);

  const handleExport = async () => {
    setIsExporting(true);
    setMessage(null);
    setWarnings([]);

    try {
      const filePath = await api.browseFile('Export Configuration', ['*.json'], true);
      
      if (!filePath) {
        setIsExporting(false);
        return;
      }

      const finalPath = filePath.endsWith('.json') ? filePath : `${filePath}.json`;
      await api.exportConfig(finalPath);
      
      setMessage({
        type: 'success',
        text: `Configuration exported successfully to ${finalPath}`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to export configuration'
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async () => {
    setIsImporting(true);
    setMessage(null);
    setWarnings([]);

    try {
      const filePath = await api.browseFile('Import Configuration', ['*.json'], false);
      
      if (!filePath) {
        setIsImporting(false);
        return;
      }

      const result = await api.importConfig(filePath);
      
      if (result.warnings && result.warnings.length > 0) {
        setWarnings(result.warnings);
        setMessage({
          type: 'warning',
          text: 'Configuration imported with warnings. Some settings were skipped.'
        });
      } else {
        setMessage({
          type: 'success',
          text: 'Configuration imported successfully!'
        });
      }

      if (onImportComplete) {
        onImportComplete();
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Failed to import configuration'
      });
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">Configuration Profiles</h2>
        <p className="text-gray-600">
          Export your current configuration to share with others or create backups.
          Import configurations to quickly switch between different setups.
        </p>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-100 border border-green-400 text-green-700'
              : message.type === 'warning'
              ? 'bg-yellow-100 border border-yellow-400 text-yellow-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}
        >
          <p className="font-medium">{message.text}</p>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-800 mb-2">Import Warnings:</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
            {warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="flex items-start mb-4">
            <div className="text-4xl mr-4">📤</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">Export Configuration</h3>
              <p className="text-sm text-gray-600">
                Save your current settings and prompts to a JSON file
              </p>
            </div>
          </div>

          <div className="space-y-3 mb-4 text-sm text-gray-600">
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Includes all settings from all categories</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Includes all AI prompts (planner and vision)</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Includes metadata (export date, version, name)</span>
            </div>
          </div>

          <button
            onClick={handleExport}
            disabled={isExporting}
            className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
              isExporting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isExporting ? 'Exporting...' : 'Export Configuration'}
          </button>
        </div>

        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="flex items-start mb-4">
            <div className="text-4xl mr-4">📥</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">Import Configuration</h3>
              <p className="text-sm text-gray-600">
                Load settings and prompts from a previously exported JSON file
              </p>
            </div>
          </div>

          <div className="space-y-3 mb-4 text-sm text-gray-600">
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Validates imported configuration structure</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Applies all valid settings automatically</span>
            </div>
            <div className="flex items-start">
              <span className="mr-2">✓</span>
              <span>Reports warnings for invalid settings</span>
            </div>
          </div>

          <button
            onClick={handleImport}
            disabled={isImporting}
            className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
              isImporting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isImporting ? 'Importing...' : 'Import Configuration'}
          </button>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-2 flex items-center">
          <span className="mr-2">💡</span>
          Tips
        </h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
          <li>Export your configuration before making major changes to create a backup</li>
          <li>Share configuration files with team members to ensure consistent settings</li>
          <li>Configuration files include metadata like export date and version for tracking</li>
          <li>Invalid settings in imported files will be skipped with warnings displayed</li>
        </ul>
      </div>
    </div>
  );
}
