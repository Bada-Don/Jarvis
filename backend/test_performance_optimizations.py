"""
Test Performance Optimizations

Tests for task 20: Performance optimization
- Model loading optimizations (caching, lazy loading, memory monitoring)
- Function execution optimizations (profiling, async execution)
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from functiongemma_service import FunctionGemmaPlannerService, FunctionCall
from function_executor import FunctionExecutor, MultiStepExecutionResult
from function_registry import FunctionRegistry


class TestModelLoadingOptimizations:
    """Test model loading optimizations (Task 20.1)"""
    
    def test_model_caching(self):
        """Test that model stays in memory after first load (caching)"""
        # Mock the transformers imports and os.path.exists
        with patch('transformers.AutoProcessor') as mock_processor, \
             patch('transformers.AutoModelForCausalLM') as mock_model, \
             patch('os.path.exists', return_value=True):
            
            mock_processor.from_pretrained.return_value = Mock()
            mock_model.from_pretrained.return_value = Mock()
            
            service = FunctionGemmaPlannerService(
                model_path="./test_model",
                lazy_load=False
            )
            
            # First load
            assert service.is_loaded()
            first_load_calls = mock_model.from_pretrained.call_count
            
            # Second load should use cache
            service.load_model()
            second_load_calls = mock_model.from_pretrained.call_count
            
            # Should not have loaded again
            assert first_load_calls == second_load_calls
    
    def test_lazy_loading(self):
        """Test that model is not loaded until first use"""
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        # Model should not be loaded yet
        assert not service.is_loaded()
    
    def test_memory_monitoring(self):
        """Test that memory usage is tracked during loading"""
        with patch('transformers.AutoProcessor') as mock_processor, \
             patch('transformers.AutoModelForCausalLM') as mock_model, \
             patch('os.path.exists', return_value=True):
            
            mock_processor.from_pretrained.return_value = Mock()
            mock_model.from_pretrained.return_value = Mock()
            
            service = FunctionGemmaPlannerService(
                model_path="./test_model",
                lazy_load=False
            )
            
            # Should have tracked memory
            assert service._memory_before_load > 0
    
    def test_get_memory_usage(self):
        """Test memory usage statistics"""
        service = FunctionGemmaPlannerService(
            model_path="./test_model",
            lazy_load=True
        )
        
        stats = service.get_memory_usage()
        
        assert "current" in stats
        assert "model_overhead" in stats
        assert "available" in stats
        assert stats["current"] > 0
        assert stats["available"] > 0


class TestFunctionExecutionOptimizations:
    """Test function execution optimizations (Task 20.2)"""
    
    def test_execution_profiling(self):
        """Test that execution times are tracked when profiling is enabled"""
        registry = FunctionRegistry()
        
        # Register a test function using a valid category and proper schema format
        def slow_function(delay: float = 0.1):
            time.sleep(delay)
            return {"success": True, "message": "Done"}
        
        registry.register_function(
            name="slow_function",
            implementation=slow_function,
            schema={
                "name": "slow_function",
                "description": "Test slow function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "delay": {"type": "number"}
                    }
                }
            },
            category="file_operations"  # Use valid category
        )
        
        executor = FunctionExecutor(
            function_registry=registry,
            enable_profiling=True
        )
        
        # Execute function
        fc = FunctionCall(name="slow_function", arguments={"delay": 0.1})
        result = executor.execute_function_call(fc)
        
        assert result.success
        
        # Check profiling data
        stats = executor.get_profiling_stats()
        assert "slow_function" in stats
        assert stats["slow_function"]["count"] == 1
        assert stats["slow_function"]["avg_time"] >= 0.1
    
    def test_get_slow_operations(self):
        """Test identification of slow operations"""
        registry = FunctionRegistry()
        
        # Register fast and slow functions
        def fast_function():
            return {"success": True}
        
        def slow_function():
            time.sleep(0.5)
            return {"success": True}
        
        registry.register_function(
            name="fast_function",
            implementation=fast_function,
            schema={
                "name": "fast_function",
                "description": "Fast test function",
                "parameters": {"type": "object", "properties": {}}
            },
            category="file_operations"
        )
        
        registry.register_function(
            name="slow_function",
            implementation=slow_function,
            schema={
                "name": "slow_function",
                "description": "Slow test function",
                "parameters": {"type": "object", "properties": {}}
            },
            category="folder_operations"
        )
        
        executor = FunctionExecutor(
            function_registry=registry,
            enable_profiling=True
        )
        
        # Execute both functions
        executor.execute_function_call(FunctionCall(name="fast_function", arguments={}))
        executor.execute_function_call(FunctionCall(name="slow_function", arguments={}))
        
        # Get slow operations (threshold: 0.3s)
        slow_ops = executor.get_slow_operations(threshold_seconds=0.3)
        
        assert "slow_function" in slow_ops
        assert "fast_function" not in slow_ops
    
    def test_profiling_report(self):
        """Test profiling report generation"""
        registry = FunctionRegistry()
        
        def test_function():
            return {"success": True}
        
        registry.register_function(
            name="test_function",
            implementation=test_function,
            schema={
                "name": "test_function",
                "description": "Test function",
                "parameters": {"type": "object", "properties": {}}
            },
            category="file_operations"
        )
        
        executor = FunctionExecutor(
            function_registry=registry,
            enable_profiling=True
        )
        
        # Execute function multiple times
        for _ in range(3):
            executor.execute_function_call(
                FunctionCall(name="test_function", arguments={})
            )
        
        # Should not raise exception
        executor.print_profiling_report()
        
        # Reset profiling data
        executor.reset_profiling_data()
        stats = executor.get_profiling_stats()
        assert len(stats) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
