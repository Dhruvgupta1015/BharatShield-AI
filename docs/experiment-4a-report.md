# BharatShield AI: Phase 4A Experiment Report
## TF-IDF + Logistic Regression vs Deterministic Baseline

### IMPORTANT LIMITATIONS
- **English-Dominant**: Dataset `dataset_v1` is primarily English.
- **Regional Gap**: Naturally occurring Hindi samples = 0. Naturally occurring Hinglish samples = 0.
- **Proxy Labels**: The UCI `spam` → `phishing` mapping is a pragmatic proxy. This experiment does NOT validate regional-language phishing detection.

### 1. Dataset Summary
- **Train Split**: 3382 samples
- **Validation Split**: 724 samples
- **Held-Out Test Split**: 726 samples

### 2. Model Selection (Validation)
Hyperparameter search was conducted purely on the Validation split.
- **Best Configuration**: `{'analyzer': 'char_wb', 'ngram_range': (3, 5), 'class_weight': 'balanced', 'C': 10.0}`
- **Validation Phishing F1-Score**: 0.8947
- **Validation Phishing Recall**: 0.8718

### 3. Final TEST Metrics Comparison

| Metric | Deterministic Baseline | TF-IDF + Logistic Regression |
| :--- | :--- | :--- |
| **Phishing Precision** | 1.0 | 0.9474 |
| **Phishing Recall** | 0.0317 | 0.8571 |
| **Phishing F1-Score** | 0.0615 | 0.9 |
| **Inference Time (sec)** | 0.0879 | 0.0725 |

*(Note: Inference time was measured strictly on the prediction pass over the 726 test samples after loading/training).*

### 4. Confusion Matrices (TEST)

**Deterministic Baseline**
- True Positives: 2
- False Positives: 0
- True Negatives: 663
- False Negatives: 61

**TF-IDF + Logistic Regression**
- True Positives: 54
- False Positives: 3
- True Negatives: 660
- False Negatives: 9

### 5. Error Analysis (TF-IDF + LR)

Representative errors from the TEST set, masked for privacy:

**False Positives (Predicted Phishing, Actually Benign):**
- **ID**: `6a10d54a32291e75b6efdcd0f4d565bc46a909853522a3beb6b89d4822747a78` | **Text snippet**: `Your daily text...[REDACTED]... this time`
- **ID**: `356c56258f67d02091988cdafbcfba78cff41a7aced41e3353a24eee77d0a823` | **Text snippet**: `[REDACTED]`
- **ID**: `f889375be1ab6f8d14f003f76730c425258010410451642fb3d68b58ad39fec2` | **Text snippet**: `Cheers for the ...[REDACTED]...xt or not.`

**False Negatives (Predicted Benign, Actually Phishing):**
- **ID**: `a912274b294493a781ade40782fbfc0fcc299e05c68841e389dfa971cc540547` | **Text snippet**: `Hello. We need ...[REDACTED]...asap. Ta r`
- **ID**: `3fd7d94e483f2a78d7e3bb35abe5cc3a65a3939a341bdce32ca036bebe0c643e` | **Text snippet**: `(Bank of Granit...[REDACTED]...5.00 per..`
- **ID**: `217365743071993cd0c7ed4e6cea94da2f91f99e2e09b4a6e6a8c6a2176f68fd` | **Text snippet**: `SMS. ac sun0819...[REDACTED]...P to 62468`
- **ID**: `b37f456f1ec5b80e7d1b2cc94e82cc5c24e095e87d1a0765f413f78b636c1122` | **Text snippet**: `Romantic Paris....[REDACTED]...&Cs apply.`
- **ID**: `afd822affe494a40a65dc395a0869f4a8c8933e1244fa5bd77c0e74abeac045e` | **Text snippet**: `88066 FROM 8806...[REDACTED]...POUND HELP`

### 6. Recommendation
Based on the objective F1-score increase, the ML baseline significantly outperforms the deterministic rules on English text. The next recommended experiment is Phase 4B: Multilingual Embeddings, to prepare for true regional-language coverage.
