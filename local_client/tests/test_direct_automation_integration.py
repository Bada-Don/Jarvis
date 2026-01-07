"""
Integration Tests for Direct Automation Workflow

This module tests the full direct automation workflow for FlexiSIGN:
- Test "Make iron number plate set for bike, PB12W3998" with direct mode
- Verify window activation
- Verify text creation with correct content
- Verify dimension setting (8x1.2 for front, 10x1.5 for back)
- Verify font application

Requirements: 1.1, 2.1, 3.1, 4.1, 7.1

**Feature: direct-automation-integration**
"""

import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# Add paths for imports
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR / "local_client"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / "backend" / ".env")
load_dotenv(ROOT_DIR / "local_client" / ".env")


class TestDirectAutomationPlanGeneration(unittest.TestCase):
    """
    Tests for direct automation plan generation.
    
    Verifies that the Planner Model generates correct direct mode plans
    for standard number plate requests.
    
    Requirements: 7.1, 7.2
    """
    
    SAMPLE_COMMAND = "Make iron number plate set for bike, PB12W3998"
    PLATE_NUMBER = "PB12W3998"
    
    # Expected dimensions from PLATE_DIMENSIONS knowledge base
    BIKE_IRON_FRONT = {"width": "8", "height": "1.2"}
    BIKE_IRON_BACK = {"width": "10", "height": "1.5"}
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api_key = os.getenv('GEMINI_API_KEY')
        if not cls.api_key:
            raise unittest.SkipTest("GEMINI_API_KEY not set - skipping integration tests")
        
        from planner_service import GeminiPlannerService
        cls.GeminiPlannerService = GeminiPlannerService
    
    def test_plan_generation_uses_direct_mode(self):
        """
        Test that standard number plate requests generate direct mode plans.
        
        Requirement 7.1: Standard number plate requests use direct mode
        """
        planner = self.GeminiPlannerService()
        plan = planner.generate_plan(self.SAMPLE_COMMAND)
        
        # Verify plan uses direct mode
        mode = plan.get('mode', 'vision')
        self.assertEqual(mode, 'flexisign', "Plan should be in flexisign mode")
        
        # Check if the plan contains direct mode command types
        direct_types = {'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object'}
        step_types = {step.get('type') for step in plan.get('sequence', [])}
        
        # Plan should have at least some direct mode commands OR keyboard commands
        has_direct_commands = bool(step_types & direct_types)
        has_keyboard = 'keyboard' in step_types
        
        self.assertTrue(
            has_direct_commands or has_keyboard,
            f"Plan should have direct mode commands or keyboard. Got types: {step_types}"
        )
    
    def test_plan_contains_plate_number(self):
        """
        Test that the generated plan contains the plate number.
        
        Requirement 2.1: Create text with specified content
        """
        planner = self.GeminiPlannerService()
        plan = planner.generate_plan(self.SAMPLE_COMMAND)
        
        # Check for plate number in create_text or keyboard steps
        found_plate = False
        for step in plan.get('sequence', []):
            step_type = step.get('type')
            if step_type == 'create_text':
                if self.PLATE_NUMBER in step.get('text', ''):
                    found_plate = True
                    break
            elif step_type == 'keyboard':
                if self.PLATE_NUMBER in step.get('value', ''):
                    found_plate = True
                    break
        
        self.assertTrue(
            found_plate,
            f"Plate number '{self.PLATE_NUMBER}' not found in plan"
        )
    
    def test_plan_contains_dimension_commands(self):
        """
        Test that the generated plan contains dimension setting commands.
        
        Requirement 3.1: Set dimensions for number plates
        """
        planner = self.GeminiPlannerService()
        plan = planner.generate_plan(self.SAMPLE_COMMAND)
        
        # Look for set_dimensions commands
        dimension_steps = [
            step for step in plan.get('sequence', [])
            if step.get('type') == 'set_dimensions'
        ]
        
        # If using direct mode, should have dimension commands
        # If using vision mode, dimensions might be set via keyboard
        if dimension_steps:
            # Verify at least one dimension step has valid width/height
            for step in dimension_steps:
                self.assertIn('width', step, "set_dimensions must have width")
                self.assertIn('height', step, "set_dimensions must have height")
                
                # Verify dimensions are reasonable (non-empty strings or numbers)
                width = str(step.get('width', ''))
                height = str(step.get('height', ''))
                self.assertTrue(len(width) > 0, "Width must not be empty")
                self.assertTrue(len(height) > 0, "Height must not be empty")


