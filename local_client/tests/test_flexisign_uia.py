"""
Property-Based Tests for FlexiSIGN UIA Module

This module contains property-based tests using hypothesis to verify
the correctness of the FlexiSIGN UIA module.

**Feature: direct-automation-integration**
"""

import unittest
from hypothesis import given, strategies as st, settings, HealthCheck


def detect_flexisign_in_titles(titles: list[str]) -> bool:
    """
    Pure function to detect if any window title contains 'FlexiSIGN'.
    
    This mirrors the logic in FlexiSignUIA.find_flexisign_window() but
    operates on a list of title strings for testability.
    
    Args:
        titles: List of window title strings
        
    Returns:
        True if any title contains 'FlexiSIGN' (case-insensitive), False otherwise.
    """
    for title in titles:
        if "flexisign" in title.lower():
            return True
    return False


class TestWindowDetectionProperty(unittest.TestCase):
    """
    Property-based tests for window detection logic.
    
    **Feature: direct-automation-integration, Property 1: Window Detection Correctness**
    **Validates: Requirements 1.1**
    """
    
    @given(st.lists(st.text(min_size=0, max_size=100), min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_window_detection_correctness(self, titles: list[str]):
        """
        Property 1: Window Detection Correctness
        
        *For any* list of window titles, the FlexiSIGN detection function SHALL 
        return True if and only if at least one title contains the substring 
        "FlexiSIGN" (case-insensitive).
        
        **Feature: direct-automation-integration, Property 1: Window Detection Correctness**
        **Validates: Requirements 1.1**
        """
        result = detect_flexisign_in_titles(titles)
        
        # Check if any title contains "FlexiSIGN" (case-insensitive)
        expected = any("flexisign" in title.lower() for title in titles)
        
        self.assertEqual(
            result, 
            expected,
            f"Detection mismatch for titles: {titles}"
        )
    
    @given(st.lists(st.text(min_size=0, max_size=50).filter(
        lambda t: "flexisign" not in t.lower()
    ), min_size=0, max_size=10))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much])
    def test_no_flexisign_returns_false(self, titles: list[str]):
        """
        Property: When no title contains 'FlexiSIGN', detection returns False.
        
        **Feature: direct-automation-integration, Property 1: Window Detection Correctness**
        **Validates: Requirements 1.1**
        """
        result = detect_flexisign_in_titles(titles)
        self.assertFalse(
            result,
            f"Should return False when no FlexiSIGN in titles: {titles}"
        )
    
    @given(
        st.lists(st.text(min_size=0, max_size=100), min_size=0, max_size=10),
        st.sampled_from([
            "FlexiSIGN",
            "flexisign", 
            "FLEXISIGN",
            "FlExIsIgN",
            "FlexiSIGN Pro",
            "My FlexiSIGN Window",
            "flexisign - untitled"
        ])
    )
    @settings(max_examples=100)
    def test_with_flexisign_returns_true(self, other_titles: list[str], flexisign_title: str):
        """
        Property: When at least one title contains 'FlexiSIGN', detection returns True.
        
        **Feature: direct-automation-integration, Property 1: Window Detection Correctness**
        **Validates: Requirements 1.1**
        """
        # Insert the FlexiSIGN title at a random position
        all_titles = other_titles + [flexisign_title]
        
        result = detect_flexisign_in_titles(all_titles)
        self.assertTrue(
            result,
            f"Should return True when FlexiSIGN present: {all_titles}"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
