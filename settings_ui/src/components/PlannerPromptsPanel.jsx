import { useState } from 'react';
import { Info } from 'lucide-react';
import PromptEditor from './PromptEditor';

export default function PlannerPromptsPanel({
  prompts,
  onChange,
  onSave,
  onReset,
}) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [activeTab, setActiveTab] = useState('general');

  const handleSave = async () => {
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">Planner Prompts</h2>
        <p className="text-sm text-gray-600">
          Configure the system prompts that guide the AI planner model in converting natural language
          commands into structured execution plans.
        </p>
      </div>

      {saveError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {saveError}
        </div>
      )}

      <div className="bg-[#171717] border border-[#3f3f46] rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">About Planner Prompts</p>
            <p className='text-gray-600'>
              These prompts define how the AI model interprets user commands and generates execution
              plans. The General prompt is used for standard computer automation, while the FlexiSIGN
              prompt is specialized for number plate and signage creation tasks.
            </p>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('general')}
            className={`
              py-2 px-1 border-b-2 font-medium text-sm transition-colors
              ${
                activeTab === 'general'
                  ? 'border-[#16e2d7] text-[#16e2d7]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            General System Prompt
          </button>
          <button
            onClick={() => setActiveTab('flexisign')}
            className={`
              py-2 px-1 border-b-2 font-medium text-sm transition-colors
              ${
                activeTab === 'flexisign'
                  ? 'border-[#16e2d7] text-[#16e2d7]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            FlexiSIGN System Prompt
          </button>
        </nav>
      </div>

      {activeTab === 'general' && (
        <div>
          <PromptEditor
            value={prompts.GENERAL_SYSTEM_PROMPT}
            onChange={(value) => onChange('GENERAL_SYSTEM_PROMPT', value)}
            language="markdown"
            height="500px"
            label="General System Prompt"
            helpText="This prompt guides the AI in understanding and planning general computer automation tasks. It defines the available actions, expected output format, and behavior guidelines."
            showActions={false}
            onReset={() => onReset('GENERAL_SYSTEM_PROMPT')}
          />
          <div className="mt-4 p-3 bg-[#171717] border border-gray-200 rounded text-sm text-gray-700">
            <p className="font-medium mb-2 text-white">Prompt Guidelines:</p>
            <ul className="list-disc list-inside space-y-1 text-xs text-gray-600">
              <li>Define all available actions (click, type, hotkey, etc.)</li>
              <li>Specify the expected JSON output format</li>
              <li>Include examples of common automation patterns</li>
              <li>Set clear boundaries for what the AI should and shouldn't do</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'flexisign' && (
        <div>
          <PromptEditor
            value={prompts.FLEXISIGN_SYSTEM_PROMPT}
            onChange={(value) => onChange('FLEXISIGN_SYSTEM_PROMPT', value)}
            language="markdown"
            height="500px"
            label="FlexiSIGN System Prompt"
            helpText="This specialized prompt g   uides the AI in planning FlexiSIGN-specific tasks like creating number plates and signage. It includes domain-specific knowledge about FlexiSIGN's interface and workflows."
            showActions={false}
            onReset={() => onReset('FLEXISIGN_SYSTEM_PROMPT')}
          />
          <div className="mt-4 p-3 bg-[#171717] border border-gray-200 rounded text-sm text-gray-700">
            <p className="font-medium mb-2 text-white">FlexiSIGN-Specific Guidelines:</p>
            <ul className="list-disc list-inside space-y-1 text-xs text-gray-600">
              <li>Include FlexiSIGN menu structure and toolbar locations</li>
              <li>Define number plate creation workflows</li>
              <li>Specify text formatting and styling procedures</li>
              <li>Include common FlexiSIGN keyboard shortcuts</li>
            </ul>
          </div>
        </div>
      )}

      <div className="flex justify-end pt-4 border-t border-gray-200">
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
