#!/usr/bin/env python3
"""Simple test to verify PyWebView is working"""

import webview

def main():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                text-align: center;
                color: white;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
            }
            button {
                padding: 15px 30px;
                font-size: 1.2em;
                background: white;
                color: #667eea;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            button:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PyWebView Test</h1>
            <p>If you can see this, PyWebView is working!</p>
            <button onclick="alert('JavaScript is working!')">Test JavaScript</button>
        </div>
    </body>
    </html>
    """
    
    window = webview.create_window('PyWebView Test', html=html, width=800, height=600)
    webview.start(debug=True)

if __name__ == "__main__":
    main()
