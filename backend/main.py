"""
BharatShield AI — Backend
FastAPI application for phishing detection and analysis.

Current stage: Foundation — health endpoint and CORS only.
Detection engine is NOT yet implemented.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import AnalyzeRequest, AnalyzeResponse
from engines.language import detect_language
from engines.fusion import fuse_signals

app = FastAPI(
    title="BharatShield AI",
    description="Explainable Regional-Language Phishing Detection API",
    version="0.1.0",
)

# CORS configuration for local development with Vite (default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "BharatShield AI",
        "stage": "foundation",
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_message(request: AnalyzeRequest):
    """
    Analyzes a message (text/URL) for phishing risks.
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    language = detect_language(text)
    risk_level, score, signals, explanation, recommended_actions, url_analysis = fuse_signals(text)
    
    return AnalyzeResponse(
        risk_level=risk_level,
        risk_score=score,
        language=language,
        signals=signals,
        explanation=explanation,
        recommended_actions=recommended_actions,
        url_analysis=url_analysis
    )
