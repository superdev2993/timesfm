"""Lookup resolved run profiles by (asset, time_increment)."""

from __future__ import annotations

from forecast.config.profiles.matrix import RUN_PROFILES
from forecast.config.symbols import asset_symbols
from forecast.config.types import RunKey, RunSpec, SUPPORTED_INTERVALS


def _validate_time_increment(time_increment: int) -> int:
    if time_increment < 60 or time_increment % 60 != 0:
        raise ValueError(
            "time_increment must be a positive multiple of 60 (seconds)"
        )
    return time_increment


def get_run_spec(asset: str, time_increment: int) -> RunSpec:
    """
    Resolved configuration for (asset, time_increment).

    Profiles live in ``config/profiles/matrix.py`` (``RUN_PROFILES``).
    """
    asset = asset.upper()
    time_increment = _validate_time_increment(time_increment)
    if asset not in asset_symbols:
        raise KeyError(
            f"Unknown asset {asset!r}. Supported: {sorted(asset_symbols)}"
        )
    key: RunKey = (asset, time_increment)
    try:
        return RUN_PROFILES[key]
    except KeyError as exc:
        raise KeyError(
            f"No run profile for {asset!r} @ {time_increment}s. "
            f"Known intervals: {sorted({k[1] for k in RUN_PROFILES})}. "
            f"Add RUN_PROFILES[{key!r}] in config/profiles/matrix.py"
        ) from exc


def list_profile_keys() -> list[RunKey]:
    return sorted(RUN_PROFILES.keys())


def list_assets() -> list[str]:
    return sorted({k[0] for k in RUN_PROFILES})


def list_intervals() -> list[int]:
    return sorted({k[1] for k in RUN_PROFILES})


def assert_profiles_complete() -> None:
    """Raise if any supported asset × interval pair is missing."""
    missing = []
    for asset in asset_symbols:
        for interval in SUPPORTED_INTERVALS:
            if (asset, interval) not in RUN_PROFILES:
                missing.append((asset, interval))
    if missing:
        raise RuntimeError(f"Missing RUN_PROFILES entries: {missing}")
