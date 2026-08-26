"""
BharatShield AI — API Schema Models
Pydantic models defining the API request/response contract.
"""

from pydantic import BaseModel
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: str


class SignalDetail(BaseModel):
    """A single detected threat signal with human-readable metadata."""
    id: str
    label: str
    description: str
    severity: str  # "low", "medium", "high"


class UrlDetail(BaseModel):
    """Analysis result for a single URL found in the input."""
    url: str
    is_shortened: bool
    scheme: Optional[str] = None
    hostname: Optional[str] = None
    is_ip: bool
    flags: List[str] = []
    risk_reasons: List[str] = []


class MlAnalysis(BaseModel):
    """ML classifier output, shown separately for transparency."""
    available: bool
    prediction: Optional[str] = None   # "phishing" / "benign"
    confidence: Optional[float] = None  # 0.0–1.0
    model_version: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Complete analysis response with verdict, evidence, and guidance."""
    verdict: str             # "HIGH_RISK" / "SUSPICIOUS" / "LOW_RISK"
    risk_score: int          # 0–100 normalized
    confidence: float        # 0.0–1.0
    language: str
    analysis_summary: str
    signals: List[SignalDetail]
    url_analysis: List[UrlDetail]
    ml_analysis: MlAnalysis
    recommended_actions: List[str]
