from typing import List, Dict, Any
from ml.datasets.schema import DatasetRow

def validate_dataset(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates a raw list of dictionaries against the DatasetRow schema.
    Detects empty rows, missing labels, unsupported tags, and missing provenance.
    """
    report = {
        "total_rows": len(rows),
        "valid_rows": 0,
        "errors": [],
        "duplicates": 0
    }
    
    seen_texts = set()
    seen_ids = set()
    
    for i, row in enumerate(rows):
        try:
            # Validate schema
            validated_row = DatasetRow(**row)
            
            # Check duplicate sample_id
            if validated_row.sample_id in seen_ids:
                report["errors"].append(f"Row {i}: Duplicate sample_id '{validated_row.sample_id}' detected.")
            else:
                seen_ids.add(validated_row.sample_id)
            
            # Check duplicate text
            text_normalized = " ".join(validated_row.text.lower().split())
            if text_normalized in seen_texts:
                report["errors"].append(f"Row {i}: Duplicate text detected.")
                report["duplicates"] += 1
            else:
                seen_texts.add(text_normalized)
                
            if validated_row.sample_id in seen_ids and text_normalized in seen_texts:
                 # It's fully valid only if it has unique ID and text (technically text duplicate is just a warning, but we'll count as valid row if schema passes)
                 pass
                 
            report["valid_rows"] += 1
                
        except Exception as e:
            report["errors"].append(f"Row {i}: Validation failed - {str(e)}")
            
    return report

def check_leakage(train_rows: List[DatasetRow], test_rows: List[DatasetRow]) -> bool:
    """
    Checks if any text from the test set is present in the training set.
    """
    train_texts = set(" ".join(r.text.lower().split()) for r in train_rows)
    for row in test_rows:
        text_normalized = " ".join(row.text.lower().split())
        if text_normalized in train_texts:
            return True # Leakage detected
    return False
