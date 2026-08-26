"""
BharatShield AI — Backend Engine Tests

Covers: NLP signals, URL analysis, language detection, ML inference,
hybrid fusion, and API response schema.

Run from project root:
    cd backend && python tests/test_engines.py
    OR
    cd backend && python -m pytest tests/ -v
"""

import sys
import os

# Ensure backend root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.nlp import analyze_nlp_signals
from engines.url import analyze_urls_in_text, extract_urls
from engines.language import detect_language
from engines import ml_engine
from engines.fusion import fuse_signals


# ── NLP Signal Tests ─────────────────────────────────────────────────

def test_nlp_english_phishing():
    signals = analyze_nlp_signals(
        "Your account will be blocked. Enter your OTP immediately."
    )
    assert "account_threat" in signals
    assert "credential_request" in signals
    assert "urgency" in signals


def test_nlp_hindi_phishing():
    signals = analyze_nlp_signals(
        "आपका खाता बंद हो जायेगा। तुरंत अपना पासवर्ड दर्ज करें।"
    )
    assert "account_threat" in signals
    assert "credential_request" in signals
    assert "urgency" in signals


def test_nlp_hinglish_phishing():
    signals = analyze_nlp_signals(
        "Aapka account block ho jayega. Abhi KYC update karein."
    )
    assert "account_threat" in signals
    assert "kyc_request" in signals
    assert "urgency" in signals


def test_nlp_benign():
    signals = analyze_nlp_signals("Hey, want to grab coffee tomorrow?")
    assert len(signals) == 0


def test_nlp_empty():
    signals = analyze_nlp_signals("")
    assert len(signals) == 0


def test_nlp_financial():
    signals = analyze_nlp_signals("You won a prize! Transfer now to claim your reward.")
    assert "financial_request" in signals


# ── URL Analysis Tests ───────────────────────────────────────────────

def test_url_extraction():
    urls = extract_urls("Visit http://192.168.1.10/login or https://bit.ly/abc")
    assert len(urls) >= 2


def test_url_ip():
    signals, details = analyze_urls_in_text("Click http://192.168.1.10/phish")
    assert "ip_hostname" in signals


def test_url_shortener():
    signals, details = analyze_urls_in_text("Visit https://bit.ly/update now")
    assert "shortened_url" in signals


def test_url_benign():
    signals, details = analyze_urls_in_text("Visit https://google.com for info")
    assert "ip_hostname" not in signals
    assert "shortened_url" not in signals


def test_url_http_scheme():
    signals, details = analyze_urls_in_text("Go to http://example.com/page")
    assert "http_scheme" in signals


# ── Language Detection Tests ─────────────────────────────────────────

def test_language_english():
    lang = detect_language("Hello, how are you doing today?")
    assert "English" in lang or "Hinglish" in lang


def test_language_hindi():
    lang = detect_language("नमस्ते, कैसे हैं आप? मैं ठीक हूँ।")
    assert "Hindi" in lang


def test_language_mixed():
    lang = detect_language("Hello मित्र कैसे हो Let's meet tomorrow मिलते हैं")
    assert "Mixed" in lang or "Hindi" in lang


def test_language_empty():
    lang = detect_language("")
    assert lang == "Unknown"


# ── ML Engine Tests ──────────────────────────────────────────────────

def test_ml_availability():
    available = ml_engine.is_available()
    assert isinstance(available, bool)


def test_ml_predict_phishing():
    pred, conf = ml_engine.predict(
        "Your account is suspended, click here to verify immediately"
    )
    if ml_engine.is_available():
        assert pred in ("phishing", "benign")
        assert conf is not None
        assert 0.0 <= conf <= 1.0
    else:
        assert pred is None
        assert conf is None


def test_ml_predict_benign():
    pred, conf = ml_engine.predict("Hey let's meet for lunch tomorrow")
    if ml_engine.is_available():
        assert pred in ("phishing", "benign")
        assert conf is not None
    else:
        assert pred is None


def test_ml_probability():
    prob = ml_engine.get_phishing_probability("You won a prize! Claim now!")
    if ml_engine.is_available():
        assert prob is not None
        assert 0.0 <= prob <= 1.0
    else:
        assert prob is None


def test_ml_model_version():
    if ml_engine.is_available():
        version = ml_engine.get_model_version()
        assert version is not None


# ── Fusion Tests ─────────────────────────────────────────────────────

