import unittest
from matcher import match_intent

class TestOpenAIEmbeddingMatcher(unittest.TestCase):
    def test_greet(self):
        intent, score = match_intent("hey")
        self.assertEqual(intent, "greet")

    def test_order_pizza(self):
        intent, score = match_intent("I'd like a pizza")
        self.assertEqual(intent, "order_pizza")

    def test_unknown(self):
        intent, score = match_intent("What is Bitcoin?")
        self.assertEqual(intent, "unknown_intent")

if __name__ == '__main__':
    unittest.main()
