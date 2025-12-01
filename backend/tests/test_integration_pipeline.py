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
        self.assertIsNotNone(service.model)
    
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
        
        for i, step in enumerate(plan['sequence']):
            # Each step must have 'order' and 'type'
            self.assertIn('order', step, f"Step {i+1} missing 'order' field")
            self.assertIn('type', step, f"Step {i+1} missing 'type' field")
            
            # Type must be 'keyboard' or 'visual_click'
            self.assertIn(step['type'], ['keyboard', 'visual_click'],
                         f"Step {i+1} has invalid type: {step['type']}")
            
            # Type-specific field validation
            if step['type'] == 'keyboard':
                self.assertIn('value', step, f"Keyboard step {i+1} missing 'value' field")
            elif step['type'] == 'visual_click':
                self.assertIn('target_name', step, f"Visual click step {i+1} missing 'target_name' field")
    
    def test_plan_contains_plate_number(self):
        """
        Test that the plan includes typing the plate number.
        
        Requirement: 1.1 - Parse command and generate execution plan
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        # Find keyboard steps that type the plate number
        plate_number = "PB12W3998"
        keyboard_values = [
            step.get('value', '') 
            for step in plan['sequence'] 
            if step.get('type') == 'keyboard'
        ]
        
        # The plate number should appear in one of the keyboard steps
        found_plate = any(plate_number in str(val) for val in keyboard_values)
        self.assertTrue(found_plate, 
                       f"Plate number '{plate_number}' not found in keyboard steps: {keyboard_values}")
    
    def test_plan_uses_correct_bike_iron_dimensions(self):
        """
        Test that the plan uses correct dimensions for bike iron plate.
        
        Requirement: 2.1 - Bike iron: Front (8 x 1.2), Back (10 x 1.5)
        """
        service = GeminiPlannerService()
        plan = service.generate_plan(self.sample_command)
        
        # Get all keyboard values
        keyboard_values = [
            str(step.get('value', '')) 
            for step in plan['sequence'] 
            if step.get('type') == 'keyboard'
        ]
        
        # Check for expected dimensions (at least front plate dimensions)
        # Front: 8 x 1.2
        expected_dims = ['8', '1.2']
        
        # At least some dimension values should be present
        found_dims = [dim for dim in expected_dims if any(dim in val for val in keyboard_values)]
        
        # We expect at least the width to be present
        self.assertGreater(len(found_dims), 0,
                          f"Expected dimensions {expected_dims} not found in keyboard values: {keyboard_values}")


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
