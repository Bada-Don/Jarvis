"""
Basic unit tests for FunctionExecutor

Tests the core functionality of the FunctionExecutor class including:
- Single function call execution with parameter validation
- Sequential execution with order preservation
- Error handling with severity-based logic
- Parallel execution support
- Overall status reporting
"""

import pytest
from function_executor import FunctionExecutor, MultiStepExecutionResult, ErrorSeverity
from function_registry import FunctionRegistry
from functiongemma_service import FunctionCall, ExecutionResult


class TestFunctionExecutorBasics:
    """Test basic executor operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = FunctionRegistry()
        
        # Register a simple test function
        def test_func(text: str) -> dict:
            return {"success": True, "message": f"Processed: {text}"}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to process"}
                },
                "required": ["text"]
            }
        }
        
        self.registry.register_function(
            name="test_func",
            implementation=test_func,
            schema=schema,
            category="keyboard_operations"
        )
        
        self.executor = FunctionExecutor(self.registry)
    
    def test_initialization(self):
        """Test executor initializes correctly."""
        executor = FunctionExecutor(self.registry)
        assert executor.function_registry == self.registry
        assert executor.abort_on_error == False
        assert executor.max_parallel_workers == 4
    
    def test_execute_valid_function_call(self):
        """Test executing a valid function call."""
        fc = FunctionCall(name="test_func", arguments={"text": "hello"})
        result = self.executor.execute_function_call(fc)
        
        assert result.success == True
        assert result.function_name == "test_func"
        assert result.result["message"] == "Processed: hello"
        assert result.error_message is None
    
    def test_execute_nonexistent_function(self):
        """Test executing a function that doesn't exist."""
        fc = FunctionCall(name="nonexistent", arguments={})
        result = self.executor.execute_function_call(fc)
        
        assert result.success == False
        assert result.function_name == "nonexistent"
        assert "not found in registry" in result.error_message
    
    def test_execute_with_invalid_parameters(self):
        """Test executing with invalid parameters."""
        fc = FunctionCall(name="test_func", arguments={"wrong_param": "value"})
        result = self.executor.execute_function_call(fc)
        
        assert result.success == False
        assert "Invalid parameters" in result.error_message
    
    def test_execute_with_missing_required_parameter(self):
        """Test executing with missing required parameter."""
        fc = FunctionCall(name="test_func", arguments={})
        result = self.executor.execute_function_call(fc)
        
        assert result.success == False
        assert "Missing required parameter" in result.error_message


class TestSequentialExecution:
    """Test sequential execution of function calls."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = FunctionRegistry()
        self.execution_order = []
        
        # Register functions that track execution order
        def func1(value: str) -> dict:
            self.execution_order.append("func1")
            return {"success": True, "value": value}
        
        def func2(value: str) -> dict:
            self.execution_order.append("func2")
            return {"success": True, "value": value}
        
        def func3(value: str) -> dict:
            self.execution_order.append("func3")
            return {"success": True, "value": value}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        }
        
        for name, impl in [("func1", func1), ("func2", func2), ("func3", func3)]:
            self.registry.register_function(
                name=name,
                implementation=impl,
                schema=schema,
                category="keyboard_operations"
            )
        
        self.executor = FunctionExecutor(self.registry)
    
    def test_execution_order_preserved(self):
        """Test that execution order is preserved in sequential mode."""
        function_calls = [
            FunctionCall(name="func1", arguments={"value": "a"}),
            FunctionCall(name="func2", arguments={"value": "b"}),
            FunctionCall(name="func3", arguments={"value": "c"})
        ]
        
        result = self.executor.execute_sequence(function_calls, parallel=False)
        
        # Verify order was preserved (Requirement 12.2)
        assert self.execution_order == ["func1", "func2", "func3"]
        assert result.overall_success == True
        assert result.total_steps == 3
        assert result.successful_steps == 3
        assert result.failed_steps == 0
    
    def test_empty_sequence(self):
        """Test executing an empty sequence."""
        result = self.executor.execute_sequence([], parallel=False)
        
        assert result.overall_success == True
        assert result.total_steps == 0
        assert result.successful_steps == 0
        assert result.failed_steps == 0


class TestErrorHandling:
    """Test error handling and severity-based logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = FunctionRegistry()
        
        # Register a function that fails
        def failing_func(value: str) -> dict:
            return {"success": False, "message": "Operation failed"}
        
        # Register a function that raises an exception
        def error_func(value: str) -> dict:
            raise ValueError("Test error")
        
        # Register a function that succeeds
        def success_func(value: str) -> dict:
            return {"success": True, "value": value}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        }
        
        for name, impl in [
            ("failing_func", failing_func),
            ("error_func", error_func),
            ("success_func", success_func)
        ]:
            self.registry.register_function(
                name=name,
                implementation=impl,
                schema=schema,
                category="keyboard_operations"
            )
        
        self.executor = FunctionExecutor(self.registry)
    
    def test_non_critical_error_continues(self):
        """Test that non-critical errors allow execution to continue."""
        function_calls = [
            FunctionCall(name="success_func", arguments={"value": "a"}),
            FunctionCall(name="failing_func", arguments={"value": "b"}),
            FunctionCall(name="success_func", arguments={"value": "c"})
        ]
        
        result = self.executor.execute_sequence(function_calls, parallel=False)
        
        # Should execute all 3 despite middle failure (Requirement 12.3)
        assert result.total_steps == 3
        assert result.successful_steps == 2
        assert result.failed_steps == 1
        assert result.overall_success == False
    
    def test_critical_error_aborts(self):
        """Test that critical errors abort execution."""
        # Register a function that returns a critical error
        def critical_error_func(value: str) -> dict:
            return {"success": False, "message": "Permission denied: access denied"}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        }
        
        self.registry.register_function(
            name="critical_error_func",
            implementation=critical_error_func,
            schema=schema,
            category="keyboard_operations"
        )
        
        function_calls = [
            FunctionCall(name="success_func", arguments={"value": "a"}),
            FunctionCall(name="critical_error_func", arguments={"value": "b"}),
            FunctionCall(name="success_func", arguments={"value": "c"})
        ]
        
        result = self.executor.execute_sequence(function_calls, parallel=False)
        
        # Should stop after critical error (Requirement 12.3)
        # total_steps is the total number of function calls provided
        # but only 2 were actually executed before abort
        assert result.total_steps == 3
        assert len(result.step_results) == 2  # Only 2 were executed
        assert result.successful_steps == 1
        assert result.failed_steps == 1
    
    def test_error_severity_determination(self):
        """Test error severity determination."""
        # Test critical patterns
        assert self.executor._determine_error_severity("Permission denied") == ErrorSeverity.CRITICAL
        assert self.executor._determine_error_severity("Access denied") == ErrorSeverity.CRITICAL
        assert self.executor._determine_error_severity("Out of memory") == ErrorSeverity.CRITICAL
        
        # Test non-critical
        assert self.executor._determine_error_severity("File not found") == ErrorSeverity.NON_CRITICAL
        assert self.executor._determine_error_severity("Invalid parameter") == ErrorSeverity.NON_CRITICAL
        assert self.executor._determine_error_severity(None) == ErrorSeverity.NON_CRITICAL


