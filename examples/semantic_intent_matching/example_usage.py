# Initialize PACT handler
pact_handler = PACTProtocolHandler()

# Test various user inputs
test_inputs = [
    "Can you show me our monthly revenue?",
    "I need to see customer complaints",
    "Display the main overview screen",
    "Who are our active customers?",
    "I want to check sales performance",
    "Something completely unrelated to our system"
]

print("PACT Semantic Matching Results:")
print("=" * 50)

for user_input in test_inputs:
    result = pact_handler.process_request(user_input)
    
    print(f"\nInput: '{user_input}'")
    if result["status"] == "success":
        print(f"✅ Matched: {result['matched_intent']}")
        print(f"   Action: {result['protocol_action']}")
        print(f"   Confidence: {result['confidence']:.3f}")
    else:
        print(f"❌ No match (confidence: {result['best_confidence']:.3f})")
        print(f"   {result['suggestion']}")
