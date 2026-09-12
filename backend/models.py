"""
SQLAlchemy ORM models for TAFA.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from .database import Base


class Watchlist(Base):
    """Persistent watchlist — tickers stay until explicitly deleted."""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Config(Base):
    """Key-value config store for screener rules."""
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, nullable=False, unique=True, index=True)
    value = Column(String, nullable=False)

    def to_dict(self):
        return {"key": self.key, "value": self.value}


# Default configuration values
DEFAULT_CONFIG = {
    "price_ema_period": "11",
    "rsi_period": "14",
    "ema_of_rsi_period": "3",
    "wma_of_rsi_period": "21",
    "rsi_threshold": "50",
    "timeframe": "1wk",       # Yahoo Finance interval format
    "data_source": "yahoo",
}


class TrackingEntry(Base):
    """Every BUY/SELL signal the screener generates."""
    __tablename__ = "tracking_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, index=True)
    signal = Column(String, nullable=False)  # "BUY" or "SELL"
    price = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    ema_value = Column(Float, nullable=True)
    wma_value = Column(Float, nullable=True)
    ema_rsi = Column(Float, nullable=True)
    wma_rsi = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    run_type = Column(String, default="manual")  # "manual" or "scheduled"

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "signal": self.signal,
            "price": self.price,
            "rsi": round(self.rsi, 2) if self.rsi else None,
            "ema_value": round(self.ema_value, 2) if self.ema_value else None,
            "wma_value": round(self.wma_value, 2) if self.wma_value else None,
            "ema_rsi": round(self.ema_rsi, 2) if self.ema_rsi else None,
            "wma_rsi": round(self.wma_rsi, 2) if self.wma_rsi else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "run_type": self.run_type,
        }
