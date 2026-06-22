# Toto configuration

One **run profile** per `(asset, time_increment)` — no merge layers.

## Layout

```
config/
  symbols.py           # asset_symbols, Pyth tickers
  types.py             # FeatureSpec, RunSpec, TIME_INCREMENT_*
  registry.py          # get_run_spec(asset, time_increment)
  builders/
    standard.py        # default OHLCV features
    registry.py        # register_feature_builder(name, fn)
  profiles/
    factory.py         # make_run_spec, make_feature_spec
    matrix.py          # RUN_PROFILES — edit here
```

## Edit settings (CRPS tuning)

**`profiles/matrix.py`**

1. **Rolling windows** — per `(asset, time_increment)`:

```python
ROLLING_WINDOWS[("BTC", TIME_INCREMENT_5MIN)] = RollingWindows(
    rolling_short=96,
    rolling_long=288,
)
```

Unlisted pairs use `ROLLING_DEFAULTS` for that interval (300s or 60s).

2. **Other knobs** — `path_sampling`, `forecast_kwargs`, etc. via `PROFILE_OVERRIDES`.
3. **Interval templates** — `_TEMPLATE_5MIN` / `_TEMPLATE_1MIN` for shared non-rolling defaults.

## Custom `build_features`

1. Implement `def my_builder(df, spec: FeatureSpec) -> pd.DataFrame: ...`
2. Register: `register_feature_builder("my_builder", my_builder)`
3. Point profile at it: `features=make_feature_spec(builder="my_builder", ...)`

Rolling windows in `FeatureSpec` apply only to the **`standard`** builder.

## API

```python
from synth.toto.config import get_run_spec, TIME_INCREMENT_5MIN

run = get_run_spec("BTC", TIME_INCREMENT_5MIN)
run.window
run.features.rolling_short
run.forecast_kwargs
run.path_sampling
```

`gen_simulations(asset, time_increment=300, ...)` uses this automatically.

## Intervals

| Constant | Seconds | Use |
|----------|---------|-----|
| `TIME_INCREMENT_5MIN` | 300 | Validator low-frequency |
| `TIME_INCREMENT_1MIN` | 60 | Validator high-frequency |

Rolling windows are in **bars** (not wall-clock seconds).
