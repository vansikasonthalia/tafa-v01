"""
Base class for screener conditions.
Each condition belongs to a category: 'driver' or 'validation'.

Driver conditions are combined with AND or OR (configurable).
Validation conditions are always combined with AND.
Signal = (Drivers combined) AND (all Validators pass)
"""

from abc import ABC, abstractmethod
import pandas as pd


class Condition(ABC):
    """Abstract base class that every condition must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this condition."""
        ...

    @property
    def category(self) -> str:
        """
        Category of this condition: 'driver' or 'validation'.
        Override in subclass. Defaults to 'validation'.
        """
        return "validation"

    @abstractmethod
    def check_buy(self, data: pd.DataFrame, config: dict) -> bool:
        """Return True if the BUY condition is met on the latest bar."""
        ...

    @abstractmethod
    def check_sell(self, data: pd.DataFrame, config: dict) -> bool:
        """Return True if the SELL condition is met on the latest bar."""
        ...

    @abstractmethod
    def get_values(self, data: pd.DataFrame, config: dict) -> dict:
        """Return a dict of indicator values for logging/display."""
        ...
