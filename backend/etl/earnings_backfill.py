"""
Historical Earnings Backfill
Loads 5 quarters  of earnings data for all S&P 500 companies into MongoDB.

Database   : company_data
Collection : earnings_history
"""

import logging
import time
from datetime import datetime, timedelta, timezone

from pathlib import Path

import pandas as pd
import yfinance as yf

from repository.past_earnings_repository import PastEarningsRepository
from core.dependencies import get_past_earnings_db, SECTOR_ETF_MAP
from utils import get_sp500_tickers, upsert_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backfill_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Fetch historical earnings for a single ticker
# ------------------------------------------------------------------

def fetch_historical_earnings(ticker: str) -> list[dict]:
    """
    Returns a list of earnings records for the past 5 quarters for a given ticker.
    yfinance returns up to ~4 years of earnings_dates history.
    """
    records = []
    try:
        t = yf.Ticker(ticker)
        dates_df = t.earnings_dates
        income_stmt = t.quarterly_income_stmt

        if dates_df is None or dates_df.empty:
            logger.debug("%s - no earnings_dates found, skipping.", ticker)
            return []
        # yfinance returns future estimates too - filter to past dates only
        now = pd.Timestamp.now(tz="UTC")
        dates_df = dates_df.head(6)

        if dates_df.empty:
            return []

        # Enrich with company info once per ticker
        try:
            info = t.info
            company_name = info.get("longName") or ticker
            sector       = info.get("sector")
            industry     = info.get("industry")
        except Exception:
            company_name, sector, industry = ticker, None, None

        sector_etf_ticker = SECTOR_ETF_MAP.get(sector, "SPY")
        
        # Fetch Macro Data (VIX and Sector ETF) for the range of earnings dates
        start_date = (dates_df.index.min() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (dates_df.index.max() + timedelta(days=2)).strftime('%Y-%m-%d')
        macro_data = yf.download(["^VIX", sector_etf_ticker], start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        for dt, row in dates_df.iterrows():
            if dt > datetime.now(tz=timezone.utc):
                continue
            
            eps_estimate = row.get("EPS Estimate")
            eps_actual   = row.get("Reported EPS")
            surprise_pct = row.get("Surprise(%)")

            # Normalise to naive UTC datetime for Mongo
            earnings_dt = dt.to_pydatetime()
            if earnings_dt.tzinfo is not None:
                earnings_dt = earnings_dt.replace(tzinfo=None)

            record = {
                "ticker": ticker,
                "earnings_date": earnings_dt,
                "eps_estimate": None if pd.isna(eps_estimate) else float(eps_estimate),
                "eps_actual": None if pd.isna(eps_actual) else float(eps_actual),
                "surprise_pct": None if pd.isna(surprise_pct) else float(surprise_pct),
                "company_name": company_name,
                "sector": sector,
                "sector_etf": sector_etf_ticker,
                "industry": industry,
                "fetched_at": datetime.now(timezone.utc).replace(tzinfo=None),
            }
            
            # Find closest available market day for VIX and Sector ETF
            report_date_str = dt.strftime('%Y-%m-%d')
            if report_date_str in macro_data.index:
                vix_val = round(macro_data.loc[report_date_str, ("Close", "^VIX")], 2)
                sector_change = (macro_data.loc[report_date_str, ("Close", sector_etf_ticker)] - macro_data.loc[report_date_str, ("Open", sector_etf_ticker)]) / macro_data.loc[report_date_str, ("Open", sector_etf_ticker)]
                sector_change = round(sector_change * 100, 2) 
            else:
                past_data = macro_data[macro_data.index <= report_date_str]
                # Fallback to the most recent previous trading day
                vix_val = round(past_data.iloc[-1].loc["Close", "^VIX"], 2) if not past_data.empty else None
                sector_change = (past_data.iloc[-1].loc["Close", sector_etf_ticker] - past_data.iloc[-1].loc["Open", sector_etf_ticker]) / past_data.iloc[-1].loc["Open", sector_etf_ticker]
                sector_change = round(sector_change * 100, 2) 
            record.update({
                "vix_close": float(vix_val) if pd.notna(vix_val) else None,
                "sector_etf_change": float(sector_change) if pd.notna(sector_change) else None
            })
            records.append(record)
            
        
        NORMALIZED_EBITDA_ROW = income_stmt.index.get_loc("Normalized EBITDA")
        TOTAL_REVENUE_ROW = income_stmt.index.get_loc("Total Revenue")
        OPERATING_INCOME_ROW = income_stmt.index.get_loc("Operating Income")
        
        for i in range(5):
            record = records[i]
            normalized_EBITA = income_stmt.iloc[NORMALIZED_EBITDA_ROW, i]
            total_revenue = income_stmt.iloc[TOTAL_REVENUE_ROW, i]
            operating_income = income_stmt.iloc[OPERATING_INCOME_ROW, i]
            
            record.update({
                "normalized_EBITA": float(normalized_EBITA) if pd.notna(normalized_EBITA) else None,
                "total_revenue": float(total_revenue) if pd.notna(total_revenue) else None,
                "operating_income": float(operating_income) if pd.notna(operating_income) else None,
            })
    except Exception as exc:
        logger.warning("%s - error fetching earnings: %s", ticker, exc)

    return records

# ------------------------------------------------------------------
# Main backfill runner
# ------------------------------------------------------------------

def run_backfill(repo: PastEarningsRepository):
    tickers = get_sp500_tickers()[:1]

    total_upserted = 0
    total_modified = 0
    total_errors   = 0
    tickers_with_data = 0

    for i, ticker in enumerate(tickers, 1):
        logger.info("[%d/%d] Processing %s ...", i, len(tickers), ticker)

        records = fetch_historical_earnings(ticker)
        if records:
            tickers_with_data += 1
            summary = upsert_records(repo, records)
            total_upserted += summary["upserted"]
            total_modified += summary["modified"]
            total_errors += summary["errors"]
            logger.info(
                "  %s - %d records | upserted: %d, modified: %d, errors: %d",
                ticker, len(records),
                summary["upserted"], summary["modified"], summary["errors"],
            )
        else:
            logger.info("  %s - no historical earnings found.", ticker)

        # Sleep to avoid hitting yfinance / Yahoo rate limits
        time.sleep(0.15)


    logger.info("=== Backfill Complete ===")
    logger.info("Tickers processed : %d", len(tickers))
    logger.info("Tickers with data : %d", tickers_with_data)
    logger.info("Total upserted    : %d", total_upserted)
    logger.info("Total modified    : %d", total_modified)
    logger.info("Total errors      : %d", total_errors)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_filename = f"backfill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    full_log_path = log_dir / log_filename

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(full_log_path),
            logging.StreamHandler()
        ],
        force=True
    )
    
    run_backfill(PastEarningsRepository(collection=get_past_earnings_db()))
        
        