# JARVIS Packaging Guide

This guide explains how to use the JARVIS packaging system to create distributable builds.

## Overview

The packaging system consists of 5 scripts that work together to create a complete, distributable JARVIS application:

1. **build_python.py** - Bundles Python components (backend and local_client) using PyInstaller
2. **build_nodejs.py** - Builds the Settings UI using Vite
3. **build_assets.py** - Packages assets (FastSAM weights, icons, configs, audio)
4. **build_structure.py** - Creates the final directory structure and organizes all components
5. **package.py** - Main orchestrator that runs all scripts and creates the ZIP archive

## Prerequisites

Before running the packaging scripts, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and **npm** installed
- **All dependencies installed**:
  ```bash
  # Install local_client requirements (includes PyInstaller)
  pip install -r local_client/requirements.txt
  
  # Install backend requirements
  pip install -r backend/requirements.txt
  ```
- **Node.js dependencies**:
  ```bash
  cd settings_ui
  npm install
  cd ..
  ```

**Note**: PyInstaller is included in `local_client/requirements.txt`.

## Quick Start

To create a complete package, simply run:

```bash
python package.py
```

This will:
1. Check prerequisites
2. Clean previous builds
3. Build Python components
4. Build Node.js components
5. Package assets
6. Create directory structure
7. Generate version information
8. Create ZIP archive
9. Validate package contents

## Individual Scripts

You can also run individual scripts for testing or debugging:

### Build Python Components

```bash
python build_python.py
```

Creates:
- `dist/jarvis_backend/` - Backend server executable
- `dist/jarvis_client/` - Local client executable

### Build Node.js Components

```bash
python build_nodejs.py
```

Creates:
- `settings_ui/dist/` - Built Settings UI (HTML, CSS, JS)

### Package Assets

```bash
python build_assets.py
```

Creates:
- `dist/assets/weights/` - FastSAM model weights
- `dist/assets/icons/` - Application icons
- `dist/assets/config/` - Configuration templates
- `dist/assets/audio/` - Audio feedback files
- `dist/data/` - Data directory structure

### Create Directory Structure

```bash
python build_structure.py
```

Creates:
- `dist/JARVIS/` - Complete application directory
- Organizes all components into proper locations
- Creates launcher scripts
- Generates README and LICENSE

## Output

After successful packaging, you'll have:

### Application Directory

```
dist/JARVIS/
├── app/
│   ├── backend/          # Backend server executable
│   ├── local_client/     # Local client executable
│   └── settings_ui/      # Settings UI (HTML/CSS/JS)
├── assets/
│   ├── weights/          # AI model weights
│   ├── icons/            # Application icons
│   ├── config/           # Configuration templates
│   └── audio/            # Audio feedback files
├── data/
│   ├── logs/             # Log files directory
│   └── config_backups/   # Configuration backups
├── JARVIS.py             # Main launcher script
├── start_jarvis.bat      # Windows launcher
├── README.txt            # User documentation
├── LICENSE.txt           # License information
└── version.json          # Version metadata
```

### ZIP Archive

```
JARVIS-1.0.0-YYYYMMDD.zip
```

A compressed archive of the entire application, ready for distribution.

## Testing the Package

Before distributing, test the package:

1. Navigate to the application directory:
   ```bash
   cd dist/JARVIS
   ```

2. Run the launcher:
   ```bash
   # On Windows
   start_jarvis.bat
   
   # Or using Python directly
   python JARVIS.py
   ```

3. Verify:
   - Settings UI opens automatically
   - Backend server starts on port 5000
   - Local client starts successfully
   - First-run setup wizard appears
   - All features work as expected

## Distribution

To distribute JARVIS:

1. Share the ZIP archive: `JARVIS-1.0.0-YYYYMMDD.zip`
2. Users should:
   - Extract the ZIP file
   - Run `start_jarvis.bat` (Windows)
   - Complete the first-run setup wizard
   - Pair their mobile device

## Troubleshooting

### PyInstaller Issues

If PyInstaller fails to build:
- Ensure all dependencies are installed
- Check for missing hidden imports in the spec files
- Try running with `--clean` flag

### Node.js Build Issues

If Vite build fails:
- Delete `node_modules` and run `npm install` again
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check for syntax errors in React components

### Missing Assets

If assets are missing:
- Verify FastSAM weights exist at `backend/weights/FastSAM-s.pt`
- Check that icon files exist in `ChatInterface/assets/Logo/`
- Ensure audio files exist in `local_client/assets/`

### Large Package Size

To reduce package size:
- Remove unnecessary dependencies
- Exclude development dependencies
- Use UPX compression (enabled by default in PyInstaller)
- Remove source maps from Node.js build

## Version Management

To update the version:

1. Edit `package.py` and change the `VERSION` constant:
   ```python
   VERSION = "1.1.0"
   ```

2. The version will be included in:
   - ZIP archive filename
   - `version.json` file
   - Build metadata

## Advanced Configuration

### Custom PyInstaller Options

Edit `build_python.py` to modify the spec files:
- Add hidden imports
- Include additional data files
- Change executable names
- Adjust compression settings

### Custom Vite Build

Edit `settings_ui/vite.config.js` to:
- Change output directory
- Modify build optimization
- Add/remove plugins
- Configure asset handling

## Support

For issues or questions:
- Check the main README.md
- Review the design document: `.kiro/specs/jarvis-desktop-packaging/design.md`
- Open an issue on GitHub

## License

See LICENSE.txt for license information.
