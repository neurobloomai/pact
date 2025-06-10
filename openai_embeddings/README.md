# Semantic Intent Matcher

This repository contains two versions of a semantic matcher for predicting the closest intent from user input using embeddings and cosine similarity:

---

## 🔹 1. Sentence Transformers Version

**Path:** `sentence_transformers/`

### Model:
- `all-MiniLM-L6-v2` from HuggingFace

### Features:
- Local embedding model (no API required)
- Fast inference
- Suitable for lightweight use cases

### Run:
```bash
cd sentence_transformers
pip install -r requirements.txt
python test_matcher.py
```

---

## 🔹 2. OpenAI Embeddings Version

**Path:** `openai_embeddings/`

### Model:
- `text-embedding-3-small` via OpenAI API

### Features:
- Accurate cloud embeddings
- Scalable and up-to-date model
- Requires OpenAI API key

### Setup:
```bash
cd openai_embeddings
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python test_matcher.py
```

---

## 🧪 Unit Tests

Each version includes a test file using `unittest` that:
- Verifies correct intent matching for simple phrases
- Ensures unknown inputs fall below the similarity threshold

---

## 📦 Requirements

You can install requirements for each version as needed:

**`sentence_transformers/requirements.txt`**
```
sentence-transformers
scikit-learn
```

**`openai_embeddings/requirements.txt`**
```
openai
scikit-learn
```

---

## ✅ Example Inputs

- "Can I get a pizza?" → `order_pizza`
- "Bye" → `goodbye`
- "What's the weather?" → `unknown_intent` (below threshold)

---

## ⚙️ Threshold Tuning

Adjust the `threshold` parameter in `match_intent()` to control the minimum cosine similarity required to accept a match.

---

## 📁 Structure

```
semantic_matcher/
│
├── sentence_transformers/
│   ├── matcher.py
│   ├── test_matcher.py
│   └── requirements.txt
│
├── openai_embeddings/
│   ├── matcher.py
│   ├── test_matcher.py
│   └── requirements.txt
│
└── README.md
```
