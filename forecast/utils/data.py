import time



import pandas as pd

import requests



from forecast.config.symbols import asset_symbols, base_url, alternate_url


class FetchHttpError(RuntimeError):
    pass

class NoPriceDataError(RuntimeError):
    pass

def get_prices(symbol: str, resolution: int, start: int, end: int) -> pd.DataFrame:

    pyth_symbol = asset_symbols[symbol.upper()]
    url = f"{base_url}?symbol={pyth_symbol}&resolution={resolution}&from={start}&to={end}"
    response = requests.get(url, timeout=60)

    if response.status_code != 200: 
        # Try the alternate URL
        url = f"{alternate_url}?symbol={pyth_symbol}&resolution={resolution}&from={start}&to={end}"
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            raise FetchHttpError(
                f"Failed to fetch {symbol} (resolution={resolution}m): HTTP {response.status_code}"
            )

    data = response.json()

    if not isinstance(data, dict) or "t" not in data:
        raise NoPriceDataError(f"No price data for {symbol} (resolution={resolution}m)")

    df = pd.DataFrame(data)
    df.drop(columns=["s", "v"], inplace=True, errors="ignore")
    df["timestamp"] = pd.to_datetime(df["t"], unit="s")
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    df.rename(
        columns={"o": "Open", "h": "High", "l": "Low", "c": "Close"},
        inplace=True,
    )
    return df

def get_prices_from(symbol: str, resolution: int, end_ts: int, lookback: int) -> pd.DataFrame:

    start = end_ts - resolution * lookback * 60
    return get_prices(symbol, resolution, start, end_ts)

def get_prices_from_now(symbol: str, resolution: int, lookback: int) -> pd.DataFrame:
    return get_prices_from(symbol, resolution, int(time.time()), lookback)