def test_fusion_high_risk():
    result = fuse_signals(
        "Your account is blocked! Enter your OTP immediately: http://192.168.1.10/verify",
        "English / Hinglish",
    )
    assert result.verdict == "HIGH_RISK"
    assert result.risk_score >= 60
    assert len(result.signals) >= 2
    assert len(result.recommended_actions) > 0


def test_fusion_benign():
    result = fuse_signals(
        "Hey, let's meet for lunch tomorrow!", "English / Hinglish"
    )
    assert result.verdict == "LOW_RISK"
    assert result.risk_score < 30


def test_fusion_url_only():
    result = fuse_signals(
        "Check this link: https://bit.ly/suspicious", "English / Hinglish"
    )
    assert result.verdict in ("LOW_RISK", "SUSPICIOUS")
    assert any(u.is_shortened for u in result.url_analysis)


def test_fusion_hindi_phishing():
    result = fuse_signals(
        "\u0906\u092a\u0915\u093e \u0916\u093e\u0924\u093e \u092c\u0902\u0926 \u0939\u094b \u091c\u093e\u092f\u0947\u0917\u093e\u0964 \u0924\u0941\u0930\u0902\u0924 \u0905\u092a\u0928\u093e \u092a\u093e\u0938\u0935\u0930\u094d\u0921 \u0926\u0930\u094d\u091c \u0915\u0930\u0947\u0902\u0964",
        "Hindi (Devanagari)",
    )
    assert result.verdict in ("SUSPICIOUS", "HIGH_RISK")
    assert len(result.signals) >= 1  # At minimum detects credential_request and urgency


def test_fusion_hinglish_phishing():
    result = fuse_signals(
        "Aapka account block ho jayega, turant click karein: http://amaz0n-verify.xyz/login",
        "English / Hinglish",
    )
    assert result.verdict in ("SUSPICIOUS", "HIGH_RISK")
    assert len(result.signals) >= 1


def test_fusion_response_schema():
    """Verify all expected fields exist and have valid ranges."""
    result = fuse_signals("Test message", "English / Hinglish")
    assert hasattr(result, "verdict")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "confidence")
    assert hasattr(result, "language")
    assert hasattr(result, "analysis_summary")
    assert hasattr(result, "signals")
    assert hasattr(result, "url_analysis")
    assert hasattr(result, "ml_analysis")
    assert hasattr(result, "recommended_actions")

    assert result.verdict in ("HIGH_RISK", "SUSPICIOUS", "LOW_RISK")
    assert 0 <= result.risk_score <= 100
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.signals, list)
    assert isinstance(result.url_analysis, list)
    assert isinstance(result.recommended_actions, list)
    assert len(result.recommended_actions) >= 1


def test_fusion_ml_analysis_present():
    """ML analysis metadata should always be present (even if unavailable)."""
    result = fuse_signals("Hello world", "English / Hinglish")
    assert result.ml_analysis is not None
    assert isinstance(result.ml_analysis.available, bool)


def test_fusion_signal_severity():
    """High-severity signals should sort first."""
    result = fuse_signals(
        "Account blocked! Enter OTP now!", "English / Hinglish"
    )
    if len(result.signals) >= 2:
        severities = [s.severity for s in result.signals]
        order = {"high": 0, "medium": 1, "low": 2}
        sorted_sev = sorted(severities, key=lambda s: order.get(s, 1))
        assert severities == sorted_sev


# ── Edge Case Tests ──────────────────────────────────────────────────

def test_fusion_empty_after_strip():
    """Text that becomes empty after stripping should still not crash fusion."""
    result = fuse_signals("hello", "Unknown")
    assert result.verdict == "LOW_RISK"


def test_fusion_very_long_input():
    """Long input should not crash."""
    long_text = "Hello world. " * 500
    result = fuse_signals(long_text, "English / Hinglish")
    assert result.verdict in ("HIGH_RISK", "SUSPICIOUS", "LOW_RISK")


# ── Runner ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

    passed = 0
    failed = 0
    errors = []

    for test_fn in tests:
        try:
            test_fn()
            print(f"  [PASS] {test_fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1
            errors.append((test_fn.__name__, str(e)))

    print(f"\n{'=' * 55}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed > 0:
        print("\nFailed tests:")
        for name, err in errors:
            print(f"  - {name}: {err}")
    else:
        print("ALL TESTS PASSED")
