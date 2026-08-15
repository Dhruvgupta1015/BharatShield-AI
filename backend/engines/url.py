import re
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse

SHORTENER_DOMAINS = [
    'bit.ly', 'tinyurl.com', 't.co', 'is.gd', 'goo.gl', 'shorturl.at', 'ow.ly'
]

def extract_urls(text: str) -> List[str]:
    """
    Extracts URLs from text.
    """
    # Regex to match URLs with or without http/https, including domains and IP addresses
    url_pattern = re.compile(
        r'(?:http[s]?://|www\.)?(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})(?::\d+)?(?:/[a-zA-Z0-9-._~:/?#\[\]@!$&\'()*+,;=%]*)?'
    )
    return url_pattern.findall(text)

def analyze_url_signals(url: str) -> Tuple[List[str], Dict[str, Any]]:
    """
    Deterministic baseline URL engine.
    Returns (signals, url_details)
    """
    signals = []
    details = {
        "url": url,
        "is_shortened": False,
        "scheme": None,
        "hostname": None,
        "is_ip": False,
        "length": len(url)
    }

    try:
        # urlparse needs a scheme to parse netloc properly
        parse_url = url if "://" in url else f"http://{url}"
        parsed = urlparse(parse_url)
        
        # Original scheme if any
        details["scheme"] = urlparse(url).scheme if "://" in url else None
        details["hostname"] = parsed.netloc

        if details["scheme"] == 'http':
            # Minor cautionary signal, not proof of risk
            signals.append("http_scheme")

        if parsed.netloc:
            # Check for shorteners
            if any(shortener in parsed.netloc.lower() for shortener in SHORTENER_DOMAINS):
                signals.append("shortened_url")
                details["is_shortened"] = True

            # Check for IP address in hostname (basic regex)
            ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$')
            if ip_pattern.match(parsed.netloc):
                signals.append("ip_hostname")
                details["is_ip"] = True

            # Suspicious URL structure (e.g., lots of subdomains)
            # Ignoring generic localhosts/IPs for subdomain count
            parts = parsed.netloc.split('.')
            if len(parts) > 4 and not details["is_ip"]:
                signals.append("suspicious_url_structure")

    except Exception:
        # If parsing fails, it might be heavily obfuscated or malformed
        pass

    return signals, details

def analyze_urls_in_text(text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Finds and analyzes all URLs in the text.
    Returns combined signals and details for all URLs.
    """
    urls = extract_urls(text)
    all_signals = set()
    all_details = []

    for url in urls:
        signals, details = analyze_url_signals(url)
        all_signals.update(signals)
        all_details.append(details)

    return list(all_signals), all_details
