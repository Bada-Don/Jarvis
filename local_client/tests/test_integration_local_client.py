"""
Integration Tests for Local Client Two-Model Pipeline Components

This module tests:
1. Screenshot capture and SoM detection
2. Vision Mapper target identification
3. Coordinate calculation for clicks
4. Plan execution flow

Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.4, 5.1, 5.2, 5.3
"""

import os
import sys
import json
import unittest
import numpy as np

# Add local_client to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision_service import VisionService, filter_boxes, draw_annotations
from plan_executor import PlanExecutor, get_click_coordinates


class TestFilterBoxes(unittest.TestCase):
    """
    Tests for bounding box filtering logic.
    
    Requirements: 3.2, 3.3
    """
    
    def test_filter_removes_tiny_boxes(self):
        """Test that boxes smaller than 10x10 are filtered out."""
        img_width, img_height = 1920, 1080
        
        boxes = np.array([
            [100, 100, 109, 109],  # 9x9 - too small (< 10)
            [200, 200, 250, 250],  # 50x50 - valid
            [300, 300, 305, 305],  # 5x5 - too small
        ])
        
        filtered = filter_boxes(boxes, img_width, img_height)
        
        # Only the 50x50 box should remain
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0][0], 200)
    
    def test_filter_removes_huge_boxes(self):
        """Test that boxes covering >90% of image are filtered out."""
        img_width, img_height = 1000, 1000
        
        boxes = np.array([
            [0, 0, 960, 960],      # 96% of image - too large
            [100, 100, 200, 200],  # 1% of image - valid
        ])
        
        filtered = filter_boxes(boxes, img_width, img_height)
        
        # Only the small box should remain
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0][0], 100)
    
    def test_filter_keeps_valid_boxes(self):
        """Test that valid UI element sized boxes are kept."""
        img_width, img_height = 1920, 1080
        
        boxes = np.array([
            [100, 100, 200, 150],  # 100x50 - valid button size
            [300, 200, 400, 230],  # 100x30 - valid input field
            [500, 300, 600, 400],  # 100x100 - valid icon
        ])
        
        filtered = filter_boxes(boxes, img_width, img_height)
        
        # All boxes should be kept
        self.assertEqual(len(filtered), 3)
    
    def test_filter_empty_input(self):
        """Test that empty input returns empty array."""
        filtered = filter_boxes(np.array([]), 1920, 1080)
        self.assertEqual(len(filtered), 0)


class TestDrawAnnotations(unittest.TestCase):
    """
    Tests for SoM annotation drawing.
    
    Requirements: 3.3, 3.4
    """
    
    def test_draw_annotations_creates_box_map(self):
        """
        Test that draw_annotations creates correct box_map.
        
        Property 2: For N boxes, box_map should have N entries with IDs 1 to N.
        """
        # Create a simple test image
        image = np.zeros((500, 500, 3), dtype=np.uint8)
        
        boxes = np.array([
            [50, 50, 100, 80],
            [150, 150, 200, 180],
            [250, 250, 300, 280],
        ])
        
        annotated, box_map = draw_annotations(image, boxes)
        
        # Verify box_map has correct number of entries
        self.assertEqual(len(box_map), 3)
        
        # Verify IDs are 1, 2, 3 (as strings)
        self.assertIn('1', box_map)
        self.assertIn('2', box_map)
        self.assertIn('3', box_map)
        
        # Verify coordinates are correct
        self.assertEqual(box_map['1'], [50.0, 50.0, 100.0, 80.0])
        self.assertEqual(box_map['2'], [150.0, 150.0, 200.0, 180.0])
        self.assertEqual(box_map['3'], [250.0, 250.0, 300.0, 280.0])
    
    def test_draw_annotations_modifies_image(self):
        """Test that annotations are actually drawn on the image."""
        # Create a black test image
        image = np.zeros((500, 500, 3), dtype=np.uint8)
        
        boxes = np.array([
            [50, 50, 100, 80],
        ])
        
        annotated, _ = draw_annotations(image, boxes)
        
        # The annotated image should have some non-zero pixels (red boxes)
        self.assertGreater(np.sum(annotated), 0)
        
        # Check that red channel has values (boxes are red)
        self.assertGreater(np.sum(annotated[:, :, 2]), 0)
    
    def test_draw_annotations_empty_boxes(self):
        """Test that empty boxes array returns empty box_map."""
        image = np.zeros((500, 500, 3), dtype=np.uint8)
        
        annotated, box_map = draw_annotations(image, np.array([]))
        
        self.assertEqual(len(box_map), 0)