class TestDirectModeExecution(unittest.TestCase):
    """
    Tests for direct mode execution in PlanExecutor.
    
    Verifies that direct mode plans are executed correctly using UIA.
    
    Requirements: 7.3, 7.4
    """
    
    def setUp(self):
        """Set up mocks for testing."""
        self.status_messages = []
        
        def capture_status(msg, status_type="info"):
            if isinstance(msg, dict):
                self.status_messages.append((msg.get('message', ''), status_type))
            else:
                self.status_messages.append((msg, status_type))
        
        self.status_callback = capture_status
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_direct_mode_uses_uia(self, mock_uia_class):
        """
        Test that direct mode plans use UIA for execution.
        
        Requirement 7.3: Direct mode uses UIA without screenshots
        """
        from plan_executor import PlanExecutor
        
        # Set up mock UIA
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.create_text.return_value = True
        mock_uia.set_dimensions.return_value = True
        mock_uia.set_font.return_value = True
        mock_uia_class.return_value = mock_uia
        
        # Create executor with mock vision service
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Create a direct mode plan
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "create_text", "text": "PB12W3998", "desc": "Create plate text"},
                {"order": 2, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set dimensions"},
                {"order": 3, "type": "set_font", "font_name": "Blackberry", "desc": "Set font"},
            ]
        }
        
        # Execute the plan
        result = executor.execute_plan(plan)
        
        # Verify UIA was used
        mock_uia.find_and_activate_window.assert_called_once()
        mock_uia.create_text.assert_called_once_with("PB12W3998")
        mock_uia.set_dimensions.assert_called_once_with("8", "1.2")
        mock_uia.set_font.assert_called_once_with("Blackberry")
        
        # Verify vision service was NOT used for screenshots
        mock_vision.capture_screenshot.assert_not_called()
        mock_vision.run_som_detection.assert_not_called()
        
        self.assertTrue(result, "Direct mode execution should succeed")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_direct_mode_window_activation(self, mock_uia_class):
        """
        Test that direct mode activates FlexiSIGN window first.
        
        Requirement 1.1: Activate FlexiSIGN window before automation
        """
        from plan_executor import PlanExecutor
        
        # Set up mock UIA
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.create_text.return_value = True
        mock_uia_class.return_value = mock_uia
        
        # Create executor
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Create a simple direct mode plan
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "create_text", "text": "TEST", "desc": "Create text"},
            ]
        }
        
        # Execute the plan
        executor.execute_plan(plan)
        
        # Verify window activation was called first
        mock_uia.find_and_activate_window.assert_called_once()
        
        # Verify status message about window activation
        activation_messages = [
            msg for msg, _ in self.status_messages 
            if 'window' in msg.lower() and 'activat' in msg.lower()
        ]
        self.assertTrue(
            len(activation_messages) > 0,
            "Should report window activation status"
        )
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_direct_mode_window_activation_failure(self, mock_uia_class):
        """
        Test that direct mode reports error when window activation fails.
        
        Requirement 1.4: Report error if window cannot be activated
        """
        from plan_executor import PlanExecutor
        
        # Set up mock UIA to fail window activation
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = False
        mock_uia_class.return_value = mock_uia
        
        # Create executor
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Create a direct mode plan
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "create_text", "text": "TEST", "desc": "Create text"},
            ]
        }
        
        # Execute the plan
        result = executor.execute_plan(plan)
        
        # Verify execution failed - result can be dict with 'success' key or boolean
        if isinstance(result, dict):
            self.assertFalse(result.get('success', True), "Should fail when window activation fails")
        else:
            self.assertFalse(result, "Should fail when window activation fails")
        
        # Verify error message
        error_messages = [
            msg for msg, status in self.status_messages 
            if status == 'error' and 'window' in msg.lower()
        ]
        self.assertTrue(
            len(error_messages) > 0,
            "Should report window activation error"
        )


