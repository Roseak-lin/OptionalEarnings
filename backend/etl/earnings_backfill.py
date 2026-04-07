"""
Historical Earnings Backfill
Loads 5 years of earnings data for all S&P 500 companies into MongoDB.

Database   : company_data
Collection : earnings_history
"""

import logging
import sys
import os
import time
from datetime import datetime, timezone
from io import StringIO

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # add backend/ to path for imports
import pandas as pd
import requests
import yfinance as yf
from pymongo.errors import BulkWriteError

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from repository.past_earnings_repository import PastEarningsRepository
from backend.core.dependencies import get_past_earnings_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backfill_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# ------------------------------------------------------------------
# Fetch S&P 500 tickers
# ------------------------------------------------------------------

def get_sp500_tickers() -> list[str]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(SP500_WIKI_URL, headers=headers)
    
    # extract the first table from the Wikipedia page, which contains the list of S&P 500 companies
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    
    # the 'Symbol' column contains the tickers, but some have dots (e.g. BRK.B) which yfinance expects as dashes (BRK-B)
    tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
    logger.info("Fetched %d S&P 500 tickers.", len(tickers))
    return tickers


# ------------------------------------------------------------------
# Fetch historical earnings for a single ticker
# ------------------------------------------------------------------

def fetch_historical_earnings(ticker: str) -> list[dict]:
    """
    Returns a list of earnings records for the past 5 years for a given ticker.
    yfinance returns up to ~4 years of earnings_dates history.
    """
    records = []
    try:
        t = yf.Ticker(ticker)
        dates_df = t.earnings_dates

        if dates_df is None or dates_df.empty:
            logger.debug("%s - no earnings_dates found, skipping.", ticker)
            return []

        # yfinance returns future estimates too - filter to past dates only
        now = pd.Timestamp.now(tz="UTC")
        five_years_ago = now - pd.DateOffset(years=5)
        dates_df = dates_df[
            (dates_df.index <= now) &
            (dates_df.index >= five_years_ago)
        ]

        if dates_df.empty:
            return []

        # Enrich with company info once per ticker
        try:
            info = t.info
            company_name = info.get("longName") or ticker
            sector       = info.get("sector")
            industry     = info.get("industry")
            market_cap   = info.get("marketCap")
        except Exception:
            company_name, sector, industry, market_cap = ticker, None, None, None

        for dt, row in dates_df.iterrows():
            eps_estimate = row.get("EPS Estimate")
            eps_actual   = row.get("Reported EPS")
            surprise_pct = row.get("Surprise(%)")

            # Normalise to naive UTC datetime for Mongo
            earnings_dt = dt.to_pydatetime()
            if earnings_dt.tzinfo is not None:
                earnings_dt = earnings_dt.replace(tzinfo=None)

            record = {
                "ticker":        ticker,
                "earnings_date": earnings_dt,
                "eps_estimate":  None if pd.isna(eps_estimate) else float(eps_estimate),
                "eps_actual":    None if pd.isna(eps_actual)   else float(eps_actual),
                "surprise_pct":  None if pd.isna(surprise_pct) else float(surprise_pct),
                "company_name":  company_name,
                "sector":        sector,
                "industry":      industry,
                "market_cap":    market_cap,
                "fetched_at":    datetime.now(timezone.utc).replace(tzinfo=None),
            }
            records.append(record)

    except Exception as exc:
        logger.warning("%s - error fetching earnings: %s", ticker, exc)

    return records


# ------------------------------------------------------------------
# Upsert into MongoDB
# ------------------------------------------------------------------

def upsert_records(repo: PastEarningsRepository, records: list[dict]) -> dict:
    # if no records to upsert, return zero summary immediately to avoid unnecessary DB call
    if not records:
        return {"upserted": 0, "modified": 0, "errors": 0}
    try:
        result = repo.bulk_upsert_earnings(records)
        return {
            "upserted": result["upserted"],
            "modified": result["modified"],
            "errors":   result["errors"],
        }
    except BulkWriteError as bwe:
        return {
            "upserted": bwe.details.get("nUpserted", 0),
            "modified": bwe.details.get("nModified", 0),
            "errors":   len(bwe.details.get("writeErrors", [])),
        }


# ------------------------------------------------------------------
# Main backfill runner
# ------------------------------------------------------------------

def run_backfill(repo: PastEarningsRepository):
    # tickers = get_sp500_tickers()
    tickers = get_sp500_tickers()

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
        
        