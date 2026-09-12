"""
Config router — get and update screener rule parameters.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import Config, DEFAULT_CONFIG

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
def get_config(db: Session = Depends(get_db)):
    """Return the full config, filling in defaults for any unset keys."""
    rows = db.query(Config).all()
    stored = {row.key: row.value for row in rows}

    # Merge defaults with stored values
    config = {**DEFAULT_CONFIG, **stored}
    return config


class ConfigUpdate(BaseModel):
    """Accepts any subset of config keys to update."""
    price_ema_period: str | None = None
    rsi_period: str | None = None
    ema_of_rsi_period: str | None = None
    wma_of_rsi_period: str | None = None
    rsi_threshold: str | None = None
    timeframe: str | None = None
    data_source: str | None = None


@router.post("")
def update_config(updates: ConfigUpdate, db: Session = Depends(get_db)):
    """Update one or more config values."""
    updated = {}
    for key, value in updates.model_dump(exclude_none=True).items():
        existing = db.query(Config).filter(Config.key == key).first()
        if existing:
            existing.value = str(value)
        else:
            db.add(Config(key=key, value=str(value)))
        updated[key] = str(value)

    db.commit()

    # Return full config after update
    rows = db.query(Config).all()
    stored = {row.key: row.value for row in rows}
    config = {**DEFAULT_CONFIG, **stored}

    return {"updated": updated, "config": config}
