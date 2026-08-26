"""
BharatShield AI — Model Training & Export
Trains the TF-IDF + Logistic Regression phishing classifier using the
best hyperparameters from the Phase 4A experiment and exports serialized
artifacts for production inference.

Usage:
    python ml/train_and_export.py
    (run from project root)
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Also ensure backend is importable (needed by baseline_adapter transitive imports)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

import joblib
from ml.models.tfidf_logreg import TfidfLogisticRegression
from ml.evaluation.metrics import ModelEvaluator

DATASET_PATH = Path(PROJECT_ROOT) / "ml" / "data" / "processed" / "dataset_v1.json"
ARTIFACTS_DIR = Path(PROJECT_ROOT) / "ml" / "artifacts"

# Best configuration from Phase 4A hyperparameter search (validated on held-out val set)
BEST_CONFIG = {
    "analyzer": "char_wb",
    "ngram_range": (3, 5),
    "class_weight": "balanced",
    "C": 10.0,
}


def load_data():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_split(data, split_name):
    texts, labels = [], []
    for row in data:
        if row["split"] == split_name:
            texts.append(row["text"])
            labels.append(1 if row["label"] == "phishing" else 0)
    return texts, labels


def train_and_export():
    print("=" * 60)
    print("BharatShield AI — Model Training & Export")
    print("=" * 60)

    # 1. Load dataset
    print("\n[1/4] Loading dataset...")
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Run `python ml/preprocessing/build_dataset.py` first.")
        sys.exit(1)

    data = load_data()
    train_texts, train_y = extract_split(data, "train")
    val_texts, val_y = extract_split(data, "val")
    test_texts, test_y = extract_split(data, "test")

    print(f"  Train: {len(train_texts)} samples")
    print(f"  Val:   {len(val_texts)} samples")
    print(f"  Test:  {len(test_texts)} samples")

    # 2. Train model with best config
    print(f"\n[2/4] Training model...")
    print(f"  Config: {BEST_CONFIG}")
    model = TfidfLogisticRegression(**BEST_CONFIG)
    train_start = time.time()
    model.fit(train_texts, train_y)
    train_time = time.time() - train_start
    print(f"  Training completed in {train_time:.2f}s")

    # 3. Evaluate on held-out test set
    print("\n[3/4] Evaluating on held-out test set...")
    evaluator = ModelEvaluator(model)
    test_metrics = evaluator.evaluate(test_texts, test_y)
    val_metrics = evaluator.evaluate(val_texts, val_y)

    print(f"  Test Precision: {test_metrics['precision']}")
    print(f"  Test Recall:    {test_metrics['recall']}")
    print(f"  Test F1:        {test_metrics['f1_score']}")
    print(f"  Val  F1:        {val_metrics['f1_score']}")

    # 4. Export artifacts
    print("\n[4/4] Exporting artifacts...")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save the full sklearn pipeline (vectorizer + classifier)
    pipeline_path = ARTIFACTS_DIR / "phishing_classifier.joblib"
    joblib.dump(model.pipeline, pipeline_path)
    print(f"  Saved: {pipeline_path}")

    # Save vectorizer separately for transparency/inspection
    vectorizer_path = ARTIFACTS_DIR / "tfidf_vectorizer.joblib"
    joblib.dump(model.pipeline.named_steps['tfidf'], vectorizer_path)
    print(f"  Saved: {vectorizer_path}")

    # Save metadata
    metadata = {
        "model_name": "TF-IDF + Logistic Regression",
        "model_version": "v1",
        "vectorizer_type": "TfidfVectorizer (char_wb, 3-5 ngrams)",
        "classifier_type": "LogisticRegression (balanced, C=10.0)",
        "config": {
            "analyzer": BEST_CONFIG["analyzer"],
            "ngram_range": list(BEST_CONFIG["ngram_range"]),
            "class_weight": BEST_CONFIG["class_weight"],
            "C": BEST_CONFIG["C"],
        },
        "dataset": {
            "name": "dataset_v1",
            "source": "UCI SMS Spam Collection",
            "language_coverage": "English-dominant (no native Hindi/Hinglish samples)",
            "total_samples": len(train_texts) + len(val_texts) + len(test_texts),
            "train_samples": len(train_texts),
            "val_samples": len(val_texts),
            "test_samples": len(test_texts),
        },
        "test_metrics": {
            "precision": test_metrics["precision"],
            "recall": test_metrics["recall"],
            "f1_score": test_metrics["f1_score"],
            "confusion_matrix": test_metrics["confusion_matrix"],
        },
        "val_metrics": {
            "precision": val_metrics["precision"],
            "recall": val_metrics["recall"],
            "f1_score": val_metrics["f1_score"],
        },
        "training_time_seconds": round(train_time, 2),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "artifact_files": [
            "phishing_classifier.joblib",
            "tfidf_vectorizer.joblib",
            "model_metadata.json",
        ],
        "limitations": [
            "English-dominant dataset — Hindi/Hinglish ML accuracy is NOT validated",
            "UCI SMS spam-to-phishing label mapping is a pragmatic proxy",
            "Model probability estimates are not calibrated",
        ],
    }

    metadata_path = ARTIFACTS_DIR / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {metadata_path}")

    print("\n" + "=" * 60)
    print(f"Export complete! {3} artifacts saved to ml/artifacts/")
    print(f"  Test F1: {test_metrics['f1_score']}")
    print("=" * 60)


if __name__ == "__main__":
    train_and_export()
