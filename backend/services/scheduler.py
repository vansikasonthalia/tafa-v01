"""
Background scheduler — runs the screener every 30 minutes.
Uses APScheduler's BackgroundScheduler so it runs in a separate thread.
"""

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Module-level state
_scheduler: BackgroundScheduler | None = None
_last_run: datetime | None = None
_is_running: bool = False
_last_result: dict | None = None


def _run_screener_job():
    """
    The scheduled job that runs the screener.
    Imports here to avoid circular imports.
    """
    global _last_run, _is_running, _last_result

    if _is_running:
        print("[Scheduler] Screener already running, skipping this tick.")
        return

    _is_running = True
    try:
        from ..database import SessionLocal
        from ..models import Watchlist, Config, TrackingEntry, DEFAULT_CONFIG
        from ..services.data_fetcher import get_fetcher
        from ..services.conditions import get_all_conditions

        db = SessionLocal()
        try:
            # Get config
            config_rows = db.query(Config).all()
            config = {**DEFAULT_CONFIG}
            for row in config_rows:
                config[row.key] = row.value

            # Get all tickers
            tickers = [w.ticker for w in db.query(Watchlist).all()]
            if not tickers:
                print("[Scheduler] No tickers in watchlist, skipping.")
                _last_run = datetime.utcnow()
                _last_result = {"signals": 0, "tickers_scanned": 0, "message": "No tickers in watchlist"}
                return

            fetcher = get_fetcher(config.get("data_source", "yahoo"))
            conditions = get_all_conditions()
            from ..services.fundamental import fetch_fundamentals

            # Split conditions into driver and validation
            drivers = [c for c in conditions if c.category == "driver"]
            validators = [c for c in conditions if c.category == "validation"]
            driver_logic = config.get("driver_logic", "and")
            signals = []

            # Bulk download all ticker data at once
            print(f"[Scheduler] Fetching data for {len(tickers)} tickers in bulk...")
            all_data = fetcher.fetch_bulk(
                tickers,
                period="2y",
                interval=config.get("timeframe", "1wk"),
            )
            print(f"[Scheduler] Got data for {len(all_data)}/{len(tickers)} tickers.")

            for ticker in tickers:
                try:
                    data = all_data.get(ticker)

                    if data is None or data.empty or len(data) < 30:
                        continue

                    # Driver conditions (AND or OR)
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

                    # Validation conditions (always AND)
                    validation_buy = all(c.check_buy(data, config) for c in validators)
                    validation_sell = all(c.check_sell(data, config) for c in validators)

                    all_buy = driver_buy and validation_buy
                    all_sell = driver_sell and validation_sell

                    if all_buy or all_sell:
                        signal = "BUY" if all_buy else "SELL"

                        values = {}
                        for c in conditions:
                            values.update(c.get_values(data, config))

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
                            run_type="scheduled",
                        )
                        db.add(entry)
                        
                        entry_dict = {
                            "ticker": ticker,
                            "signal": signal,
                            "price": values.get("price"),
                            "rsi": values.get("rsi"),
                            "market_cap": fundamentals.get("market_cap"),
                            "pe_ratio": fundamentals.get("pe_ratio"),
                            "run_type": "scheduled",
                        }
                        
                        from ..services.telegram import send_telegram_alert
                        send_telegram_alert(entry_dict)
                        
                        signals.append({"ticker": ticker, "signal": signal})

                except Exception as e:
                    print(f"[Scheduler] Error processing {ticker}: {e}")
                    continue

            db.commit()
            _last_run = datetime.utcnow()
            _last_result = {
                "signals": len(signals),
                "tickers_scanned": len(tickers),
                "details": signals,
            }
            print(f"[Scheduler] Screener completed: {len(signals)} signals from {len(tickers)} tickers")

        finally:
            db.close()

    except Exception as e:
        print(f"[Scheduler] Error: {e}")
    finally:
        _is_running = False


def start_scheduler():
    """Start the background scheduler."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _run_screener_job,
        "interval",
        minutes=30,
        id="screener_job",
        name="Run stock screener",
        max_instances=1,
    )
    _scheduler.start()
    print("[Scheduler] Started — screener will run every 30 minutes.")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        print("[Scheduler] Stopped.")


def get_scheduler_status() -> dict:
    """Get current scheduler state."""
    next_run = None
    if _scheduler and _scheduler.get_jobs():
        job = _scheduler.get_job("screener_job")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return {
        "is_running": _is_running,
        "last_run": _last_run.isoformat() if _last_run else None,
        "next_run": next_run,
        "last_result": _last_result,
        "scheduler_active": _scheduler is not None and _scheduler.running,
    }
