import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ml')))
from datasets.validation import validate_dataset, check_leakage
from datasets.schema import DatasetRow

def run_validation():
    path = "ml/data/processed/dataset_v1.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    report = validate_dataset(data)
    print("Validation Report:")
    print(f"Total Rows: {report['total_rows']}")
    print(f"Valid Rows: {report['valid_rows']}")
    print(f"Duplicates Detected: {report['duplicates']}")
    if report["errors"]:
        print(f"Errors found: {len(report['errors'])}")
        for err in report["errors"][:5]:
            print(f" - {err}")
            
    # Check Leakage
    train_rows = [DatasetRow(**r) for r in data if r["split"] == "train"]
    test_rows = [DatasetRow(**r) for r in data if r["split"] == "test"]
    val_rows = [DatasetRow(**r) for r in data if r["split"] == "val"]
    
    leakage_test = check_leakage(train_rows, test_rows)
    leakage_val = check_leakage(train_rows, val_rows)
    print(f"Leakage Train -> Test: {leakage_test}")
    print(f"Leakage Train -> Val: {leakage_val}")

if __name__ == "__main__":
    run_validation()
