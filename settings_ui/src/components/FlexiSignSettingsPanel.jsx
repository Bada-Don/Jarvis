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
    return text.toLowerCase().includes(searchQuery.toLowerCase());
  };

  const showProcessName =
    matchesSearch("Process Name") ||
    matchesSearch("FLEXISIGN_PROCESS_NAME") ||
    matchesSearch(settings.FLEXISIGN_PROCESS_NAME);
  const showExePath =
    matchesSearch("Executable Path") ||
    matchesSearch("FLEXISIGN_EXE_PATH") ||
    matchesSearch(settings.FLEXISIGN_EXE_PATH);
  const showWindowTitle =
    matchesSearch("Window Title") ||
    matchesSearch("FLEXISIGN_WINDOW_TITLE") ||
    matchesSearch(settings.FLEXISIGN_WINDOW_TITLE);
  const showModalEnabled =
    matchesSearch("Startup Modal") || matchesSearch("STARTUP_MODAL_ENABLED");
  const showModalTitle =
    matchesSearch("Modal Title") ||
    matchesSearch("STARTUP_MODAL_TITLE") ||
    matchesSearch(settings.STARTUP_MODAL_TITLE);
  const showModalButton =
    matchesSearch("Modal Button") ||
    matchesSearch("STARTUP_MODAL_BUTTON") ||
    matchesSearch(settings.STARTUP_MODAL_BUTTON);
  const showModalTimeout =
    matchesSearch("Modal Timeout") || matchesSearch("STARTUP_MODAL_TIMEOUT");

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
                value={settings.FLEXISIGN_PROCESS_NAME}
                type="text"
                onChange={(value) => onChange("FLEXISIGN_PROCESS_NAME", value)}
                validation={[
                  {
                    type: "required",
                    message: "Process name is required",
                  },
                ]}
                helpText="The exact process name of FlexiSIGN as it appears in Task Manager"
                placeholder="Production Suite Scanner 10.5.1 Build 1806 Protected"
                onReset={() => onReset("FLEXISIGN_PROCESS_NAME")}
                highlight={searchQuery}
              />
            )}

            {showExePath && (
              <FormField
                label="FlexiSIGN Executable Path"
                value={settings.FLEXISIGN_EXE_PATH}
                type="path"
                onChange={(value) => onChange("FLEXISIGN_EXE_PATH", value)}
                helpText="Path to the FlexiSIGN executable file (.exe)"
                pathType="file"
                fileTypes={[".exe"]}
                placeholder="C:\\Program Files\\SAi\\FlexiSIGN\\FlexiSIGN.exe"
                onReset={() => onReset("FLEXISIGN_EXE_PATH")}
                highlight={searchQuery}
              />
            )}

            {showWindowTitle && (
              <FormField
                label="FlexiSIGN Window Title"
                value={settings.FLEXISIGN_WINDOW_TITLE}
                type="text"
                onChange={(value) => onChange("FLEXISIGN_WINDOW_TITLE", value)}
                validation={[
                  {
                    type: "required",
                    message: "Window title is required",
                  },
                ]}
                helpText="The window title used to identify the FlexiSIGN application window"
                placeholder="FlexiSIGN-PRO"
                onReset={() => onReset("FLEXISIGN_WINDOW_TITLE")}
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
                value={settings.STARTUP_MODAL_ENABLED}
                type="boolean"
                onChange={(value) => onChange("STARTUP_MODAL_ENABLED", value)}
                helpText="Enable automatic handling of the startup modal dialog that appears when FlexiSIGN launches"
                onReset={() => onReset("STARTUP_MODAL_ENABLED")}
                highlight={searchQuery}
              />
            )}

            <div
              className={`space-y-4 transition-opacity ${
                settings.STARTUP_MODAL_ENABLED ? "opacity-100" : "opacity-50"
              }`}
            >
              {showModalTitle && (
                <FormField
                  label="Startup Modal Title"
                  value={settings.STARTUP_MODAL_TITLE}
                  type="text"
                  onChange={(value) => onChange("STARTUP_MODAL_TITLE", value)}
                  disabled={!settings.STARTUP_MODAL_ENABLED}
                  validation={
                    settings.STARTUP_MODAL_ENABLED
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
                  onReset={() => onReset("STARTUP_MODAL_TITLE")}
                  highlight={searchQuery}
                />
              )}

              {showModalButton && (
                <FormField
                  label="Startup Modal Button Text"
                  value={settings.STARTUP_MODAL_BUTTON}
                  type="text"
                  onChange={(value) => onChange("STARTUP_MODAL_BUTTON", value)}
                  disabled={!settings.STARTUP_MODAL_ENABLED}
                  validation={
                    settings.STARTUP_MODAL_ENABLED
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
                  onReset={() => onReset("STARTUP_MODAL_BUTTON")}
                  highlight={searchQuery}
                />
              )}

              {showModalTimeout && (
                <FormField
                  label="Startup Modal Timeout"
                  value={settings.STARTUP_MODAL_TIMEOUT}
                  type="number"
                  onChange={(value) => onChange("STARTUP_MODAL_TIMEOUT", value)}
                  disabled={!settings.STARTUP_MODAL_ENABLED}
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
                  onReset={() => onReset("STARTUP_MODAL_TIMEOUT")}
                  highlight={searchQuery}
                />
              )}
            </div>

            {!settings.STARTUP_MODAL_ENABLED && !searchQuery && (
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
            ${
              isSaving
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
