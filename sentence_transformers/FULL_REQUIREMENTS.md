# Full Requirements Description

This document provides detailed requirements and descriptions for each version of the semantic matcher system, which uses sentence embeddings and cosine similarity to identify user intent from free-text input.

---

## 🧠 Purpose

Build a **resilient semantic intent matcher** that:
- Understands free-form natural language inputs
- Handles variations in phrasing
- Maps user utterances to a predefined set of intents
- Returns the most relevant intent or "unknown" if confidence is too low

---

## 📌 Core Features

- **Embeddings**: Convert text to dense vectors using either:
  - `SentenceTransformers` (local model)
  - `OpenAI` Embeddings (cloud API)
- **Similarity Metric**: Cosine similarity used to compare user input with known intents
- **Threshold**: Tunable parameter for minimum similarity required to accept a match
- **Fallback**: If no match exceeds the threshold, return `"unknown_intent"`

---

## 📂 System Variants

### 1. Sentence Transformers Version

**Model**: `all-MiniLM-L6-v2`  
**Library**: `sentence-transformers`  
**Use Case**: Local, lightweight environments with no internet or API cost

#### Requirements:
- sentence-transformers
- scikit-learn

#### Pros:
- Fast, privacy-preserving
- Free after model download

#### Limitations:
- May be less accurate than large models or OpenAI
- Requires Python environment with some memory/CPU

---

### 2. OpenAI Embeddings Version

**Model**: `text-embedding-3-small`  
**Library**: `openai` (requires API key)  
**Use Case**: Production-grade, cloud-based inference with high-quality embeddings

#### Requirements:
- openai
- scikit-learn

#### Pros:
- Better accuracy for diverse real-world input
- Maintained and scalable infrastructure

#### Limitations:
- Requires internet + API key
- Cost per token for usage

---

## 🧪 Unit Testing

Each version includes:
- Unit tests using `unittest`
- Test coverage for:
  - Known intent mapping
  - Unknown/fallback detection
  - Accuracy under natural phrasing

---

## ⚙️ Configuration Parameters

- **Threshold (float)**: Controls sensitivity
  - Typical value: `0.65–0.85`
  - Higher value = more cautious, fewer false positives
- **Intent Definitions (dict)**: Key → canonical phrase

---

## 💡 Example Inputs and Outputs

| Input Text                   | Predicted Intent   | Score (Example) |
|-----------------------------|--------------------|-----------------|
| "I'd like a pizza"          | order_pizza        | 0.92            |
| "Where is my delivery?"     | track_order        | 0.88            |
| "What is Bitcoin?"          | unknown_intent     | 0.31            |

---

## 📈 Extensibility

- Add more intents with associated sample phrases
- Improve matching with sentence augmentation (synonyms, paraphrases)
- Wrap in a REST API (Flask/FastAPI) or GUI (Gradio)
- Persist vectors using vector DBs like FAISS for scale

---

## 📁 File Structure

```
semantic_matcher/
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
├── README.md
└── FULL_REQUIREMENTS.md  ← (this file)
```

---

## ✅ End Goal

Enable intelligent, robust text understanding in low-resource bots, assistants, or interfaces with graceful fallback when inputs don't match.

