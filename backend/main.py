"""
BharatShield AI — Backend API
FastAPI application for explainable phishing detection and analysis.

Phase 2 MVP — Integrated ML + Rule-based hybrid analysis pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import AnalyzeRequest, AnalyzeResponse
from engines.language import detect_language
from engines.fusion import fuse_signals

app = FastAPI(
    title="BharatShield AI",
    description="Explainable Regional-Language Phishing Detection API",
    version="0.2.0",
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
    """Health check endpoint with ML model status."""
    from engines import ml_engine
    return {
        "status": "ok",
        "service": "BharatShield AI",
        "version": "0.2.0",
        "stage": "phase2-mvp",
        "ml_model_loaded": ml_engine.is_available(),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_message(request: AnalyzeRequest):
    """
    Analyzes a message for phishing risks using hybrid ML + rule-based detection.

    Pipeline:
        Input → Language Detection → ML Classification → NLP Signals
        → URL Analysis → Hybrid Risk Fusion → Explainable Response
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    language = detect_language(text)
    result = fuse_signals(text, language)

    return result
