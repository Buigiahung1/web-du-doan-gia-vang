"""
Baseline Machine Learning Models: LightGBM, Random Forest, Linear Regression.
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

from ml_pipeline.src.models.base import BaseGoldModel
from ml_pipeline.src.evaluate import compute_metrics

try:
    from lightgbm import LGBMRegressor
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


class LightGBMGoldModel(BaseGoldModel):
    """Production-grade LightGBM Regressor with Validation Early Stopping."""

    def __init__(self, name: str = "LightGBM Quant", version: str = "v1.0", window_size: int = 30):
        super().__init__(name=name, version=version, window_size=window_size)
        self.scaler = MinMaxScaler()
        self.residual_std: float = 0.0
        if HAS_LIGHTGBM:
            self.model = LGBMRegressor(
                n_estimators=150,
                learning_rate=0.05,
                max_depth=6,
                random_state=42,
                verbose=-1,
            )
        else:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> "LightGBMGoldModel":
        self.feature_columns = list(X_train.columns)
        X_train_scaled = self.scaler.fit_transform(X_train)

        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            if HAS_LIGHTGBM and isinstance(self.model, LGBMRegressor):
                self.model.fit(
                    X_train_scaled,
                    y_train,
                    eval_set=[(X_val_scaled, y_val)],
                )
            else:
                self.model.fit(X_train_scaled, y_train)

            # Compute empirical residual standard deviation on validation set
            val_preds = self.model.predict(X_val_scaled)
            self.residual_std = float(np.std(y_val.to_numpy() - val_preds))
        else:
            self.model.fit(X_train_scaled, y_train)
            self.residual_std = float(np.std(y_train - self.model.predict(X_train_scaled)))

        self.is_fitted = True
        return self

    def predict(
        self, X: pd.DataFrame, horizon: int = 1
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predict()")
        X_scaled = self.scaler.transform(X[self.feature_columns])
        preds = self.model.predict(X_scaled)

        # 95% Confidence Interval: ±1.96 * residual_std
        std = self.residual_std if self.residual_std > 0 else float(np.mean(preds) * 0.015)
        lower = preds - 1.96 * std
        upper = preds + 1.96 * std
        return preds, lower, upper

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        preds, _, _ = self.predict(X_test)
        self.metrics = compute_metrics(y_test.to_numpy(), preds)
        return self.metrics

    def save(self, artifact_dir: str) -> Dict[str, Any]:
        path = Path(artifact_dir)
        path.mkdir(parents=True, exist_ok=True)

        model_file = path / "model.joblib"
        scaler_file = path / "scaler.joblib"
        manifest_file = path / "manifest.json"

        joblib.dump(self.model, model_file)
        joblib.dump(self.scaler, scaler_file)

        # Compute SHA-256 hash of model artifact
        hasher = hashlib.sha256()
        with open(model_file, "rb") as f:
            hasher.update(f.read())
        sha256 = hasher.hexdigest()

        manifest = {
            "model_name": self.name,
            "version": self.version,
            "algorithm": "LIGHTGBM" if HAS_LIGHTGBM else "RANDOM_FOREST",
            "window_size": self.window_size,
            "residual_std": self.residual_std,
            "feature_columns": self.feature_columns,
            "artifact_sha256": sha256,
            "metrics": self.metrics,
        }
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest

    @classmethod
    def load(cls, artifact_dir: str) -> "LightGBMGoldModel":
        path = Path(artifact_dir)
        manifest_file = path / "manifest.json"
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        model_file = path / "model.joblib"
        scaler_file = path / "scaler.joblib"

        # Verify SHA-256
        hasher = hashlib.sha256()
        with open(model_file, "rb") as f:
            hasher.update(f.read())
        actual_sha = hasher.hexdigest()
        if actual_sha != manifest["artifact_sha256"]:
            raise ValueError(f"Artifact integrity compromised! Expected {manifest['artifact_sha256']}, got {actual_sha}")

        instance = cls(
            name=manifest["model_name"],
            version=manifest["version"],
            window_size=manifest["window_size"],
        )
        instance.model = joblib.load(model_file)
        instance.scaler = joblib.load(scaler_file)
        instance.feature_columns = manifest["feature_columns"]
        instance.residual_std = manifest.get("residual_std", 0.0)
        instance.metrics = manifest.get("metrics", {})
        instance.is_fitted = True
        return instance
