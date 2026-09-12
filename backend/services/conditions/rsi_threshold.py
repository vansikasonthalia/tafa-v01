"""
RSI Threshold condition.
BUY: RSI > threshold
SELL: RSI < threshold
"""

from .base import Condition
from ..indicators import calc_rsi
import pandas as pd


class RSIThreshold(Condition):

    @property
    def name(self) -> str:
        return "RSI Threshold"

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        rsi_period = int(config.get("rsi_period", "14"))
        threshold = float(config.get("rsi_threshold", "50"))

        rsi = calc_rsi(data["Close"], period=rsi_period)
        if rsi.empty or pd.isna(rsi.iloc[-1]):
            return False

        return float(rsi.iloc[-1]) > threshold

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        rsi_period = int(config.get("rsi_period", "14"))
        threshold = float(config.get("rsi_threshold", "50"))

        rsi = calc_rsi(data["Close"], period=rsi_period)
        if rsi.empty or pd.isna(rsi.iloc[-1]):
            return False

        return float(rsi.iloc[-1]) < threshold

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        rsi_period = int(config.get("rsi_period", "14"))
        rsi = calc_rsi(data["Close"], period=rsi_period)
        return {"rsi": float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else None}
