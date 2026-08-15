from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from ml.models.base import BaseDetector

class TfidfLogisticRegression(BaseDetector):
    def __init__(self, analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True, C=1.0, class_weight=None):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                analyzer=analyzer,
                ngram_range=ngram_range,
                min_df=min_df,
                sublinear_tf=sublinear_tf
            )),
            ('clf', LogisticRegression(
                C=C,
                class_weight=class_weight,
                random_state=42,
                max_iter=1000
            ))
        ])

    def fit(self, texts: List[str], y: List[int]):
        self.pipeline.fit(texts, y)

    def predict(self, texts: List[str]) -> List[int]:
        return self.pipeline.predict(texts).tolist()

    def predict_proba(self, texts: List[str]) -> List[float]:
        # Return probability of the positive class (class 1)
        probs = self.pipeline.predict_proba(texts)
        # Class 1 is usually at index 1, but we should be careful. 
        # Since we train with [0, 1], it will be at index 1.
        return probs[:, 1].tolist()
