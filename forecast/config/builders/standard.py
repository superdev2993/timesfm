"""Default OHLCV → feature DataFrame builder."""

from __future__ import annotations

import numpy as np
import pandas as pd

from forecast.config.types import FeatureSpec


def build_standard_features(df: pd.DataFrame, spec: FeatureSpec) -> pd.DataFrame:
    rs = spec.rolling_short
    rl = spec.rolling_long

    out = df.copy()
    out["log_return"] = np.log(out["Close"] / out["Close"].shift(1))
    out["log_close"] = np.log(out["Close"])
    out["range"] = (out["High"] - out["Low"]) / out["Close"]

    hl_log = np.log(out["High"] / out["Low"])
    out["rv_parkinson_96"] = np.sqrt(
        hl_log.pow(2).rolling(rs).mean() / (4 * np.log(2))
    )
    out["vol_96"] = out["log_return"].rolling(rs).std()
    vol_long = out["log_return"].rolling(rl).std()
    out["vol_ratio"] = out["vol_96"] / vol_long.replace(0, np.nan)
    out["mom_96"] = out["log_return"].rolling(rs).sum()
    out["lag_1"] = out["log_return"].shift(1)
    out["lag_96"] = out["log_return"].shift(rs)

    return out.dropna()
