"""
Run profiles for every (asset, time_increment).

Edit this file after CRPS eval:
  - Rolling windows: ``ROLLING_WINDOWS[(asset, interval)]``
  - Other knobs: ``PROFILE_OVERRIDES[(asset, interval)]``

Each entry is a full ``RunSpec`` (not a merge layer).
"""

from __future__ import annotations

from forecast.config.profiles.factory import (
    make_feature_spec,
    make_run_spec,
    resolve_rolling_windows,
)
from forecast.config.symbols import SUPPORTED_ASSETS
from forecast.config.types import (
    TIME_INCREMENT_1MIN,
    TIME_INCREMENT_5MIN,
    RollingWindows,
    RunKey,
    RunSpec,
)

# --- Rolling windows (bars) per (asset, time_increment) ----------------------
# Edit one cell to tune rolling_short / rolling_long independently.
# Keys not listed here use ``ROLLING_DEFAULTS`` for that interval.

ROLLING_DEFAULTS: dict[int, RollingWindows] = {
    TIME_INCREMENT_5MIN: RollingWindows(rolling_short=96, rolling_long=288),
    TIME_INCREMENT_1MIN: RollingWindows(rolling_short=96, rolling_long=288),
}

# High-frequency (1h forecast, 1min bars) — per-asset rolling windows
ROLLING_WINDOWS: dict[RunKey, RollingWindows] = {
    ("BTC", TIME_INCREMENT_1MIN): RollingWindows(rolling_short=116, rolling_long=348),
    ("ETH", TIME_INCREMENT_1MIN): RollingWindows(rolling_short=72, rolling_long=216),
    ("SOL", TIME_INCREMENT_1MIN): RollingWindows(rolling_short=45, rolling_long=120),
    ("XAU", TIME_INCREMENT_1MIN): RollingWindows(rolling_short=45, rolling_long=120),
    ("HYPE", TIME_INCREMENT_1MIN): RollingWindows(rolling_short=45, rolling_long=120),
}

# --- Interval templates -------------------------------------------------------

_TEMPLATE_5MIN = make_run_spec(
    TIME_INCREMENT_5MIN,
    forecast_kwargs={"quantile_real_cap_k": 2.0},
    path_sampling={"sigma_scale": 1.0, "ar_rho": 0.0, "t_df": 5},
)

_TEMPLATE_1MIN = make_run_spec(
    TIME_INCREMENT_1MIN,
    forecast_kwargs={"quantile_real_cap_k": 2.0},
    path_sampling={"sigma_scale": 1.0, "ar_rho": 0.0, "t_df": 5},
)


def _clone_template(template: RunSpec, time_increment: int) -> RunSpec:
    return make_run_spec(
        time_increment,
        window=template.window,
        lookback_bars=template.lookback_bars,
        forecast_kwargs=dict(template.forecast_kwargs),
        path_sampling=dict(template.path_sampling),
        features=make_feature_spec(
            builder=template.features.builder,
            rolling_short=template.features.rolling_short,
            rolling_long=template.features.rolling_long,
            columns=template.features.columns,
        ),
    )


def _apply_rolling(spec: RunSpec, rolling: RollingWindows) -> RunSpec:
    return make_run_spec(
        spec.time_increment,
        window=spec.window,
        lookback_bars=spec.lookback_bars,
        forecast_kwargs=dict(spec.forecast_kwargs),
        path_sampling=dict(spec.path_sampling),
        features=make_feature_spec(
            builder=spec.features.builder,
            rolling_short=rolling.rolling_short,
            rolling_long=rolling.rolling_long,
            columns=spec.features.columns,
        ),
    )


# Optional: only list keys that differ from the interval template.
PROFILE_OVERRIDES: dict[RunKey, RunSpec] = {
    ("XAU", TIME_INCREMENT_5MIN): make_run_spec(
        TIME_INCREMENT_5MIN,
        path_sampling={"sigma_scale": 0.45, "ar_rho": 0.0, "t_df": 3},
        forecast_kwargs={"quantile_real_cap_k": 2.0},
    ),
    ("XAU", TIME_INCREMENT_1MIN): make_run_spec(
        TIME_INCREMENT_1MIN,
        path_sampling={"sigma_scale": 1.0, "ar_rho": 0.3, "t_df": 12},
        forecast_kwargs={"quantile_real_cap_k": 2.0},
    ),
}


def _build_run_profiles() -> dict[RunKey, RunSpec]:
    profiles: dict[RunKey, RunSpec] = {}
    for asset in SUPPORTED_ASSETS:
        for time_increment, template in (
            (TIME_INCREMENT_5MIN, _TEMPLATE_5MIN),
            (TIME_INCREMENT_1MIN, _TEMPLATE_1MIN),
        ):
            rolling = resolve_rolling_windows(
                asset,
                time_increment,
                overrides=ROLLING_WINDOWS,
                defaults=ROLLING_DEFAULTS,
            )
            profiles[(asset, time_increment)] = _apply_rolling(
                _clone_template(template, time_increment),
                rolling,
            )

    for key, override in PROFILE_OVERRIDES.items():
        base = profiles[key]
        rolling = resolve_rolling_windows(
            key[0],
            key[1],
            overrides=ROLLING_WINDOWS,
            defaults=ROLLING_DEFAULTS,
        )
        profiles[key] = make_run_spec(
            override.time_increment,
            window=override.window,
            lookback_bars=override.lookback_bars,
            forecast_kwargs=dict(override.forecast_kwargs),
            path_sampling=dict(override.path_sampling),
            features=make_feature_spec(
                builder=base.features.builder,
                rolling_short=rolling.rolling_short,
                rolling_long=rolling.rolling_long,
                columns=base.features.columns,
            ),
        )
    return profiles


RUN_PROFILES: dict[RunKey, RunSpec] = _build_run_profiles()
