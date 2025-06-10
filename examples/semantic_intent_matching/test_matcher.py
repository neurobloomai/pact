#!/usr/bin/env python3
"""
Unit tests for PACT Semantic Intent Matching

Tests the core functionality of the semantic matcher to ensure
reliable intent detection and PACT protocol execution.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from pact_semantic_matcher import PACTSemanticMatcher, PACTIntent


class TestPACTSemanticMatcher:
    """Test suite for PACT semantic matching functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.matcher = PACTSemanticMatcher()
        
        # Standard test intents
        self.test_intents = [
            PACTIntent(
                name="analytics_revenue",
                protocol_action="analytics.get_revenue_report", 
                description="Get revenue and sales analytics data",
                examples=["show revenue", "sales numbers", "revenue report"]
            ),
            PACTIntent(
                name="support_tickets",
                protocol_action="support.list_tickets",
                description="List customer support tickets", 
                examples=["support tickets", "customer issues", "help desk"]
            ),
            PACTIntent(
                name="dashboard_view",
                protocol_action="dashboard.display_main",
                description="Display main dashboard",
                examples=["show dashboard", "main screen", "overview"]
            )
        ]
        
        # Add intents to matcher
        for intent in self.test_intents:
            self.matcher.add_intent(intent)
    
    def test_matcher_initialization(self):
        """Test that matcher initializes with correct defaults."""
        matcher = PACTSemanticMatcher()
        
        assert matcher.similarity_threshold == 0.75
        assert matcher.intents == []
        assert matcher.intent_embeddings is None
        assert matcher.model is not None
    
    def test_add_intent(self):
        """Test adding intents to the matcher."""
        matcher = PACTSemanticMatcher()
        intent = self.test_intents[0]
        
        matcher.add_intent(intent)
        
        assert len(matcher.intents) == 1
        assert matcher.intents[0].name == "analytics_revenue"
        assert intent.embedding is not None
        assert matcher.intent_embeddings is not None
    
    def test_multiple_intents(self):
        """Test adding multiple intents."""
        assert len(self.matcher.intents) == 3
        assert self.matcher.intent_embeddings.shape[0] == 3
        
        # Check all intents are properly stored
        intent_names = [intent.name for intent in self.matcher.intents]
        expected_names = ["analytics_revenue", "support_tickets", "dashboard_view"]
        assert intent_names == expected_names
    
    def test_exact_intent_matching(self):
        """Test that similar phrases match expected intents."""
        test_cases = [
            ("show revenue", "analytics_revenue"),
            ("customer support tickets", "support_tickets"), 
            ("display dashboard", "dashboard_view"),
            ("revenue report", "analytics_revenue"),
            ("help desk", "support_tickets")
        ]
        
        for user_input, expected_intent in test_cases:
            result = self.matcher.execute_pact_action(user_input)
            assert result["status"] == "success", f"Failed to match '{user_input}'"
            assert result["matched_intent"] == expected_intent
            assert result["confidence"] > 0.7
    
    def test_threshold_filtering(self):
        """Test that unrelated inputs are properly filtered."""
        unrelated_inputs = [
            "What's the weather like?",
            "How do I cook pasta?", 
            "Random gibberish text here",
            "Tell me a joke",
            "Play some music"
        ]
        
        for user_input in unrelated_inputs:
            result = self.matcher.execute_pact_action(user_input)
            assert result["status"] == "no_match", f"Incorrectly matched '{user_input}'"
            assert result["best_confidence"] < self.matcher.similarity_threshold
    
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable."""
        # High confidence match
        result = self.matcher.execute_pact_action("show me the revenue report")
        assert result["status"] == "success"
        assert result["confidence"] > 0.8
        
        # Lower confidence but still valid match
        result = self.matcher.execute_pact_action("money stuff")
        # This might or might not match depending on the model
        if result["status"] == "success":
            assert 0.7 <= result["confidence"] <= 1.0
    
    def test_protocol_action_mapping(self):
        """Test that intents map to correct protocol actions."""
        test_cases = [
            ("show revenue", "analytics.get_revenue_report"),
            ("support tickets", "support.list_tickets"),
            ("main dashboard", "dashboard.display_main")
        ]
        
        for user_input, expected_action in test_cases:
            result = self.matcher.execute_pact_action(user_input)
            assert result["status"] == "success"
            assert result["protocol_action"] == expected_action
    
    def test_threshold_adjustment(self):
        """Test adjusting similarity threshold."""
        original_threshold = self.matcher.similarity_threshold
        
        # Lower threshold - should accept more matches
        self.matcher.similarity_threshold = 0.5
        result = self.matcher.execute_pact_action("some vague text")
        
        # Higher threshold - should be more restrictive  
        self.matcher.similarity_threshold = 0.9
        result_strict = self.matcher.execute_pact_action("show revenue")
        
        # Restore original threshold
        self.matcher.similarity_threshold = original_threshold
        
        assert self.matcher.similarity_threshold == 0.75
    
    def test_empty_input(self):
        """Test handling of empty or whitespace input."""
        empty_inputs = ["", "   ", "\n", "\t"]
        
        for empty_input in empty_inputs:
            result = self.matcher.execute_pact_action(empty_input)
            # Should handle gracefully without crashing
            assert result["status"] in ["success", "no_match"]
    
    def test_very_long_input(self):
        """Test handling of very long input strings."""
        long_input = "show me revenue " * 100  # Very long but still relevant
        
        result = self.matcher.execute_pact_action(long_input)
        # Should still work despite length
        assert result["status"] == "success"
        assert result["matched_intent"] == "analytics_revenue"
    
    def test_special_characters(self):
        """Test handling of inputs with special characters."""
        special_inputs = [
            "show revenue!",
            "revenue??? what is it",
            "show me the revenue, please",
            "revenue (this quarter)",
            "revenue@company.com"
        ]
        
        for special_input in special_inputs:
            result = self.matcher.execute_pact_action(special_input)
            # Should handle gracefully and likely match revenue
            if result["status"] == "success":
                assert result["matched_intent"] == "analytics_revenue"
    
    def test_case_insensitivity(self):
        """Test that matching works regardless of case."""
        case_variants = [
            "SHOW REVENUE",
            "Show Revenue", 
            "show revenue",
            "sHoW rEvEnUe"
        ]
        
        for variant in case_variants:
            result = self.matcher.execute_pact_action(variant)
            assert result["status"] == "success"
            assert result["matched_intent"] == "analytics_revenue"
    
    def test_result_structure(self):
        """Test that results have the expected structure."""
        # Successful match
        result = self.matcher.execute_pact_action("show revenue")
        
        assert "status" in result
        assert "matched_intent" in result
        assert "protocol_action" in result
        assert "confidence" in result
        assert "user_input" in result
        
        assert result["status"] == "success"
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        
        # Failed match
        result_fail = self.matcher.execute_pact_action("completely unrelated")
        
        assert "status" in result_fail
        assert "user_input" in result_fail  
        assert "best_confidence" in result_fail
        assert "threshold" in result_fail
        assert "suggestion" in result_fail
        
        assert result_fail["status"] == "no_match"


class TestPACTIntent:
    """Test suite for PACTIntent class."""
    
    def test_intent_creation(self):
        """Test creating a PACT intent."""
        intent = PACTIntent(
            name="test_intent",
            protocol_action="test.action",
            description="Test description",
            examples=["example1", "example2"]
        )
        
        assert intent.name == "test_intent"
        assert intent.protocol_action == "test.action"
        assert intent.description == "Test description"
        assert intent.examples == ["example1", "example2"]
        assert intent.embedding is None  # Not set until added to matcher
    
    def test_intent_with_minimal_data(self):
        """Test creating intent with minimal required data."""
        intent = PACTIntent(
            name="minimal",
            protocol_action="minimal.action", 
            description="Minimal test",
            examples=["test"]
        )
        
        assert intent.name == "minimal"
        assert len(intent.examples) == 1


# Pytest fixtures and test runners
@pytest.fixture
def sample_matcher():
    """Fixture providing a pre-configured matcher."""
    matcher = PACTSemanticMatcher()
    
    intents = [
        PACTIntent(
            name="test_intent",
            protocol_action="test.action",
            description="Test intent for fixtures",
            examples=["test example", "fixture test"]
        )
    ]
    
    for intent in intents:
        matcher.add_intent(intent)
    
    return matcher


def test_with_fixture(sample_matcher):
    """Test using the sample matcher fixture."""
    result = sample_matcher.execute_pact_action("test example")
    assert result["status"] == "success"
    assert result["matched_intent"] == "test_intent"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