class TestCoordinateLookup(unittest.TestCase):
    """
    Tests for coordinate lookup from box map.
    
    Property 4: Coordinate Lookup Correctness
    Requirements: 4.4
    """
    
    def test_get_click_coordinates_center_calculation(self):
        """
        Test that center coordinates are calculated correctly.
        
        Property 4: cx = (x1 + x2) / 2, cy = (y1 + y2) / 2
        """
        box_map = {
            '1': [100.0, 200.0, 200.0, 300.0],  # Center: (150, 250)
            '2': [0.0, 0.0, 100.0, 100.0],       # Center: (50, 50)
        }
        
        # Test element 1
        coords = get_click_coordinates(1, box_map)
        self.assertIsNotNone(coords)
        self.assertEqual(coords[0], 150.0)  # cx
        self.assertEqual(coords[1], 250.0)  # cy
        
        # Test element 2
        coords = get_click_coordinates(2, box_map)
        self.assertIsNotNone(coords)
        self.assertEqual(coords[0], 50.0)   # cx
        self.assertEqual(coords[1], 50.0)   # cy
    
    def test_get_click_coordinates_not_found(self):
        """Test that missing ID returns None."""
        box_map = {
            '1': [100.0, 200.0, 200.0, 300.0],
        }
        
        coords = get_click_coordinates(999, box_map)
        self.assertIsNone(coords)
    
    def test_get_click_coordinates_string_id_lookup(self):
        """Test that integer IDs are converted to string for lookup."""
        box_map = {
            '42': [0.0, 0.0, 100.0, 100.0],
        }
        
        # Pass integer ID, should find string key
        coords = get_click_coordinates(42, box_map)
        self.assertIsNotNone(coords)
        self.assertEqual(coords[0], 50.0)
        self.assertEqual(coords[1], 50.0)


class TestPlanExecutorKeyboard(unittest.TestCase):
    """
    Tests for keyboard step execution logic.
    
    Requirements: 1.3, 5.1
    """
    
    def setUp(self):
        """Set up mock vision service."""
        self.mock_vision = unittest.mock.MagicMock(spec=VisionService)
        self.status_messages = []
        
        def capture_status(msg, status_type="info"):
            self.status_messages.append((msg, status_type))
        
        self.executor = PlanExecutor(self.mock_vision, status_callback=capture_status)
    
    def test_is_hotkey_detection(self):
        """Test hotkey detection logic."""
        # These should be detected as hotkeys
        self.assertTrue(self.executor._is_hotkey("ctrl+n"))
        self.assertTrue(self.executor._is_hotkey("ctrl+shift+s"))
        self.assertTrue(self.executor._is_hotkey("alt+f4"))
        self.assertTrue(self.executor._is_hotkey("shift+up"))
        
        # These should NOT be detected as hotkeys (regular text with +)
        self.assertFalse(self.executor._is_hotkey("1+1"))
        self.assertFalse(self.executor._is_hotkey("a+b"))
    
    def test_collect_visual_targets(self):
        """Test collection of visual targets from sequence."""
        sequence = [
            {"order": 1, "type": "keyboard", "value": "ctrl+n"},
            {"order": 2, "type": "visual_click", "target_name": "text_tool"},
            {"order": 3, "type": "keyboard", "value": "test"},
            {"order": 4, "type": "visual_click", "target_name": "canvas_center"},
            {"order": 5, "type": "visual_click", "target_name": "text_tool"},  # Duplicate
        ]
        
        targets = self.executor._collect_visual_targets(sequence)
        
        # Should have unique targets only
        self.assertEqual(len(targets), 2)
        self.assertIn("text_tool", targets)
        self.assertIn("canvas_center", targets)


