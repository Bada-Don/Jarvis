"""
JARVIS Packaging Service

This module provides functionality for packaging the JARVIS application
as a standalone executable using PyInstaller.
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List


class PackagingService:
    """
    Service for building standalone executables using PyInstaller.
    Handles spec file generation, build process management, and progress tracking.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the PackagingService.
        
        Args:
            project_root (str): Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.build_dir = self.project_root / "dist"
        self.spec_dir = self.project_root / "build"
        
        # Build state
        self.is_building = False
        self.build_thread: Optional[threading.Thread] = None
        self.build_logs: List[str] = []
        self.build_progress = 0
        self.current_step = ""
        self.build_success: Optional[bool] = None
        self.output_path: Optional[str] = None
        self.build_error: Optional[str] = None
    
    def build_executable(self, options: Dict[str, Any], progress_callback: Optional[Callable] = None) -> bool:
        """
        Build standalone executable using PyInstaller.
        
        Args:
            options (dict): Build options containing:
                - output_name (str): Name for the output executable
                - include_console (bool): Whether to show console window
                - one_file (bool): Whether to bundle into a single file
                - icon (str, optional): Path to icon file
            progress_callback (callable, optional): Callback for progress updates
                
        Returns:
            bool: True if build started successfully, False otherwise
        """
        if self.is_building:
            return False
        
        # Reset build state
        self.build_logs = []
        self.build_progress = 0
        self.current_step = "Initializing build"
        self.build_success = None
        self.output_path = None
        self.build_error = None
        self.is_building = True
        
        # Start build in a separate thread
        self.build_thread = threading.Thread(
            target=self._build_worker,
            args=(options, progress_callback),
            daemon=True
        )
        self.build_thread.start()
        
        return True
    
    def _build_worker(self, options: Dict[str, Any], progress_callback: Optional[Callable] = None):
        """
        Worker thread for building the executable.
        
        Args:
            options (dict): Build options
            progress_callback (callable, optional): Callback for progress updates
        """
        try:
            # Step 1: Generate spec file
            self._update_progress(10, "Generating PyInstaller spec file", progress_callback)
            spec_content = self.get_build_spec(options)
            
            spec_file = self.project_root / f"{options['output_name']}.spec"
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            
            self._log(f"Spec file created: {spec_file}")
            
            # Step 2: Run PyInstaller
            self._update_progress(20, "Running PyInstaller", progress_callback)
            
            # Build PyInstaller command
            cmd = [
                sys.executable,
                "-m",
                "PyInstaller",
                str(spec_file),
                "--clean",
                "--noconfirm"
            ]
            
            self._log(f"Running command: {' '.join(cmd)}")
            
            # Run PyInstaller and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.project_root)
            )
            
            # Read output line by line
            progress_steps = {
                "Analyzing": 30,
                "Building": 50,
                "Collecting": 70,
                "Creating": 85,
                "Successfully": 95
            }
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    self._log(line)
                    
                    # Update progress based on output
                    for keyword, progress in progress_steps.items():
                        if keyword.lower() in line.lower():
                            self._update_progress(progress, f"Building: {keyword}...", progress_callback)
                            break
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code == 0:
                # Build successful
                self._update_progress(100, "Build completed successfully", progress_callback)
                
                # Determine output path
                if options.get('one_file', True):
                    output_file = self.build_dir / f"{options['output_name']}.exe"
                else:
                    output_file = self.build_dir / options['output_name'] / f"{options['output_name']}.exe"
                
                if output_file.exists():
                    self.output_path = str(output_file)
                    self._log(f"Executable created: {self.output_path}")
                else:
                    self._log(f"Warning: Expected output not found at {output_file}")
                    # Try to find the executable
                    for exe_file in self.build_dir.rglob("*.exe"):
                        self.output_path = str(exe_file)
                        self._log(f"Found executable: {self.output_path}")
                        break
                
                self.build_success = True
            else:
                # Build failed
                self.build_success = False
                self.build_error = f"PyInstaller exited with code {return_code}"
                self._log(f"Build failed: {self.build_error}")
                self._update_progress(100, "Build failed", progress_callback)
            
        except FileNotFoundError:
            self.build_success = False
            self.build_error = "PyInstaller not found. Please install it with: pip install pyinstaller"
            self._log(f"Error: {self.build_error}")
            self._update_progress(100, "Build failed", progress_callback)
            
        except Exception as e:
            self.build_success = False
            self.build_error = str(e)
            self._log(f"Unexpected error: {e}")
            import traceback
            self._log(traceback.format_exc())
            self._update_progress(100, "Build failed", progress_callback)
            
        finally:
            self.is_building = False
    
    def get_build_spec(self, options: Dict[str, Any]) -> str:
        """
        Generate PyInstaller spec file content.
        
        Args:
            options (dict): Build options
            
        Returns:
            str: Spec file content
        """
        output_name = options.get('output_name', 'JARVIS')
        include_console = options.get('include_console', True)
        one_file = options.get('one_file', True)
        icon_path = options.get('icon', '')
        
        # Convert icon path to absolute if provided
        if icon_path and not Path(icon_path).is_absolute():
            icon_path = str(self.project_root / icon_path)
        
        # Build hidden imports list
        hidden_imports = [
            'google.generativeai',
            'pyautogui',
            'pygetwindow',
            'PIL',
            'cv2',
            'flask',
            'flask_socketio',
            'flask_cors',
            'pywinauto',
            'pywinauto.application',
            'pywinauto.findwindows',
            'pywinauto.timings',
            'comtypes',
            'comtypes.client',
            'win32gui',
            'win32con',
            'win32api',
            'pywintypes',
        ]
        
        # Build data files list
        datas = [
            "('backend', 'backend')",
            "('local_client', 'local_client')",
            "('.env', '.')",
        ]
        
        # Add weights directory if it exists
        weights_dir = self.project_root / "backend" / "weights"
        if weights_dir.exists():
            datas.append("('backend/weights', 'backend/weights')")
        
        # Generate spec file content
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for {output_name}
# Generated by JARVIS Packaging Service

