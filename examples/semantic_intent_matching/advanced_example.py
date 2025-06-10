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
