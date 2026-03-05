"""
JARVIS Application Launcher
Manages the lifecycle of all JARVIS components with process monitoring and automatic restart.
"""

import subprocess
import sys
import os
import time
import logging
import signal
import psutil
import threading
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# Import error handler
try:
    sys.path.insert(0, str(Path(__file__).parent / 'local_client'))
    from error_handler import (
        ErrorHandler,
        ComponentError,
        get_error_handler,
        set_error_handler
    )
    ERROR_HANDLER_AVAILABLE = True
except ImportError:
    ERROR_HANDLER_AVAILABLE = False
    print("⚠️ Warning: error_handler.py not found")


@dataclass
class ComponentConfig:
    """Configuration for a JARVIS component."""
    name: str
    script_path: str
    working_dir: str
    startup_delay: float = 0.0
    max_restart_attempts: int = 3
    restart_delay: float = 5.0


class ApplicationLauncher:
    """
    Manages the lifecycle of all JARVIS components.
    
    Responsibilities:
    - Start components in correct order
    - Monitor component health
    - Restart crashed components automatically
    - Handle graceful shutdown
    """
    
    def __init__(self, log_level: int = logging.INFO):
        """
        Initialize the Application Launcher.
        
        Args:
            log_level: Logging level (default: INFO)
        """
        self.processes: Dict[str, subprocess.Popen] = {}
        self.restart_counts: Dict[str, int] = {}
        self.last_restart_time: Dict[str, datetime] = {}
        self.running = False
        self.shutdown_requested = False
        self._log_files = {}
        self._log_threads = {}
        
        # Setup logging
        self._setup_logging(log_level)
        
        # Setup error handler
        self.error_handler = None
        if ERROR_HANDLER_AVAILABLE:
            self.error_handler = ErrorHandler()
            set_error_handler(self.error_handler)
            self.logger.info('✅ Error handler initialized')
        
        # Define component configurations
        self.components = self._define_components()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self, log_level: int) -> None:
        """Setup logging configuration."""
        log_dir = Path('data/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'launcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Ensure stdout can handle UTF-8 symbols (emojis)
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('ApplicationLauncher')
        self.logger.info(f'Logging initialized: {log_file}')
    
    def _define_components(self) -> Dict[str, ComponentConfig]:
        """
        Define all JARVIS components with their configurations.
        
        Returns:
            Dictionary of component configurations
        """
        return {
            'backend': ComponentConfig(
                name='Backend Server',
                script_path='backend/server.py',
                working_dir='backend',
                startup_delay=2.0,  # Wait for backend to initialize
                max_restart_attempts=3,
                restart_delay=5.0
            ),
            'local_client': ComponentConfig(
                name='Local Client',
                script_path='local_client/client.py',
                working_dir='local_client',
                startup_delay=3.0,  # Wait for backend to be ready
                max_restart_attempts=3,
                restart_delay=5.0
            ),
            'settings_ui': ComponentConfig(
                name='Settings UI',
                script_path='local_client/run_settings.py',
                working_dir='local_client',
                startup_delay=1.0,  # UI can start quickly
                max_restart_attempts=3,
                restart_delay=5.0
            )
        }
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f'Received signal {signum}, initiating graceful shutdown...')
        self.shutdown_requested = True
        self.shutdown()
    
    def _stream_output(self, component_id: str, stream, stream_type: str, log_file) -> None:
        """
        Stream output from subprocess to both console and log file.
        
        Args:
            component_id: Component identifier
            stream: Subprocess stream (stdout or stderr)
            stream_type: Type of stream ('stdout' or 'stderr')
            log_file: File handle to write logs to
        """
        config = self.components[component_id]
        
        # Color codes for different components (if terminal supports it)
        colors = {
            'backend': '\033[94m',      # Blue
            'local_client': '\033[92m', # Green
            'settings_ui': '\033[93m',  # Yellow
        }
        reset_color = '\033[0m'
        
        color = colors.get(component_id, '')
        prefix = f"{color}[{config.name}]{reset_color} "
        
        try:
            for line in iter(stream.readline, b''):
                if not line:
                    break
                
                try:
                    decoded_line = line.decode('utf-8', errors='replace').rstrip()
                except Exception:
                    decoded_line = str(line).rstrip()
                
                if decoded_line:
                    # Write to log file
                    log_file.write(decoded_line + '\n')
                    log_file.flush()
                    
                    # Also log to console with component prefix
                    if stream_type == 'stderr':
                        self.logger.warning(f"{prefix}{decoded_line}")
                    else:
                        self.logger.info(f"{prefix}{decoded_line}")
        except Exception as e:
            self.logger.error(f"Error streaming {stream_type} for {config.name}: {e}")
        finally:
            stream.close()
    
    def start(self) -> bool:
        """
        Start all JARVIS components in the correct order.
        
        Returns:
            True if all components started successfully, False otherwise
        """
        self.logger.info('=' * 60)
        self.logger.info('🚀 Starting JARVIS Application Launcher')
        self.logger.info('=' * 60)
        
        self.running = True
        
        # Start components in order: Backend → Local Client → Settings UI
        component_order = ['backend', 'local_client', 'settings_ui']
        
        for component_id in component_order:
            if self.shutdown_requested:
                self.logger.warning('Shutdown requested during startup, aborting...')
                return False
            
            config = self.components[component_id]
            
            if not self._start_component(component_id, config):
                self.logger.error(f'Failed to start {config.name}, aborting startup')
                self.shutdown()
                return False
            
            # Wait for component to initialize
            if config.startup_delay > 0:
                self.logger.info(f'Waiting {config.startup_delay}s for {config.name} to initialize...')
                time.sleep(config.startup_delay)
        
        self.logger.info('✅ All components started successfully')
        return True
    
    def _start_component(self, component_id: str, config: ComponentConfig) -> bool:
        """
        Start a single component.
        
        Args:
            component_id: Unique identifier for the component
            config: Component configuration
            
        Returns:
            True if component started successfully, False otherwise
        """
        try:
            self.logger.info(f'Starting {config.name}...')
            
            # Check if script exists
            script_path = Path(config.script_path)
            if not script_path.exists():
                self.logger.error(f'Script not found: {script_path}')
                return False
            
            # Use absolute path for the script to avoid issues with different working directories
            abs_script_path = script_path.resolve()
            
            # Prepare environment
            env = os.environ.copy()
            # Ensure environmental variables support UTF-8
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Create log files for stdout and stderr
            log_dir = Path('data/logs')
            log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stdout_log = log_dir / f'{component_id}_stdout_{timestamp}.log'
            stderr_log = log_dir / f'{component_id}_stderr_{timestamp}.log'
            
            stdout_file = open(stdout_log, 'w', encoding='utf-8')
            stderr_file = open(stderr_log, 'w', encoding='utf-8')
            
            self.logger.info(f'   Stdout log: {stdout_log}')
            self.logger.info(f'   Stderr log: {stderr_log}')
            
            # Start process with PIPE for real-time output streaming
            process = subprocess.Popen(
                [sys.executable, str(abs_script_path)],
                cwd=config.working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            # Store process and file handles
            self.processes[component_id] = process
            self.restart_counts[component_id] = 0
            
            # Store file handles for cleanup
            self._log_files[component_id] = (stdout_file, stderr_file)
            
            # Start threads to stream output in real-time
            stdout_thread = threading.Thread(
                target=self._stream_output,
                args=(component_id, process.stdout, 'stdout', stdout_file),
                daemon=True,
                name=f'{component_id}_stdout'
            )
            stderr_thread = threading.Thread(
                target=self._stream_output,
                args=(component_id, process.stderr, 'stderr', stderr_file),
                daemon=True,
                name=f'{component_id}_stderr'
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Store thread references
            self._log_threads[component_id] = (stdout_thread, stderr_thread)
            
            # Verify process started
            time.sleep(0.5)
            if process.poll() is not None:
                self.logger.error(f'{config.name} exited immediately with code {process.returncode}')
                # Give threads a moment to flush output
                time.sleep(0.5)
                return False
            
            self.logger.info(f'✅ {config.name} started (PID: {process.pid})')
            return True
            
        except Exception as e:
            self.logger.error(f'Failed to start {config.name}: {e}')
            return False
    
    def monitor(self) -> None:
        """
        Monitor all components and restart crashed ones.
        This method blocks until shutdown is requested.
        """
        self.logger.info('🔍 Starting component monitoring...')
        
        while self.running and not self.shutdown_requested:
            try:
                for component_id, process in list(self.processes.items()):
                    # Check if process is still running
                    if process.poll() is not None:
                        config = self.components[component_id]
                        exit_code = process.returncode
                        
                        # Handle normal exit (code 0) - don't restart
                        if exit_code == 0:
                            self.logger.info(f'✅ {config.name} exited normally')
                            if component_id in self.processes:
                                del self.processes[component_id]
                            continue

                        self.logger.warning(
                            f'⚠️ {config.name} crashed with exit code {exit_code}'
                        )
                        
                        # Report error via error handler
                        if self.error_handler:
                            error = ComponentError(
                                f"{config.name} crashed with exit code {exit_code}",
                                component=config.name,
                                details={
                                    'exit_code': exit_code,
                                    'restart_count': self.restart_counts.get(component_id, 0)
                                }
                            )
                            
                            # Attempt restart via error handler
                            def restart_callback(err):
                                if self._should_restart(component_id, config):
                                    return self._restart_component(component_id, config)
                                return False
                            
                            success = self.error_handler.handle_component_crash(error, restart_callback)
                            
                            if not success:
                                self.logger.error(
                                    f'❌ {config.name} exceeded max restart attempts, giving up'
                                )
                                self.running = False
                                break
                        else:
                            # Fallback to direct restart
                            if self._should_restart(component_id, config):
                                self._restart_component(component_id, config)
                            else:
                                self.logger.error(
                                    f'❌ {config.name} exceeded max restart attempts, giving up'
                                )
                                self.running = False
                                break
                
                # Sleep before next check
                time.sleep(2.0)
                
            except KeyboardInterrupt:
                self.logger.info('Keyboard interrupt received')
                break
            except Exception as e:
                self.logger.error(f'Error in monitoring loop: {e}')
                time.sleep(5.0)
        
        self.logger.info('Monitoring stopped')
    
    def _should_restart(self, component_id: str, config: ComponentConfig) -> bool:
        """
        Determine if a component should be restarted.
        
        Args:
            component_id: Component identifier
            config: Component configuration
            
        Returns:
            True if component should be restarted, False otherwise
        """
        restart_count = self.restart_counts.get(component_id, 0)
        
        # Check if max restart attempts exceeded
        if restart_count >= config.max_restart_attempts:
            return False
        
        # Check if we're restarting too frequently (within 30 seconds)
        last_restart = self.last_restart_time.get(component_id)
        if last_restart:
            time_since_restart = (datetime.now() - last_restart).total_seconds()
            if time_since_restart < 30:
                self.logger.warning(
                    f'{config.name} crashed too soon after restart ({time_since_restart:.1f}s)'
                )
                # Still allow restart but count it
        
        return True
    
    def _restart_component(self, component_id: str, config: ComponentConfig) -> bool:
        """
        Restart a crashed component.
        
        Args:
            component_id: Component identifier
            config: Component configuration
            
        Returns:
            True if restart successful, False otherwise
        """
        restart_count = self.restart_counts.get(component_id, 0) + 1
        self.restart_counts[component_id] = restart_count
        self.last_restart_time[component_id] = datetime.now()
        
        self.logger.info(
            f'🔄 Restarting {config.name} (attempt {restart_count}/{config.max_restart_attempts})...'
        )
        
        # Wait before restart
        if config.restart_delay > 0:
            time.sleep(config.restart_delay)
        
        # Start component
        return self._start_component(component_id, config)
    
    def shutdown(self) -> None:
        """Gracefully shutdown all components."""
        if not self.running:
            return
        
        self.logger.info('=' * 60)
        self.logger.info('🛑 Shutting down JARVIS Application Launcher')
        self.logger.info('=' * 60)
        
        self.running = False
        
        # Shutdown components in reverse order: Settings UI → Local Client → Backend
        component_order = ['settings_ui', 'local_client', 'backend']
        
        for component_id in component_order:
            if component_id in self.processes:
                self._stop_component(component_id)
        
        self.logger.info('✅ All components stopped')
    
    def _stop_component(self, component_id: str) -> None:
        """
        Stop a single component gracefully.
        
        Args:
            component_id: Component identifier
        """
        process = self.processes.get(component_id)
        if not process:
            return
        
        config = self.components[component_id]
        self.logger.info(f'Stopping {config.name}...')
        
        try:
            # Try graceful shutdown first
            if sys.platform == 'win32':
                # On Windows, send CTRL_BREAK_EVENT
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # On Unix, send SIGTERM
                process.terminate()
            
            # Wait for process to exit
            try:
                process.wait(timeout=10.0)
                self.logger.info(f'✅ {config.name} stopped gracefully')
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown failed
                self.logger.warning(f'⚠️ {config.name} did not stop gracefully, forcing...')
                process.kill()
                process.wait(timeout=5.0)
                self.logger.info(f'✅ {config.name} force stopped')
                
        except Exception as e:
            self.logger.error(f'Error stopping {config.name}: {e}')
        finally:
            # Wait for log threads to finish (give them a moment to flush)
            if component_id in self._log_threads:
                stdout_thread, stderr_thread = self._log_threads[component_id]
                stdout_thread.join(timeout=2.0)
                stderr_thread.join(timeout=2.0)
                del self._log_threads[component_id]
            
            # Close log files
            if component_id in self._log_files:
                stdout_file, stderr_file = self._log_files[component_id]
                try:
                    stdout_file.close()
                    stderr_file.close()
                except Exception:
                    pass
                del self._log_files[component_id]
            
            # Remove from processes dict
            if component_id in self.processes:
                del self.processes[component_id]
    
    def restart_all(self) -> bool:
        """
        Restart all components.
        
        Returns:
            True if restart successful, False otherwise
        """
        self.logger.info('🔄 Restarting all components...')
        
        # Shutdown all components
        self.shutdown()
        
        # Wait a moment
        time.sleep(2.0)
        
        # Reset restart counts
        self.restart_counts.clear()
        self.last_restart_time.clear()
        
        # Start all components
        return self.start()
    
    def get_status(self) -> Dict[str, dict]:
        """
        Get status of all components.
        
        Returns:
            Dictionary with component status information
        """
        status = {}
        
        for component_id, config in self.components.items():
            process = self.processes.get(component_id)
            
            if process and process.poll() is None:
                # Process is running
                try:
                    proc = psutil.Process(process.pid)
                    status[component_id] = {
                        'name': config.name,
                        'status': 'running',
                        'pid': process.pid,
                        'cpu_percent': proc.cpu_percent(interval=0.1),
                        'memory_mb': proc.memory_info().rss / 1024 / 1024,
                        'restart_count': self.restart_counts.get(component_id, 0)
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    status[component_id] = {
                        'name': config.name,
                        'status': 'unknown',
                        'pid': process.pid,
                        'restart_count': self.restart_counts.get(component_id, 0)
                    }
            else:
                # Process is not running
                status[component_id] = {
                    'name': config.name,
                    'status': 'stopped',
                    'restart_count': self.restart_counts.get(component_id, 0)
                }
        
        return status
