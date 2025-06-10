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
