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
