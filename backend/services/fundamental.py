"""
Fundamental data fetcher.
Pulls PE ratio, market cap, sales, and growth data from Yahoo Finance
for stocks that matched the technical screener.
"""

import yfinance as yf

# 1 crore = 10,000,000
CRORE = 10_000_000


def fetch_fundamentals(ticker: str) -> dict:
    """
    Fetch fundamental data for a single ticker from Yahoo Finance.

    Returns a dict with:
        - market_cap: Market cap in crores (INR)
        - pe_ratio: Trailing P/E ratio
        - sales_growth_3yr: Revenue growth % (proxy for 3yr CAGR)
        - profit_growth_3yr: Earnings growth % (proxy for 3yr CAGR)
        - annual_sales: Total revenue in crores (INR)
        - mcap_sales_ratio: Market cap / Annual sales
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return {}

        market_cap_raw = info.get("marketCap")
        total_revenue_raw = info.get("totalRevenue")

        market_cap = round(market_cap_raw / CRORE, 2) if market_cap_raw else None
        annual_sales = round(total_revenue_raw / CRORE, 2) if total_revenue_raw else None

        pe_ratio = info.get("trailingPE")
        if pe_ratio and isinstance(pe_ratio, (int, float)):
            pe_ratio = round(pe_ratio, 2)
        else:
            pe_ratio = None

        # Revenue growth and earnings growth (Yahoo provides these as decimals, e.g. 0.15 = 15%)
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")

        sales_growth_3yr = round(revenue_growth * 100, 2) if revenue_growth and isinstance(revenue_growth, (int, float)) else None
        profit_growth_3yr = round(earnings_growth * 100, 2) if earnings_growth and isinstance(earnings_growth, (int, float)) else None

        # Market cap to sales ratio
        mcap_sales_ratio = None
        if market_cap and annual_sales and annual_sales > 0:
            mcap_sales_ratio = round(market_cap / annual_sales, 2)

        return {
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "sales_growth_3yr": sales_growth_3yr,
            "profit_growth_3yr": profit_growth_3yr,
            "annual_sales": annual_sales,
            "mcap_sales_ratio": mcap_sales_ratio,
        }

    except Exception as e:
        print(f"[Fundamental] Error fetching fundamentals for {ticker}: {e}")
        return {}


def fetch_fundamentals_batch(tickers: list[str]) -> dict[str, dict]:
    """
    Fetch fundamental data for multiple tickers.
    Returns dict mapping ticker -> fundamentals dict.
    """
    result = {}
    for ticker in tickers:
        data = fetch_fundamentals(ticker)
        if data:
            result[ticker] = data
    return result
