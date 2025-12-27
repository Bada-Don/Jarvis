"""
Unit tests for window_management module.

Tests window management functions including activate, close, minimize, maximize,
and get_active_window operations.
"""

import pytest
import sys
import os

# Add backend/functions to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions'))

from window_management import (
    activate_window,
    close_window,
    minimize_window,
    maximize_window,
    get_active_window
)


class TestWindowManagement:
    """Test suite for window management functions."""
    
    def test_activate_window_invalid_type(self):
        """Test activate_window with invalid identifier type."""
        result = activate_window(123)
        assert result["success"] is False
        assert "must be a string" in result["message"]
    
    def test_activate_window_empty_identifier(self):
        """Test activate_window with empty identifier."""
        result = activate_window("")
        assert result["success"] is False
        assert "cannot be empty" in result["message"]
    
    def test_activate_window_whitespace_identifier(self):
        """Test activate_window with whitespace-only identifier."""
        result = activate_window("   ")
        assert result["success"] is False
        assert "cannot be empty" in result["message"]
    
    def test_activate_window_nonexistent(self):
        """Test activate_window with non-existent window."""
        result = activate_window("NonExistentWindowXYZ123")
        assert result["success"] is False
        assert "Window not found" in result["message"]
        assert result["identifier"] == "NonExistentWindowXYZ123"
    
    def test_close_window_invalid_type(self):
        """Test close_window with invalid identifier type."""
        result = close_window(123)
        assert result["success"] is False
        assert "must be a string" in result["message"]
    
    def test_close_window_empty_identifier(self):
        """Test close_window with empty identifier."""
        result = close_window("")
        assert result["success"] is False
        assert "cannot be empty" in result["message"]
    
    def test_close_window_nonexistent(self):
        """Test close_window with non-existent window."""
        result = close_window("NonExistentWindowXYZ123")
        assert result["success"] is False
        assert "Window not found" in result["message"]
    
    def test_minimize_window_invalid_type(self):
        """Test minimize_window with invalid identifier type."""
        result = minimize_window(123)
        assert result["success"] is False
        assert "must be a string" in result["message"]
    
    def test_minimize_window_empty_identifier(self):
        """Test minimize_window with empty identifier."""
        result = minimize_window("")
        assert result["success"] is False
        assert "cannot be empty" in result["message"]
    
    def test_minimize_window_nonexistent(self):
        """Test minimize_window with non-existent window."""
        result = minimize_window("NonExistentWindowXYZ123")
        assert result["success"] is False
        assert "Window not found" in result["message"]
    
    def test_maximize_window_invalid_type(self):
        """Test maximize_window with invalid identifier type."""
        result = maximize_window(123)
        assert result["success"] is False
        assert "must be a string" in result["message"]
    
    def test_maximize_window_empty_identifier(self):
        """Test maximize_window with empty identifier."""
        result = maximize_window("")
        assert result["success"] is False
        assert "cannot be empty" in result["message"]
    
    def test_maximize_window_nonexistent(self):
        """Test maximize_window with non-existent window."""
        result = maximize_window("NonExistentWindowXYZ123")
        assert result["success"] is False
        assert "Window not found" in result["message"]
    
    def test_get_active_window(self):
        """Test get_active_window returns a result."""
        result = get_active_window()
        # Should always return a result (success or failure)
        assert "success" in result
        assert "title" in result
        assert "message" in result
        # The result depends on whether there's an active window
        # We just verify the structure is correct
    
    def test_activate_window_return_structure(self):
        """Test activate_window returns correct structure."""
        result = activate_window("test")
        assert "success" in result
        assert "message" in result
        assert "identifier" in result
        assert "window_title" in result
    
    def test_close_window_return_structure(self):
        """Test close_window returns correct structure."""
        result = close_window("test")
        assert "success" in result
        assert "message" in result
        assert "identifier" in result
        assert "window_title" in result
    
    def test_minimize_window_return_structure(self):
        """Test minimize_window returns correct structure."""
        result = minimize_window("test")
        assert "success" in result
        assert "message" in result
        assert "identifier" in result
        assert "window_title" in result
    
    def test_maximize_window_return_structure(self):
        """Test maximize_window returns correct structure."""
        result = maximize_window("test")
        assert "success" in result
        assert "message" in result
        assert "identifier" in result
        assert "window_title" in result
    
    def test_get_active_window_return_structure(self):
        """Test get_active_window returns correct structure."""
        result = get_active_window()
        assert "success" in result
        assert "title" in result
        assert "message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
