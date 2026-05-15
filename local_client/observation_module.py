"""
Observation Module for ReAct Loop.
Captures the state of the PC after each action: active window, file existence,
terminal output, and provides tiered verification logic.
"""

import os
import subprocess
import time
import psutil
from typing import Optional, Dict, List, Any, Set
from pathlib import Path
from dataclasses import dataclass, asdict, field

try:
    import win32gui
    import win32process
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


@dataclass
class EvidenceBundle:
    # Window state
    active_window_title: str = ""
    active_window_title_before: str = ""
    foreground_process: str = ""
    new_windows_opened: List[str] = field(default_factory=list)
    windows_closed: List[str] = field(default_factory=list)

    # Process state  
    new_processes_spawned: List[str] = field(default_factory=list)

    # Shell output (if applicable)
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None

    # Filesystem (if a path was involved in the step)
    path_involved: Optional[str] = None
    path_exists_after: Optional[bool] = None
    file_size_after: Optional[int] = None
    file_modified_time_after: Optional[float] = None

    # Timing
    execution_duration_ms: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ObservationResult:
    verified: bool
    confidence: float          # 0.0 - 1.0
    strategy_used: str
    evidence: Dict             # raw evidence that led to this conclusion
    reasoning: str             # human readable, for agent's thought log
    needs_escalation: bool = False # True = bump to next tier

    def to_dict(self):
        return asdict(self)


