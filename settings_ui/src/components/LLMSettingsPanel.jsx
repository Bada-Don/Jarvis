import { useState } from 'react';
import { AlertTriangle, Check, Bot } from 'lucide-react';
import Loader from './Loader';
import FormField from './FormField';

export default function LLMSettingsPanel({
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

    const showProvider = matchesSearch('LLM Provider') || matchesSearch('LLM_PROVIDER');
    const showOpenAiKey = matchesSearch('OpenAI API Key') || matchesSearch('OPENAI_API_KEY');

    const hasVisibleSettings = showProvider || showOpenAiKey;

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
                <h2 className="text-2xl font-bold text-secondary-900 mb-2 flex items-center">
                    <Bot className="w-6 h-6 mr-2" />
                    LLM Settings
                </h2>
                <p className="text-sm text-secondary-600 leading-relaxed">
                    Configure the Language Model Provider for Planner Service.
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
                {showProvider && (
                    <FormField
                        label="LLM Provider"
                        value={settings?.LLM_PROVIDER || 'gemini'}
                        type="select"
                        options={[
                            { value: 'gemini', label: 'Google Gemini' },
                            { value: 'openai', label: 'OpenAI' },
                        ]}
                        onChange={(value) => onChange('LLM_PROVIDER', value)}
                        helpText="Select the AI provider to use for planning tasks."
                        onReset={() => onReset('LLM_PROVIDER')}
                        highlight={searchQuery}
                    />
                )}

                {showOpenAiKey && (settings?.LLM_PROVIDER === 'openai') && (
                    <FormField
                        label="OpenAI API Key"
                        value={settings?.OPENAI_API_KEY}
                        type="password"
                        onChange={(value) => onChange('OPENAI_API_KEY', value)}
                        validation={[
                            {
                                type: 'required',
                                message: 'OpenAI API Key is required when using OpenAI provider',
                            },
                        ]}
                        helpText="Your OpenAI API Key (sk-...)"
                        placeholder="sk-..."
                        onReset={() => onReset('OPENAI_API_KEY')}
                        highlight={searchQuery}
                    />
                )}

                {showOpenAiKey && (settings?.LLM_PROVIDER !== 'openai') && (
                    <div className="opacity-50 pointer-events-none">
                        <FormField
                            label="OpenAI API Key"
                            value={settings?.OPENAI_API_KEY}
                            type="password"
                            onChange={() => { }}
                            helpText="Switch provider to OpenAI to configure this key."
                            placeholder="sk-..."
                            disabled={true}
                            highlight={searchQuery}
                        />
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
