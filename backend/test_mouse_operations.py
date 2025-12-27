"""
Unit tests for mouse operations module.

Tests the mouse automation functions including clicking, double-clicking,
right-clicking, moving the mouse, and dragging.
"""

import pytest
from unittest.mock import patch, MagicMock
from functions.mouse_operations import (
    click, double_click, right_click, move_mouse, drag,
    validate_coordinates, get_screen_size
)


@pytest.fixture
def mock_screen_size():
    """Mock screen size for testing."""
    with patch('functions.mouse_operations.pyautogui.size') as mock_size:
        mock_size.return_value = (1920, 1080)
        yield mock_size


@pytest.fixture
def mock_pyautogui():
    """Mock pyautogui functions."""
    with patch('functions.mouse_operations.pyautogui') as mock:
        mock.size.return_value = (1920, 1080)
        mock.FAILSAFE = False
        mock.PAUSE = 0
        yield mock


class TestCoordinateValidation:
    """Test coordinate validation functionality."""
    
    def test_validate_coordinates_valid(self, mock_screen_size):
        """Test validation with valid coordinates."""
        is_valid, error_msg = validate_coordinates(100, 200)
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_coordinates_negative_x(self, mock_screen_size):
        """Test validation with negative X coordinate."""
        is_valid, error_msg = validate_coordinates(-10, 200)
        assert is_valid is False
        assert "out of bounds" in error_msg
    
    def test_validate_coordinates_negative_y(self, mock_screen_size):
        """Test validation with negative Y coordinate."""
        is_valid, error_msg = validate_coordinates(100, -10)
        assert is_valid is False
        assert "out of bounds" in error_msg
    
    def test_validate_coordinates_x_too_large(self, mock_screen_size):
        """Test validation with X coordinate beyond screen width."""
        is_valid, error_msg = validate_coordinates(2000, 200)
        assert is_valid is False
        assert "out of bounds" in error_msg
    
    def test_validate_coordinates_y_too_large(self, mock_screen_size):
        """Test validation with Y coordinate beyond screen height."""
        is_valid, error_msg = validate_coordinates(100, 1100)
        assert is_valid is False
        assert "out of bounds" in error_msg
    
    def test_validate_coordinates_at_boundary(self, mock_screen_size):
        """Test validation at screen boundaries."""
        # At max valid coordinates (width-1, height-1)
        is_valid, error_msg = validate_coordinates(1919, 1079)
        assert is_valid is True
        assert error_msg == ""


class TestClick:
    """Test click function."""
    
    def test_click_valid_coordinates(self, mock_pyautogui):
        """Test clicking at valid coordinates."""
        result = click(100, 200)
        
        assert result["success"] is True
        assert result["x"] == 100
        assert result["y"] == 200
        assert "successfully" in result["message"]
        
        mock_pyautogui.click.assert_called_once_with(100, 200)
    
    def test_click_invalid_x_type(self, mock_pyautogui):
        """Test clicking with invalid X coordinate type."""
        result = click("100", 200)
        
        assert result["success"] is False
        assert "must be an integer" in result["message"]
        mock_pyautogui.click.assert_not_called()
    
    def test_click_invalid_y_type(self, mock_pyautogui):
        """Test clicking with invalid Y coordinate type."""
        result = click(100, "200")
        
        assert result["success"] is False
        assert "must be an integer" in result["message"]
        mock_pyautogui.click.assert_not_called()
    
    def test_click_out_of_bounds(self, mock_pyautogui):
        """Test clicking at out-of-bounds coordinates."""
        result = click(3000, 200)
        
        assert result["success"] is False
        assert "out of bounds" in result["message"]
        mock_pyautogui.click.assert_not_called()


class TestDoubleClick:
    """Test double_click function."""
    
    def test_double_click_valid_coordinates(self, mock_pyautogui):
        """Test double-clicking at valid coordinates."""
        result = double_click(100, 200)
        
        assert result["success"] is True
        assert result["x"] == 100
        assert result["y"] == 200
        assert "successfully" in result["message"]
        
        mock_pyautogui.doubleClick.assert_called_once_with(100, 200)
    
    def test_double_click_out_of_bounds(self, mock_pyautogui):
        """Test double-clicking at out-of-bounds coordinates."""
        result = double_click(-10, 200)
        
        assert result["success"] is False
        assert "out of bounds" in result["message"]
        mock_pyautogui.doubleClick.assert_not_called()


