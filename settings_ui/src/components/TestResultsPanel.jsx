import { useState } from "react";
import { Check, X, AlertTriangle, Search } from "lucide-react";
import { api } from "../api";

export default function TestResultsPanel({ onClose }) {
  const [testReport, setTestReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runTests = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const report = await api.testConfiguration();
      setTestReport(report);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run tests");
      console.error("Failed to run tests:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "passed":
        return <Check className="text-green-600 w-5 h-5" />;
      case "failed":
        return <X className="text-red-600 w-5 h-5" />;
      case "warning":
        return <AlertTriangle className="text-yellow-600 w-5 h-5" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "passed":
        return "bg-green-50 border-green-200";
      case "failed":
        return "bg-red-50 border-red-200";
      case "warning":
        return "bg-yellow-50 border-yellow-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">
            Test Configuration
          </h2>
          <p className="text-gray-600 mt-1">
            Run validation tests to verify your configuration is correct
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={runTests}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-s hover:shadow-m disabled:shadow-none"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              Running Tests...
            </span>
          ) : (
            "Run Tests"
          )}
        </button>

        {testReport && (
          <div className="text-sm text-gray-600">
            Last run: {new Date().toLocaleTimeString()}
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5" />
            <div>
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {testReport && (
        <div className="space-y-6">
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-s hover:shadow-m transition-shadow duration-200">
              <div className="text-2xl font-bold text-gray-800">
                {testReport.summary.total_tests}
              </div>
              <div className="text-sm text-gray-600">Total Tests</div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 shadow-s hover:shadow-m transition-shadow duration-200">
              <div className="text-2xl font-bold text-green-700">
                {testReport.summary.passed_count}
              </div>
              <div className="text-sm text-green-700">Passed</div>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4 shadow-s hover:shadow-m transition-shadow duration-200">
              <div className="text-2xl font-bold text-red-700">
                {testReport.summary.failed_count}
              </div>
              <div className="text-sm text-red-700">Failed</div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-s hover:shadow-m transition-shadow duration-200">
              <div className="text-2xl font-bold text-yellow-700">
                {testReport.summary.warning_count}
              </div>
              <div className="text-sm text-yellow-700">Warnings</div>
            </div>
          </div>

          {testReport.passed.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                {getStatusIcon("passed")}
                Passed Tests ({testReport.passed.length})
              </h3>
              <div className="space-y-2">
                {testReport.passed.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg ${getStatusColor(
                      "passed"
                    )}`}
                  >
                    <div className="flex items-start gap-3">
                      {getStatusIcon("passed")}
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">
                          {result.test}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {result.message}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {testReport.failed.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                {getStatusIcon("failed")}
                Failed Tests ({testReport.failed.length})
              </h3>
              <div className="space-y-2">
                {testReport.failed.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg ${getStatusColor(
                      "failed"
                    )}`}
                  >
                    <div className="flex items-start gap-3">
                      {getStatusIcon("failed")}
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">
                          {result.test}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {result.message}
                        </div>
                        {result.guidance && (
                          <div className="mt-2 p-2 bg-white rounded border border-red-300">
                            <div className="text-xs font-semibold text-red-700 mb-1">
                              How to fix:
                            </div>
                            <div className="text-sm text-gray-700">
                              {result.guidance}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {testReport.warnings.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                {getStatusIcon("warning")}
                Warnings ({testReport.warnings.length})
              </h3>
              <div className="space-y-2">
                {testReport.warnings.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg ${getStatusColor(
                      "warning"
                    )}`}
                  >
                    <div className="flex items-start gap-3">
                      {getStatusIcon("warning")}
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">
                          {result.test}
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {result.message}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            {testReport.summary.failed_count === 0 ? (
              <div className="flex items-center gap-3 text-green-700">
                <Check className="w-6 h-6" />
                <div>
                  <div className="font-semibold text-lg">
                    Configuration Valid
                  </div>
                  <div className="text-sm">
                    All tests passed successfully. Your configuration is ready
                    to use.
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-red-700">
                <X className="w-6 h-6" />
                <div>
                  <div className="font-semibold text-lg">
                    Configuration Issues Found
                  </div>
                  <div className="text-sm">
                    Please fix the failed tests above before using this
                    configuration.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!testReport && !isLoading && !error && (
        <div className="text-center py-12 text-gray-500">
          <Search className="w-16 h-16 mx-auto mb-4" />
          <p className="text-lg">
            Click "Run Tests" to validate your configuration
          </p>
          <p className="text-sm mt-2">
            This will check all settings, paths, and connections
          </p>
        </div>
      )}
    </div>
  );
}
