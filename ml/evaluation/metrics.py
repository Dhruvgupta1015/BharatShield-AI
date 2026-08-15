import time
from typing import List, Dict, Any
from ml.models.base import BaseDetector

class ModelEvaluator:
    """
    Evaluates any BaseDetector implementation, computing standard ML metrics.
    Currently avoids heavy dependencies like scikit-learn, but provides the exact structure.
    """
    
    def __init__(self, model: BaseDetector):
        self.model = model
        
    def evaluate(self, texts: List[str], y_true: List[int]) -> Dict[str, Any]:
        if not texts or not y_true:
            return {"error": "Dataset is empty. Metrics are not available."}
            
        start_time = time.time()
        y_pred = self.model.predict(texts)
        inference_time = time.time() - start_time
        
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "sample_count": len(texts),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": {
                "tp": tp, "fp": fp, "tn": tn, "fn": fn
            },
            "inference_time_seconds": round(inference_time, 4)
        }
