"""
BharatShield AI — Hybrid Risk Fusion Engine

Combines three independent evidence sources into a unified risk assessment:
  1. Rule-based NLP signals (deterministic, multilingual)
  2. URL intelligence (deterministic)
  3. ML classifier probability (when available)

Fusion Formula:
  With ML:    hybrid = 0.40 × ML_prob + 0.35 × NLP_norm + 0.25 × URL_norm
  Without ML: hybrid = 0.65 × NLP_norm + 0.35 × URL_norm

  NLP_norm = min(raw_nlp_score / 8, 1.0)
  URL_norm = min(raw_url_score / 6, 1.0)

  risk_score = round(hybrid × 100)   → 0–100

Design rationale:
  - No single weak signal produces HIGH_RISK alone
  - Strong independent signals reinforce each other
  - ML does not completely override deterministic evidence
  - The system remains fully explainable
  - Thresholds are configurable constants
"""

from typing import List, Tuple, Optional
from engines.nlp import analyze_nlp_signals
from engines.url import analyze_urls_in_text
from engines import ml_engine
from models.schemas import SignalDetail, UrlDetail, MlAnalysis, AnalyzeResponse


# ── Signal Configuration ──────────────────────────────────────────────

SIGNAL_WEIGHTS = {
    # NLP signals
    "urgency": 1,
    "account_threat": 2,
    "kyc_request": 2,
    "credential_request": 3,
    "financial_request": 2,
    "suspicious_cta": 1,
    # URL signals
    "shortened_url": 2,
    "ip_hostname": 3,
    "suspicious_url_structure": 1,
    "http_scheme": 1,
}

SIGNAL_LABELS = {
    "urgency": "Urgency Manipulation",
    "account_threat": "Account Suspension Threat",
    "kyc_request": "KYC / Verification Request",
    "credential_request": "Credential / OTP / PIN Request",
    "financial_request": "Financial Manipulation",
    "suspicious_cta": "Suspicious Call to Action",
    "shortened_url": "URL Shortener Detected",
    "ip_hostname": "IP Address URL",
    "suspicious_url_structure": "Suspicious URL Structure",
    "http_scheme": "Insecure HTTP Connection",
}

SIGNAL_DESCRIPTIONS = {
    "urgency": "The message uses urgent language designed to pressure you into acting quickly without thinking.",
    "account_threat": "The message threatens account suspension or blocking to create panic.",
    "kyc_request": "The message requests KYC or identity verification — a common phishing tactic in India.",
    "credential_request": "The message asks for sensitive credentials such as passwords, PINs, or OTPs.",
    "financial_request": "The message involves suspicious financial transactions, rewards, or payment requests.",
    "suspicious_cta": "The message contains a call-to-action urging you to click a suspicious link.",
    "shortened_url": "A URL shortener hides the true destination, which is a common phishing technique.",
    "ip_hostname": "The URL uses a raw IP address instead of a domain name — a strong phishing indicator.",
    "suspicious_url_structure": "The URL has an unusually complex structure often used to disguise malicious destinations.",
    "http_scheme": "The URL uses unencrypted HTTP instead of HTTPS, meaning data is not protected.",
}

SIGNAL_SEVERITY = {
    "urgency": "medium",
    "account_threat": "high",
    "kyc_request": "medium",
    "credential_request": "high",
    "financial_request": "high",
    "suspicious_cta": "medium",
    "shortened_url": "medium",
    "ip_hostname": "high",
    "suspicious_url_structure": "low",
    "http_scheme": "low",
}

ACTIONS = {
    "credential_request": "Never share passwords, PINs, or OTPs — no legitimate service will ask for these via message.",
    "kyc_request": "Verify KYC requests only through the official app or website of the service.",
    "account_threat": "Check your account status directly through the official app or website — not through message links.",
    "financial_request": "Do not send money or accept unexpected prizes. Verify through official channels.",
    "shortened_url": "Do not click shortened links. Verify the destination independently before opening.",
    "ip_hostname": "Do not visit URLs using IP addresses. Legitimate services use proper domain names.",
    "suspicious_cta": "Do not follow suspicious links. Navigate to the official website directly.",
}


# ── Scoring Constants ─────────────────────────────────────────────────

MAX_NLP_SCORE = 8    # Practical maximum for NLP signal scores
MAX_URL_SCORE = 6    # Practical maximum for URL signal scores

# Hybrid fusion weights (with ML available)
W_ML  = 0.40
W_NLP = 0.35
W_URL = 0.25

