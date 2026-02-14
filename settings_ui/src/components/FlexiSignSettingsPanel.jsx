import { useState } from "react";
import { Info } from "lucide-react";
import FormField from "./FormField";

export default function FlexiSignSettingsPanel({
  settings,
  onChange,
  onSave,
  onReset,
  searchQuery = "",
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

  const matchesSearch = (text) => {
    if (!searchQuery) return true;
    return String(text || '').toLowerCase().includes(searchQuery.toLowerCase());
  };

  const showProcessName =
    matchesSearch("Process Name") ||
    matchesSearch("process_name") ||
    matchesSearch(settings.process_name);
  const showExePath =
    matchesSearch("Executable Path") ||
    matchesSearch("exe_path") ||
    matchesSearch(settings.exe_path);
  const showWindowTitle =
    matchesSearch("Window Title") ||
    matchesSearch("window_title") ||
    matchesSearch(settings.window_title);
  const showModalEnabled =
    matchesSearch("Startup Modal") || matchesSearch("startup_modal_enabled");
  const showModalTitle =
    matchesSearch("Modal Title") ||
    matchesSearch("startup_modal_title") ||
    matchesSearch(settings.startup_modal_title);
  const showModalButton =
    matchesSearch("Modal Button") ||
    matchesSearch("startup_modal_button") ||
    matchesSearch(settings.startup_modal_button);
  const showModalTimeout =
    matchesSearch("Modal Timeout") || matchesSearch("startup_modal_timeout");

  const hasBasicSettings = showProcessName || showExePath || showWindowTitle;
  const hasModalSettings =
    showModalEnabled || showModalTitle || showModalButton || showModalTimeout;
  const hasVisibleSettings = hasBasicSettings || hasModalSettings;

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
        <h2 className="text-xl font-semibold text-white mb-2">
          FlexiSIGN Settings
        </h2>
        <p className="text-sm text-gray-600">
          Configure settings specific to FlexiSIGN automation for number plate
          and signage creation.
        </p>
      </div>

      {saveError && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {saveError}
        </div>
      )}

      <div className="space-y-6">
        {hasBasicSettings && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white border-b pb-2">
              Application Configuration
            </h3>

            {showProcessName && (
              <FormField
                label="FlexiSIGN Process Name"
                value={settings.process_name}
                type="text"
                onChange={(value) => onChange("process_name", value)}
                validation={[
                  {
                    type: "required",
                    message: "Process name is required",
                  },
                ]}
                helpText="The exact process name of FlexiSIGN as it appears in Task Manager"
                placeholder="Production Suite Scanner 10.5.1 Build 1806 Protected"
                onReset={() => onReset("process_name")}
                highlight={searchQuery}
              />
            )}

            {showExePath && (
              <FormField
                label="FlexiSIGN Executable Path"
                value={settings.exe_path}
                type="path"
                onChange={(value) => onChange("exe_path", value)}
                helpText="Path to the FlexiSIGN executable file (.exe)"
                pathType="file"
                fileTypes={[".exe"]}
                placeholder="C:\\Program Files\\SAi\\FlexiSIGN\\FlexiSIGN.exe"
                onReset={() => onReset("exe_path")}
                highlight={searchQuery}
              />
            )}

            {showWindowTitle && (
              <FormField
                label="FlexiSIGN Window Title"
                value={settings.window_title}
                type="text"
                onChange={(value) => onChange("window_title", value)}
                validation={[
                  {
                    type: "required",
                    message: "Window title is required",
                  },
                ]}
                helpText="The window title used to identify the FlexiSIGN application window"
                placeholder="FlexiSIGN-PRO"
                onReset={() => onReset("window_title")}
                highlight={searchQuery}
              />
            )}
          </div>
        )}

        {hasModalSettings && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white border-b pb-2">
              Startup Modal Configuration
            </h3>

            {showModalEnabled && (
              <FormField
                label="Enable Startup Modal Handling"
                value={settings.startup_modal_enabled}
                type="boolean"
                onChange={(value) => onChange("startup_modal_enabled", value)}
                helpText="Enable automatic handling of the startup modal dialog that appears when FlexiSIGN launches"
                onReset={() => onReset("startup_modal_enabled")}
                highlight={searchQuery}
              />
            )}

            <div
              className={`space-y-4 transition-opacity ${settings.startup_modal_enabled ? "opacity-100" : "opacity-50"
                }`}
            >
              {showModalTitle && (
                <FormField
                  label="Startup Modal Title"
                  value={settings.startup_modal_title}
                  type="text"
                  onChange={(value) => onChange("startup_modal_title", value)}
                  disabled={!settings.startup_modal_enabled}
                  validation={
                    settings.startup_modal_enabled
                      ? [
                        {
                          type: "required",
                          message:
                            "Modal title is required when modal handling is enabled",
                        },
                      ]
                      : []
                  }
                  helpText="The title of the startup modal window"
                  placeholder="FlexiSIGN"
                  onReset={() => onReset("startup_modal_title")}
                  highlight={searchQuery}
                />
              )}

              {showModalButton && (
                <FormField
                  label="Startup Modal Button Text"
                  value={settings.startup_modal_button}
                  type="text"
                  onChange={(value) => onChange("startup_modal_button", value)}
                  disabled={!settings.startup_modal_enabled}
                  validation={
                    settings.startup_modal_enabled
                      ? [
                        {
                          type: "required",
                          message:
                            "Button text is required when modal handling is enabled",
                        },
                      ]
                      : []
                  }
                  helpText="The text on the button to click in the startup modal"
                  placeholder="OK"
                  onReset={() => onReset("startup_modal_button")}
                  highlight={searchQuery}
                />
              )}

              {showModalTimeout && (
                <FormField
                  label="Startup Modal Timeout"
                  value={settings.startup_modal_timeout}
                  type="number"
                  onChange={(value) => onChange("startup_modal_timeout", value)}
                  disabled={!settings.startup_modal_enabled}
                  validation={[
                    {
                      type: "min",
                      value: 5,
                      message: "Timeout must be at least 5 seconds",
                    },
                    {
                      type: "max",
                      value: 120,
                      message: "Timeout must be at most 120 seconds",
                    },
                  ]}
                  helpText="Maximum time to wait for the startup modal to appear"
                  unit="seconds"
                  min={5}
                  max={120}
                  step={5}
                  onReset={() => onReset("startup_modal_timeout")}
                  highlight={searchQuery}
                />
              )}
            </div>

            {!settings.startup_modal_enabled && !searchQuery && (
              <div className="p-3 bg-blue-50 border border-blue-300 rounded text-sm text-blue-800 flex items-center">
                <Info className="w-4 h-4 mr-2" />
                Startup modal handling is disabled. The system will not
                automatically handle FlexiSIGN's startup dialog.
              </div>
            )}
          </div>
        )}
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
