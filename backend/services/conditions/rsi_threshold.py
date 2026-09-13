"""
Validation condition: RSI Threshold.
Buy when RSI > threshold (default 50).
Sell when RSI < threshold.
"""

import pandas as pd
from .base import Condition
from ..indicators import calc_rsi


class RSIThreshold(Condition):

    @property
    def name(self) -> str:
        return "RSI Threshold"

    @property
    def category(self) -> str:
        return "validation"

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("rsi_period", 14))
        threshold = float(config.get("rsi_threshold", 50))
        rsi = calc_rsi(data["Close"], period)
        return rsi.iloc[-1] > threshold

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("rsi_period", 14))
        threshold = float(config.get("rsi_threshold", 50))
        rsi = calc_rsi(data["Close"], period)
        return rsi.iloc[-1] < threshold

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        period = int(config.get("rsi_period", 14))
        rsi = calc_rsi(data["Close"], period)
        return {"rsi": float(rsi.iloc[-1])}
