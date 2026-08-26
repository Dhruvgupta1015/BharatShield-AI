# BharatShield AI

**Explainable Regional-Language Phishing Detection**

> Omnikon National Hackathon 2026  
> Team: Dhruv Gupta (Leader) · Vivek Pandey

---

## Purpose

BharatShield AI detects phishing risks in **Hindi**, **English**, and **Hinglish** (code-mixed / transliterated Hindi) messages. It provides clear, explainable results so users understand *why* something is flagged — not just *that* it was flagged.

## Problem Statement

Phishing attacks increasingly target regional-language speakers using SMS, WhatsApp, and email in Hindi and Hinglish. Existing phishing-detection tools are primarily trained on English-only content and fail to detect threats written in Devanagari, transliterated Hindi, or code-mixed text. BharatShield AI addresses this gap.

## Current Implementation (Phase 2 MVP)

The project has achieved its **Phase 2 MVP** (Hackathon Demo Candidate) milestone:

- **Frontend**: Redesigned React/Vite UI with dynamic risk visualization, URL intelligence panels, and AI classification confidence.
- **Backend**: FastAPI pipeline handling hybrid detection.
- **Hybrid Fusion Engine**: Combines rule-based NLP signals (multilingual), URL analysis, and ML inference (English-dominant) into a unified risk score (0-100).
- **ML Integration**: TF-IDF + Logistic Regression model is fully serialized and running in the live pipeline.
- **Explainable risk signals**: Clear explanations of triggered rules and human-readable advice.
- **Graceful Fallbacks**: The system falls back to robust deterministic rules if ML is unavailable or if the text is out-of-distribution (e.g. Devanagari Hindi).

## IMPORTANT LIMITATIONS

This is an early-stage hackathon prototype. Please note:
- The current ML dataset (`dataset_v1`) is **English-dominant**.
- Naturally occurring **Hindi and Hinglish samples are not yet established** for ML training. The system relies on its multilingual deterministic rule-based engine to detect threats in these languages.
- The UCI SMS spam ➔ phishing mapping is a **pragmatic proxy mapping**.
- **Multilingual ML performance is NOT yet established**. We do not falsely claim AI accuracy for Hindi/Hinglish.
- **Final production-grade detection is NOT being claimed.** We do not guarantee protection or claim to have a final multilingual ML model.

## Architecture

```
USER INPUT
      ↓
REACT + VITE UI
      ↓
FASTAPI BACKEND
      ↓
 ┌─────────────────────────────────────────────────────────┐
 │               LANGUAGE DETECTION ENGINE                 │
 │                           ↓                             │
 │       ML INFERENCE        NLP ENGINE       URL ENGINE   │
 │       (English only)      (Multilingual)   (Structural) │
 │                           ↓                             │
 │                  HYBRID RISK FUSION                     │
 │                 (0-100 Normalization)                   │
 └─────────────────────────────────────────────────────────┘
      ↓
EXPLAIN + GUIDE
      ↓
LOW RISK / SUSPICIOUS / HIGH RISK
```

## Tech Stack

| Layer    | Technology              |
|----------|-------------------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend  | Python, FastAPI, Uvicorn |
| ML       | Scikit-Learn (TF-IDF + LR) |

## Setup

### Prerequisites
- **Node.js** ≥ 18
- **Python** ≥ 3.10

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server starts at `http://localhost:5173`.

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app
```
The FastAPI server starts at `http://localhost:8000`.

### Verify
1. Open `http://localhost:8000/health` — should return `{"status": "ok", ...}`
2. Open `http://localhost:5173` — BharatShield AI interface should load
3. Paste a message and click **Analyze** — deterministic result should appear

## License
Private — Hackathon project.