class TestVisionServiceIntegration(unittest.TestCase):
    """
    Integration tests for VisionService.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2
    """
    
    @classmethod
    def setUpClass(cls):
        """Check if required dependencies are available."""
        cls.api_key = os.getenv('GEMINI_API_KEY')
        
        # Check for FastSAM
        try:
            from ultralytics import FastSAM
            cls.fastsam_available = True
        except ImportError:
            cls.fastsam_available = False
    
    def test_vision_service_initialization(self):
        """Test VisionService initializes with API key."""
        if not self.api_key:
            self.skipTest("GEMINI_API_KEY not set")
        
        service = VisionService()
        self.assertIsNotNone(service.api_key)
        self.assertIsNotNone(service.vision_model)
    
    def test_vision_service_missing_api_key(self):
        """Test VisionService raises error without API key."""
        # Temporarily unset the API key
        original_key = os.environ.get('GEMINI_API_KEY')
        if original_key:
            del os.environ['GEMINI_API_KEY']
        
        try:
            with self.assertRaises(ValueError) as ctx:
                VisionService(api_key=None)
            
            self.assertIn("API key", str(ctx.exception))
        finally:
            # Restore the key
            if original_key:
                os.environ['GEMINI_API_KEY'] = original_key
    
    def test_capture_screenshot(self):
        """
        Test screenshot capture returns valid image.
        
        Requirement: 3.1
        """
        if not self.api_key:
            self.skipTest("GEMINI_API_KEY not set")
        
        service = VisionService()
        screenshot = service.capture_screenshot()
        
        # Should be a numpy array
        self.assertIsInstance(screenshot, np.ndarray)
        
        # Should have 3 dimensions (height, width, channels)
        self.assertEqual(len(screenshot.shape), 3)
        
        # Should have 3 color channels (BGR)
        self.assertEqual(screenshot.shape[2], 3)
        
        # Should have reasonable dimensions
        self.assertGreater(screenshot.shape[0], 100)  # height
        self.assertGreater(screenshot.shape[1], 100)  # width


class TestEndToEndPipelineSimulation(unittest.TestCase):
    """
    End-to-end simulation tests for the full pipeline.
    
    These tests simulate the full flow without actually executing clicks.
    
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    
    def test_sample_plan_structure(self):
        """
        Test that a sample plan for "Make iron number plate set for bike, PB12W3998"
        has the expected structure.
        """
        # This is a representative plan structure
        sample_plan = {
            "sequence": [
                {"order": 1, "type": "keyboard", "value": "ctrl+n", "desc": "Open new page"},
                {"order": 2, "type": "visual_click", "target_name": "width_input", "desc": "Click width"},
                {"order": 3, "type": "keyboard", "value": "8", "desc": "Enter width"},
                {"order": 4, "type": "visual_click", "target_name": "height_input", "desc": "Click height"},
                {"order": 5, "type": "keyboard", "value": "1.2", "desc": "Enter height"},
                {"order": 6, "type": "visual_click", "target_name": "ok_button", "desc": "Confirm"},
                {"order": 7, "type": "visual_click", "target_name": "text_tool", "desc": "Select text"},
                {"order": 8, "type": "visual_click", "target_name": "canvas_center", "desc": "Click canvas"},
                {"order": 9, "type": "keyboard", "value": "PB12W3998", "desc": "Type number"},
            ]
        }
        
        # Verify structure
        self.assertIn('sequence', sample_plan)
        self.assertEqual(len(sample_plan['sequence']), 9)
        
        # Verify all steps have required fields
        for step in sample_plan['sequence']:
            self.assertIn('order', step)
            self.assertIn('type', step)
            self.assertIn(step['type'], ['keyboard', 'visual_click'])
    
    def test_id_map_to_coordinates_flow(self):
        """
        Test the flow from ID map to click coordinates.
        
        Simulates: Vision Mapper output -> coordinate lookup -> click position
        """
        # Simulated Vision Mapper output
        id_map = {
            "text_tool": 45,
            "canvas_center": 78,
            "width_input": 88,
        }
        
        # Simulated box map from SoM detection
        box_map = {
            "45": [100.0, 50.0, 150.0, 80.0],   # text_tool
            "78": [500.0, 300.0, 900.0, 700.0], # canvas_center
            "88": [200.0, 100.0, 300.0, 130.0], # width_input
        }
        
        # Test coordinate lookup for each target
        for target_name, element_id in id_map.items():
            coords = get_click_coordinates(element_id, box_map)
            self.assertIsNotNone(coords, f"Failed to get coordinates for {target_name}")
            
            # Verify center calculation
            box = box_map[str(element_id)]
            expected_cx = (box[0] + box[2]) / 2
            expected_cy = (box[1] + box[3]) / 2
            
            self.assertEqual(coords[0], expected_cx)
            self.assertEqual(coords[1], expected_cy)


if __name__ == '__main__':
    unittest.main(verbosity=2)
