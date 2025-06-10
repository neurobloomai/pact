import unittest
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from matcher import match_intent

class TestSentenceTransformerMatcher(unittest.TestCase):
    def test_greet(self):
        intent, score = match_intent("hey")
        self.assertEqual(intent, "greet")

    def test_order_pizza(self):
        intent, score = match_intent("Can I get a pizza?")
        self.assertEqual(intent, "order_pizza")

    def test_unknown(self):
        intent, score = match_intent("What's the weather?")
        self.assertEqual(intent, "unknown_intent")

if __name__ == '__main__':
    unittest.main()