# Fallback weights (ML unavailable)
W_NLP_FALLBACK = 0.65
W_URL_FALLBACK = 0.35

# Verdict thresholds (0–100 scale)
THRESHOLD_HIGH_RISK  = 60
THRESHOLD_SUSPICIOUS = 30


# ── Internal Helpers ──────────────────────────────────────────────────

def _build_signal_details(signal_ids: List[str]) -> List[SignalDetail]:
    """Convert raw signal IDs into structured SignalDetail objects."""
    details = []
    for sid in signal_ids:
        details.append(SignalDetail(
            id=sid,
            label=SIGNAL_LABELS.get(sid, sid.replace("_", " ").title()),
            description=SIGNAL_DESCRIPTIONS.get(sid, ""),
            severity=SIGNAL_SEVERITY.get(sid, "medium"),
        ))
    # Sort by severity: high first, then medium, then low
    severity_order = {"high": 0, "medium": 1, "low": 2}
    details.sort(key=lambda s: severity_order.get(s.severity, 1))
    return details


def _build_url_details(raw_details: list) -> List[UrlDetail]:
    """Convert raw URL analysis dicts into structured UrlDetail objects."""
    url_details = []
    for d in raw_details:
        flags = []
        reasons = []

        if d.get("is_shortened"):
            flags.append("shortened_url")
            reasons.append("This URL uses a shortener that hides the real destination.")
        if d.get("is_ip"):
            flags.append("ip_hostname")
            reasons.append("This URL uses a raw IP address instead of a domain name.")
        if d.get("scheme") == "http":
            flags.append("http_scheme")
            reasons.append("This URL uses unencrypted HTTP.")

        hostname = d.get("hostname", "")
        if hostname and not d.get("is_ip") and len(hostname.split(".")) > 4:
            flags.append("suspicious_url_structure")
            reasons.append("This URL has an unusually complex subdomain structure.")

        url_details.append(UrlDetail(
            url=d.get("url", ""),
            is_shortened=d.get("is_shortened", False),
            scheme=d.get("scheme"),
            hostname=d.get("hostname"),
            is_ip=d.get("is_ip", False),
            flags=flags,
            risk_reasons=reasons,
        ))
    return url_details


def _compute_hybrid_score(
    nlp_signals: List[str],
    url_signals: List[str],
    ml_phishing_prob: Optional[float],
) -> Tuple[int, float]:
    """
    Compute a hybrid risk score (0–100) and confidence (0.0–1.0).

    The fusion combines three normalized evidence sources with configurable
    weights. Confidence reflects how much independent evidence supports
    the final verdict.
    """
    # Raw component scores
    nlp_raw = sum(SIGNAL_WEIGHTS.get(s, 0) for s in nlp_signals)
    url_raw = sum(SIGNAL_WEIGHTS.get(s, 0) for s in url_signals)

    # Normalize to 0–1
    nlp_norm = min(nlp_raw / MAX_NLP_SCORE, 1.0)
    url_norm = min(url_raw / MAX_URL_SCORE, 1.0)

    # Weighted combination
    if ml_phishing_prob is not None:
        hybrid = (
            W_ML  * ml_phishing_prob +
            W_NLP * nlp_norm +
            W_URL * url_norm
        )
    else:
        hybrid = (
            W_NLP_FALLBACK * nlp_norm +
            W_URL_FALLBACK * url_norm
        )

    risk_score = max(0, min(100, round(hybrid * 100)))

    # ── Confidence calculation ──
    # Based on number of independent evidence sources and their agreement
    is_risky = risk_score >= THRESHOLD_SUSPICIOUS
    sources_active = 0
    sources_agreeing = 0

    if nlp_raw > 0:
        sources_active += 1
        if is_risky:
            sources_agreeing += 1

    if url_raw > 0:
        sources_active += 1
        if is_risky:
            sources_agreeing += 1

    if ml_phishing_prob is not None:
        sources_active += 1
        ml_agrees = (
            (is_risky and ml_phishing_prob >= 0.5)
            or (not is_risky and ml_phishing_prob < 0.5)
        )
        if ml_agrees:
            sources_agreeing += 1

    if sources_active == 0:
        confidence = 0.60       # No signals — moderate confidence it's safe
    elif sources_active == 1:
        confidence = 0.65
    elif sources_agreeing == sources_active:
        confidence = min(0.95, 0.70 + sources_active * 0.08)
    else:
        confidence = 0.55       # Partial disagreement

    return risk_score, round(confidence, 2)


