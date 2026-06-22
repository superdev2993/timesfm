"""Named feature builders — register custom fns per asset/interval profile."""

from __future__ import annotations

from typing import Callable

import pandas as pd

from forecast.config.builders.standard import build_standard_features
from forecast.config.types import FeatureSpec

FeatureBuilderFn = Callable[[pd.DataFrame, FeatureSpec], pd.DataFrame]

_BUILDERS: dict[str, FeatureBuilderFn] = {
    "standard": build_standard_features,
}


def register_feature_builder(name: str, fn: FeatureBuilderFn) -> None:
    if not name or name == "standard":
        raise ValueError("Use a non-empty name other than 'standard' for custom builders")
    _BUILDERS[name] = fn


def get_feature_builder(name: str) -> FeatureBuilderFn:
    try:
        return _BUILDERS[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown feature builder {name!r}. Registered: {sorted(_BUILDERS)}"
        ) from exc


def build_features(df: pd.DataFrame, spec: FeatureSpec) -> pd.DataFrame:
    return get_feature_builder(spec.builder)(df, spec)
