import pytest

class TestPACTSemanticMatcher:
    """Test suite for PACT semantic matching"""
    
    def setup_method(self):
        self.handler = PACTProtocolHandler()
    
    def test_exact_intent_matching(self):
        """Test that similar phrases match expected intents"""
        test_cases = [
            ("show revenue", "analytics_revenue"),
            ("customer support tickets", "support_tickets"),
            ("display dashboard", "dashboard_view"),
            ("list users", "user_management")
        ]
        
        for user_input, expected_intent in test_cases:
            result = self.handler.process_request(user_input)
            assert result["status"] == "success"
            assert result["matched_intent"] == expected_intent
    
    def test_threshold_filtering(self):
        """Test that unrelated inputs are properly filtered"""
        unrelated_inputs = [
            "What's the weather like?",
            "How do I cook pasta?",
            "Random gibberish text here"
        ]
        
        for user_input in unrelated_inputs:
            result = self.handler.process_request(user_input)
            assert result["status"] == "no_match"
    
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable"""
        result = self.handler.process_request("show me the revenue report")
        assert result["status"] == "success"
        assert result["confidence"] > 0.8  # High confidence for clear match
