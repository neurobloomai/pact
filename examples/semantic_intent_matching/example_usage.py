#!/usr/bin/env python3
"""
PACT Semantic Intent Matching - Basic Usage Example

This example demonstrates how to use the semantic matcher to convert
natural language inputs into PACT protocol actions.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from pact_semantic_matcher import PACTSemanticMatcher, PACTIntent


def main():
    """Demonstrate basic semantic intent matching functionality."""
    
    print("🚀 PACT Semantic Intent Matching - Basic Example")
    print("=" * 55)
    
    # Initialize the semantic matcher
    print("\n1. Initializing PACT Semantic Matcher...")
    matcher = PACTSemanticMatcher()
    
    # Define PACT intents
    print("\n2. Adding PACT protocol intents...")
    
    intents = [
        PACTIntent(
            name="analytics_revenue",
            protocol_action="analytics.get_revenue_report",
            description="Get revenue and sales analytics data",
            examples=[
                "show me revenue",
                "what are our sales numbers",
                "revenue report",
                "how much money did we make",
                "sales analytics",
                "monthly revenue"
            ]
        ),
        PACTIntent(
            name="support_tickets",
            protocol_action="support.list_tickets",
            description="List and manage customer support tickets",
            examples=[
                "show support tickets",
                "customer issues",
                "help desk tickets",
                "support queue",
                "customer problems",
                "open tickets"
            ]
        ),
        PACTIntent(
            name="user_management",
            protocol_action="users.list_active",
            description="Manage and view user accounts",
            examples=[
                "show users",
                "list customers",
                "user accounts",
                "who is online",
                "active users",
                "current users"
            ]
        ),
        PACTIntent(
            name="dashboard_view",
            protocol_action="dashboard.display_main",
            description="Display main dashboard and overview",
            examples=[
                "show dashboard",
                "main screen",
                "overview",
                "home page",
                "control panel",
                "main view"
            ]
        )
    ]
    
    # Add intents to matcher
    for intent in intents:
        matcher.add_intent(intent)
        print(f"   ✅ Added intent: {intent.name}")
    
    # Test various user inputs
    print(f"\n3. Testing semantic matching...")
    print(f"   Similarity threshold: {matcher.similarity_threshold}")
    
    test_inputs = [
        "Can you show me our monthly revenue?",
        "I need to see customer complaints",
        "Display the main overview screen", 
        "Who are our active customers?",
        "I want to check sales performance",
        "Show me the help desk queue",
        "What's on the main dashboard?",
        "List all current users",
        "Something completely unrelated to our system"  # Should fail
    ]
    
    print(f"\n4. Processing {len(test_inputs)} test inputs:")
    print("-" * 55)
    
    success_count = 0
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n[{i}] Input: '{user_input}'")
        
        result = matcher.execute_pact_action(user_input)
        
        if result["status"] == "success":
            print(f"    ✅ MATCHED: {result['matched_intent']}")
            print(f"    🎯 Action: {result['protocol_action']}")
            print(f"    📊 Confidence: {result['confidence']:.3f}")
            success_count += 1
        else:
            print(f"    ❌ NO MATCH (confidence: {result['best_confidence']:.3f})")
            print(f"    💡 Suggestion: {result['suggestion']}")
    
    # Summary
    print(f"\n5. Results Summary:")
    print("=" * 55)
    print(f"✅ Successful matches: {success_count}/{len(test_inputs)}")
    print(f"📈 Success rate: {(success_count/len(test_inputs)*100):.1f}%")
    print(f"🎯 Threshold: {matcher.similarity_threshold}")
    
    # Interactive mode
    print(f"\n6. Interactive Mode:")
    print("-" * 55)
    print("Try your own inputs! (Press Ctrl+C to exit)")
    
    try:
        while True:
            user_input = input("\n💬 Enter your request: ").strip()
            
            if not user_input:
                continue
                
            result = matcher.execute_pact_action(user_input)
            
            if result["status"] == "success":
                print(f"✅ Matched: {result['matched_intent']}")
                print(f"🚀 Would execute: {result['protocol_action']}")
                print(f"📊 Confidence: {result['confidence']:.3f}")
            else:
                print(f"❌ No match found (confidence: {result['best_confidence']:.3f})")
                print(f"💡 Try rephrasing or being more specific")
                
    except KeyboardInterrupt:
        print(f"\n\n👋 Thanks for trying PACT Semantic Intent Matching!")


if __name__ == "__main__":
    main()
