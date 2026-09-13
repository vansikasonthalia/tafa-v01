"""
Screener router — run the screener manually and check scheduler status.
Uses Driver/Validation condition split with configurable AND/OR logic.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Watchlist, Config, TrackingEntry, DEFAULT_CONFIG
from ..services.data_fetcher import get_fetcher
from ..services.conditions import get_all_conditions
from ..services.fundamental import fetch_fundamentals
from ..services.scheduler import get_scheduler_status

router = APIRouter(prefix="/api/screener", tags=["screener"])


@router.post("/run")
def run_screener(db: Session = Depends(get_db)):
    """
    Manually run the screener on all watchlist tickers.
    Signal logic: (Driver conditions [AND/OR]) AND (all Validation conditions)
    Then fetches fundamental data for matched stocks.
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

    # Split conditions into driver and validation
    drivers = [c for c in conditions if c.category == "driver"]
    validators = [c for c in conditions if c.category == "validation"]
    driver_logic = config.get("driver_logic", "and")

    signals = []
    errors = []

    # Bulk download all ticker data at once
    print(f"[Screener] Fetching data for {len(tickers)} tickers in bulk...")
    all_data = fetcher.fetch_bulk(
        tickers,
        period="2y",
        interval=config.get("timeframe", "1wk"),
    )
    print(f"[Screener] Got data for {len(all_data)}/{len(tickers)} tickers.")

    for ticker in tickers:
        try:
            data = all_data.get(ticker)

            if data is None or data.empty:
                errors.append({"ticker": ticker, "error": "No data returned"})
                continue

            if len(data) < 30:
                errors.append({"ticker": ticker, "error": f"Insufficient data ({len(data)} bars)"})
                continue

            # --- Driver conditions (AND or OR) ---
            if drivers:
                if driver_logic == "or":
                    driver_buy = any(c.check_buy(data, config) for c in drivers)
                    driver_sell = any(c.check_sell(data, config) for c in drivers)
                else:
                    driver_buy = all(c.check_buy(data, config) for c in drivers)
                    driver_sell = all(c.check_sell(data, config) for c in drivers)
            else:
                driver_buy = True
                driver_sell = True

            # --- Validation conditions (always AND) ---
            validation_buy = all(c.check_buy(data, config) for c in validators)
            validation_sell = all(c.check_sell(data, config) for c in validators)

            # --- Final signal = Driver AND Validation ---
            all_buy = driver_buy and validation_buy
            all_sell = driver_sell and validation_sell

            if all_buy or all_sell:
                signal = "BUY" if all_buy else "SELL"

                # Gather indicator values from all conditions
                values = {}
                for c in conditions:
                    values.update(c.get_values(data, config))

                # Fetch fundamental data for this matched stock
                fundamentals = fetch_fundamentals(ticker)

                entry = TrackingEntry(
                    ticker=ticker,
                    signal=signal,
                    price=values.get("price"),
                    rsi=values.get("rsi"),
                    ema_value=values.get("ema_value"),
                    wma_value=values.get("wma_value"),
                    ema_rsi=values.get("ema_rsi"),
                    wma_rsi=values.get("wma_rsi"),
                    market_cap=fundamentals.get("market_cap"),
                    pe_ratio=fundamentals.get("pe_ratio"),
                    sales_growth_3yr=fundamentals.get("sales_growth_3yr"),
                    profit_growth_3yr=fundamentals.get("profit_growth_3yr"),
                    annual_sales=fundamentals.get("annual_sales"),
                    mcap_sales_ratio=fundamentals.get("mcap_sales_ratio"),
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
        "data_fetched": len(all_data),
        "errors": errors,
        "conditions_checked": [c.name for c in conditions],
        "driver_logic": driver_logic,
    }


@router.get("/status")
def screener_status():
    """Get the background scheduler status."""
    return get_scheduler_status()
