import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

intents = {
    "greet": "Hello",
    "goodbye": "See you later",
    "order_pizza": "I want to order a pizza",
    "track_order": "Where is my order",
    "cancel_order": "I need to cancel my order"
}

intent_names = list(intents.keys())
intent_texts = list(intents.values())

def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return np.array(response.data[0].embedding)

intent_embeddings = np.array([get_embedding(text) for text in intent_texts])

def match_intent(user_input, threshold=0.75):
    input_embedding = get_embedding(user_input)
    similarities = cosine_similarity([input_embedding], intent_embeddings)[0]
    best_idx = np.argmax(similarities)
    best_score = similarities[best_idx]
    if best_score >= threshold:
        return intent_names[best_idx], best_score
    else:
        return "unknown_intent", best_score
