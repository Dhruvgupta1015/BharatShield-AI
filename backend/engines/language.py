import re

def detect_language(text: str) -> str:
    """
    Lightweight language/script detector for MVP UX.
    Distinguishes English/Latin dominant, Hindi/Devanagari dominant, 
    Hinglish/mixed, or Unknown.
    """
    if not text.strip():
        return "Unknown"

    # Count Devanagari characters (Unicode range: \u0900-\u097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    
    # Count Latin alphabetic characters
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    total_alpha = devanagari_chars + latin_chars
    
    if total_alpha == 0:
        return "Unknown"

    devanagari_ratio = devanagari_chars / total_alpha
    latin_ratio = latin_chars / total_alpha

    if devanagari_ratio > 0.8:
        return "Hindi (Devanagari)"
    elif latin_ratio > 0.8:
        # It could be pure English or Hinglish. We'll refine this later 
        # or treat it as English/Hinglish in NLP checks.
        return "English / Hinglish"
    else:
        return "Mixed (Hindi + English)"
