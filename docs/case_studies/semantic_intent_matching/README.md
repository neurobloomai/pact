# PACT Case Study: Building a Semantic Intent Matcher

## Overview
This case study demonstrates how PACT (Protocol for AI-Computer Transaction) can be enhanced with semantic intent matching to handle natural language inputs that don't exactly match predefined protocol actions.

## The Problem
Traditional protocol systems require exact matches between user inputs and defined actions. This creates friction when users express intents in natural language:

- User says: "Show me last month's revenue" 
- System expects: `analytics.get_revenue_report`
- Result: **No match found**

## The PACT Solution
We'll build a semantic matcher that bridges natural language to PACT protocols using embeddings and similarity search.

## Architecture

```
Natural Language Input
         ↓
    Embedding Model
         ↓
   Similarity Search
         ↓
   Threshold Check
         ↓
    PACT Protocol Action
```

## Implementation

### 1. Core Semantic Matcher

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass

@dataclass
class PACTIntent:
    """Represents a PACT protocol intent with semantic matching capability"""
    name: str
    protocol_action: str
    description: str
    examples: List[str]
    embedding: Optional[np.ndarray] = None

class PACTSemanticMatcher:
    """Semantic intent matcher for PACT protocols"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.intents: List[PACTIntent] = []
        self.intent_embeddings: np.ndarray = None
        self.similarity_threshold = 0.75
        
    def add_intent(self, intent: PACTIntent):
        """Add a new PACT intent to the matcher"""
        # Create embedding from description and examples
        text_to_embed = f"{intent.description}. Examples: {' | '.join(intent.examples)}"
        intent.embedding = self.model.encode(text_to_embed)
        self.intents.append(intent)
        self._rebuild_embeddings()
    
    def _rebuild_embeddings(self):
        """Rebuild the embeddings matrix after adding intents"""
        if self.intents:
            self.intent_embeddings = np.vstack([intent.embedding for intent in self.intents])
    
    def find_best_match(self, user_input: str) -> Tuple[Optional[PACTIntent], float]:
        """Find the best matching PACT intent for user input"""
        if not self.intents:
            return None, 0.0
        
        # Encode user input
        user_embedding = self.model.encode(user_input)
        
        # Calculate cosine similarities
        similarities = np.dot(self.intent_embeddings, user_embedding) / (
            np.linalg.norm(self.intent_embeddings, axis=1) * np.linalg.norm(user_embedding)
        )
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        # Check threshold
        if best_score >= self.similarity_threshold:
            return self.intents[best_idx], best_score
        else:
            return None, best_score
    
    def execute_pact_action(self, user_input: str) -> Dict:
        """Execute PACT protocol action based on semantic matching"""
        intent, confidence = self.find_best_match(user_input)
        
        if intent:
            return {
                "status": "success",
                "matched_intent": intent.name,
                "protocol_action": intent.protocol_action,
                "confidence": float(confidence),
                "user_input": user_input
            }
        else:
            return {
                "status": "no_match",
                "user_input": user_input,
                "best_confidence": float(confidence),
                "threshold": self.similarity_threshold,
                "suggestion": "Please rephrase your request or use more specific terms"
            }
```

### 2. PACT Protocol Integration

```python
class PACTProtocolHandler:
    """Handles execution of PACT protocol actions"""
    
    def __init__(self):
        self.semantic_matcher = PACTSemanticMatcher()
        self._setup_default_intents()
    
    def _setup_default_intents(self):
        """Setup common PACT protocol intents"""
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
                    "sales analytics"
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
                    "customer problems"
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
                    "active users"
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
                    "control panel"
                ]
            )
        ]
        
        for intent in intents:
            self.semantic_matcher.add_intent(intent)
    
    def process_request(self, user_input: str) -> Dict:
        """Process user request through PACT semantic matching"""
        return self.semantic_matcher.execute_pact_action(user_input)
```

### 3. Usage Example

```python
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
```

## Advanced Features

### 1. Dynamic Threshold Adjustment

```python
class AdaptivePACTMatcher(PACTSemanticMatcher):
    """PACT matcher with adaptive threshold based on usage patterns"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.match_history = []
        self.false_positive_threshold = 0.1  # 10% false positive rate
    
    def record_feedback(self, user_input: str, was_correct: bool):
        """Record user feedback to improve threshold"""
        intent, confidence = self.find_best_match(user_input)
        self.match_history.append({
            "confidence": confidence,
            "correct": was_correct,
            "input": user_input
        })
        
        # Adjust threshold based on recent feedback
        if len(self.match_history) > 20:
            self._adjust_threshold()
    
    def _adjust_threshold(self):
        """Adjust similarity threshold based on feedback"""
        recent_history = self.match_history[-20:]
        
        false_positives = [h for h in recent_history 
                          if h["confidence"] >= self.similarity_threshold and not h["correct"]]
        
        false_positive_rate = len(false_positives) / len(recent_history)
        
        if false_positive_rate > self.false_positive_threshold:
            self.similarity_threshold += 0.05  # More conservative
        elif false_positive_rate < 0.05:
            self.similarity_threshold -= 0.02  # More permissive
