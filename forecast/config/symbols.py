"""Pyth symbols and API base URL (no run-profile imports)."""

base_url = "https://pyth.dourolabs.app/v1/fixed_rate@200ms/history" 
alternate_url = "http://localhost:8080/v1/shims/tradingview/history"

asset_symbols: dict[str, str] = {
    "BTC": "Crypto.BTC/USD",
    "ETH": "Crypto.ETH/USD",
    "XAU": "Metal.XAU/USD",
    "SOL": "Crypto.SOL/USD",
    "SPYX": "Crypto.SPYX/USD",
    "NVDAX": "Crypto.NVDAX/USD",
    "TSLAX": "Crypto.TSLAX/USD",
    "AAPLX": "Crypto.AAPLX/USD",
    "GOOGLX": "Crypto.GOOGLX/USD",
    "XRP": "Crypto.XRP/USD",
    "HYPE": "Crypto.HYPE/USD",
    "WTIOIL": "Commodities.WTIM6/USD",
}

SUPPORTED_ASSETS: tuple[str, ...] = tuple(sorted(asset_symbols))