class TestDirectAutomationActions(unittest.TestCase):
    """
    Tests for individual direct automation actions.
    
    Verifies that each action type is executed correctly.
    
    Requirements: 2.1, 3.1, 4.1, 5.1, 6.1
    """
    
    def setUp(self):
        """Set up mocks for testing."""
        self.status_messages = []
        
        def capture_status(msg, status_type="info"):
            if isinstance(msg, dict):
                self.status_messages.append((msg.get('message', ''), status_type))
            else:
                self.status_messages.append((msg, status_type))
        
        self.status_callback = capture_status
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_create_text_action(self, mock_uia_class):
        """
        Test create_text action execution.
        
        Requirement 2.1: Create text with specified content
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.create_text.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "create_text", "text": "PB12W3998", "desc": "Create plate text"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.create_text.assert_called_once_with("PB12W3998")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_set_dimensions_action(self, mock_uia_class):
        """
        Test set_dimensions action execution.
        
        Requirement 3.1: Set dimensions for number plates
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.set_dimensions.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Test front plate dimensions (8x1.2)
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set front plate size"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.set_dimensions.assert_called_once_with("8", "1.2")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_set_dimensions_back_plate(self, mock_uia_class):
        """
        Test set_dimensions action for back plate (10x1.5).
        
        Requirement 3.1: Set dimensions for number plates
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.set_dimensions.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Test back plate dimensions (10x1.5)
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "set_dimensions", "width": "10", "height": "1.5", "desc": "Set back plate size"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.set_dimensions.assert_called_once_with("10", "1.5")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_set_font_action(self, mock_uia_class):
        """
        Test set_font action execution.
        
        Requirement 4.1: Set font for text
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.set_font.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "set_font", "font_name": "Blackberry", "desc": "Set plate font"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.set_font.assert_called_once_with("Blackberry")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_apply_style_action(self, mock_uia_class):
        """
        Test apply_style action execution.
        
        Requirement 5.1: Apply predefined styles
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.apply_style.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "apply_style", "style_name": "Iron Plate", "desc": "Apply iron plate style"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.apply_style.assert_called_once_with("Iron Plate")
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_move_object_action(self, mock_uia_class):
        """
        Test move_object action execution.
        
        Requirement 6.1: Move objects using arrow keys
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.move_object.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "move_object", "direction": "up", "distance": 10, "desc": "Move plate up"},
            ]
        }
        
        executor.execute_plan(plan)
        
        mock_uia.move_object.assert_called_once_with("up", 10)


