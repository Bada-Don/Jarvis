"""
Test PyWebView connection and API availability
This creates a minimal PyWebView window to test if the API bridge works
"""
import webview
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from settings_app import SettingsAPI

# Create a simple HTML page for testing
test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>PyWebView API Test</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .test-result {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .success {
            background: #1a3a1a;
            border-color: #4caf50;
        }
        .error {
            background: #3a1a1a;
            border-color: #f44336;
        }
        .info {
            background: #1a2a3a;
            border-color: #2196f3;
        }
        button {
            background: #2196f3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #1976d2;
        }
        pre {
            background: #2a2a2a;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>PyWebView API Connection Test</h1>
    
    <div id="results"></div>
    
    <button onclick="runTests()">Run Tests</button>
    <button onclick="testGetSettings()">Test Get Settings</button>
    
    <script>
        function addResult(message, type = 'info') {
            const div = document.createElement('div');
            div.className = `test-result ${type}`;
            div.innerHTML = message;
            document.getElementById('results').appendChild(div);
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '';
        }
        
        async function runTests() {
            clearResults();
            
            // Test 1: Check if window.pywebview exists
            addResult('<strong>Test 1:</strong> Checking window.pywebview...', 'info');
            if (typeof window.pywebview !== 'undefined') {
                addResult('✓ window.pywebview exists', 'success');
            } else {
                addResult('✗ window.pywebview is undefined', 'error');
                return;
            }
            
            // Test 2: Check if window.pywebview.api exists
            addResult('<strong>Test 2:</strong> Checking window.pywebview.api...', 'info');
            if (window.pywebview.api) {
                addResult('✓ window.pywebview.api exists', 'success');
            } else {
                addResult('✗ window.pywebview.api is undefined', 'error');
                return;
            }
            
            // Test 3: Check available methods
            addResult('<strong>Test 3:</strong> Checking available API methods...', 'info');
            const methods = Object.keys(window.pywebview.api);
            if (methods.length > 0) {
                addResult(`✓ Found ${methods.length} methods: ${methods.join(', ')}`, 'success');
            } else {
                addResult('✗ No methods found on window.pywebview.api', 'error');
            }
            
            // Test 4: Try calling get_settings
            addResult('<strong>Test 4:</strong> Calling get_settings()...', 'info');
            try {
                const response = await window.pywebview.api.get_settings();
                if (response.success) {
                    addResult('✓ get_settings() returned success', 'success');
                    
                    // Check if prompts are included
                    if (response.data && response.data.prompts) {
                        addResult('✓ Prompts included in response', 'success');
                        
                        const planner = response.data.prompts.planner || {};
                        const generalLen = (planner.GENERAL_SYSTEM_PROMPT || '').length;
                        const flexisignLen = (planner.FLEXISIGN_SYSTEM_PROMPT || '').length;
                        
                        if (generalLen > 0) {
                            addResult(`✓ GENERAL_SYSTEM_PROMPT: ${generalLen} chars`, 'success');
                        } else {
                            addResult('✗ GENERAL_SYSTEM_PROMPT is empty', 'error');
                        }
                        
                        if (flexisignLen > 0) {
                            addResult(`✓ FLEXISIGN_SYSTEM_PROMPT: ${flexisignLen} chars`, 'success');
                        } else {
                            addResult('✗ FLEXISIGN_SYSTEM_PROMPT is empty', 'error');
                        }
                    } else {
                        addResult('✗ No prompts in response', 'error');
                    }
                    
                    // Show sample data
                    addResult('<strong>Sample Response Data:</strong><pre>' + 
                        JSON.stringify(response.data, null, 2).substring(0, 500) + '...</pre>', 'info');
                } else {
                    addResult('✗ get_settings() returned error: ' + 
                        (response.error?.message || 'Unknown error'), 'error');
                }
            } catch (error) {
                addResult('✗ Exception calling get_settings(): ' + error.message, 'error');
            }
        }
        
        async function testGetSettings() {
            clearResults();
            addResult('<strong>Direct get_settings() call...</strong>', 'info');
            
            try {
                const response = await window.pywebview.api.get_settings();
                addResult('<pre>' + JSON.stringify(response, null, 2) + '</pre>', 'info');
            } catch (error) {
                addResult('✗ Error: ' + error.message, 'error');
            }
        }
        
        // Auto-run tests on load
        window.addEventListener('load', () => {
            setTimeout(runTests, 500);
        });
    </script>
</body>
</html>
"""

def main():
    print("=" * 70)
    print("PyWebView API Connection Test")
    print("=" * 70)
    
    # Create API instance
    api = SettingsAPI()
    print("✓ SettingsAPI initialized")
    
    # Create window with inline HTML
    window = webview.create_window(
        title="PyWebView API Test",
        html=test_html,
        js_api=api,
        width=900,
        height=700
    )
    
    print("✓ Window created")
    print("\nStarting PyWebView...")
    print("The test page will open and automatically run tests.")
    print("Check the window for results.")
    print("=" * 70)
    
    webview.start(debug=True)

if __name__ == '__main__':
    main()
