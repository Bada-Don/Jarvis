"""
FunctionGemma Planner Service for Local Function Calling

This module provides the FunctionGemmaPlannerService class that uses a local
FunctionGemma-270M model to convert natural language commands into structured
function calls. This replaces the cloud-based Gemini API with a fully local solution.

Key Features:
- Local model loading with AutoProcessor (not AutoTokenizer)
- Model caching and lazy loading for performance
- Function call generation from natural language
- Multi-step task execution with conversation turns
- Integration with Function Registry for available functions
"""

import os
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FunctionCall:
    """A function call with name and arguments."""
    name: str
    arguments: dict
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "arguments": self.arguments
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FunctionCall':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            arguments=data["arguments"]
        )


@dataclass
class ExecutionResult:
    """Result of function execution."""
    success: bool
    function_name: str
    result: dict
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "function_name": self.function_name,
            "result": self.result,
            "error_message": self.error_message
        }


class FunctionGemmaPlannerService:
    """
    Service class for generating function calls using local FunctionGemma model.
    
    This service loads the FunctionGemma-270M model locally and uses it to
    convert natural language commands into structured function calls without
    requiring external API access.
    
    Attributes:
        model_path: Path to the local FunctionGemma model
        function_registry: Registry of available functions
        processor: AutoProcessor for model input processing
        model: The loaded FunctionGemma model
        _model_loaded: Flag indicating if model is loaded
    """
    
    # System prompt as specified in requirements 1.5
    SYSTEM_PROMPT = "You are a model that can do function calling with the following functions"
    
    def __init__(
        self, 
        model_path: str = None,
        function_registry = None,
        lazy_load: bool = True
    ):
        """
        Initialize the FunctionGemma Planner Service.
        
        Args:
            model_path: Path to local FunctionGemma model. If None, uses default path.
            function_registry: Registry of available functions. Can be set later.
            lazy_load: If True, delay model loading until first use (default: True)
        
        Raises:
            ValueError: If model_path is invalid
        """
        # Set default model path if not provided
        if model_path is None:
            # Try to find model in common locations
            possible_paths = [
                "./local_models/functiongemma-270m-it",
                "../FunctionGemma Files/local_models/functiongemma-270m-it",
                "./FunctionGemma Files/local_models/functiongemma-270m-it"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path is None:
                model_path = "./local_models/functiongemma-270m-it"
                logger.warning(
                    f"Model not found in common locations. "
                    f"Will attempt to use: {model_path}"
                )
        
        self.model_path = model_path
        self.function_registry = function_registry
        
        # Model components (loaded lazily if lazy_load=True)
        self.processor = None
        self.model = None
        self._model_loaded = False
        
        # Load model immediately if not lazy loading
        if not lazy_load:
            self.load_model()
        
        logger.info(f"FunctionGemmaPlannerService initialized (lazy_load={lazy_load})")
    
    def load_model(self) -> bool:
        """
        Load the FunctionGemma model from local storage.
        
        Uses AutoProcessor (not AutoTokenizer) as specified in requirements.
        Implements model caching by keeping model in memory after first load.
        
        Returns:
            True if model loaded successfully, False otherwise
        
        Raises:
            ImportError: If transformers library is not installed
            FileNotFoundError: If model files are not found
            Exception: For other loading errors
        """
        if self._model_loaded:
            logger.info("Model already loaded (using cached instance)")
            return True
        
        try:
            logger.info(f"Loading FunctionGemma model from: {self.model_path}")
            
            # Import transformers (lazy import to avoid startup overhead)
            try:
                from transformers import AutoProcessor, AutoModelForCausalLM
            except ImportError as e:
                raise ImportError(
                    "transformers library not found. "
                    "Install with: pip install transformers torch"
                ) from e
            
            # Check if model path exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Model not found at: {self.model_path}\n"
                    f"Please download the model first using the download script."
                )
            
            # Load processor (using AutoProcessor as specified in requirements 1.4)
            logger.info("Loading AutoProcessor...")
            self.processor = AutoProcessor.from_pretrained(
                "google/functiongemma-270m-it",
                cache_dir=self.model_path,
                local_files_only=True
            )
            
            # Load model
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                "google/functiongemma-270m-it",
                cache_dir=self.model_path,
                local_files_only=True,
                device_map="auto"  # Automatically select best device (CPU/GPU)
            )
            
            self._model_loaded = True
            logger.info("✓ FunctionGemma model loaded successfully")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            raise
        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise Exception(f"Model loading failed: {e}") from e
    
    def _ensure_model_loaded(self):
        """Ensure model is loaded before use (for lazy loading)."""
        if not self._model_loaded:
            self.load_model()
    
    def set_function_registry(self, function_registry):
        """
        Set the function registry after initialization.
        
        Args:
            function_registry: Registry of available functions
        """
        self.function_registry = function_registry
        logger.info("Function registry set")
    
    def generate_function_calls(
        self, 
        user_command: str,
        max_tokens: int = 256,
        temperature: float = 0.1
    ) -> List[FunctionCall]:
        """
        Generate function calls from a user command.
        
        Processes the user command using the local FunctionGemma model and
        returns a list of function calls to execute.
        
        Args:
            user_command: Natural language command from user
            max_tokens: Maximum tokens to generate (default: 256)
            temperature: Sampling temperature (default: 0.1 for deterministic)
        
        Returns:
            List of FunctionCall objects
        
        Raises:
            ValueError: If user_command is empty or function_registry not set
            Exception: If model generation fails
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        if self.function_registry is None:
            raise ValueError(
                "Function registry not set. "
                "Call set_function_registry() before generating function calls."
            )
        
        # Ensure model is loaded
        self._ensure_model_loaded()
        
        try:
            # Get function schemas from registry
            tools = self.function_registry.get_all_schemas()
            
            # Build conversation with system prompt
            messages = [
                {
                    "role": "developer",
                    "content": self.SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_command
                }
            ]
            
            # Apply chat template with tools
            inputs = self.processor.apply_chat_template(
                messages,
                tools=tools,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt"
            )
            
            # Generate function calls
            logger.info(f"Generating function calls for: {user_command}")
            outputs = self.model.generate(
                **inputs.to(self.model.device),
                pad_token_id=self.processor.eos_token_id,
                max_new_tokens=max_tokens,
                temperature=temperature
            )
            
            # Decode output
            generated_tokens = outputs[0][len(inputs["input_ids"][0]):]
            output_text = self.processor.decode(generated_tokens, skip_special_tokens=True)
            
            logger.info(f"Model output: {output_text}")
            
            # Parse function calls from output
            # Import parser here to avoid circular dependency
            from function_parser import extract_function_calls
            
            function_calls_data = extract_function_calls(output_text)
            function_calls = [FunctionCall.from_dict(fc) for fc in function_calls_data]
            
            logger.info(f"Generated {len(function_calls)} function call(s)")
            return function_calls
            
        except Exception as e:
            logger.error(f"Failed to generate function calls: {e}")
            raise Exception(f"Function call generation failed: {e}") from e
    
    def execute_multi_step_task(
        self,
        user_command: str,
        max_turns: int = 15,
        executor: Callable = None
    ) -> Dict:
        """
        Execute a multi-step task with conversation turns.
        
        This method handles complex tasks that require multiple function calls
        and conversation turns between the model and the execution environment.
        
        Args:
            user_command: Natural language command from user
            max_turns: Maximum conversation turns (default: 15)
            executor: Optional function executor. If None, only generates calls.
        
        Returns:
            Dict with execution results:
            {
                "success": bool,
                "turns": int,
                "function_calls": List[FunctionCall],
                "results": List[ExecutionResult],
                "final_output": str
            }
        
        Raises:
            ValueError: If user_command is empty or function_registry not set
        """
        if not user_command or not user_command.strip():
            raise ValueError("User command cannot be empty")
        
        if self.function_registry is None:
            raise ValueError("Function registry not set")
        
        # Ensure model is loaded
        self._ensure_model_loaded()
        
        logger.info(f"Starting multi-step task: {user_command}")
        
        # Get function schemas
        tools = self.function_registry.get_all_schemas()
        
        # Initialize conversation
        messages = [
            {
                "role": "developer",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_command
            }
        ]
        
        all_function_calls = []
        all_results = []
        
        for turn in range(1, max_turns + 1):
            logger.info(f"Turn {turn}/{max_turns}")
            
            try:
                # Generate model response
                inputs = self.processor.apply_chat_template(
                    messages,
                    tools=tools,
                    add_generation_prompt=True,
                    return_dict=True,
                    return_tensors="pt"
                )
                
                outputs = self.model.generate(
                    **inputs.to(self.model.device),
                    pad_token_id=self.processor.eos_token_id,
                    max_new_tokens=256,
                    temperature=0.1
                )
                
                generated_tokens = outputs[0][len(inputs["input_ids"][0]):]
                output_text = self.processor.decode(generated_tokens, skip_special_tokens=True)
                
                logger.info(f"Model output: {output_text}")
                
                # Check if model is done (no function calls)
                if "<start_function_call>" not in output_text:
                    logger.info(f"Task complete. Final response: {output_text}")
                    return {
                        "success": True,
                        "turns": turn,
                        "function_calls": all_function_calls,
                        "results": all_results,
                        "final_output": output_text
                    }
                
                # Parse function calls
                from function_parser import extract_function_calls
                function_calls_data = extract_function_calls(output_text)
                
                if not function_calls_data:
                    logger.warning("No valid function calls detected")
                    break
                
                # Convert to FunctionCall objects
                function_calls = [FunctionCall.from_dict(fc) for fc in function_calls_data]
                all_function_calls.extend(function_calls)
                
                # Add assistant's tool calls to conversation
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {"type": "function", "function": fc.to_dict()} 
                        for fc in function_calls
                    ]
                })
                
                # Execute function calls if executor provided
                if executor:
                    results = []
                    for fc in function_calls:
                        result = executor(fc)
                        results.append(result)
                        all_results.append(result)
                    
                    # Add tool results to conversation
                    messages.append({
                        "role": "tool",
                        "content": [r.to_dict() for r in results]
                    })
                else:
                    # No executor, just return the function calls
                    logger.info("No executor provided, returning function calls")
                    return {
                        "success": True,
                        "turns": turn,
                        "function_calls": all_function_calls,
                        "results": [],
                        "final_output": "Function calls generated (no execution)"
                    }
                
            except Exception as e:
                logger.error(f"Error in turn {turn}: {e}")
                return {
                    "success": False,
                    "turns": turn,
                    "function_calls": all_function_calls,
                    "results": all_results,
                    "final_output": f"Error: {e}"
                }
        
        # Max turns reached
        logger.warning(f"Max turns ({max_turns}) reached")
        return {
            "success": False,
            "turns": max_turns,
            "function_calls": all_function_calls,
            "results": all_results,
            "final_output": "Max turns reached"
        }
    
    def unload_model(self):
        """
        Unload the model from memory.
        
        Useful for freeing memory when the model is not needed for extended periods.
        """
        if self._model_loaded:
            logger.info("Unloading model from memory")
            self.model = None
            self.processor = None
            self._model_loaded = False
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("Model unloaded")
    
    def is_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self._model_loaded