class TestRightClick:
    """Test right_click function."""
    
    def test_right_click_valid_coordinates(self, mock_pyautogui):
        """Test right-clicking at valid coordinates."""
        result = right_click(100, 200)
        
        assert result["success"] is True
        assert result["x"] == 100
        assert result["y"] == 200
        assert "successfully" in result["message"]
        
        mock_pyautogui.rightClick.assert_called_once_with(100, 200)
    
    def test_right_click_out_of_bounds(self, mock_pyautogui):
        """Test right-clicking at out-of-bounds coordinates."""
        result = right_click(100, 2000)
        
        assert result["success"] is False
        assert "out of bounds" in result["message"]
        mock_pyautogui.rightClick.assert_not_called()


class TestMoveMouse:
    """Test move_mouse function."""
    
    def test_move_mouse_valid_coordinates(self, mock_pyautogui):
        """Test moving mouse to valid coordinates."""
        result = move_mouse(100, 200)
        
        assert result["success"] is True
        assert result["x"] == 100
        assert result["y"] == 200
        assert result["duration"] == 0.0
        assert "successfully" in result["message"]
        
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.0)
    
    def test_move_mouse_with_duration(self, mock_pyautogui):
        """Test moving mouse with custom duration."""
        result = move_mouse(100, 200, duration=1.5)
        
        assert result["success"] is True
        assert result["duration"] == 1.5
        
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=1.5)
    
    def test_move_mouse_negative_duration(self, mock_pyautogui):
        """Test moving mouse with negative duration."""
        result = move_mouse(100, 200, duration=-1.0)
        
        assert result["success"] is False
        assert "must be non-negative" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
    
    def test_move_mouse_invalid_duration_type(self, mock_pyautogui):
        """Test moving mouse with invalid duration type."""
        result = move_mouse(100, 200, duration="fast")
        
        assert result["success"] is False
        assert "must be a number" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
    
    def test_move_mouse_out_of_bounds(self, mock_pyautogui):
        """Test moving mouse to out-of-bounds coordinates."""
        result = move_mouse(3000, 200)
        
        assert result["success"] is False
        assert "out of bounds" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()


class TestDrag:
    """Test drag function."""
    
    def test_drag_valid_coordinates(self, mock_pyautogui):
        """Test dragging between valid coordinates."""
        result = drag(100, 200, 300, 400)
        
        assert result["success"] is True
        assert result["start_x"] == 100
        assert result["start_y"] == 200
        assert result["end_x"] == 300
        assert result["end_y"] == 400
        assert result["duration"] == 0.5
        assert "successfully" in result["message"]
        
        # Should move to start position first
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0)
        
        # Then drag relative distance
        mock_pyautogui.drag.assert_called_once_with(200, 200, duration=0.5, button='left')
    
    def test_drag_with_custom_duration(self, mock_pyautogui):
        """Test dragging with custom duration."""
        result = drag(100, 200, 300, 400, duration=2.0)
        
        assert result["success"] is True
        assert result["duration"] == 2.0
        
        mock_pyautogui.drag.assert_called_once_with(200, 200, duration=2.0, button='left')
    
    def test_drag_start_out_of_bounds(self, mock_pyautogui):
        """Test dragging with start coordinates out of bounds."""
        result = drag(-10, 200, 300, 400)
        
        assert result["success"] is False
        assert "Start coordinates invalid" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.drag.assert_not_called()
    
    def test_drag_end_out_of_bounds(self, mock_pyautogui):
        """Test dragging with end coordinates out of bounds."""
        result = drag(100, 200, 3000, 400)
        
        assert result["success"] is False
        assert "End coordinates invalid" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.drag.assert_not_called()
    
    def test_drag_invalid_start_x_type(self, mock_pyautogui):
        """Test dragging with invalid start X type."""
        result = drag("100", 200, 300, 400)
        
        assert result["success"] is False
        assert "must be an integer" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.drag.assert_not_called()
    
    def test_drag_negative_duration(self, mock_pyautogui):
        """Test dragging with negative duration."""
        result = drag(100, 200, 300, 400, duration=-1.0)
        
        assert result["success"] is False
        assert "must be non-negative" in result["message"]
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.drag.assert_not_called()


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_click_at_origin(self, mock_pyautogui):
        """Test clicking at (0, 0)."""
        result = click(0, 0)
        
        assert result["success"] is True
        mock_pyautogui.click.assert_called_once_with(0, 0)
    
    def test_drag_zero_distance(self, mock_pyautogui):
        """Test dragging with zero distance (same start and end)."""
        result = drag(100, 200, 100, 200)
        
        assert result["success"] is True
        mock_pyautogui.drag.assert_called_once_with(0, 0, duration=0.5, button='left')
    
    def test_move_mouse_zero_duration(self, mock_pyautogui):
        """Test moving mouse with zero duration (instant)."""
        result = move_mouse(100, 200, duration=0)
        
        assert result["success"] is True
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
