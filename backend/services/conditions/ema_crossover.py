"""
EMA Crossover condition.
BUY:  Price crosses ABOVE EMA(price, period)
SELL: Price crosses BELOW EMA(price, period)

"Crosses above" = previous close <= previous EMA AND current close > current EMA.
"""

from .base import Condition
from ..indicators import calc_ema
import pandas as pd


class EMACrossover(Condition):

    @property
    def name(self) -> str:
        return "Price EMA Crossover"

    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("price_ema_period", "11"))
        ema = calc_ema(data["Close"], period=period)

        if len(ema) < 2 or pd.isna(ema.iloc[-1]) or pd.isna(ema.iloc[-2]):
            return False

        prev_close = float(data["Close"].iloc[-2])
        curr_close = float(data["Close"].iloc[-1])
        prev_ema = float(ema.iloc[-2])
        curr_ema = float(ema.iloc[-1])

        # Price crosses above EMA
        return prev_close <= prev_ema and curr_close > curr_ema

    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        period = int(config.get("price_ema_period", "11"))
        ema = calc_ema(data["Close"], period=period)

        if len(ema) < 2 or pd.isna(ema.iloc[-1]) or pd.isna(ema.iloc[-2]):
            return False

        prev_close = float(data["Close"].iloc[-2])
        curr_close = float(data["Close"].iloc[-1])
        prev_ema = float(ema.iloc[-2])
        curr_ema = float(ema.iloc[-1])

        # Price crosses below EMA
        return prev_close >= prev_ema and curr_close < curr_ema

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        period = int(config.get("price_ema_period", "11"))
        ema = calc_ema(data["Close"], period=period)
        return {
            "ema_value": float(ema.iloc[-1]) if not ema.empty and not pd.isna(ema.iloc[-1]) else None,
            "price": float(data["Close"].iloc[-1]) if not data.empty else None,
        }
