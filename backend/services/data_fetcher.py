"""
Data fetcher abstraction.
V1 supports Yahoo Finance via bulk download. Designed for easy addition of Kite data source later.
"""

import time
import requests
import yfinance as yf
import pandas as pd
from abc import ABC, abstractmethod

# Create a shared session to reuse connections and spoof User-Agent
_yf_session = requests.Session()
_yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})


class DataFetcher(ABC):
    """Base class for all data sources."""

    @abstractmethod
    def fetch_ohlcv(self, ticker: str, period: str, interval: str) -> pd.DataFrame:
        """
        Fetch OHLCV data for a single ticker.

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        ...

    def fetch_bulk(self, tickers: list[str], period: str, interval: str) -> dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple tickers at once.
        Default implementation calls fetch_ohlcv in a loop.
        """
        result = {}
        for ticker in tickers:
            df = self.fetch_ohlcv(ticker, period, interval)
            if not df.empty:
                result[ticker] = df
        return result


def _flatten_columns(df: pd.DataFrame, ticker: str = None) -> pd.DataFrame:
    """
    Handle yfinance v1.7+ multi-level columns.
    Converts (Price, Ticker) multi-index to flat column names.
    """
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance v1.7 returns columns like (Close, RELIANCE.NS)
        # We want just: Close, Open, High, Low, Volume
        df.columns = df.columns.get_level_values(0)

    # Ensure we have standard OHLCV columns
    required = ["Open", "High", "Low", "Close", "Volume"]
    available = [c for c in required if c in df.columns]
    if not available:
        return pd.DataFrame()

    df = df[available].copy()
    df.dropna(subset=["Close"], inplace=True)
    return df


class YahooFetcher(DataFetcher):
    """
    Fetches data from Yahoo Finance using yfinance v1.7+.
    Uses curl_cffi internally for better bot-detection bypass.
    """

    BATCH_SIZE = 50

    def fetch_ohlcv(self, ticker: str, period: str = "2y", interval: str = "1wk") -> pd.DataFrame:
        """Fetch data for a single ticker."""
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True,
                threads=False,
                session=_yf_session,
            )

            if df.empty:
                return pd.DataFrame()

            return _flatten_columns(df, ticker)

        except Exception as e:
            print(f"[YahooFetcher] Error fetching {ticker}: {e}")
            return pd.DataFrame()

    def fetch_bulk(self, tickers: list[str], period: str = "2y", interval: str = "1wk") -> dict[str, pd.DataFrame]:
        """
        Fetch data for ALL tickers using yf.download() in batches.
        """
        all_data = {}
        total = len(tickers)

        for i in range(0, total, self.BATCH_SIZE):
            batch = tickers[i : i + self.BATCH_SIZE]
            batch_num = (i // self.BATCH_SIZE) + 1
            total_batches = (total + self.BATCH_SIZE - 1) // self.BATCH_SIZE
            print(f"[YahooFetcher] Downloading batch {batch_num}/{total_batches} ({len(batch)} tickers)...")

            try:
                raw = yf.download(
                    batch,
                    period=period,
                    interval=interval,
                    group_by="ticker",
                    progress=False,
                    auto_adjust=True,
                    threads=True,
                    session=_yf_session,
                )

                if raw.empty:
                    print(f"[YahooFetcher] Batch {batch_num} returned empty data.")
                    continue

                if len(batch) == 1:
                    ticker = batch[0]
                    df = _flatten_columns(raw.copy(), ticker)
                    if not df.empty:
                        all_data[ticker] = df
                else:
                    for ticker in batch:
                        try:
                            # In multi-ticker mode, top-level columns are tickers
                            if ticker in raw.columns.get_level_values(0):
                                df = raw[ticker].copy()
                            elif isinstance(raw.columns, pd.MultiIndex) and ticker in raw.columns.get_level_values(1):
                                # Alternative: columns might be (Price, Ticker)
                                df = raw.xs(ticker, level=1, axis=1).copy()
                            else:
                                continue

                            df = _flatten_columns(df, ticker)
                            if not df.empty:
                                all_data[ticker] = df
                        except (KeyError, TypeError) as e:
                            print(f"[YahooFetcher] Could not extract data for {ticker}: {e}")
                            continue

            except Exception as e:
                print(f"[YahooFetcher] Batch {batch_num} failed: {e}")
                continue

            # Brief pause between batches
            if i + self.BATCH_SIZE < total:
                time.sleep(2)

        print(f"[YahooFetcher] Successfully fetched data for {len(all_data)}/{total} tickers.")
        return all_data


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