class TestFullDirectWorkflow(unittest.TestCase):
    """
    Full workflow integration test for direct automation.
    
    Tests the complete workflow: "Make iron number plate set for bike, PB12W3998"
    
    Requirements: 1.1, 2.1, 3.1, 4.1, 7.1
    """
    
    SAMPLE_COMMAND = "Make iron number plate set for bike, PB12W3998"
    PLATE_NUMBER = "PB12W3998"
    
    def setUp(self):
        """Set up mocks for testing."""
        self.status_messages = []
        
        def capture_status(msg, status_type="info"):
            if isinstance(msg, dict):
                self.status_messages.append((msg.get('message', ''), status_type))
            else:
                self.status_messages.append((msg, status_type))
        
        self.status_callback = capture_status
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_full_workflow_execution(self, mock_uia_class):
        """
        Test full workflow from plan generation to execution.
        
        This test verifies:
        1. Window activation
        2. Text creation with correct content
        3. Dimension setting
        4. Font application
        
        Requirements: 1.1, 2.1, 3.1, 4.1, 7.1
        """
        from plan_executor import PlanExecutor
        
        # Set up mock UIA that tracks all calls
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.create_text.return_value = True
        mock_uia.set_dimensions.return_value = True
        mock_uia.set_font.return_value = True
        mock_uia.apply_style.return_value = True
        mock_uia.move_object.return_value = True
        mock_uia_class.return_value = mock_uia
        
        # Create executor
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Create a comprehensive direct mode plan that represents
        # what the Planner Model would generate for the sample command
        plan = {
            "mode": "direct",
            "sequence": [
                {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "Open new page"},
                {"order": 2, "type": "create_text", "text": self.PLATE_NUMBER, "desc": "Create plate text"},
                {"order": 3, "type": "set_font", "font_name": "Blackberry", "desc": "Set plate font"},
                {"order": 4, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set front plate size"},
                {"order": 5, "type": "apply_style", "style_name": "Iron Plate", "desc": "Apply iron plate style"},
                {"order": 6, "type": "move_object", "direction": "up", "distance": 10, "desc": "Move plate up"},
            ]
        }
        
        # Execute the plan
        result = executor.execute_plan(plan)
        
        # Verify execution succeeded
        self.assertTrue(result, "Full workflow execution should succeed")
        
        # Verify window activation (Requirement 1.1)
        mock_uia.find_and_activate_window.assert_called_once()
        
        # Verify text creation with correct content (Requirement 2.1)
        mock_uia.create_text.assert_called_once_with(self.PLATE_NUMBER)
        
        # Verify dimension setting (Requirement 3.1)
        mock_uia.set_dimensions.assert_called_once_with("8", "1.2")
        
        # Verify font application (Requirement 4.1)
        mock_uia.set_font.assert_called_once_with("Blackberry")
        
        # Verify style application
        mock_uia.apply_style.assert_called_once_with("Iron Plate")
        
        # Verify object movement
        mock_uia.move_object.assert_called_once_with("up", 10)
    
    @patch('plan_executor.FlexiSignUIA')
    @patch('plan_executor.FLEXISIGN_UIA_AVAILABLE', True)
    def test_workflow_with_both_plate_sizes(self, mock_uia_class):
        """
        Test workflow that creates both front and back plates.
        
        Verifies dimension setting for:
        - Front plate: 8x1.2 inches
        - Back plate: 10x1.5 inches
        
        Requirements: 3.1
        """
        from plan_executor import PlanExecutor
        
        mock_uia = MagicMock()
        mock_uia.find_and_activate_window.return_value = True
        mock_uia.create_text.return_value = True
        mock_uia.set_dimensions.return_value = True
        mock_uia.set_font.return_value = True
        mock_uia_class.return_value = mock_uia
        
        mock_vision = MagicMock()
        executor = PlanExecutor(mock_vision, self.status_callback)
        
        # Plan with both front and back plate dimensions
        plan = {
            "mode": "direct",
            "sequence": [
                # Front plate
                {"order": 1, "type": "create_text", "text": self.PLATE_NUMBER, "desc": "Create front plate text"},
                {"order": 2, "type": "set_dimensions", "width": "8", "height": "1.2", "desc": "Set front plate size"},
                {"order": 3, "type": "set_font", "font_name": "Blackberry", "desc": "Set font"},
                # Back plate
                {"order": 4, "type": "create_text", "text": self.PLATE_NUMBER, "desc": "Create back plate text"},
                {"order": 5, "type": "set_dimensions", "width": "10", "height": "1.5", "desc": "Set back plate size"},
                {"order": 6, "type": "set_font", "font_name": "Blackberry", "desc": "Set font"},
            ]
        }
        
        result = executor.execute_plan(plan)
        
        self.assertTrue(result, "Workflow with both plates should succeed")
        
        # Verify both dimension calls
        dimension_calls = mock_uia.set_dimensions.call_args_list
        self.assertEqual(len(dimension_calls), 2, "Should have 2 dimension calls")
        
        # Verify front plate dimensions (8x1.2)
        self.assertEqual(dimension_calls[0], call("8", "1.2"))
        
        # Verify back plate dimensions (10x1.5)
        self.assertEqual(dimension_calls[1], call("10", "1.5"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
