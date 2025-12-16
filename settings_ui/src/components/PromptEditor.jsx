import { useState } from 'react';
import Editor from '@monaco-editor/react';

export default function PromptEditor({
  value,
  onChange,
  language = 'markdown',
  height = '400px',
  readOnly = false,
  label,
  helpText,
  onSave,
  onReset,
  showActions = true,
}) {
  const [isModified, setIsModified] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleEditorChange = (newValue) => {
    if (newValue !== undefined && newValue !== value) {
      onChange(newValue);
      setIsModified(true);
    }
  };

  const handleSave = async () => {
    if (onSave) {
      setIsSaving(true);
      try {
        await onSave();
        setIsModified(false);
      } catch (err) {
        console.error('Save error:', err);
      } finally {
        setIsSaving(false);
      }
    }
  };

  const handleReset = () => {
    if (onReset) {
      const confirmed = window.confirm(
        'Are you sure you want to reset this prompt to its default value? This action cannot be undone.'
      );
      if (confirmed) {
        onReset();
        setIsModified(false);
      }
    }
  };

  return (
    <div className="mb-6">
      {label && (
        <div className="mb-2">
          <label className="text-sm font-medium text-gray-700 flex items-center space-x-2">
            <span>{label}</span>
            {isModified && (
              <span className="text-xs text-amber-600 font-normal">
                (Modified)
              </span>
            )}
          </label>
          {helpText && (
            <p className="text-xs text-gray-500 mt-1">{helpText}</p>
          )}
        </div>
      )}

      <div className="border border-gray-300 rounded-md overflow-hidden">
        <Editor
          height={height}
          language={language}
          value={value}
          onChange={handleEditorChange}
          theme="vs-light"
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            wrappingIndent: 'indent',
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            folding: true,
            renderWhitespace: 'selection',
            scrollbar: {
              vertical: 'auto',
              horizontal: 'auto',
            },
          }}
          loading={
            <div className="flex items-center justify-center h-full bg-gray-50">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Loading editor...</p>
              </div>
            </div>
          }
        />
      </div>

      {showActions && !readOnly && (
        <div className="flex justify-between items-center mt-3">
          <div className="text-xs text-gray-500">
            {value.length} characters
          </div>
          <div className="flex space-x-2">
            {onReset && (
              <button
                type="button"
                onClick={handleReset}
                className="px-3 py-1.5 text-sm text-gray-700 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
              >
                Reset to Default
              </button>
            )}
            {onSave && (
              <button
                type="button"
                onClick={handleSave}
                disabled={!isModified || isSaving}
                className={`
                  px-4 py-1.5 text-sm text-white rounded transition-colors
                  ${
                    isModified && !isSaving
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : 'bg-gray-400 cursor-not-allowed'
                  }
                `}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            )}
          </div>
        </div>
      )}

      {readOnly && (
        <div className="mt-2 text-xs text-gray-500 italic">
          This prompt is read-only
        </div>
      )}
    </div>
  );
}
