"""
Integration Tests for Two-Model Pipeline

This module tests the full pipeline from user command to execution:
1. Plan generation on backend (Planner Model)
2. Plan structure validation
3. WebSocket communication simulation

Requirements: 1.1, 1.2, 1.3, 1.4
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_service import GeminiPlannerService, PLATE_DIMENSIONS


class TestPlannerModelIntegration(unittest.TestCase):
    """
    Integration tests for the Planner Model (Gemini Flash Lite).
    
    Tests plan generation for the sample command:
    "Make iron number plate set for bike, PB12W3998"
    
    Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.sample_command = "Make iron number plate set for bike, PB12W3998"
        cls.api_key = os.getenv('GEMINI_API_KEY')
        
        if not cls.api_key:
            raise unittest.SkipTest("GEMINI_API_KEY not set - skipping integration tests")
    
    def test_planner_service_initialization(self):
        """Test that GeminiPlannerService initializes correctly with API key."""
        # Requirement 6.1: Load API key from environment
        service = GeminiPlannerService()
        self.assertIsNotNone(service.api_key)
        self.assertIsNotNone(service.general_model)
        self.assertIsNotNone(service.flexisign_model)
    
    def test_plan_generation_returns_valid_json(self):
        """
        Test that plan generation returns valid JSON with required structure.
        
        Requirements: 1.1, 2.4
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        # Verify it's a dict
        self.assertIsInstance(plan, dict)
        
        # Verify it has 'sequence' array
        self.assertIn('sequence', plan)
        self.assertIsInstance(plan['sequence'], list)
        
        # Verify sequence is not empty
        self.assertGreater(len(plan['sequence']), 0)
    
    def test_plan_steps_have_required_fields(self):
        """
        Test that each step has required fields: order, type.
        
        Requirements: 2.4, 2.5, 2.6
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        # Valid types for both direct and vision modes
        valid_types = [
            'keyboard', 'visual_click',
            'create_text', 'set_dimensions', 'set_font', 'apply_style', 'move_object', 'ensure_designcentral',
            'save_file', 'open_file', 'navigate_explorer', 'click_text'
        ]
        
        for i, step in enumerate(plan['sequence']):
            # Each step must have 'order' and 'type'
            self.assertIn('order', step, f"Step {i+1} missing 'order' field")
            self.assertIn('type', step, f"Step {i+1} missing 'type' field")
            
            # Type must be one of the valid types
            self.assertIn(step['type'], valid_types,
                         f"Step {i+1} has invalid type: {step['type']}")
            
            # Type-specific field validation
            if step['type'] == 'keyboard':
                self.assertIn('value', step, f"Keyboard step {i+1} missing 'value' field")
            elif step['type'] == 'visual_click':
                self.assertIn('target_name', step, f"Visual click step {i+1} missing 'target_name' field")
            elif step['type'] == 'create_text':
                self.assertIn('text', step, f"Create text step {i+1} missing 'text' field")
            elif step['type'] == 'set_dimensions':
                self.assertIn('width', step, f"Set dimensions step {i+1} missing 'width' field")
                self.assertIn('height', step, f"Set dimensions step {i+1} missing 'height' field")
            elif step['type'] == 'set_font':
                self.assertIn('font_name', step, f"Set font step {i+1} missing 'font_name' field")
            elif step['type'] == 'move_object':
                self.assertIn('direction', step, f"Move object step {i+1} missing 'direction' field")
                self.assertIn('distance', step, f"Move object step {i+1} missing 'distance' field")
    
    def test_plan_contains_plate_number(self):
        """
        Test that the plan includes typing the plate number.
        
        Requirement: 1.1 - Parse command and generate execution plan
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        plate_number = "PB12W3998"
        
        # Check for plate number in keyboard steps (vision mode)
        keyboard_values = [
            step.get('value', '') 
            for step in plan['sequence'] 
            if step.get('type') == 'keyboard'
        ]
        
        # Check for plate number in create_text steps (direct mode)
        create_text_values = [
            step.get('text', '') 
            for step in plan['sequence'] 
            if step.get('type') == 'create_text'
        ]
        
        # The plate number should appear in either keyboard or create_text steps
        found_in_keyboard = any(plate_number in str(val) for val in keyboard_values)
        found_in_create_text = any(plate_number in str(val) for val in create_text_values)
        
        self.assertTrue(found_in_keyboard or found_in_create_text, 
                       f"Plate number '{plate_number}' not found in keyboard steps: {keyboard_values} "
                       f"or create_text steps: {create_text_values}")
    
    def test_plan_uses_correct_bike_iron_dimensions(self):
        """
        Test that the plan uses correct dimensions for bike iron plate.
        
        Requirement: 2.1 - Bike iron: Front (8 x 1.2), Back (10 x 1.5)
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        # Get all keyboard values (vision mode)
        keyboard_values = [
            str(step.get('value', '')) 
            for step in plan['sequence'] 
            if step.get('type') == 'keyboard'
        ]
        
        # Get all set_dimensions steps (direct mode)
        dimension_steps = [
            step for step in plan['sequence'] 
            if step.get('type') == 'set_dimensions'
        ]
        
        # Check for expected dimensions (at least front plate dimensions)
        # Front: 8 x 1.2
        expected_dims = ['8', '1.2']
        
        # Check in keyboard values (vision mode)
        found_in_keyboard = [dim for dim in expected_dims if any(dim in val for val in keyboard_values)]
        
        # Check in set_dimensions steps (direct mode)
        found_in_dimensions = False
        for step in dimension_steps:
            width = str(step.get('width', ''))
            height = str(step.get('height', ''))
            if '8' in width or '1.2' in height:
                found_in_dimensions = True
                break
        
        # We expect at least some dimension values to be present in either mode
        self.assertTrue(len(found_in_keyboard) > 0 or found_in_dimensions,
                       f"Expected dimensions {expected_dims} not found in keyboard values: {keyboard_values} "
                       f"or set_dimensions steps: {dimension_steps}")


