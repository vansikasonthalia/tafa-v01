"""
Technical indicator calculations: RSI, EMA, WMA.
Pure functions operating on pandas Series.
"""

import pandas as pd
import numpy as np


def calc_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average.
    Uses pandas ewm with span = period.
    """
    return series.ewm(span=period, adjust=False).mean()


def calc_wma(series: pd.Series, period: int) -> pd.Series:
    """
    Weighted Moving Average.
    More recent values get linearly higher weights.
    """
    weights = np.arange(1, period + 1, dtype=float)

    def _wma(window):
        return np.dot(window, weights) / weights.sum()

    return series.rolling(window=period).apply(_wma, raw=True)


def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index using Wilder's smoothing method.
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # First average: simple mean over the first `period` values
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi
