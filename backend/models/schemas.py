from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    risk_level: str
    risk_score: int
    language: str
    signals: List[str]
    explanation: str
    recommended_actions: List[str]
    url_analysis: Optional[Dict[str, Any]] = None
