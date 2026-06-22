"""Factory helpers for ``RunSpec`` / ``FeatureSpec`` profiles."""

from __future__ import annotations

from typing import Any

from forecast.config.types import (
    DEFAULT_FEATURE_COLUMNS,
    FeatureSpec,
    RollingWindows,
    RunKey,
    RunSpec,
)


def resolve_rolling_windows(
    asset: str,
    time_increment: int,
    *,
    overrides: dict[RunKey, RollingWindows],
    defaults: dict[int, RollingWindows],
) -> RollingWindows:
    """Per-(asset, interval) rolling windows, falling back to interval defaults."""
    key: RunKey = (asset.upper(), time_increment)
    if key in overrides:
        return overrides[key]
    if time_increment in defaults:
        return defaults[time_increment]
    raise KeyError(
        f"No rolling windows for {asset!r} @ {time_increment}s. "
        f"Add ROLLING_WINDOWS[{key!r}] or a default for this interval."
    )


def make_feature_spec(
    *,
    builder: str = "standard",
    rolling_short: int = 96,
    rolling_long: int = 288,
    columns: tuple[str, ...] = DEFAULT_FEATURE_COLUMNS,
) -> FeatureSpec:
    return FeatureSpec(
        builder=builder,
        rolling_short=rolling_short,
        rolling_long=rolling_long,
        columns=columns,
    )


def make_run_spec(
    time_increment: int,
    *,
    window: int = 1024,
    lookback_bars: int | None = None,
    forecast_kwargs: dict[str, Any] | None = None,
    path_sampling: dict[str, Any] | None = None,
    features: FeatureSpec | None = None,
) -> RunSpec:
    return RunSpec(
        time_increment=time_increment,
        window=window,
        lookback_bars=lookback_bars,
        forecast_kwargs=dict(
            forecast_kwargs if forecast_kwargs is not None else {"quantile_real_cap_k": 2.0}
        ),
        path_sampling=dict(
            path_sampling
            if path_sampling is not None
            else {"sigma_scale": 1.0, "ar_rho": 0.0, "t_df": 5}
        ),
        features=features if features is not None else FeatureSpec(),
    )
