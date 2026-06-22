"""Configuration types for (asset, time_increment) run profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Validator bar spacing (seconds)
TIME_INCREMENT_5MIN = 300
TIME_INCREMENT_1MIN = 60

SUPPORTED_INTERVALS: tuple[int, ...] = (TIME_INCREMENT_5MIN, TIME_INCREMENT_1MIN)

# Model tensor column order (names are historical; windows are in bars)
DEFAULT_FEATURE_COLUMNS: tuple[str, ...] = (
    "log_return",
    "log_close",
    "range",
    "rv_parkinson_96",
    "vol_96",
    "vol_ratio",
    "mom_96",
    "lag_1",
    "lag_96",
)


@dataclass(frozen=True)
class RollingWindows:
    """Rolling bar counts for the standard feature builder."""

    rolling_short: int
    rolling_long: int


@dataclass(frozen=True)
class FeatureSpec:
    """
    How to build features for one (asset, interval) profile.

    - ``builder``: registered name in ``config.builders`` (default ``"standard"``).
    - ``rolling_short`` / ``rolling_long``: bar counts for the standard builder.
    - ``columns``: model input order (must exist in builder output + ``Close``).
    """

    builder: str = "standard"
    rolling_short: int = 96
    rolling_long: int = 288
    columns: tuple[str, ...] = DEFAULT_FEATURE_COLUMNS


@dataclass(frozen=True)
class RunSpec:
    """Full pipeline settings for one (asset, time_increment)."""

    time_increment: int
    window: int = 1024
    lookback_bars: int | None = None
    forecast_kwargs: dict[str, Any] = field(
        default_factory=lambda: {"quantile_real_cap_k": 2.0}
    )
    path_sampling: dict[str, Any] = field(
        default_factory=lambda: {"sigma_scale": 1.0, "ar_rho": 0.0, "t_df": 5}
    )
    features: FeatureSpec = field(default_factory=FeatureSpec)


RunKey = tuple[str, int]