```

### 2. Multi-Modal Intent Context

```python
@dataclass
class ContextualPACTIntent(PACTIntent):
    """PACT intent with contextual information"""
    required_permissions: List[str] = None
    context_tags: List[str] = None
    time_sensitive: bool = False
    
class ContextualPACTMatcher(PACTSemanticMatcher):
    """Context-aware PACT semantic matcher"""
    
    def find_best_match_with_context(self, user_input: str, user_context: Dict) -> Tuple[Optional[PACTIntent], float]:
        """Find best match considering user context"""
        intent, confidence = self.find_best_match(user_input)
        
        if intent and hasattr(intent, 'required_permissions'):
            # Check permissions
            user_permissions = user_context.get('permissions', [])
            if intent.required_permissions:
                if not all(perm in user_permissions for perm in intent.required_permissions):
                    return None, 0.0  # No permission
        
        return intent, confidence
```

## Testing and Validation

```python
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
```

## Performance Considerations

### Optimization Strategies:

1. **Embedding Caching**: Pre-compute and cache intent embeddings
2. **Batch Processing**: Process multiple inputs simultaneously
3. **Model Selection**: Balance accuracy vs speed based on use case
4. **FAISS Integration**: For large-scale intent databases (1000+ intents)

```python
# Example FAISS optimization for large intent sets
import faiss

class ScalablePACTMatcher(PACTSemanticMatcher):
    """Scalable PACT matcher using FAISS for large intent databases"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faiss_index = None
    
    def _rebuild_embeddings(self):
        """Build FAISS index for fast similarity search"""
        if self.intents:
            embeddings = np.vstack([intent.embedding for intent in self.intents])
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.faiss_index.add(embeddings.astype('float32'))
    
    def find_best_match(self, user_input: str) -> Tuple[Optional[PACTIntent], float]:
        """Fast similarity search using FAISS"""
        if not self.faiss_index:
            return None, 0.0
        
        user_embedding = self.model.encode(user_input).reshape(1, -1).astype('float32')
        faiss.normalize_L2(user_embedding)
        
        similarities, indices = self.faiss_index.search(user_embedding, 1)
        
        best_score = similarities[0][0]
        best_idx = indices[0][0]
        
        if best_score >= self.similarity_threshold:
            return self.intents[best_idx], best_score
        else:
            return None, best_score
```

## Deployment and Monitoring

### Production Checklist:

- [ ] Set up intent performance monitoring
- [ ] Implement user feedback collection
- [ ] Configure confidence threshold alerting
- [ ] Set up A/B testing for different models
- [ ] Create intent analytics dashboard
- [ ] Plan for intent database updates

## Benefits for PACT Protocol

1. **Enhanced User Experience**: Natural language interaction
2. **Reduced Training Time**: Users don't need to memorize exact commands
3. **Increased Adoption**: Lower barrier to entry
4. **Better Analytics**: Track intent patterns and user behavior
5. **Scalable Architecture**: Easy to add new intents and protocols

## Next Steps

1. **Integrate with existing PACT implementations**
2. **Add support for multi-turn conversations**
3. **Implement intent parameter extraction**
4. **Build visual intent management interface**
5. **Create automated intent suggestion system**

---

This case study demonstrates how PACT can evolve from a rigid protocol system to an intelligent, user-friendly interface that bridges natural language and structured actions. The semantic matching capability makes PACT more accessible while maintaining its core protocol benefits.
