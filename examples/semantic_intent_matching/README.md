Guide to building semantic matcher:

**Start with the Architecture Overview:**
```
User Input → Embedding → Similarity Search → Threshold Check → Best Match/Fallback
```

**Step-by-Step Guidance:**

**1. Choose Your Embedding Approach**
- Start with Sentence Transformers (lighter, faster): `sentence-transformers/all-MiniLM-L6-v2`
- OpenAI embeddings for higher accuracy but API dependency
- Test both, compare results on your actual PACT intents

**2. Build the Intent Database**
```python
# Precompute embeddings for all PACT intents/actions
intents_db = {
    "get_sales_report": {"embedding": [...], "action": "analytics.sales"},
    "handle_support": {"embedding": [...], "action": "support.ticket"},
}
```

**3. Similarity Search Implementation**
- Use cosine similarity (simple dot product works well)
- Consider FAISS if you have many intents (>1000)
- Start simple with numpy/scipy

**4. Threshold Tuning Strategy**
- Start with 0.7-0.8 similarity threshold
- Log all matches with scores for analysis
- Build a small test dataset of expected matches

**5. Integration with PACT**
- Fallback layer: exact match first, then semantic search
- Return confidence scores alongside matches
- Add logging for continuous improvement

