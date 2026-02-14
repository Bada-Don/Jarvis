import { useState } from "react";
import { AlertTriangle, Info } from "lucide-react";
import FormField from "./FormField";

const presets = [
  {
    name: "Fast Testing",
    description: "Quick iterations with minimal verification",
    settings: {
      enabled: false,
      max_retries: 0,
      confidence_threshold: 0.6,
    },
  },
  {
    name: "Production",
    description: "Balanced verification for production use",
    settings: {
      enabled: true,
      max_retries: 2,
      confidence_threshold: 0.7,
    },
  },
  {
    name: "Critical Tasks",
    description: "Maximum verification for critical operations",
    settings: {
      enabled: true,
      max_retries: 5,
      confidence_threshold: 0.85,
    },
  },
];

export default function VerificationSettingsPanel({
  settings,
  onChange,
  onSave,
  onReset,
}) {
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const handleSave = async () => {
    setIsSaving(true);
    setSaveError(null);
    try {
      await onSave();
    } catch (err) {
      setSaveError(
        err instanceof Error ? err.message : "Failed to save settings"
      );
    } finally {
      setIsSaving(false);
    }
  };

  const applyPreset = (preset) => {
    Object.entries(preset.settings).forEach(([key, value]) => {
      onChange(key, value);
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white mb-2">
          Verification Settings
        </h2>
        <p className="text-sm text-gray-600">
          Configure verification and retry settings to control how the system
          validates task completion.
        </p>
      </div>

      {saveError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {saveError}
        </div>
      )}

      <div className="space-y-3">
        <h3 className="text-sm font-medium text-white">Quick Presets</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {presets.map((preset) => (
            <button
              key={preset.name}
              onClick={() => applyPreset(preset)}
              className="p-4 border-2  border-[#3f3f46] rounded-lg hover:border-[#737373] hover:bg-[#171717] transition-colors text-left"
            >
              <div className="font-medium text-white mb-1">{preset.name}</div>
              <div className="text-xs text-gray-600">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white border-b pb-2">
          Verification Configuration
        </h3>

        <FormField
          label="Enable Verification"
          value={settings.enabled}
          type="boolean"
          onChange={(value) => onChange("enabled", value)}
          helpText="Enable task verification after execution to confirm successful completion"
          onReset={() => onReset("enabled")}
        />

        {!settings.enabled && (
          <div className="p-3 bg-amber-50 border border-amber-300 rounded text-sm text-amber-800 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2" />
            Verification is disabled. Tasks will execute without confirmation of
            success.
          </div>
        )}

        <div
          className={`space-y-4 transition-opacity ${settings.enabled ? "opacity-100" : "opacity-50"
            }`}
        >
          <FormField
            label="Maximum Retries"
            value={settings.max_retries}
            type="number"
            onChange={(value) => onChange("max_retries", value)}
            disabled={!settings.enabled}
            validation={[
              {
                type: "min",
                value: 0,
                message: "Must be at least 0",
              },
              {
                type: "max",
                value: 10,
                message: "Must be at most 10",
              },
            ]}
            helpText="Maximum number of retry attempts if verification fails"
            min={0}
            max={10}
            step={1}
            onReset={() => onReset("max_retries")}
          />

          <FormField
            label="Confidence Threshold"
            value={settings.confidence_threshold}
            type="number"
            onChange={(value) => onChange("confidence_threshold", value)}
            disabled={!settings.enabled}
            validation={[
              {
                type: "min",
                value: 0.0,
                message: "Must be between 0.0 and 1.0",
              },
              {
                type: "max",
                value: 1.0,
                message: "Must be between 0.0 and 1.0",
              },
            ]}
            helpText="Minimum confidence score (0.0-1.0) for successful verification. Higher values require more certainty."
            min={0.0}
            max={1.0}
            step={0.05}
            onReset={() => onReset("confidence_threshold")}
          />

          {settings.confidence_threshold > 0.9 && (
            <div className="p-3 bg-blue-50 border border-blue-300 rounded text-sm text-blue-800 flex items-center">
              <Info className="w-4 h-4 mr-2" />
              High confidence threshold (
              {settings.confidence_threshold.toFixed(2)}) may cause more
              verification failures. Consider lowering if experiencing issues.
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t border-[#404040]">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`
            px-6 py-2 rounded-md font-medium transition-colors
            ${isSaving
              ? "bg-gray-400 cursor-not-allowed text-white"
              : "bg-blue-600 hover:bg-blue-700 text-white"
            }
          `}
        >
          {isSaving ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </div>
  );
}
