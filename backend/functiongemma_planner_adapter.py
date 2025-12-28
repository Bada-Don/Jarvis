"""
FunctionGemma Planner Adapter

This adapter wraps FunctionGemmaPlannerService to provide a generate_plan() method
that's compatible with the existing server.py interface, allowing us to use
local FunctionGemma instead of the Gemini API for cost savings.

The adapter converts FunctionGemma's function calls into execution plan format.
"""

import os
import logging
from typing import Dict, List
from functiongemma_service import FunctionGemmaPlannerService
from initialize_registry import get_global_registry

logger = logging.getLogger(__name__)


class FunctionGemmaPlannerAdapter:
    """
    Adapter that makes FunctionGemma compatible with the existing planner interface.
    
    Provides a generate_plan() method that returns execution plans in the format
    expected by server.py, while using FunctionGemma locally for inference.
    """
    
    def __init__(self, model_path: str = None, config: dict = None):
        """
        Initialize the adapter.
        
        Args:
            model_path: Path to FunctionGemma model (optional)
            config: User configuration dict (optional, for compatibility)
        """
        self.config = config or {}
        
        # Find model path if not provided
        if model_path is None:
            possible_paths = [
                "../local_models/functiongemma-270m-it",
                "./local_models/functiongemma-270m-it",
                "../FunctionGemma Files/local_models/functiongemma-270m-it",
                "./FunctionGemma Files/local_models/functiongemma-270m-it"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    logger.info(f"Found model at: {model_path}")
                    break
        
        # Initialize FunctionGemma service with lazy loading
        self.functiongemma_service = FunctionGemmaPlannerService(
            model_path=model_path,
            lazy_load=True,
            auto_unload_timeout=300  # Unload after 5 minutes of inactivity
        )
        
        # Get the global initialized function registry
        self.function_registry = get_global_registry()
        self.functiongemma_service.set_function_registry(self.function_registry)
        
        logger.info("FunctionGemma Planner Adapter initialized (using local model)")
    
    def detect_mode(self, user_command: str) -> str:
        """
        Detect whether the command is for FlexiSIGN or general use.
        
        Args:
            user_command: The user's natural language command
            
        Returns:
            str: "flexisign" or "general"
        """
        command_lower = user_command.lower()
        
        # FlexiSIGN keywords
        flexisign_keywords = [
            "plate", "number plate", "numberplate", 
            "bike", "car", "iron", "glass",
            "flexisign", "flexi sign", "flexi-sign",
            "nameplate", "name plate", "sticker", "stickers"
        ]
        
        for keyword in flexisign_keywords:
            if keyword in command_lower:
                return "flexisign"
        
        return "general"
    
    def _convert_function_calls_to_plan(
        self, 
        function_calls: List, 
        mode: str,
        user_command: str
    ) -> Dict:
        """
        Convert FunctionGemma function calls to execution plan format.
        
        Args:
            function_calls: List of FunctionCall objects from FunctionGemma
            mode: "general" or "flexisign"
            user_command: Original user command
            
        Returns:
            Dict with "sequence" array and "mode" field
        """
        sequence = []
        
        for i, fc in enumerate(function_calls, start=1):
            step = {
                "order": i,
                "desc": f"{fc.name}: {fc.arguments}"
            }
            
            # Map function names to step types
            if fc.name == "press_key":
                step["type"] = "keyboard"
                step["value"] = fc.arguments.get("key", "")
                
            elif fc.name == "type_text":
                step["type"] = "keyboard"
                step["value"] = fc.arguments.get("text", "")
                
            elif fc.name == "click_element":
                step["type"] = "visual_click"
                step["target_name"] = fc.arguments.get("element_name", "")
                
            elif fc.name == "open_file":
                step["type"] = "open_file"
                step["path"] = fc.arguments.get("path", "")
                
            elif fc.name == "open_folder":
                step["type"] = "open_folder"
                step["path"] = fc.arguments.get("path", "")
                
            elif fc.name == "save_file":
                step["type"] = "save_file"
                step["path"] = fc.arguments.get("path", "")
                
            # FlexiSIGN-specific functions
            elif fc.name == "create_text":
                step["type"] = "create_text"
                step["text"] = fc.arguments.get("text", "")
                
            elif fc.name == "set_dimensions":
                step["type"] = "set_dimensions"
                step["width"] = fc.arguments.get("width", "")
                step["height"] = fc.arguments.get("height", "")
                
            elif fc.name == "set_font":
                step["type"] = "set_font"
                step["font_name"] = fc.arguments.get("font_name", "")
                
            elif fc.name == "apply_style":
                step["type"] = "apply_style"
                step["style_name"] = fc.arguments.get("style_name", "")
                
            elif fc.name == "move_object":
                step["type"] = "move_object"
                step["direction"] = fc.arguments.get("direction", "")
                step["distance"] = fc.arguments.get("distance", 0)
                
            elif fc.name == "ensure_designcentral":
                step["type"] = "ensure_designcentral"
                
            else:
                # Generic function call - pass through as-is
                step["type"] = fc.name
                step.update(fc.arguments)
            
            sequence.append(step)
        
        # Generate expected final state description
        expected_final_state = self._generate_expected_state(
            sequence, 
            mode, 
            user_command
        )
        
        return {
            "mode": mode,
            "sequence": sequence,
            "expected_final_state": expected_final_state
        }
    
    def _generate_expected_state(
        self, 
        sequence: List[Dict], 
        mode: str,
        user_command: str
    ) -> str:
        """
        Generate a description of the expected final state.
        
        Args:
            sequence: List of execution steps
            mode: "general" or "flexisign"
            user_command: Original user command
            
        Returns:
            String describing expected final state
        """
        if not sequence:
            return "No changes expected"
        
        # Try to infer from the last few steps
        last_steps = sequence[-3:] if len(sequence) >= 3 else sequence
        
        if mode == "flexisign":
            return f"FlexiSIGN window showing completed design for: {user_command}"
        else:
            # For general mode, try to describe based on actions
            actions = [step.get("desc", "") for step in last_steps]
            return f"Completed actions: {', '.join(actions)}"
    
    def generate_plan(self, user_command: str, mode: str = None) -> Dict:
        """
        Generate an execution plan from a user command.
        
        This method provides compatibility with the existing server.py interface
        while using FunctionGemma locally instead of the Gemini API.
        
        Args:
            user_command: Natural language command from the user
            mode: Optional mode override ("general" or "flexisign")
                  If not provided, auto-detects based on command content.
        
        Returns:
            dict: Execution plan with "sequence" array and "mode" field.
        
        Raises:
            ValueError: If the command is invalid or generation fails.
            Exception: If the model fails.
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        # Auto-detect mode if not specified
        if mode is None:
            mode = self.detect_mode(user_command)
        
        try:
            logger.info(f"Generating plan using FunctionGemma (mode: {mode})")
            
            # Generate function calls using FunctionGemma
            function_calls = self.functiongemma_service.generate_function_calls(
                user_command=user_command,
                max_tokens=512,  # Increased for complex tasks
                temperature=0.1  # Low temperature for deterministic output
            )
            
            logger.info(f"Generated {len(function_calls)} function calls")
            
            # Convert to execution plan format
            plan = self._convert_function_calls_to_plan(
                function_calls,
                mode,
                user_command
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            raise ValueError(f"Failed to generate plan: {e}")
    
    def is_loaded(self) -> bool:
        """Check if the FunctionGemma model is loaded."""
        return self.functiongemma_service.is_loaded()
    
    def unload_model(self):
        """Unload the model from memory."""
        self.functiongemma_service.unload_model()
    
    def get_memory_usage(self) -> Dict:
        """Get memory usage statistics."""
        return self.functiongemma_service.get_memory_usage()
