from typing import List, Dict, Any, Tuple
from engines.nlp import analyze_nlp_signals
from engines.url import analyze_urls_in_text

SIGNAL_SCORES = {
    # NLP Signals
    "urgency": 1,
    "account_threat": 2,
    "kyc_request": 2,
    "credential_request": 3,
    "financial_request": 2,
    "suspicious_cta": 1,
    
    # URL Signals
    "shortened_url": 2,
    "ip_hostname": 3,
    "suspicious_url_structure": 1,
    "http_scheme": 1, # Small cautionary contribution
}

EXPLANATIONS = {
    "urgency": "The message uses urgent language that pressures the user to act quickly.",
    "account_threat": "The message claims that an account may be suspended or blocked.",
    "kyc_request": "The message requests KYC or account verification.",
    "credential_request": "The message asks for credentials such as a password, PIN or OTP.",
    "financial_request": "The message involves a financial transaction, reward, or payment request.",
    "suspicious_cta": "The message contains a call-to-action urging the user to click a link.",
    "shortened_url": "The link uses a URL shortener, which hides the destination URL and raises the risk.",
    "ip_hostname": "The link uses an IP address instead of a standard domain name, which is a strong risk signal.",
    "suspicious_url_structure": "The link has a complex or unusual structure often used to obfuscate destinations.",
    "http_scheme": "The link uses HTTP instead of HTTPS, meaning the connection is not encrypted."
}

ACTIONS = {
    "credential_request": "Do not provide passwords, PINs or OTPs.",
    "kyc_request": "Verify account status through the official app or official website.",
    "account_threat": "Verify account status through the official app or official website.",
    "financial_request": "Do not send money or accept unexpected prizes.",
    "shortened_url": "Do not open the link until the destination is independently verified.",
    "ip_hostname": "Do not open the link until the destination is independently verified.",
    "suspicious_cta": "Do not follow suspicious links.",
}

def determine_risk_level(score: int) -> str:
    if score >= 6:
        return "High Risk"
    elif score >= 3:
        return "Suspicious"
    else:
        return "Lower Risk"

def fuse_signals(text: str) -> Tuple[str, int, List[str], str, List[str], Dict[str, Any]]:
    nlp_signals = analyze_nlp_signals(text)
    url_signals, url_details = analyze_urls_in_text(text)
    
    # Combine unique signals
    all_signals = list(set(nlp_signals + url_signals))
    
    # Calculate score
    score = 0
    for signal in all_signals:
        score += SIGNAL_SCORES.get(signal, 0)
        
    risk_level = determine_risk_level(score)
    
    # Generate explanation
    if not all_signals:
        explanation = "No specific phishing risk signals were detected in this message."
    else:
        explanation_parts = [EXPLANATIONS.get(sig) for sig in all_signals if sig in EXPLANATIONS]
        explanation = " ".join(explanation_parts)
        
    # Generate recommended actions
    actions_set = set()
    for signal in all_signals:
        if signal in ACTIONS:
            actions_set.add(ACTIONS[signal])
            
    if risk_level == "High Risk":
        actions_set.add("Do not provide sensitive information or follow the suspicious link.")
    elif risk_level == "Lower Risk" and not actions_set:
         actions_set.add("No immediate action required, but always remain cautious.")
         
    recommended_actions = list(actions_set)
    
    url_analysis_data = {"urls_found": len(url_details), "details": url_details} if url_details else None
    
    return risk_level, score, all_signals, explanation, recommended_actions, url_analysis_data