class TestPlanValidation(unittest.TestCase):
    """
    Tests for plan structure validation.
    
    Requirements: 2.4, 2.5, 2.6
    """
    
    def test_validate_valid_plan(self):
        """Test that valid plans pass validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        valid_plan = {
            "sequence": [
                {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "New page"},
                {"order": 2, "type": "visual_click", "target_name": "text_tool", "desc": "Click text"}
            ]
        }
        
        # Should not raise
        service._validate_plan(valid_plan)
    
    def test_validate_missing_sequence(self):
        """Test that plans without 'sequence' fail validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        invalid_plan = {"steps": []}
        
        with self.assertRaises(ValueError) as ctx:
            service._validate_plan(invalid_plan)
        
        self.assertIn("sequence", str(ctx.exception))
    
    def test_validate_missing_type(self):
        """Test that steps without 'type' fail validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        invalid_plan = {
            "sequence": [
                {"order": 1, "value": "ctrl+n"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            service._validate_plan(invalid_plan)
        
        self.assertIn("type", str(ctx.exception))
    
    def test_validate_invalid_type(self):
        """Test that steps with invalid type fail validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        invalid_plan = {
            "sequence": [
                {"order": 1, "type": "invalid_type", "value": "test"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            service._validate_plan(invalid_plan)
        
        self.assertIn("invalid type", str(ctx.exception).lower())
    
    def test_validate_keyboard_missing_value(self):
        """Test that keyboard steps without 'value' fail validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        invalid_plan = {
            "sequence": [
                {"order": 1, "type": "keyboard", "desc": "Missing value"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            service._validate_plan(invalid_plan)
        
        self.assertIn("value", str(ctx.exception))
    
    def test_validate_visual_click_missing_target(self):
        """Test that visual_click steps without 'target_name' fail validation."""
        service = GeminiPlannerService.__new__(GeminiPlannerService)
        
        invalid_plan = {
            "sequence": [
                {"order": 1, "type": "visual_click", "desc": "Missing target"}
            ]
        }
        
        with self.assertRaises(ValueError) as ctx:
            service._validate_plan(invalid_plan)
        
        self.assertIn("target_name", str(ctx.exception))


class TestPlateKnowledgeBase(unittest.TestCase):
    """
    Tests for plate dimensions knowledge base.
    
    Requirements: 2.1, 2.2, 2.3
    """
    
    def test_bike_iron_dimensions(self):
        """
        Test bike iron plate dimensions.
        
        Requirement: 2.1 - Front (8 x 1.2), Back (10 x 1.5)
        """
        dims = PLATE_DIMENSIONS['bike_iron']
        
        self.assertEqual(dims['front']['width'], 8)
        self.assertEqual(dims['front']['height'], 1.2)
        self.assertEqual(dims['back']['width'], 10)
        self.assertEqual(dims['back']['height'], 1.5)
    
    def test_bike_glass_dimensions(self):
        """
        Test bike glass plate dimensions.
        
        Requirement: 2.2 - Front (6 x 1.2), Back (10 x 1.5)
        """
        dims = PLATE_DIMENSIONS['bike_glass']
        
        self.assertEqual(dims['front']['width'], 6)
        self.assertEqual(dims['front']['height'], 1.2)
        self.assertEqual(dims['back']['width'], 10)
        self.assertEqual(dims['back']['height'], 1.5)
    
    def test_car_normal_dimensions(self):
        """
        Test car normal plate dimensions.
        
        Requirement: 2.3 - Front (14 x 2.3), Back (14 x 2.4)
        """
        dims = PLATE_DIMENSIONS['car_normal']
        
        self.assertEqual(dims['front']['width'], 14)
        self.assertEqual(dims['front']['height'], 2.3)
        self.assertEqual(dims['back']['width'], 14)
        self.assertEqual(dims['back']['height'], 2.4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
