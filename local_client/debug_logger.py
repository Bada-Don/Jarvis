"""
Debug Logger for Two-Model Pipeline

Saves all model outputs, screenshots, and annotated images to timestamped folders
for troubleshooting and analysis.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np


class DebugLogger:
    """
    Logs all pipeline data to a timestamped debug folder.
    
    Creates folder structure:
    debug_logs/
      └── 2024-12-01_16-39-33/
          ├── session_info.json      # Command, timestamps, status
          ├── planner_output.json    # Execution plan from Model 1
          ├── screenshot.png         # Original screenshot
          ├── annotated.png          # SoM annotated image
          ├── box_map.json           # Element ID to coordinates mapping
          ├── vision_mapper_output.json  # Target to ID mapping from Model 2
          └── execution_log.txt      # Step-by-step execution log
    """
    
    def __init__(self, base_dir: str = "debug_logs"):
        """Initialize debug logger with timestamped session folder."""
        self.base_dir = Path(base_dir)
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = self.base_dir / self.session_id
        self.enabled = True
        self.execution_log = []
        
        # Create directories
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session info
        self.session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "status": "started",
            "user_command": None,
            "errors": []
        }
    
    def set_user_command(self, command: str):
        """Set the user command for this session."""
        self.session_info["user_command"] = command
        self._save_session_info()
    
    def log_planner_output(self, plan: dict):
        """Save the execution plan from Planner Model (Model 1)."""
        if not self.enabled:
            return
        
        filepath = self.session_dir / "planner_output.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
        
        self._log(f"Saved planner output: {len(plan.get('sequence', []))} steps")
    
    def log_screenshot(self, image: np.ndarray):
        """Save the original screenshot."""
        if not self.enabled:
            return
        
        filepath = self.session_dir / "screenshot.png"
        cv2.imwrite(str(filepath), image)
        
        h, w = image.shape[:2]
        self._log(f"Saved screenshot: {w}x{h} pixels")
    
    def log_annotated_image(self, image: np.ndarray):
        """Save the SoM annotated image."""
        if not self.enabled:
            return
        
        filepath = self.session_dir / "annotated.png"
        cv2.imwrite(str(filepath), image)
        
        self._log("Saved annotated image with SoM boxes")
    
    def log_box_map(self, box_map: dict):
        """Save the box map (element ID to coordinates)."""
        if not self.enabled:
            return
        
        filepath = self.session_dir / "box_map.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(box_map, f, indent=2)
        
        self._log(f"Saved box map: {len(box_map)} elements")
    
    def log_vision_mapper_output(self, id_map: dict, targets: list):
        """Save the Vision Mapper output (Model 2)."""
        if not self.enabled:
            return
        
        output = {
            "requested_targets": targets,
            "mapped_ids": id_map,
            "found_count": sum(1 for v in id_map.values() if v is not None),
            "not_found": [k for k, v in id_map.items() if v is None]
        }
        
        filepath = self.session_dir / "vision_mapper_output.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        self._log(f"Saved vision mapper output: {output['found_count']}/{len(targets)} targets found")
    
    def log_step_execution(self, step_num: int, step_type: str, details: str, success: bool = True):
        """Log a step execution."""
        if not self.enabled:
            return
        
        status = "✓" if success else "✗"
        entry = f"[Step {step_num}] {status} {step_type}: {details}"
        self.execution_log.append(entry)
        
        # Append to execution log file
        filepath = self.session_dir / "execution_log.txt"
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} {entry}\n")
    
    def log_error(self, error: str):
        """Log an error."""
        self.session_info["errors"].append({
            "time": datetime.now().isoformat(),
            "error": error
        })
        self._log(f"ERROR: {error}")
        self._save_session_info()
    
    def complete(self, success: bool = True):
        """Mark the session as complete."""
        self.session_info["end_time"] = datetime.now().isoformat()
        self.session_info["status"] = "success" if success else "failed"
        self._save_session_info()
        
        self._log(f"Session completed: {'SUCCESS' if success else 'FAILED'}")
        print(f"📁 Debug logs saved to: {self.session_dir}")
    
    def _log(self, message: str):
        """Internal logging."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[DEBUG {timestamp}] {message}")
    
    def _save_session_info(self):
        """Save session info to file."""
        filepath = self.session_dir / "session_info.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session_info, f, indent=2)


# Global debug logger instance (can be None if disabled)
_debug_logger: DebugLogger = None


def get_debug_logger() -> DebugLogger:
    """Get or create the global debug logger."""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger()
    return _debug_logger


def create_new_session() -> DebugLogger:
    """Create a new debug session."""
    global _debug_logger
    _debug_logger = DebugLogger()
    return _debug_logger
