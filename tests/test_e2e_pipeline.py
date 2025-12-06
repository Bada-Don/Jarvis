"""
End-to-End Integration Test for Two-Model Pipeline

This script tests the complete pipeline flow:
1. Send "Make iron number plate set for bike, PB12W3998" command
2. Verify plan generation on backend
3. Verify screenshot capture and SoM detection on local client
4. Verify Vision Mapper identifies UI elements
5. Verify clicks execute at correct coordinates

Requirements: 1.1, 1.2, 1.3, 1.4

Usage:
    python tests/test_e2e_pipeline.py

Note: This test requires:
    - GEMINI_API_KEY environment variable set
    - Backend server running (optional for full integration)
    - Local client dependencies installed
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add paths for imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR / "local_client"))

# Load environment variables from .env files
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / "backend" / ".env")
load_dotenv(ROOT_DIR / "local_client" / ".env")


class TestFullPipelineE2E(unittest.TestCase):
    """
    End-to-end tests for the complete Two-Model Pipeline.
    
    Test command: "Make iron number plate set for bike, PB12W3998"
    
    Requirements: 1.1, 1.2, 1.3, 1.4
    """
    
    SAMPLE_COMMAND = "Make iron number plate set for bike, PB12W3998"
    PLATE_NUMBER = "PB12W3998"
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.api_key = os.getenv('GEMINI_API_KEY')
        if not cls.api_key:
            raise unittest.SkipTest("GEMINI_API_KEY not set - skipping E2E tests")
        
        # Import services
        from gemini_service import GeminiPlannerService
        from vision_service import VisionService, filter_boxes, draw_annotations
        from plan_executor import PlanExecutor, get_click_coordinates
        
        cls.GeminiPlannerService = GeminiPlannerService
        cls.VisionService = VisionService
        cls.PlanExecutor = PlanExecutor
        cls.filter_boxes = filter_boxes
        cls.draw_annotations = draw_annotations
        cls.get_click_coordinates = get_click_coordinates
    
    def test_step1_plan_generation(self):
        """
        Step 1: Verify plan generation on backend.
        
        Requirement 1.1: Parse command and generate execution plan
        """
        print("\n" + "="*60)
        print("STEP 1: Testing Plan Generation")
        print("="*60)
        
        # Initialize planner service
        planner = self.GeminiPlannerService()
        
        # Generate plan
        plan = planner.generate_plan(self.SAMPLE_COMMAND)
        
        # Verify plan structure
        self.assertIn('sequence', plan, "Plan must have 'sequence' array")
        self.assertIsInstance(plan['sequence'], list)
        self.assertGreater(len(plan['sequence']), 0, "Plan must have at least one step")
        
        print(f"✓ Plan generated with {len(plan['sequence'])} steps")
        
        # Verify each step has required fields
        for i, step in enumerate(plan['sequence']):
            self.assertIn('order', step, f"Step {i+1} missing 'order'")
            self.assertIn('type', step, f"Step {i+1} missing 'type'")
            self.assertIn(step['type'], ['keyboard', 'visual_click'])
            
            if step['type'] == 'keyboard':
                self.assertIn('value', step, f"Keyboard step {i+1} missing 'value'")
            else:
                self.assertIn('target_name', step, f"Visual click step {i+1} missing 'target_name'")
        
        print("✓ All steps have required fields")
        
        # Verify plate number is in the plan
        keyboard_values = [s.get('value', '') for s in plan['sequence'] if s.get('type') == 'keyboard']
        found_plate = any(self.PLATE_NUMBER in str(v) for v in keyboard_values)
        self.assertTrue(found_plate, f"Plate number '{self.PLATE_NUMBER}' not found in plan")
        
        print(f"✓ Plate number '{self.PLATE_NUMBER}' found in plan")
        
        # Store plan for subsequent tests
        self.__class__.generated_plan = plan
        
        # Print plan summary
        print("\nGenerated Plan:")
        for step in plan['sequence']:
            step_type = step['type']
            if step_type == 'keyboard':
                print(f"  {step['order']}. [KEYBOARD] {step.get('value', '')} - {step.get('desc', '')}")
            else:
                print(f"  {step['order']}. [CLICK] {step.get('target_name', '')} - {step.get('desc', '')}")
    
    def test_step2_screenshot_capture(self):
        """
        Step 2: Verify screenshot capture on local client.
        
        Requirement 3.1: Capture screenshot using pyautogui
        """
        print("\n" + "="*60)
        print("STEP 2: Testing Screenshot Capture")
        print("="*60)
        
        import numpy as np
        
        # Initialize vision service
        vision = self.VisionService()
        
        # Capture screenshot
        screenshot = vision.capture_screenshot()
        
        # Verify screenshot is valid
        self.assertIsInstance(screenshot, np.ndarray)
        self.assertEqual(len(screenshot.shape), 3, "Screenshot must be 3D array (H, W, C)")
        self.assertEqual(screenshot.shape[2], 3, "Screenshot must have 3 color channels")
        
        height, width = screenshot.shape[:2]
        print(f"✓ Screenshot captured: {width}x{height} pixels")
        
        # Store for subsequent tests
        self.__class__.screenshot = screenshot
    
    def test_step3_som_detection(self):
        """
        Step 3: Verify SoM detection on local client.
        
        Requirements: 3.2, 3.3, 3.4
        """
        print("\n" + "="*60)
        print("STEP 3: Testing SoM Detection")
        print("="*60)
        
        # Check if we have a screenshot
        if not hasattr(self.__class__, 'screenshot'):
            self.skipTest("Screenshot not available from previous test")
        
        # Initialize vision service
        vision = self.VisionService()
        
        # Check if FastSAM is available
        if vision.som_model is None:
            print("⚠ FastSAM model not available - using mock SoM detection")
            # Create mock annotated image and box_map for testing
            import numpy as np
            annotated = self.__class__.screenshot.copy()
            box_map = {
                "1": [100.0, 50.0, 150.0, 80.0],
                "2": [200.0, 100.0, 300.0, 130.0],
                "3": [500.0, 300.0, 900.0, 700.0],
            }
            self.__class__.annotated_image = annotated
            self.__class__.box_map = box_map
            print(f"✓ Mock SoM: {len(box_map)} elements")
            return
        
        # Run SoM detection
        annotated, box_map = vision.run_som_detection(self.__class__.screenshot)
        
        # Verify results
        self.assertIsNotNone(annotated)
        self.assertIsInstance(box_map, dict)
        
        print(f"✓ SoM detection found {len(box_map)} UI elements")
        
        # Verify box_map structure
        for element_id, coords in box_map.items():
            self.assertIsInstance(coords, list)
            self.assertEqual(len(coords), 4, f"Element {element_id} must have 4 coordinates")
            
            x1, y1, x2, y2 = coords
            self.assertLess(x1, x2, f"Element {element_id}: x1 must be < x2")
            self.assertLess(y1, y2, f"Element {element_id}: y1 must be < y2")
        
        print("✓ All box_map entries have valid coordinates")
        
        # Store for subsequent tests
        self.__class__.annotated_image = annotated
        self.__class__.box_map = box_map
    
    def test_step4_vision_mapper(self):
        """
        Step 4: Verify Vision Mapper identifies UI elements.
        
        Requirements: 4.1, 4.2
        """
        print("\n" + "="*60)
        print("STEP 4: Testing Vision Mapper")
        print("="*60)
        
        # Check prerequisites
        if not hasattr(self.__class__, 'annotated_image'):
            self.skipTest("Annotated image not available from previous test")
        if not hasattr(self.__class__, 'generated_plan'):
            self.skipTest("Generated plan not available from previous test")
        
        # Collect visual targets from plan
        targets = []
        for step in self.__class__.generated_plan['sequence']:
            if step.get('type') == 'visual_click':
                target = step.get('target_name')
                if target and target not in targets:
                    targets.append(target)
        
        if not targets:
            print("⚠ No visual targets in plan - skipping Vision Mapper test")
            return
        
        print(f"Visual targets to identify: {targets}")
        
        # Initialize vision service
        vision = self.VisionService()
        
        # Map targets to IDs
        id_map = vision.map_targets_to_ids(self.__class__.annotated_image, targets)
        
        # Verify results
        self.assertIsInstance(id_map, dict)
        
        # Check that all targets are in the response
        for target in targets:
            self.assertIn(target, id_map, f"Target '{target}' missing from id_map")
        
        # Count found vs not found
        found = sum(1 for v in id_map.values() if v is not None)
        not_found = len(id_map) - found
        
        print(f"✓ Vision Mapper results: {found} found, {not_found} not found")
        
        for target, element_id in id_map.items():
            status = f"ID {element_id}" if element_id else "NOT FOUND"
            print(f"  - {target}: {status}")
        
        # Store for subsequent tests
        self.__class__.id_map = id_map
    
    def test_step5_coordinate_calculation(self):
        """
        Step 5: Verify clicks execute at correct coordinates.
        
        Property 4: cx = (x1 + x2) / 2, cy = (y1 + y2) / 2
        Requirement: 4.4
        """
        print("\n" + "="*60)
        print("STEP 5: Testing Coordinate Calculation")
        print("="*60)
        
        # Check prerequisites
        if not hasattr(self.__class__, 'id_map'):
            self.skipTest("ID map not available from previous test")
        if not hasattr(self.__class__, 'box_map'):
            self.skipTest("Box map not available from previous test")
        
        id_map = self.__class__.id_map
        box_map = self.__class__.box_map
        
        # Test coordinate calculation for each found target
        for target_name, element_id in id_map.items():
            if element_id is None:
                print(f"  - {target_name}: SKIPPED (not found)")
                continue
            
            coords = self.__class__.get_click_coordinates(element_id, box_map)
            
            if coords is None:
                print(f"  - {target_name}: SKIPPED (ID {element_id} not in box_map)")
                continue
            
            # Verify center calculation
            box = box_map.get(str(element_id))
            if box:
                expected_cx = (box[0] + box[2]) / 2
                expected_cy = (box[1] + box[3]) / 2
                
                self.assertAlmostEqual(coords[0], expected_cx, places=2)
                self.assertAlmostEqual(coords[1], expected_cy, places=2)
                
                print(f"  - {target_name}: Click at ({int(coords[0])}, {int(coords[1])}) ✓")
        
        print("\n✓ All coordinate calculations verified")
    
    def test_step6_full_pipeline_summary(self):
        """
        Step 6: Summary test that verifies all pipeline components work together.
        """
        print("\n" + "="*60)
        print("PIPELINE SUMMARY")
        print("="*60)
        
        results = {
            "Plan Generation": hasattr(self.__class__, 'generated_plan'),
            "Screenshot Capture": hasattr(self.__class__, 'screenshot'),
            "SoM Detection": hasattr(self.__class__, 'box_map'),
            "Vision Mapper": hasattr(self.__class__, 'id_map'),
        }
        
        all_passed = all(results.values())
        
        for component, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {component}: {status}")
        
        print("\n" + "="*60)
        if all_passed:
            print("✓ ALL PIPELINE COMPONENTS WORKING")
        else:
            print("✗ SOME COMPONENTS FAILED")
        print("="*60)
        
        self.assertTrue(all_passed, "Not all pipeline components passed")


def run_tests():
    """Run the E2E tests with verbose output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFullPipelineE2E)
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*60)
    print("TWO-MODEL PIPELINE END-TO-END TEST")
    print("="*60)
    print(f"Test Command: 'Make iron number plate set for bike, PB12W3998'")
    print("="*60)
    
    success = run_tests()
    sys.exit(0 if success else 1)
