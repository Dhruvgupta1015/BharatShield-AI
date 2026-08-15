
from ml.datasets.validation import validate_dataset
from ml.datasets.schema import DatasetRow
from ml.models.baseline_adapter import BaselineAdapter
from ml.evaluation.metrics import ModelEvaluator

def test_validation_empty_dataset():
    report = validate_dataset([])
    assert report["total_rows"] == 0
    assert report["valid_rows"] == 0

def test_validation_missing_fields():
    data = [
        {"text": "Hello world"} # Missing label, language, etc.
    ]
    report = validate_dataset(data)
    assert report["valid_rows"] == 0
    assert len(report["errors"]) == 1

def test_validation_valid_row():
    data = [
        {
            "sample_id": "test-001",
            "text": "Your account is blocked",
            "label": "phishing",
            "language": "english",
            "script_type": "latin",
            "source_name": "manual_test",
            "source_type": "manual",
            "split": "train"
        }
    ]
    report = validate_dataset(data)
    assert report["valid_rows"] == 1
    assert len(report["errors"]) == 0

def test_validation_duplicate_id():
    data = [
        {
            "sample_id": "test-001",
            "text": "Your account is blocked",
            "label": "phishing",
            "language": "english",
            "script_type": "latin",
            "source_name": "manual_test",
            "source_type": "manual",
            "split": "train"
        },
        {
            "sample_id": "test-001",
            "text": "Your account is closed",
            "label": "phishing",
            "language": "english",
            "script_type": "latin",
            "source_name": "manual_test",
            "source_type": "manual",
            "split": "train"
        }
    ]
    report = validate_dataset(data)
    assert any("Duplicate sample_id" in err for err in report["errors"])

def test_baseline_adapter():
    adapter = BaselineAdapter()
    texts = ["Your account is blocked. Verify immediately.", "Hello friend"]
    preds = adapter.predict(texts)
    
    assert len(preds) == 2
    assert preds[0] == 1 # "account blocked" is Suspicious/High Risk -> 1
    assert preds[1] == 0 # Benign -> 0

def test_evaluator():
    adapter = BaselineAdapter()
    evaluator = ModelEvaluator(adapter)
    
    texts = ["Your account is blocked. Verify immediately.", "Hello friend"]
    y_true = [1, 0]
    
    metrics = evaluator.evaluate(texts, y_true)
    assert metrics["sample_count"] == 2
    assert metrics["confusion_matrix"]["tp"] == 1
    assert metrics["confusion_matrix"]["tn"] == 1
    assert metrics["precision"] == 1.0