class TestParallelExecution:
    """Test parallel execution support."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = FunctionRegistry()
        
        # Register independent functions
        def func_a(value: str) -> dict:
            import time
            time.sleep(0.1)
            return {"success": True, "value": f"a_{value}"}
        
        def func_b(value: str) -> dict:
            import time
            time.sleep(0.1)
            return {"success": True, "value": f"b_{value}"}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        }
        
        for name, impl in [("func_a", func_a), ("func_b", func_b)]:
            self.registry.register_function(
                name=name,
                implementation=impl,
                schema=schema,
                category="keyboard_operations"
            )
        
        self.executor = FunctionExecutor(self.registry)
    
    def test_parallel_execution(self):
        """Test parallel execution of independent operations."""
        function_calls = [
            FunctionCall(name="func_a", arguments={"value": "1"}),
            FunctionCall(name="func_b", arguments={"value": "2"})
        ]
        
        result = self.executor.execute_sequence(function_calls, parallel=True)
        
        # Verify all executed successfully (Requirement 12.4)
        assert result.overall_success == True
        assert result.total_steps == 2
        assert result.successful_steps == 2
        assert result.failed_steps == 0
        
        # Verify results are in original order
        assert result.step_results[0].function_name == "func_a"
        assert result.step_results[1].function_name == "func_b"


class TestOverallStatusReporting:
    """Test overall status reporting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = FunctionRegistry()
        
        def success_func(value: str) -> dict:
            return {"success": True, "value": value}
        
        def fail_func(value: str) -> dict:
            return {"success": False, "message": "Failed"}
        
        schema = {
            "description": "Test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"}
                },
                "required": ["value"]
            }
        }
        
        for name, impl in [("success_func", success_func), ("fail_func", fail_func)]:
            self.registry.register_function(
                name=name,
                implementation=impl,
                schema=schema,
                category="keyboard_operations"
            )
        
        self.executor = FunctionExecutor(self.registry)
    
    def test_all_success_status(self):
        """Test overall status when all steps succeed."""
        function_calls = [
            FunctionCall(name="success_func", arguments={"value": "a"}),
            FunctionCall(name="success_func", arguments={"value": "b"})
        ]
        
        result = self.executor.execute_sequence(function_calls)
        
        # Verify overall status (Requirement 12.5)
        assert result.overall_success == True
        assert result.total_steps == 2
        assert result.successful_steps == 2
        assert result.failed_steps == 0
    
    def test_partial_failure_status(self):
        """Test overall status when some steps fail."""
        function_calls = [
            FunctionCall(name="success_func", arguments={"value": "a"}),
            FunctionCall(name="fail_func", arguments={"value": "b"}),
            FunctionCall(name="success_func", arguments={"value": "c"})
        ]
        
        result = self.executor.execute_sequence(function_calls)
        
        # Verify overall status reflects failures (Requirement 12.5)
        assert result.overall_success == False
        assert result.total_steps == 3
        assert result.successful_steps == 2
        assert result.failed_steps == 1
    
    def test_multi_step_result_to_dict(self):
        """Test MultiStepExecutionResult serialization."""
        function_calls = [
            FunctionCall(name="success_func", arguments={"value": "a"})
        ]
        
        result = self.executor.execute_sequence(function_calls)
        result_dict = result.to_dict()
        
        assert "overall_success" in result_dict
        assert "step_results" in result_dict
        assert "total_steps" in result_dict
        assert "successful_steps" in result_dict
        assert "failed_steps" in result_dict
        assert isinstance(result_dict["step_results"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