block_cipher = None

a = Analysis(
    ['local_client/run_client.py'],
    pathex=[],
    binaries=[],
    datas=[
        {',\n        '.join(datas)}
    ],
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
'''
        
        if one_file:
            # Single file executable
            spec_content += f'''
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(include_console)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,'''
            
            if icon_path:
                spec_content += f"\n    icon='{icon_path}'"
            
            spec_content += "\n)\n"
        else:
            # Directory-based executable
            spec_content += f'''
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console={str(include_console)},'''
            
            if icon_path:
                spec_content += f"\n    icon='{icon_path}',"
            
            spec_content += "\n)\n\n"
            
            spec_content += f'''coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{output_name}',
)
'''
        
        return spec_content
    
    def clean_build_artifacts(self) -> None:
        """
        Remove temporary build files and directories.
        """
        import shutil
        
        # Remove build directory
        if self.spec_dir.exists():
            shutil.rmtree(self.spec_dir, ignore_errors=True)
        
        # Remove spec files
        for spec_file in self.project_root.glob("*.spec"):
            try:
                spec_file.unlink()
            except Exception:
                pass
    
    def get_build_status(self) -> Dict[str, Any]:
        """
        Get current build status.
        
        Returns:
            dict: Build status information
        """
        return {
            "is_building": self.is_building,
            "progress": self.build_progress,
            "current_step": self.current_step,
            "success": self.build_success,
            "output_path": self.output_path,
            "error": self.build_error,
            "logs": self.build_logs.copy()
        }
    
    def _update_progress(self, progress: int, step: str, callback: Optional[Callable] = None):
        """
        Update build progress.
        
        Args:
            progress (int): Progress percentage (0-100)
            step (str): Current step description
            callback (callable, optional): Callback to notify of progress
        """
        self.build_progress = progress
        self.current_step = step
        
        if callback:
            try:
                callback(progress, step)
            except Exception:
                pass
    
    def _log(self, message: str):
        """
        Add a message to the build log.
        
        Args:
            message (str): Log message
        """
        self.build_logs.append(message)
        print(f"[PackagingService] {message}")
