"""Base class for all Gold Price Prediction models (ML & DL)."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class BaseGoldModel(ABC):
    """Abstract Base Class for Gold Forecasting Models enforcing contract."""

    def __init__(self, name: str, version: str = "v1.0", window_size: int = 30):
        self.name = name
        self.version = version
        self.window_size = window_size
        self.is_fitted = False
        self.feature_columns: List[str] = []
        self.metrics: Dict[str, float] = {}

    @abstractmethod
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> "BaseGoldModel":
        """Fit model strictly on chronological training data."""
        pass

    @abstractmethod
    def predict(
        self, X: pd.DataFrame, horizon: int = 1
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Generate prediction with bounds.
        Returns:
            (predicted_prices, lower_bounds, upper_bounds)
        """
        pass

    @abstractmethod
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Compute MAE, MSE, RMSE, MAPE (%), R2 and Directional Accuracy."""
        pass

    @abstractmethod
    def save(self, artifact_dir: str) -> Dict[str, Any]:
        """Persist model, scaler and manifest metadata with SHA-256."""
        pass

    @classmethod
    @abstractmethod
    def load(cls, artifact_dir: str) -> "BaseGoldModel":
        """Load artifact and verify SHA-256 hash."""
        pass
