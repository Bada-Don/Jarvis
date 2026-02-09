import { StrictMode, Component } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

console.log('main.jsx: Starting React app initialization...');

// Add error boundary
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    console.error('ErrorBoundary caught error:', error);
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary details:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '20px',
          fontFamily: 'Arial, sans-serif',
          backgroundColor: '#0a0a0a',
          color: '#fafafa'
        }}>
          <h1 style={{ color: '#ef4444', marginBottom: '20px' }}>Application Error</h1>
          <p style={{ marginBottom: '10px' }}>Something went wrong:</p>
          <pre style={{
            backgroundColor: '#18181b',
            padding: '20px',
            borderRadius: '8px',
            maxWidth: '600px',
            overflow: 'auto'
          }}>
            {this.state.error?.toString()}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}

try {
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    console.error('Root element not found!');
    document.body.innerHTML = '<div style="color: red; padding: 20px;">Error: Root element not found</div>';
  } else {
    console.log('Root element found, creating React root...');
    const root = createRoot(rootElement);
    console.log('React root created, rendering app...');
    root.render(
      <StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </StrictMode>
    );
    console.log('App rendered successfully');
  }
} catch (error) {
  console.error('Fatal error during initialization:', error);
  document.body.innerHTML = `<div style="color: red; padding: 20px;">Fatal Error: ${error.message}</div>`;
}
