# PyInstaller Build System

> 12 nodes · cohesion 0.24

## Key Concepts

- **build_python.py** (6 connections) — `build_python.py`
- **main()** (6 connections) — `build_python.py`
- **clean_build_dirs()** (3 connections) — `build_python.py`
- **create_backend_spec()** (3 connections) — `build_python.py`
- **create_local_client_spec()** (3 connections) — `build_python.py`
- **build_component()** (3 connections) — `build_python.py`
- **verify_build()** (3 connections) — `build_python.py`
- **Remove previous build artifacts.** (1 connections) — `build_python.py`
- **Create PyInstaller spec file for backend server.** (1 connections) — `build_python.py`
- **Create PyInstaller spec file for local client.** (1 connections) — `build_python.py`
- **Build a component using PyInstaller.** (1 connections) — `build_python.py`
- **Verify that build artifacts were created.** (1 connections) — `build_python.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `build_python.py`

## Audit Trail

- EXTRACTED: 32 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*