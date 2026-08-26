"""
Module: Machine Learning Water & Flood Classification
Owner: Agent 6 (GEE / ML Lead)
Project: Dam Break Inundation Modelling (SIH 26161)
Location: src/gee/ml_classifier.py

Trains and deploys ML classifiers (Random Forest / Gradient Boosting)
on Sentinel-1 SAR and Sentinel-2 multi-spectral features for water extraction.
"""

import os
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

DEFAULT_FEATURES: List[str] = [
    "VV",
    "VH",
    "VV_minus_VH",
    "VV_plus_VH",
    "SAR_Ratio",
    "NDPI",
    "MNDWI",
    "NDWI",
    "NDVI",
]


class WaterClassifier:
    """
    Supervised Machine Learning classifier for SAR and Optical water/flood detection.
    """

    def __init__(
        self,
        model_type: str = "rf",
        n_estimators: int = 100,
        max_depth: Optional[int] = 10,
        random_state: int = 42,
        features: Optional[List[str]] = None,
    ):
        self.model_type = model_type
        self.features = list(features) if features is not None else list(DEFAULT_FEATURES)
        self.random_state = random_state

        if model_type == "rf":
            self.model: Any = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
            )
        elif model_type == "gb":
            self.model = GradientBoostingClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
            )
        else:
            raise ValueError(f"Unsupported model_type '{model_type}'. Choose 'rf' or 'gb'.")

        self.is_trained: bool = False

    def _prepare_input_data(
        self, data: Union[pd.DataFrame, Dict[str, Any], np.ndarray]
    ) -> pd.DataFrame:
        """
        Converts input data into a standardized DataFrame containing required feature columns.
        """
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, np.ndarray):
            if data.ndim == 1:
                df = pd.DataFrame([data], columns=self.features[: data.shape[0]])
            elif data.ndim == 2:
                cols = (
                    self.features[: data.shape[1]]
                    if data.shape[1] <= len(self.features)
                    else None
                )
                df = pd.DataFrame(data, columns=cols)
            else:
                raise ValueError(f"Expected 1D or 2D numpy array, got shape {data.shape}")
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

        # Reindex to guarantee all feature columns exist, filling missing with 0
        return df.reindex(columns=self.features, fill_value=0.0).fillna(0.0)

    def train(
        self,
        data: pd.DataFrame,
        target_column: str = "label",
        test_size: float = 0.2,
    ) -> Dict[str, float]:
        """
        Trains the classifier and returns performance evaluation metrics.
        """
        if data.empty:
            raise ValueError("Training dataset cannot be empty.")

        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in training data.")

        available_features = [f for f in self.features if f in data.columns]
        if not available_features:
            raise ValueError(f"None of the required features {self.features} found in data.")

        self.features = available_features
        X = data[self.features].fillna(0.0)
        y = data[target_column]

        stratify_target = y if len(np.unique(y)) > 1 else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=stratify_target,
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        }
        return metrics

    def predict(self, data: Union[pd.DataFrame, Dict[str, Any], np.ndarray]) -> np.ndarray:
        """
        Predicts binary water/non-water classification (1=Water/Flood, 0=Land).
        """
        if not self.is_trained:
            raise RuntimeError(
                "Model is not trained yet. Call .train() or load a pretrained model."
            )

        X = self._prepare_input_data(data)
        return self.model.predict(X)

    def predict_proba(self, data: Union[pd.DataFrame, Dict[str, Any], np.ndarray]) -> np.ndarray:
        """
        Returns prediction probabilities for each class.
        """
        if not self.is_trained:
            raise RuntimeError("Model is not trained yet.")

        X = self._prepare_input_data(data)
        return self.model.predict_proba(X)

    def save(self, filepath: str) -> None:
        """Saves model to a joblib file, ensuring directory exists."""
        dirname = os.path.dirname(os.path.abspath(filepath))
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        joblib.dump(
            {
                "model": self.model,
                "features": self.features,
                "model_type": self.model_type,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: str) -> "WaterClassifier":
        """Loads a pretrained model from a joblib file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file '{filepath}' not found.")

        data = joblib.load(filepath)
        instance = cls(
            model_type=data.get("model_type", "rf"),
            features=data.get("features"),
        )
        instance.model = data["model"]
        instance.is_trained = True
        return instance
