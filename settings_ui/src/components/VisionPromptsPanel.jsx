import { useState } from 'react';
import { Info, AlertTriangle, Eye, EyeOff } from 'lucide-react';
import PromptEditor from './PromptEditor';

const promptConfigs = [
  {
    key: 'GENERAL_VISION_PROMPT',
    label: 'General Vision Prompt',
    helpText: 'Used for identifying UI elements in general computer automation tasks',
    requiredPlaceholders: ['{screenshot}', '{task}'],
    description:
      'This prompt guides the vision model in analyzing screenshots and identifying clickable UI elements, text fields, buttons, and other interactive components.',
  },
  {
    key: 'VERIFICATION_PROMPT',
    label: 'Verification Prompt',
    helpText: 'Used for verifying task completion after execution',
    requiredPlaceholders: ['{screenshot}', '{expected_outcome}'],
    description:
      'This prompt helps the vision model verify whether a task was completed successfully by comparing the current screen state with the expected outcome.',
  },
  {
    key: 'FLEXISIGN_VISION_PROMPT',
    label: 'FlexiSIGN Vision Prompt',
    helpText: 'Specialized prompt for identifying FlexiSIGN UI elements',
    requiredPlaceholders: ['{screenshot}', '{task}'],
    description:
      'This specialized prompt helps the vision model understand FlexiSIGN-specific UI elements, toolbars, and design canvas interactions.',
  },
];

export default function VisionPromptsPanel({
  prompts,
  onChange,
  onSave,
  onReset,
}) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [activePrompt, setActivePrompt] = useState('GENERAL_VISION_PROMPT');
  const [validationErrors, setValidationErrors] = useState({});
  const [showPreview, setShowPreview] = useState(false);

  const handleSave = async () => {
    const errors = {};
    let hasErrors = false;

    promptConfigs.forEach((config) => {
      const missingPlaceholders = validatePromptPlaceholders(
        prompts[config.key],
        config.requiredPlaceholders
      );
      if (missingPlaceholders.length > 0) {
        errors[config.key] = missingPlaceholders;
        hasErrors = true;
      }
    });

    setValidationErrors(errors);

    if (hasErrors) {
      setSaveError('Some prompts are missing required placeholders. Please fix them before saving.');
      return;
    }

    setIsSaving(true);
    setSaveError(null);
    try {
      await onSave();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save prompts');
    } finally {
      setIsSaving(false);
    }
  };

  const validatePromptPlaceholders = (prompt, requiredPlaceholders) => {
    const missing = [];
    requiredPlaceholders.forEach((placeholder) => {
      if (!prompt.includes(placeholder)) {
        missing.push(placeholder);
      }
    });
    return missing;
  };

  const handlePromptChange = (key, value) => {
    onChange(key, value);
    if (validationErrors[key]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[key];
        return newErrors;
      });
    }
    if (saveError) {
      setSaveError(null);
    }
  };

  const getPreviewText = (config) => {
    let preview = prompts[config.key];
    preview = preview.replace('{screenshot}', '[Screenshot Image Data]');
    preview = preview.replace('{task}', 'Click on the "Save" button');
    preview = preview.replace('{expected_outcome}', 'File should be saved successfully');
    return preview;
  };

  const activeConfig = promptConfigs.find((c) => c.key === activePrompt);
  const missingPlaceholders = validatePromptPlaceholders(
    prompts[activePrompt],
    activeConfig.requiredPlaceholders
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">Vision Prompts</h2>
        <p className="text-sm text-gray-600">
          Configure the prompts that guide the vision model in analyzing screenshots and identifying
          UI elements for automation.
        </p>
      </div>

      {saveError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          {saveError}
        </div>
      )}

      <div className="border border-[#404040] rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">About Vision Prompts</p>
            <p className='text-gray-600'>
              Vision prompts must include specific placeholders that will be replaced with dynamic
              content at runtime. Missing required placeholders will prevent the system from
              functioning correctly.
            </p>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-4">
          {promptConfigs.map((config) => (
            <button
              key={config.key}
              onClick={() => setActivePrompt(config.key)}
              className={`
                py-2 px-3 border-b-2 font-medium text-sm transition-colors relative
                ${
                  activePrompt === config.key
                    ? 'border-[#16e2d7] text-[#16e2d7]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {config.label}
              {validationErrors[config.key] && validationErrors[config.key].length > 0 && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div>
        <div className="mb-4 p-3 border border-[#404040] rounded">
          <p className="text-sm text-gray-700 mb-2">{activeConfig.description}</p>
          <div className="text-xs text-gray-600">
            <span className="font-medium text-[#737373]">Required placeholders:</span>{' '}
            {activeConfig.requiredPlaceholders.map((ph, idx) => (
              <span key={ph}>
                <code className="bg-[#404040] text-white px-1 py-0.5 rounded">{ph}</code>
                {idx < activeConfig.requiredPlaceholders.length - 1 && ', '}
              </span>
            ))}
          </div>
        </div>

        {missingPlaceholders.length > 0 && (
          <div className="mb-4 p-3 border border-[#404040] text-red-700 rounded">
            <p className="font-medium text-sm mb-1 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Missing Required Placeholders:
            </p>
            <ul className="list-disc list-inside text-sm ml-6 text-gray-600 ">
              {missingPlaceholders.map((ph) => (
                <li key={ph}>
                  <code className="bg-[#404040] text-white px-1 py-0.5 rounded">{ph}</code>
                </li>
              ))}
            </ul>
          </div>
        )}

        <PromptEditor
          value={prompts[activePrompt]}
          onChange={(value) => handlePromptChange(activePrompt, value)}
          language="markdown"
          height="450px"
          label={activeConfig.label}
          helpText={activeConfig.helpText}
          showActions={false}
          onReset={() => onReset(activePrompt)}
        />

        <div className="mt-4 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowPreview(!showPreview)}
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
          >
            {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            <span>{showPreview ? 'Hide' : 'Show'} Preview with Sample Data</span>
          </button>
        </div>

        {showPreview && (
          <div className="mt-4 p-4 border border-[#404040] rounded">
            <p className="text-xs font-medium text-gray-700 mb-2">
              Preview (with placeholders replaced):
            </p>
            <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono bg-white p-3 rounded border border-gray-200 max-h-64 overflow-y-auto">
              {getPreviewText(activeConfig)}
            </pre>
          </div>
        )}
      </div>

      <div className="flex justify-end pt-4 border-t border-[#404040]">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`
            px-6 py-2 rounded-md font-medium transition-colors
            ${
              isSaving
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }
          `}
        >
          {isSaving ? 'Saving...' : 'Save All Prompts'}
        </button>
      </div>
    </div>
  );
}
