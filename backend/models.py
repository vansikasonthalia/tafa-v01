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
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "industry": self.industry,
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
    # Driver conditions (EMA crossover)
    "fast_ema_period": "11",
    "slow_ema_period": "100",
    "driver_logic": "and",           # "and" or "or" — how driver conditions combine

    # Validation conditions (RSI)
    "rsi_period": "14",
    "ema_of_rsi_period": "3",
    "wma_of_rsi_period": "21",
    "rsi_threshold": "50",

    # General
    "timeframe": "1wk",             # Yahoo Finance interval format
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
    market_cap = Column(Float, nullable=True)       # Market cap in crores
    pe_ratio = Column(Float, nullable=True)
    sales_growth_3yr = Column(Float, nullable=True)  # 3yr CAGR %
    profit_growth_3yr = Column(Float, nullable=True) # 3yr CAGR %
    annual_sales = Column(Float, nullable=True)      # In crores
    mcap_sales_ratio = Column(Float, nullable=True)  # Market cap / Annual sales
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
            "market_cap": round(self.market_cap, 2) if self.market_cap else None,
            "pe_ratio": round(self.pe_ratio, 2) if self.pe_ratio else None,
            "sales_growth_3yr": round(self.sales_growth_3yr, 2) if self.sales_growth_3yr else None,
            "profit_growth_3yr": round(self.profit_growth_3yr, 2) if self.profit_growth_3yr else None,
            "annual_sales": round(self.annual_sales, 2) if self.annual_sales else None,
            "mcap_sales_ratio": round(self.mcap_sales_ratio, 2) if self.mcap_sales_ratio else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "run_type": self.run_type,
        }
