import argparse
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import timesfm

from forecast.utils.data import get_prices, get_prices_from

# --- settings ---
SYMBOL = "BTC"
RESOLUTION = 5  # 5-minute bars
LOOKBACK = 10_000
HORIZON = 288  # 24h * 60min / 5min
PLOT_CONTEXT_BARS = 500
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
PATCH_SIZE = 32
MAX_CONTEXT = math.ceil(LOOKBACK / PATCH_SIZE) * PATCH_SIZE
MAX_HORIZON = math.ceil(HORIZON / 128) * 128


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest TimesFM BTC forecast against actual 5m prices."
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Forecast start date (YYYY-MM-DD), UTC unless --timezone is set.",
    )
    parser.add_argument(
        "--time",
        default="00:00:00",
        help="Forecast start time (HH:MM or HH:MM:SS). Default: 00:00:00.",
    )
    parser.add_argument(
        "--timezone",
        default="UTC",
        help="Timezone for --date and --time (e.g. UTC, Asia/Seoul). Default: UTC.",
    )
    parser.add_argument(
        "--symbol",
        default=SYMBOL,
        help=f"Asset symbol. Default: {SYMBOL}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output image path. Default: forecast/output/<symbol>_forecast_<timestamp>.png",
    )
    return parser.parse_args()


def parse_cutoff_timestamp(date: str, time: str, timezone: str) -> tuple[int, pd.Timestamp]:
    if len(time.split(":")) == 2:
        time = f"{time}:00"
    cutoff = pd.Timestamp(f"{date} {time}", tz=timezone)
    return int(cutoff.timestamp()), cutoff


def output_path(symbol: str, cutoff: pd.Timestamp, output: Path | None) -> Path:
    if output is not None:
        return output
    stamp = cutoff.strftime("%Y%m%d_%H%M%S")
    return OUTPUT_DIR / f"{symbol.lower()}_forecast_{stamp}.png"
def load_model():
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    model.compile(
        timesfm.ForecastConfig(
            max_context=MAX_CONTEXT,
            max_horizon=MAX_HORIZON,
            normalize_inputs=True,
            use_continuous_quantile_head=True,
            force_flip_invariance=True,
            infer_is_positive=True,
            fix_quantile_crossing=True,
        )
    )
    return model


def fetch_backtest_data(symbol: str, cutoff_ts: int):
    history = get_prices_from(symbol, RESOLUTION, cutoff_ts, LOOKBACK)
    future_end = cutoff_ts + HORIZON * RESOLUTION * 60
    actual = get_prices(symbol, RESOLUTION, cutoff_ts, future_end)
    return history, actual

def run_forecast(model, history: pd.DataFrame):
    values = history["Close"].values.astype(np.float32)
    point, quantiles = model.forecast(horizon=HORIZON, inputs=[values])
    return point[0], quantiles[0]


def compute_metrics(forecast: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    errors = forecast - actual
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mape": float(np.mean(np.abs(errors / actual)) * 100),
    }


def plot_backtest(
    symbol: str,
    history: pd.DataFrame,
    cutoff: pd.Timestamp,
    point_forecast: np.ndarray,
    quantile_forecast: np.ndarray,
    actual: pd.DataFrame,
    metrics: dict[str, float],
    output_file: Path,
):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    freq = pd.Timedelta(minutes=RESOLUTION)
    forecast_index = pd.date_range(cutoff, periods=HORIZON + 1, freq=freq)[1:]
    actual_close = actual["Close"].iloc[:HORIZON].values
    actual_index = actual.index[:HORIZON]
    n_actual = min(len(actual_close), HORIZON)
    forecast_index = forecast_index[:n_actual]
    point_forecast = point_forecast[:n_actual]
    quantile_forecast = quantile_forecast[:n_actual]
    actual_close = actual_close[:n_actual]
    actual_index = actual_index[:n_actual]

    q10 = quantile_forecast[:, 1]
    q90 = quantile_forecast[:, 9]

    hist_plot = history.iloc[-PLOT_CONTEXT_BARS:]

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        hist_plot.index,
        hist_plot["Close"],
        color="#2563eb",
        linewidth=1.2,
        label=f"History (last {PLOT_CONTEXT_BARS} bars)",
    )
    ax.plot(
        actual_index,
        actual_close,
        color="#111827",
        linewidth=1.5,
        linestyle="--",
        label="Actual (next 24h)",
    )
    ax.plot(
        forecast_index,
        point_forecast,
        color="#dc2626",
        linewidth=1.5,
        label="TimesFM forecast",
    )
    ax.fill_between(
        forecast_index,
        q10,
        q90,
        color="#dc2626",
        alpha=0.2,
        label="80% interval",
    )
    ax.axvline(cutoff, color="#6b7280", linestyle=":", linewidth=1.2, label="Forecast start")

    ax.set_title(
        f"{symbol} 5m forecast vs actual @ {cutoff.strftime('%Y-%m-%d %H:%M %Z')}\n"
        f"lookback={LOOKBACK}, horizon={HORIZON} ({HORIZON * RESOLUTION / 60:.0f}h) "
        f"| MAE={metrics['mae']:.2f} RMSE={metrics['rmse']:.2f} MAPE={metrics['mape']:.3f}%"
    )
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Close price (USD)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    fig.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved plot to {output_file}")


def main():
    args = parse_args()
    cutoff_ts, cutoff = parse_cutoff_timestamp(args.date, args.time, args.timezone)
    out_file = output_path(args.symbol, cutoff, args.output)

    print(
        f"Backtest {args.symbol} @ {cutoff.isoformat()} | "
        f"resolution={RESOLUTION}m lookback={LOOKBACK} horizon={HORIZON}"
    )

    model = load_model()
    history, actual = fetch_backtest_data(args.symbol, cutoff_ts)
    print(f"History rows: {len(history)}, actual future rows: {len(actual)}")

    point_forecast, quantile_forecast = run_forecast(model, history)

    actual_close = actual["Close"].iloc[:HORIZON].values
    n = min(len(actual_close), HORIZON)
    metrics = compute_metrics(point_forecast[:n], actual_close[:n])
    print(
        f"Metrics — MAE: {metrics['mae']:.2f}, "
        f"RMSE: {metrics['rmse']:.2f}, MAPE: {metrics['mape']:.3f}%"
    )

    plot_backtest(
        args.symbol,
        history,
        cutoff,
        point_forecast,
        quantile_forecast,
        actual,
        metrics,
        out_file,
    )

if __name__ == "__main__":
    main()
