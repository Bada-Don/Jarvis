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
        return String(text || '').toLowerCase().includes(searchQuery.toLowerCase());
    };

    const showProvider = matchesSearch('LLM Provider') || matchesSearch('provider');
    const showOpenAiKey = matchesSearch('OpenAI API Key') || matchesSearch('openai_api_key');
    const showGeminiKey = matchesSearch('Gemini API Key') || matchesSearch('gemini_api_key');

    const hasVisibleSettings = showProvider || showOpenAiKey || showGeminiKey;

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
                        value={settings?.provider || 'gemini'}
                        type="select"
                        options={[
                            { value: 'gemini', label: 'Google Gemini' },
                            { value: 'openai', label: 'OpenAI' },
                        ]}
                        onChange={(value) => onChange('provider', value)}
                        helpText="Select the AI provider to use for planning tasks."
                        onReset={() => onReset('provider')}
                        highlight={searchQuery}
                    />
                )}

                {showGeminiKey && (
                    <FormField
                        label="Gemini API Key"
                        value={settings?.gemini_api_key}
                        type="password"
                        onChange={(value) => onChange('gemini_api_key', value)}
                        validation={[
                            {
                                type: 'required',
                                message: 'Gemini API Key is required',
                            },
                        ]}
                        helpText="Your Google Gemini API Key (Recommended)"
                        placeholder="AIza..."
                        onReset={() => onReset('gemini_api_key')}
                        highlight={searchQuery}
                    />
                )}

                {showOpenAiKey && settings?.provider === 'openai' && (
                    <FormField
                        label="OpenAI API Key"
                        value={settings?.openai_api_key}
                        type="password"
                        onChange={(value) => onChange('openai_api_key', value)}
                        validation={[
                            {
                                type: 'required',
                                message: 'OpenAI API Key is required when using OpenAI provider',
                            },
                        ]}
                        helpText="Your OpenAI API Key (Legacy Support)"
                        placeholder="sk-..."
                        onReset={() => onReset('openai_api_key')}
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
