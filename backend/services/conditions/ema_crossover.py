"""
Driver condition: EMA Crossover.
Buy when price crosses above the fast EMA.
Sell when price crosses below the fast EMA.
"""

import pandas as pd
from .base import Condition
from ..indicators import calc_ema


class EMACrossover(Condition):

    @property
    def name(self) -> str:
        return "Price EMA Crossover"

    @property
    def category(self) -> str:
        return "driver"

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("fast_ema_period", 11))
        ema = calc_ema(data["Close"], period)

        if len(data) < 2:
            return False

        prev_close = data["Close"].iloc[-2]
        curr_close = data["Close"].iloc[-1]
        prev_ema = ema.iloc[-2]
        curr_ema = ema.iloc[-1]

        # Price crossed ABOVE the fast EMA
        return prev_close <= prev_ema and curr_close > curr_ema

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("fast_ema_period", 11))
        ema = calc_ema(data["Close"], period)

        if len(data) < 2:
            return False

        prev_close = data["Close"].iloc[-2]
        curr_close = data["Close"].iloc[-1]
        prev_ema = ema.iloc[-2]
        curr_ema = ema.iloc[-1]

        # Price crossed BELOW the fast EMA
        return prev_close >= prev_ema and curr_close < curr_ema

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        fast_period = int(config.get("fast_ema_period", 11))
        slow_period = int(config.get("slow_ema_period", 50))
        fast_ema = calc_ema(data["Close"], fast_period)
        slow_ema = calc_ema(data["Close"], slow_period)

        return {
            "price": float(data["Close"].iloc[-1]),
            "ema_value": float(fast_ema.iloc[-1]),
            "slow_ema_value": float(slow_ema.iloc[-1]),
        }
