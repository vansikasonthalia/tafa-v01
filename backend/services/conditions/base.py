"""
Abstract base class for screener conditions.
Every condition module must subclass this.
"""

from abc import ABC, abstractmethod
import pandas as pd


class Condition(ABC):
    """
    A single screening condition (e.g., RSI threshold, EMA crossover).

    To add a new condition:
    1. Create a new .py file in this directory
    2. Subclass Condition
    3. Implement name, check_buy(), check_sell()
    4. It will be auto-discovered and registered.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this condition."""
        ...

    @abstractmethod
    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        """
        Return True if the BUY condition is met on the latest bar.

        Args:
            data: OHLCV DataFrame with calculated indicators attached.
            config: Current config dict (e.g., {"rsi_period": "14", ...}).
        """
        ...

    @abstractmethod
    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        """
        Return True if the SELL condition is met on the latest bar.
        """
        ...

    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        """
        Return indicator values relevant to this condition for logging.
        Override this to provide values that get stored in TrackingEntry.
        """
        return {}
