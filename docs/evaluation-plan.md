# BharatShield AI: Evaluation Plan

## Metrics
To empirically compare the deterministic baseline against lightweight ML models, we will capture:
- **Precision:** How many flagged messages were actually phishing?
- **Recall:** How many actual phishing messages did we catch?
- **F1-Score:** Harmonic mean of precision and recall.
- **Confusion Matrix:** True Positives, False Positives, True Negatives, False Negatives.
- **Inference Time:** Crucial for MVP responsiveness.

## Splits & Leakage Prevention
Data will be strictly split into:
- **TRAIN (70%)**: Used exclusively for fitting ML models.
- **VALIDATION (15%)**: Used for hyperparameter tuning.
- **HELD-OUT TEST (15%)**: Strictly used for final evaluation of the baseline vs ML models. Never to be viewed during training or model selection.

Obvious near-duplicate leakage (e.g., the same template with a different URL) will be removed across splits.
