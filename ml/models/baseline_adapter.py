import sys
import os
from typing import List

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from engines.fusion import fuse_signals
from ml.models.base import BaseDetector

class BaselineAdapter(BaseDetector):
    """
    Adapts the deterministic backend.engines.fusion rule-based engine into the BaseDetector interface
    so it can be evaluated exactly like an ML model.
    """
    
    def predict(self, texts: List[str]) -> List[int]:
        predictions = []
        for text in texts:
            risk_level, score, _, _, _, _ = fuse_signals(text)
            # Threshold: Suspicious (3-5) and High Risk (6+) are treated as positive for evaluation
            if score >= 3:
                predictions.append(1)
            else:
                predictions.append(0)
        return predictions


