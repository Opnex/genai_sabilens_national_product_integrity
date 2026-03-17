import pickle
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class TextAnomalyClassifier:

    def __init__(self):
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.feature_order = None

    def train(self, X: list[dict], y: list[int]):
        self.feature_order = list(X[0].keys())

        X_matrix = np.array([
            [row[f] for f in self.feature_order]
            for row in X
        ])

        X_scaled = self.scaler.fit_transform(X_matrix)
        self.model.fit(X_scaled, y)

    def predict_proba(self, features: dict):
        if self.feature_order is None:
            raise ValueError("Model not trained or loaded")

        X = np.array([[features[f] for f in self.feature_order]])
        X_scaled = self.scaler.transform(X)

        return float(self.model.predict_proba(X_scaled)[0][1])

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump({
            "model": self.model,
            "scaler": self.scaler,
            "feature_order": self.feature_order
            }, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_order = data["feature_order"]