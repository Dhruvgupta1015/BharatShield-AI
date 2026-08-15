# BharatShield AI: ML Roadmap

This roadmap documents the transition from our current deterministic baseline to a lightweight ML system.

## Phase 1 & 2: Deterministic Baseline (Completed)
- Rule-based text detection (Regex).
- Rule-based URL feature extraction.
- Fused scoring.

## Phase 3: ML Evaluation Framework & Dataset Prep (Current)
- Establish strict Pydantic schemas for data.
- Build dataset validation utilities.
- Implement unified model evaluation interfaces.

## Phase 4: Candidate Experiments (Future)
We will evaluate the following architectures against the baseline using the held-out test set:

1. **Candidate A (Lightweight):**
   - Features: TF-IDF / character n-grams.
   - Classifier: Logistic Regression.
   - Pros: Extremely fast, low memory.

2. **Candidate B (Semantic):**
   - Features: Lightweight multilingual sentence embeddings (e.g., LaBSE or mini-LM).
   - Classifier: Logistic Regression.
   - Pros: Better cross-lingual understanding for Hinglish.

3. **Candidate C (Semantic Ensemble):**
   - Features: Multilingual sentence embeddings.
   - Classifier: Random Forest.
   - Pros: Handles non-linear decision boundaries between URLs and text.
