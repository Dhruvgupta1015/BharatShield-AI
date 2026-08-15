# BharatShield AI

**Explainable Regional-Language Phishing Detection**

> Omnikon National Hackathon 2026  
> Team: Dhruv Gupta (Leader) · Vivek Pandey

---

## Purpose

BharatShield AI detects phishing risks in **Hindi**, **English**, and **Hinglish** (code-mixed / transliterated Hindi) messages. It provides clear, explainable results so users understand *why* something is flagged — not just *that* it was flagged.

## Problem Statement

Phishing attacks increasingly target regional-language speakers using SMS, WhatsApp, and email in Hindi and Hinglish. Existing phishing-detection tools are primarily trained on English-only content and fail to detect threats written in Devanagari, transliterated Hindi, or code-mixed text. BharatShield AI addresses this gap.

## Current Implementation

The project has completed Phase 1 through 4A, establishing the full MVP pipeline:

- **React/Vite frontend**: User-facing UI to input suspicious messages.
- **FastAPI backend**: API for handling detection.
- **Frontend/backend integration**: Fully wired input/output.
- **Deterministic NLP baseline**: Regex and heuristic-based text classification.
- **URL analysis baseline**: URL extraction and basic risk heuristics.
- **Risk Fusion**: Cumulative scoring yielding Lower Risk (0-2), Suspicious (3-5), or High Risk (6+).
- **Explainable risk signals**: Clear explanations of triggered rules.
- **Actionable guidance**: Step-by-step user recommendations based on risk.
- **ML dataset/evaluation infrastructure**: Pydantic schemas, deduplication, and isolated evaluation pipelines.
- **Dataset v1**: Curated SMS phishing baseline (UCI).
- **TF-IDF + Logistic Regression experiment**: Classical ML benchmark compared against deterministic rules.

## IMPORTANT LIMITATIONS

This is an early-stage hackathon prototype. Please note:
- The current `dataset_v1` is **English-dominant**.
- Naturally occurring **Hindi and Hinglish samples are not yet established** due to a lack of ethically-sourced public datasets.
- The UCI SMS spam → phishing mapping is a **pragmatic proxy mapping**.
- **Multilingual ML performance is NOT yet established** or proven by the current baseline.
- **Final production-grade detection is NOT being claimed.** We do not guarantee protection or claim to have a final multilingual ML model.

## Architecture

```
USER INPUT
      ↓
REACT + VITE UI
      ↓
FASTAPI BACKEND
      ↓
 ┌───────────────┬───────────────┐
 ↓               ↓               ↓
NLP ENGINE    URL ENGINE    RISK FUSION
                                 ↓
                          EXPLAIN + GUIDE
                                 ↓
                 LOWER RISK / SUSPICIOUS / HIGH RISK
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
