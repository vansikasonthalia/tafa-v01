"""
Validation condition: RSI Momentum.
Buy when EMA(RSI) > WMA(RSI) — fast RSI momentum above slow.
Sell when EMA(RSI) < WMA(RSI).
"""

import pandas as pd
from .base import Condition
from ..indicators import calc_rsi, calc_ema, calc_wma


class RSIMomentum(Condition):

    @property
    def name(self) -> str:
        return "RSI Momentum (EMA/WMA)"

    @property
    def category(self) -> str:
        return "validation"

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        rsi_period = int(config.get("rsi_period", 14))
        ema_period = int(config.get("ema_of_rsi_period", 3))
        wma_period = int(config.get("wma_of_rsi_period", 21))

        rsi = calc_rsi(data["Close"], rsi_period)
        ema_rsi = calc_ema(rsi, ema_period)
        wma_rsi = calc_wma(rsi, wma_period)

        return ema_rsi.iloc[-1] > wma_rsi.iloc[-1]

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        rsi_period = int(config.get("rsi_period", 14))
        ema_period = int(config.get("ema_of_rsi_period", 3))
        wma_period = int(config.get("wma_of_rsi_period", 21))

        rsi = calc_rsi(data["Close"], rsi_period)
        ema_rsi = calc_ema(rsi, ema_period)
        wma_rsi = calc_wma(rsi, wma_period)

        return ema_rsi.iloc[-1] < wma_rsi.iloc[-1]

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        rsi_period = int(config.get("rsi_period", 14))
        ema_period = int(config.get("ema_of_rsi_period", 3))
        wma_period = int(config.get("wma_of_rsi_period", 21))

        rsi = calc_rsi(data["Close"], rsi_period)
        ema_rsi = calc_ema(rsi, ema_period)
        wma_rsi = calc_wma(rsi, wma_period)

        return {
            "ema_rsi": float(ema_rsi.iloc[-1]),
            "wma_rsi": float(wma_rsi.iloc[-1]),
        }
