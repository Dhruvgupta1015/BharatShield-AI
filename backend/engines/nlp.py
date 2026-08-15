import re
from typing import List

# Define keyword patterns for different risk categories
# Lowercase for normalization

URGENCY_KEYWORDS = [
    r'\bimmediately\b', r'\burgent\b', r'\bnow\b', r'\bact now\b',
    r'तुरंत', r'अभी', r'जल्दी', r'तुरंत करें',
    r'\babhi\b', r'\bturant\b', r'\bjaldi\b'
]

ACCOUNT_THREAT_KEYWORDS = [
    r'account suspended', r'account blocked', r'account disabled', r'account will be blocked',
    r'खाता बंद', r'खाता निलंबित', r'खाता ब्लॉक',
    r'account band', r'account block', r'account suspend',
    # Mixed-language / Code-mixed
    r'account\s*(?:is|abhi)?\s*(?:बंद|blocked|suspend)',
    r'(?:आपका|aapka)\s*account\s*(?:suspend|blocked|band)',
    r'account\s*बंद\s*हो\s*गया'
]

KYC_KEYWORDS = [
    r'\bkyc\b', r'\bverify\b', r'\bverification\b',
    r'अपडेट kyc', r'सत्यापन',
    r'kyc update', r'verify now'
]

CREDENTIAL_KEYWORDS = [
    r'\bpassword\b', r'\bpin\b', r'\botp\b', r'\bpasscode\b', r'\blogin\b', r'\bcredentials\b',
    r'पासवर्ड', r'पिन', r'ओटीपी'
]

FINANCIAL_KEYWORDS = [
    r'\bpayment\b', r'\btransfer\b', r'\brefund\b', r'\bprize\b', r'\breward\b',
    r'पैसे भेजें', r'भुगतान', r'transfer now'
]

SUSPICIOUS_CTA_KEYWORDS = [
    r'click here', r'click the link', r'verify using this link',
    r'link par click', r'link par jaye', r'click karein'
]

def analyze_nlp_signals(text: str) -> List[str]:
    """
    Deterministic baseline NLP engine.
    Returns a list of detected signal categories.
    """
    signals = []
    
    # Normalize text (lowercase)
    normalized_text = text.lower()
    
    # Bug 1 Fix: Punctuation & Obfuscation Evasion
    # Remove dots and commas completely to fix 'u.r.g.e.n.t' -> 'urgent' and 'account,,,blocked' -> 'accountblocked'
    # Wait, 'account,,,blocked' -> if we remove commas completely, it becomes 'accountblocked'.
    # Our regex is r'account blocked', so we need a space.
    # So let's replace repeated punctuation with space, but for dots, maybe remove them?
    # Actually, the simplest for MVP:
    normalized_text = normalized_text.replace('.', '')
    # Replace other non-alphanumeric with space
    normalized_text = re.sub(r'[^\w\s\u0900-\u097F]+', ' ', normalized_text)
    
    # Remove excess whitespace
    normalized_text = " ".join(normalized_text.split())
    
    def check_match(patterns: List[str]) -> bool:
        for pattern in patterns:
            if re.search(pattern, normalized_text):
                return True
        return False

    if check_match(URGENCY_KEYWORDS):
        signals.append("urgency")
        
    if check_match(ACCOUNT_THREAT_KEYWORDS):
        signals.append("account_threat")
        
    if check_match(KYC_KEYWORDS):
        signals.append("kyc_request")
        
    if check_match(CREDENTIAL_KEYWORDS):
        signals.append("credential_request")
        
    if check_match(FINANCIAL_KEYWORDS):
        signals.append("financial_request")
        
    if check_match(SUSPICIOUS_CTA_KEYWORDS):
        signals.append("suspicious_cta")
        
    return signals
