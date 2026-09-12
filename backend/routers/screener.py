"""
Screener router — run the screener manually and check scheduler status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Watchlist, Config, TrackingEntry, DEFAULT_CONFIG
from ..services.data_fetcher import get_fetcher
from ..services.conditions import get_all_conditions
from ..services.scheduler import get_scheduler_status

router = APIRouter(prefix="/api/screener", tags=["screener"])


@router.post("/run")
def run_screener(db: Session = Depends(get_db)):
    """
    Manually run the screener on all watchlist tickers.
    Fetches data, applies all conditions, saves signals.
    """
    # Get config
    config_rows = db.query(Config).all()
    config = {**DEFAULT_CONFIG}
    for row in config_rows:
        config[row.key] = row.value

    # Get all tickers
    tickers = [w.ticker for w in db.query(Watchlist).all()]
    if not tickers:
        return {
            "signals": [],
            "tickers_scanned": 0,
            "message": "No tickers in watchlist. Upload a watchlist first.",
        }

    fetcher = get_fetcher(config.get("data_source", "yahoo"))
    conditions = get_all_conditions()
    signals = []
    errors = []

    for ticker in tickers:
        try:
            data = fetcher.fetch_ohlcv(
                ticker,
                period="2y",
                interval=config.get("timeframe", "1wk"),
            )

            if data.empty:
                errors.append({"ticker": ticker, "error": "No data returned"})
                continue

            if len(data) < 30:
                errors.append({"ticker": ticker, "error": f"Insufficient data ({len(data)} bars)"})
                continue

            # Check all conditions
            all_buy = all(c.check_buy(data, config) for c in conditions)
            all_sell = all(c.check_sell(data, config) for c in conditions)

            if all_buy or all_sell:
                signal = "BUY" if all_buy else "SELL"

                # Gather indicator values from all conditions
                values = {}
                for c in conditions:
                    values.update(c.get_values(data, config))

                entry = TrackingEntry(
                    ticker=ticker,
                    signal=signal,
                    price=values.get("price"),
                    rsi=values.get("rsi"),
                    ema_value=values.get("ema_value"),
                    wma_value=values.get("wma_value"),
                    ema_rsi=values.get("ema_rsi"),
                    wma_rsi=values.get("wma_rsi"),
                    run_type="manual",
                )
                db.add(entry)
                signals.append(entry.to_dict())

        except Exception as e:
            errors.append({"ticker": ticker, "error": str(e)})
            continue

    db.commit()

    # Re-fetch to get IDs
    if signals:
        latest = (
            db.query(TrackingEntry)
            .order_by(TrackingEntry.id.desc())
            .limit(len(signals))
            .all()
        )
        signals = [e.to_dict() for e in reversed(latest)]

    return {
        "signals": signals,
        "tickers_scanned": len(tickers),
        "errors": errors,
        "conditions_checked": [c.name for c in conditions],
    }


@router.get("/status")
def screener_status():
    """Get the background scheduler status."""
    return get_scheduler_status()
