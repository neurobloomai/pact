from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

intents = {
    "greet": "Hello",
    "goodbye": "See you later",
    "order_pizza": "I want to order a pizza",
    "track_order": "Where is my order",
    "cancel_order": "I need to cancel my order",
}

intent_names = list(intents.keys())
intent_texts = list(intents.values())
model = SentenceTransformer("all-MiniLM-L6-v2")
intent_embeddings = model.encode(intent_texts)

def match_intent(user_input, threshold=0.65):
    input_embedding = model.encode([user_input])
    similarities = cosine_similarity(input_embedding, intent_embeddings)[0]
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    if best_score >= threshold:
        return intent_names[best_idx], best_score
    else:
        return "unknown_intent", best_score
