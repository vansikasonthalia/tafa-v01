"""
Data fetcher abstraction.
V1 supports Yahoo Finance only. Designed for easy addition of Kite data source later.
"""

import yfinance as yf
import pandas as pd
from abc import ABC, abstractmethod


class DataFetcher(ABC):
    """Base class for all data sources."""

    @abstractmethod
    def fetch_ohlcv(self, ticker: str, period: str, interval: str) -> pd.DataFrame:
        """
        Fetch OHLCV data for a ticker.

        Args:
            ticker: Stock ticker symbol (e.g., "RELIANCE.NS" for NSE)
            period: Lookback period (e.g., "2y" for 2 years)
            interval: Bar interval (e.g., "1wk" for weekly)

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        ...


class YahooFetcher(DataFetcher):
    """Fetches data from Yahoo Finance (free, no API key needed)."""

    def fetch_ohlcv(self, ticker: str, period: str = "2y", interval: str = "1wk") -> pd.DataFrame:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                return pd.DataFrame()

            # Standardize column names
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.dropna(inplace=True)
            return df

        except Exception as e:
            print(f"[YahooFetcher] Error fetching {ticker}: {e}")
            return pd.DataFrame()


# --- Factory ---

_FETCHERS = {
    "yahoo": YahooFetcher,
    # "kite": KiteFetcher,  # Future: add Kite data source here
}


def get_fetcher(source: str = "yahoo") -> DataFetcher:
    """Get a data fetcher instance by name."""
    cls = _FETCHERS.get(source)
    if cls is None:
        raise ValueError(f"Unknown data source: {source}. Available: {list(_FETCHERS.keys())}")
    return cls()