class ObservationModule:
    """
    Evidence-gathering first, verification second.
    Collects a base evidence bundle after every step and applies verifiers.
    """
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback or (lambda msg, status="info": print(f"[{status}] {msg}"))
        self._last_state = {}

    def capture_pre_step_state(self) -> Dict:
        """Capture the state before a step executes."""
        state = {
            'timestamp': time.time(),
            'active_window_title': self.get_active_window_title(),
            'windows': self.get_all_window_titles(),
            'processes': self.get_running_processes()
        }
        self._last_state = state
        return state

    def collect_evidence_bundle(self, pre_state: Dict, step_result: Dict, step_metadata: Dict) -> EvidenceBundle:
        """
        Collect evidence after step execution and compare with pre-step state.
        """
        start_time = pre_state.get('timestamp', time.time())
        duration_ms = int((time.time() - start_time) * 1000)
        
        post_windows = self.get_all_window_titles()
        pre_windows = pre_state.get('windows', set())
        
        new_windows = list(post_windows - pre_windows)
        closed_windows = list(pre_windows - post_windows)
        
        post_processes = self.get_running_processes()
        pre_processes = pre_state.get('processes', set())
        new_processes = list(post_processes - pre_processes)
        
        # Filesystem check if path was involved
        path_involved = step_metadata.get('path') or step_metadata.get('command_path')
        # Some steps might have 'command' that contains a path, but we'll stick to explicit 'path' for now
        
        fs_info = {}
        if path_involved:
            expanded_path = os.path.expandvars(str(path_involved))
            if os.path.exists(expanded_path):
                fs_info['exists'] = True
                fs_info['size'] = os.path.getsize(expanded_path)
                fs_info['mtime'] = os.path.getmtime(expanded_path)
            else:
                fs_info['exists'] = False

        bundle = EvidenceBundle(
            active_window_title=self.get_active_window_title(),
            active_window_title_before=pre_state.get('active_window_title', ""),
            foreground_process=self.get_foreground_app(),
            new_windows_opened=new_windows,
            windows_closed=closed_windows,
            new_processes_spawned=new_processes,
            stdout=step_result.get('stdout', ""),
            stderr=step_result.get('stderr', ""),
            exit_code=step_result.get('exit_code') if 'exit_code' in step_result else (0 if step_result.get('success') else 1),
            path_involved=path_involved,
            path_exists_after=fs_info.get('exists'),
            file_size_after=fs_info.get('size'),
            file_modified_time_after=fs_info.get('mtime'),
            execution_duration_ms=duration_ms,
            timestamp=time.time()
        )
        return bundle

    def verify(self, bundle: EvidenceBundle, step_metadata: Dict) -> ObservationResult:
        """
        Determine verification strategy and return structured result.
        """
        expected_fragment = step_metadata.get('expected_output') or step_metadata.get('desc', "")
        
        # 1. Window Diff Verifier (New windows appeared)
        if bundle.new_windows_opened:
            for window in bundle.new_windows_opened:
                # If we have a hint from metadata about what window to expect
                expected_win = step_metadata.get('expected_window_title')
                if expected_win and expected_win.lower() in window.lower():
                    return ObservationResult(
                        verified=True, confidence=0.98,
                        strategy_used='window_diff',
                        evidence={'new_window': window},
                        reasoning=f"New window '{window}' matched expected '{expected_win}'"
                    )
                # Generic match against step description if no specific window expected
                if expected_fragment.lower() in window.lower():
                     return ObservationResult(
                        verified=True, confidence=0.90,
                        strategy_used='window_diff',
                        evidence={'new_window': window},
                        reasoning=f"New window '{window}' matched description/fragment '{expected_fragment}'"
                    )

        # 2. Window Title Verifier (Title changed)
        if bundle.active_window_title != bundle.active_window_title_before:
            expected_win = step_metadata.get('expected_window_title')
            if expected_win and expected_win.lower() in bundle.active_window_title.lower():
                return ObservationResult(
                    verified=True, confidence=0.95,
                    strategy_used='window_title_change',
                    evidence={'active_window': bundle.active_window_title},
                    reasoning=f"Active window changed to '{bundle.active_window_title}', matching '{expected_win}'"
                )

        # 3. Filesystem Verifier
        if bundle.path_involved and bundle.path_exists_after:
            # If the step was meant to create or modify a file
            if step_metadata.get('type') in ('write_file', 'create_directory', 'save_file'):
                 return ObservationResult(
                    verified=True, confidence=1.0,
                    strategy_used='filesystem',
                    evidence={'path': bundle.path_involved},
                    reasoning=f"Verified existence of path: {bundle.path_involved}"
                )

        # 4. Shell Output Verifier
        if bundle.exit_code is not None:
            # Check for success based on exit code and output
            success = bundle.exit_code == 0
            if step_metadata.get('expected_output'):
                success = success and (step_metadata['expected_output'].lower() in bundle.stdout.lower())
            
            if success:
                return ObservationResult(
                    verified=True, confidence=0.99,
                    strategy_used='shell_output',
                    evidence={'exit_code': bundle.exit_code, 'stdout_len': len(bundle.stdout)},
                    reasoning="Command returned success exit code and expected output patterns (if any)."
                )

        # 5. Visual Verifier (Last resort or for UI specific steps)
        if step_metadata.get('type') in ('visual_click', 'click_text', 'keyboard') or not bundle.new_windows_opened:
            # Here we would normally call a vision LLM, but for now we provide a placeholder
            # that indicates escalation might be needed if confidence is low.
            return ObservationResult(
                verified=step_metadata.get('success', False),
                confidence=0.7,
                strategy_used='basic_flow',
                evidence={'step_type': step_metadata.get('type')},
                reasoning="Verification relied on basic execution success. Visual verification not yet performed.",
                needs_escalation=True
            )

        return ObservationResult(
            verified=False, confidence=0.0,
            strategy_used='none',
            evidence={},
            reasoning="Could not verify state change with available evidence.",
            needs_escalation=True
        )

    # --- Utility Methods ---

    def get_active_window_title(self) -> str:
        """Get the title of the currently active window."""
        if not WIN32_AVAILABLE:
            return ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                return win32gui.GetWindowText(hwnd)
        except Exception:
            pass
        return ""

    def get_all_window_titles(self) -> Set[str]:
        """Get titles of all visible windows."""
        titles = set()
        if not WIN32_AVAILABLE:
            return titles
        
        def enum_windows_proc(hwnd, l_param):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if text:
                    titles.add(text)
        
        try:
            win32gui.EnumWindows(enum_windows_proc, None)
        except Exception:
            pass
        return titles

    def get_running_processes(self) -> Set[str]:
        """Get names of all running processes."""
        processes = set()
        try:
            for proc in psutil.process_iter(['name']):
                processes.add(proc.info['name'])
        except Exception:
            pass
        return processes

    def get_foreground_app(self) -> str:
        """Get the name of the foreground application."""
        if not WIN32_AVAILABLE:
            return ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                return proc.name()
        except Exception:
            pass
        return ""

    def build_observation_text(self, result: Dict) -> str:
        """Build a human-readable observation text from step result."""
        obs = result.get('observation', '')
        if obs:
            return obs
        
        # Fallback for missing observation field
        parts = []
        if result.get('stdout'):
            parts.append(f"Output: {self.summarize_output(result['stdout'])}")
        if result.get('stderr'):
            parts.append(f"Error: {self.summarize_output(result['stderr'])}")
        if result.get('active_window'):
            parts.append(f"Active Window: {result['active_window']}")
        
        return "\n".join(parts) if parts else "Step executed."

    def summarize_output(self, output: str, max_chars: int = 2000) -> str:
        """Summarize long tool outputs."""
        if not output or len(output) <= max_chars:
            return output
        lines = output.split('\n')
        if len(lines) > 20:
            head = '\n'.join(lines[:10])
            tail = '\n'.join(lines[-5:])
            return f"{head}\n... [{len(lines) - 15} more lines omitted] ...\n{tail}"
        half = max_chars // 2
        return f"{output[:half]}\n... [truncated {len(output) - max_chars} chars] ...\n{output[-half:]}"