# JARVIS Settings Interface - Setup Guide

This guide covers the setup and configuration of the JARVIS Settings Interface.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **pip** for Python package management

## Initial Setup

### 1. Frontend Setup

The frontend is a React application built with Vite and TypeScript.

```bash
cd settings_ui
npm install
```

### 2. Backend Setup

The backend uses PyWebView to host the React frontend in a native window.

```bash
cd local_client
pip install -r requirements.txt
```

Or install the specific dependencies:

```bash
pip install pywebview hypothesis
```

## Development Workflow

### Running the Frontend in Development Mode

To develop the React frontend with hot reload:

```bash
cd settings_ui
npm run dev
```

This will start the Vite dev server at `http://localhost:5173/`

### Building the Frontend

Before running the PyWebView application, you need to build the React frontend:

```bash
cd settings_ui
npm run build
```

This creates a production build in the `settings_ui/dist` directory.

### Running the Settings Interface

After building the frontend, launch the settings interface:

```bash
python local_client/run_settings.py
```

Or directly:

```bash
python local_client/settings_app.py
```

## Project Structure

```
settings_ui/
├── src/                    # React source code
│   ├── components/         # React components (to be created)
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles (Tailwind)
├── public/                # Static assets
├── dist/                  # Build output (generated)
├── package.json           # Node dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration

local_client/
├── settings_app.py        # PyWebView backend application
├── run_settings.py        # Launcher script
└── requirements.txt       # Python dependencies
```

## Dependencies

### Frontend Dependencies

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form state management
- **Monaco Editor** - Code editor component for prompts

### Backend Dependencies

- **pywebview** - Native window hosting for web content
- **hypothesis** - Property-based testing framework

## Build Scripts

The following npm scripts are available in `settings_ui/package.json`:

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Configuration

### Vite Configuration

The Vite configuration (`vite.config.ts`) is set up to:
- Use React plugin for JSX/TSX support
- Output to `dist` directory
- Use relative paths for assets (required for PyWebView)

### Tailwind Configuration

Tailwind is configured to scan all React files in the `src` directory for class names.

### TypeScript Configuration

TypeScript is configured with strict mode and React JSX support.

## Troubleshooting

### Frontend Build Fails

If the build fails, ensure all dependencies are installed:

```bash
cd settings_ui
npm install
```

### PyWebView Window Doesn't Open

1. Ensure the frontend is built: `npm run build` in `settings_ui`
2. Check that Python dependencies are installed: `pip install pywebview`
3. On Windows, ensure you have the WebView2 runtime installed

### Import Errors in Python

Ensure you're running the script from the project root or that the Python path is set correctly.

## Next Steps

After completing the setup:

1. Implement the backend services (ConfigManager, ValidationService, etc.)
2. Build the React components for the settings interface
3. Connect the frontend to the backend API bridge
4. Test the complete application

## Development Tips

- Use `npm run dev` for rapid frontend development
- Build the frontend (`npm run build`) before testing with PyWebView
- Check the browser console (F12 in PyWebView debug mode) for frontend errors
- Check the terminal output for backend errors
