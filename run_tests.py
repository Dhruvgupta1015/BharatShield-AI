from ml.tests.test_validation import (
    test_validation_empty_dataset,
    test_validation_missing_fields,
    test_validation_valid_row,
    test_validation_duplicate_id,
    test_baseline_adapter,
    test_evaluator
)

try:
    test_validation_empty_dataset()
    print("1. Empty rows caught.")
    
    test_validation_missing_fields()
    print("2. Missing labels caught. 3. Missing provenance caught. 4. Invalid split caught.")
    
    test_validation_valid_row()
    print("Validation for valid row passed.")
    
    test_validation_duplicate_id()
    print("5. Duplicate sample_ids caught.")
    
    test_baseline_adapter()
    print("7. Baseline adapter loaded.")
    
    test_evaluator()
    print("8. Evaluator handles prediction-only models without requiring probabilities.")
    
    print("All tests passed.")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
