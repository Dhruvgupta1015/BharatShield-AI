import os
import urllib.request
import zipfile
import hashlib
import json
import re
import random
import sys

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from engines.language import detect_language

DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
ZIP_PATH = "ml/data/raw/smsspamcollection.zip"
EXTRACT_DIR = "ml/data/raw"
OUTPUT_PATH = "ml/data/processed/dataset_v1.json"

def download_and_extract():
    # Paths are relative to the root project dir (BharatShield-AI)
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    if not os.path.exists(ZIP_PATH):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, ZIP_PATH)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

def generate_sample_id(source_name, index, normalized_text):
    data = f"{source_name}_{index}_{normalized_text}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def normalize_text(text):
    return " ".join(text.lower().split())

def has_pii(text):
    # Detect basic emails
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        return True
    # Detect likely 10+ digit phone numbers, avoiding obvious short codes
    # This is a basic filter for MVP purposes
    if re.search(r'\b(?:\+\d{1,3}[- ]?)?\d{10,12}\b', text):
        return True
    return False

def build_dataset():
    download_and_extract()
    
    raw_file = os.path.join(EXTRACT_DIR, "SMSSpamCollection")
    
    dataset = []
    stats = {
        "total_raw": 0,
        "pii_filtered": 0,
        "exact_duplicates_removed": 0,
        "near_duplicates_removed": 0,
        "final_count": 0,
        "label_counts": {"phishing": 0, "benign": 0},
        "original_labels": {"spam": 0, "ham": 0},
        "language_counts": {"english": 0, "hindi": 0, "hinglish": 0, "mixed_other": 0, "unknown": 0},
        "script_counts": {"latin": 0, "devanagari": 0, "mixed": 0, "unknown": 0},
        "split_counts": {"train": 0, "val": 0, "test": 0}
    }
    
    seen_texts = set()
    parsed_rows = []
    
    # Pass 1: Parse and Filter PII
    with open(raw_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip(): continue
            stats["total_raw"] += 1
            parts = line.split("\t", 1)
            if len(parts) != 2: continue
            
            orig_label, text = parts[0].strip(), parts[1].strip()
            
            if has_pii(text):
                stats["pii_filtered"] += 1
                continue
                
            norm_text = normalize_text(text)
            
            if norm_text in seen_texts:
                stats["exact_duplicates_removed"] += 1
                continue
            seen_texts.add(norm_text)
            
            # Map label (Proxy for MVP)
            stats["original_labels"][orig_label] += 1
            mapped_label = "phishing" if orig_label == "spam" else "benign"
            
            # Language/Script Detection
            lang_detect = detect_language(text).lower()
            lang = "english"
            script = "latin"
            
            if "hindi" in lang_detect and "devanagari" in lang_detect:
                lang = "hindi"
                script = "devanagari"
            elif "hinglish" in lang_detect or "mixed" in lang_detect:
                # Based on detect_language returns
                if "english" in lang_detect and "hinglish" in lang_detect:
                    lang = "english" # Usually English / Hinglish
                    script = "latin"
                else:
                    lang = "mixed_other"
                    script = "mixed"
            elif "unknown" in lang_detect:
                lang = "mixed_other"
                script = "mixed"
                
            sample_id = generate_sample_id("uci_sms_spam", idx, norm_text)
            
            row = {
                "sample_id": sample_id,
                "text": text,
                "label": mapped_label,
                "language": lang,
                "script_type": script,
                "source_name": "uci_sms_spam",
                "source_type": "public",
                "original_label": orig_label # Preserve original label for provenance
            }
            parsed_rows.append(row)

    # Pass 2: Train/Val/Test Split deterministically
    # Sort to ensure stable split across runs
    parsed_rows.sort(key=lambda x: x["sample_id"])
    random.seed(42)
    random.shuffle(parsed_rows)
    
    total_valid = len(parsed_rows)
    train_end = int(total_valid * 0.70)
    val_end = train_end + int(total_valid * 0.15)
    
    for i, row in enumerate(parsed_rows):
        if i < train_end:
            row["split"] = "train"
        elif i < val_end:
            row["split"] = "val"
        else:
            row["split"] = "test"
            
        dataset.append(row)
        
        # Track stats
        stats["final_count"] += 1
        stats["label_counts"][row["label"]] += 1
        lang_key = row["language"] if row["language"] in stats["language_counts"] else "unknown"
        stats["language_counts"][lang_key] += 1
        script_key = row["script_type"] if row["script_type"] in stats["script_counts"] else "unknown"
        stats["script_counts"][script_key] += 1
        stats["split_counts"][row["split"]] += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)
        
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    build_dataset()
