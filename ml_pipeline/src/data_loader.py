"""
Data Loading & Anti-Leakage Chronological Splitting for Gold Prices.
"""
from typing import Tuple
import pandas as pd


def chronological_split(
    df: pd.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split time series into Train, Validation, and Test strictly chronologically.
    CẤM shuffle để tránh rò rỉ dữ liệu tương lai.
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy().reset_index(drop=True)
    val_df = df.iloc[train_end:val_end].copy().reset_index(drop=True)
    test_df = df.iloc[val_end:].copy().reset_index(drop=True)
    return train_df, val_df, test_df
