"""
Toto configuration: one ``RunSpec`` per (asset, time_increment).

Primary API:
  ``get_run_spec(asset, time_increment)`` → window, features, forecast, path sampling

Feature building:
  ``config.builders.build_features(df, spec.features)``
  ``register_feature_builder(name, fn)`` for custom pipelines
"""

from forecast.config.builders import (
    build_features,
    register_feature_builder,
)
from forecast.config.profiles.factory import make_feature_spec, make_run_spec
from forecast.config.profiles.matrix import (
    PROFILE_OVERRIDES,
    ROLLING_DEFAULTS,
    ROLLING_WINDOWS,
    RUN_PROFILES,
)
from forecast.config.registry import (
    assert_profiles_complete,
    get_run_spec,
    list_assets,
    list_intervals,
    list_profile_keys,
)
from forecast.config.symbols import SUPPORTED_ASSETS, asset_symbols, base_url
from forecast.config.types import (
    DEFAULT_FEATURE_COLUMNS,
    TIME_INCREMENT_1MIN,
    TIME_INCREMENT_5MIN,
    FeatureSpec,
    RollingWindows,
    RunKey,
    RunSpec,
    SUPPORTED_INTERVALS,
)

# Backward-compatible aliases
get_run_config = get_run_spec
AssetRunConfig = RunSpec
FeatureParams = FeatureSpec


def get_asset_config(asset: str) -> RunSpec:
    return get_run_spec(asset, TIME_INCREMENT_5MIN)


__all__ = [
    "AssetRunConfig",
    "DEFAULT_FEATURE_COLUMNS",
    "FeatureParams",
    "FeatureSpec",
    "PROFILE_OVERRIDES",
    "ROLLING_DEFAULTS",
    "ROLLING_WINDOWS",
    "RollingWindows",
    "RUN_PROFILES",
    "RunKey",
    "RunSpec",
    "SUPPORTED_ASSETS",
    "SUPPORTED_INTERVALS",
    "TIME_INCREMENT_1MIN",
    "TIME_INCREMENT_5MIN",
    "assert_profiles_complete",
    "asset_symbols",
    "base_url",
    "build_features",
    "get_asset_config",
    "get_run_config",
    "get_run_spec",
    "list_assets",
    "list_intervals",
    "list_profile_keys",
    "make_feature_spec",
    "make_run_spec",
    "register_feature_builder",
]
