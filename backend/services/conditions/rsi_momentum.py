"""
RSI Momentum condition.
BUY:  EMA(RSI, fast_period) > WMA(RSI, slow_period)
SELL: EMA(RSI, fast_period) < WMA(RSI, slow_period)

This measures the momentum of RSI itself — a fast EMA of RSI
crossing above a slow WMA of RSI indicates building momentum.
"""

from .base import Condition
from ..indicators import calc_rsi, calc_ema, calc_wma
import pandas as pd


class RSIMomentum(Condition):

    @property
    def name(self) -> str:
        return "RSI Momentum (EMA/WMA)"

    def _compute(self, data: pd.DataFrame, config: dict):
        rsi_period = int(config.get("rsi_period", "14"))
        ema_period = int(config.get("ema_of_rsi_period", "3"))
        wma_period = int(config.get("wma_of_rsi_period", "21"))

        rsi = calc_rsi(data["Close"], period=rsi_period)
        ema_rsi = calc_ema(rsi, period=ema_period)
        wma_rsi = calc_wma(rsi, period=wma_period)

        return ema_rsi, wma_rsi

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        ema_rsi, wma_rsi = self._compute(data, config)

        if ema_rsi.empty or wma_rsi.empty:
            return False
        if pd.isna(ema_rsi.iloc[-1]) or pd.isna(wma_rsi.iloc[-1]):
            return False

        return float(ema_rsi.iloc[-1]) > float(wma_rsi.iloc[-1])

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        ema_rsi, wma_rsi = self._compute(data, config)

        if ema_rsi.empty or wma_rsi.empty:
            return False
        if pd.isna(ema_rsi.iloc[-1]) or pd.isna(wma_rsi.iloc[-1]):
            return False

        return float(ema_rsi.iloc[-1]) < float(wma_rsi.iloc[-1])

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        ema_rsi, wma_rsi = self._compute(data, config)
        return {
            "ema_rsi": float(ema_rsi.iloc[-1]) if not ema_rsi.empty and not pd.isna(ema_rsi.iloc[-1]) else None,
            "wma_rsi": float(wma_rsi.iloc[-1]) if not wma_rsi.empty and not pd.isna(wma_rsi.iloc[-1]) else None,
        }
