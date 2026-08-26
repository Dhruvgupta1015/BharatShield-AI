"""
BharatShield AI — Baseline Adapter

Wraps the deterministic rule-based detection engine into the BaseDetector
interface so it can be evaluated fairly against ML models.

This adapter uses the NLP and URL engines directly (not the full fusion
pipeline) to isolate the rule-based detection performance.
"""

import sys
import os
from typing import List

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from engines.nlp import analyze_nlp_signals
from engines.url import analyze_urls_in_text
from ml.models.base import BaseDetector

# Signal weights (matching the production fusion engine)
SIGNAL_WEIGHTS = {
    "urgency": 1,
    "account_threat": 2,
    "kyc_request": 2,
    "credential_request": 3,
    "financial_request": 2,
    "suspicious_cta": 1,
    "shortened_url": 2,
    "ip_hostname": 3,
    "suspicious_url_structure": 1,
    "http_scheme": 1,
}


class BaselineAdapter(BaseDetector):
    """
    Adapts the deterministic rule-based engine into the BaseDetector interface
    so it can be evaluated exactly like an ML model.

    Threshold: score >= 3 → phishing (positive)
    """

    def predict(self, texts: List[str]) -> List[int]:
        predictions = []
        for text in texts:
            nlp_signals = analyze_nlp_signals(text)
            url_signals, _ = analyze_urls_in_text(text)
            all_signals = set(nlp_signals + url_signals)
            score = sum(SIGNAL_WEIGHTS.get(s, 0) for s in all_signals)
            predictions.append(1 if score >= 3 else 0)
        return predictions
