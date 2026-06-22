from __future__ import annotations

import numpy as np
import pandas as pd

from forecast.config import build_features as _build_features
from forecast.config import get_run_spec
from forecast.config.types import DEFAULT_FEATURE_COLUMNS, FeatureSpec

FEATURE_COLUMNS = list(DEFAULT_FEATURE_COLUMNS)


def build_features(
    df: pd.DataFrame,
    spec: FeatureSpec | None = None,
    asset: str | None = None,
    time_increment: int | None = None,
) -> pd.DataFrame:
    """
    Build model features using the profile's ``FeatureSpec``.

    Pass ``(asset, time_increment)`` or an explicit ``spec``.
    """
    if spec is None:
        if asset is None or time_increment is None:
            raise ValueError(
                "Provide spec or both asset and time_increment"
            )
        spec = get_run_spec(asset, time_increment).features
    return _build_features(df, spec)


def get_context(
    df: pd.DataFrame,
    asset: str,
    time_increment: int,
    window: int | None = None,
) -> tuple[np.ndarray, float]:
    """Last ``window`` bars of features and latest close for path anchoring."""
    run = get_run_spec(asset, time_increment)
    window = window if window is not None else run.window
    feat = build_features(df, spec=run.features)
    cols = list(run.features.columns)
    missing = [c for c in cols if c not in feat.columns]
    if missing:
        raise ValueError(f"Feature columns missing after build: {missing}")
    if len(feat) < window:
        raise ValueError(f"Need at least {window} feature rows, got {len(feat)}")
    data = feat[cols].values.T
    train = data[:, -window:]
    last_price = float(feat["Close"].iloc[-1])
    return train, last_price
