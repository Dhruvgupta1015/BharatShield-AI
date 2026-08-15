from abc import ABC, abstractmethod
from typing import List, Dict, Union

class BaseDetector(ABC):
    """
    Abstract base class for all detection models, including the deterministic baseline and future ML models.
    """
    
    @abstractmethod
    def predict(self, texts: List[str]) -> List[int]:
        """
        Returns binary predictions: 1 for phishing, 0 for benign.
        """
        pass
        
    def predict_proba(self, texts: List[str]) -> List[float]:
        """
        Returns probability of phishing (0.0 to 1.0).
        Optional method. Raises NotImplementedError if the model only outputs binary predictions.
        """
        raise NotImplementedError("This detector does not provide calibrated probabilities.")
