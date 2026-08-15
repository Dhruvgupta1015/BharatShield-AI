# BharatShield AI: Dataset Report (v1)

This document details the generation of the first machine learning dataset (`dataset_v1.json`) used for evaluating BharatShield AI.

## IMPORTANT LIMITATIONS & CAVEATS
1. **Label Semantics**: The dataset maps the original source label `spam` to `phishing` and `ham` to `benign` as a pragmatic proxy for our initial baseline. It must be noted that not all "spam" is definitively "phishing."
2. **Regional Language Data Gap**: There are zero (`0`) legally-cleared, freely-available naturally occurring Hindi/Hinglish SMS phishing samples in this dataset. We have chosen not to fabricate or synthesize data for this release to maintain absolute integrity of the evaluation dataset.

## Dataset Summary Metrics
- **Source Used:** UCI SMS Spam Collection
- **Total Raw Samples:** 5,574
- **Privacy/PII Filtering Removals:** 379
- **Exact/Near Duplicates Removed:** 363
- **Final Valid Dataset Size:** 4,832

## Label Distribution
- **Phishing (Proxy from Spam):** 317
- **Benign (Proxy from Ham):** 4,515
- **Original Spam:** 317
- **Original Ham:** 4,515

## Language & Script Distribution
- **English:** 4,829
- **Hindi:** 0
- **Hinglish:** 0
- **Mixed/Other:** 3
- **Latin Script:** 4,829
- **Devanagari Script:** 0
- **Mixed Script:** 3

## Deterministic Splits & Leakage
The train/val/test splits were generated using a deterministic shuffle (`random.seed(42)`) keyed on a reproducible, hash-based `sample_id` derived from the source name, row index, and normalized text. The dataset validation pipeline strictly verified that **0 leakage** exists between Train and Val/Test.
- **Train (70%):** 3,382
- **Validation (15%):** 724
- **Test (15%):** 726

## Reproducibility
To fully reproduce this dataset from scratch:
```bash
python ml/preprocessing/build_dataset.py
```