def _determine_verdict(risk_score: int) -> str:
    """Map normalized risk score to verdict label."""
    if risk_score >= THRESHOLD_HIGH_RISK:
        return "HIGH_RISK"
    elif risk_score >= THRESHOLD_SUSPICIOUS:
        return "SUSPICIOUS"
    else:
        return "LOW_RISK"


def _generate_summary(
    verdict: str,
    signals: List[SignalDetail],
    ml_pred: Optional[str],
    language: str,
) -> str:
    """Generate a concise human-readable analysis summary."""
    if verdict == "LOW_RISK" and len(signals) == 0:
        return "No significant phishing indicators were detected in this message."

    parts = []

    if verdict == "HIGH_RISK":
        parts.append("This message shows multiple strong phishing indicators.")
    elif verdict == "SUSPICIOUS":
        parts.append("This message contains patterns commonly associated with phishing attempts.")
    else:
        parts.append("Minor caution flags were detected, but overall risk appears low.")

    if ml_pred == "phishing":
        parts.append("AI classification supports this assessment.")

    high_severity = [s for s in signals if s.severity == "high"]
    if high_severity:
        labels = [s.label for s in high_severity[:3]]  # Limit to 3 for brevity
        parts.append(f"Key concerns: {', '.join(labels)}.")

    return " ".join(parts)


def _generate_actions(signals: List[SignalDetail], verdict: str) -> List[str]:
    """Generate recommended safety actions based on detected signals."""
    actions = []
    seen = set()

    for signal in signals:
        action = ACTIONS.get(signal.id)
        if action and action not in seen:
            actions.append(action)
            seen.add(action)

    if verdict == "HIGH_RISK":
        report_action = "Report this message to the platform where you received it."
        if report_action not in seen:
            actions.append(report_action)

    if not actions:
        actions.append(
            "No immediate action required, but always remain cautious with unsolicited messages."
        )

    return actions


# ── Public API ────────────────────────────────────────────────────────

def fuse_signals(text: str, language: str) -> AnalyzeResponse:
    """
    Main fusion function.

    Combines NLP signals, URL analysis, and ML prediction into a
    structured, explainable risk assessment.

    Args:
        text: The user's input text
        language: Detected language string from language engine

    Returns:
        AnalyzeResponse with all fields populated
    """
    # 1. Rule-based NLP signal detection
    nlp_signal_ids = analyze_nlp_signals(text)

    # 2. URL analysis
    url_signal_ids, url_raw_details = analyze_urls_in_text(text)

    # 3. ML inference (graceful fallback if unavailable)
    ml_prediction, ml_confidence = ml_engine.predict(text)
    ml_phishing_prob = ml_engine.get_phishing_probability(text)
    ml_version = ml_engine.get_model_version()

    # The current ML model is English-dominant. If the text is purely Hindi (Devanagari),
    # the model is out-of-distribution and often gives false negatives. Disable its
    # influence on the fusion score to rely on the multilingual rule-based NLP engine.
    if "Hindi (Devanagari)" in language:
        ml_phishing_prob = None

    # 4. Build structured signal details (deduped)
    all_signal_ids = list(set(nlp_signal_ids + url_signal_ids))
    signal_details = _build_signal_details(all_signal_ids)

    # 5. Build structured URL details
    url_details = _build_url_details(url_raw_details)

    # 6. Hybrid risk fusion
    risk_score, confidence = _compute_hybrid_score(
        nlp_signal_ids, url_signal_ids, ml_phishing_prob
    )

    # 7. Determine verdict
    verdict = _determine_verdict(risk_score)

    # 8. ML analysis metadata
    ml_analysis = MlAnalysis(
        available=ml_engine.is_available(),
        prediction=ml_prediction,
        confidence=ml_confidence,
        model_version=ml_version,
    )

    # 9. Generate summary
    analysis_summary = _generate_summary(verdict, signal_details, ml_prediction, language)

    # 10. Generate recommended actions
    recommended_actions = _generate_actions(signal_details, verdict)

    return AnalyzeResponse(
        verdict=verdict,
        risk_score=risk_score,
        confidence=confidence,
        language=language,
        analysis_summary=analysis_summary,
        signals=signal_details,
        url_analysis=url_details,
        ml_analysis=ml_analysis,
        recommended_actions=recommended_actions,
    )
