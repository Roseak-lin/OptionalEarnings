import logging
import time
from datetime import datetime, timedelta, timezone

from pathlib import Path

import pandas as pd
import yfinance as yf

from repository.past_earnings_repository import PastEarningsRepository
from core.dependencies import get_company_data_db, SECTOR_ETF_MAP
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

def fetch_historical_earnings(ticker: str) -> list[dict]:
    records = []
    try:
        t = yf.Ticker(ticker)
        dates_df = t.earnings_dates
        income_stmt = t.quarterly_income_stmt

        if dates_df is None or dates_df.empty:
            logger.debug("%s - no earnings_dates found, skipping.", ticker)
            return []

        dates_df = dates_df.head(6)

        if dates_df.empty:
            return []

        try:
            info = t.info
            company_name = info.get("longName") or ticker
            sector       = info.get("sector")
            industry     = info.get("industry")
        except Exception:
            company_name, sector, industry = ticker, None, None

        sector_etf_ticker = SECTOR_ETF_MAP.get(sector, "SPY")

        start_date = (dates_df.index.min() - timedelta(days=10)).strftime('%Y-%m-%d')
        end_date   = (dates_df.index.max() + timedelta(days=5)).strftime('%Y-%m-%d')

        macro_data = yf.download(
            ["^VIX", sector_etf_ticker],
            start=start_date, end=end_date,
            progress=False, auto_adjust=False
        )

        price_data = yf.download(
            ticker,
            start=start_date, end=end_date,
            progress=False, auto_adjust=False
        )
        if isinstance(price_data.columns, pd.MultiIndex):
            price_data.columns = price_data.columns.get_level_values(0)

        trading_days = sorted(price_data.index.strftime('%Y-%m-%d').tolist())

        def get_prev_trading_day(date_str: str) -> str | None:
            before = [d for d in trading_days if d < date_str]
            return before[-1] if before else None

        def get_next_trading_day(date_str: str) -> str | None:
            after = [d for d in trading_days if d > date_str]
            return after[0] if after else None

        def safe_float(df, date_str: str, col) -> float | None:
            if date_str and date_str in df.index:
                val = df.loc[date_str, col]
                return float(val) if pd.notna(val) else None
            return None

        # Market open is at 9:30am ET, which is 14:30 UTC during standard time and 13:30 UTC during daylight saving time.
        MARKET_OPEN_HOUR_UTC = 14

        for dt, row in dates_df.iterrows():
            if dt > datetime.now(tz=timezone.utc):
                continue
            eps_estimate = row.get("EPS Estimate")
            eps_actual   = row.get("Reported EPS")
            surprise_pct = row.get("Surprise(%)")

            earnings_dt = dt.to_pydatetime()
            if earnings_dt.tzinfo is not None:
                earnings_dt = earnings_dt.replace(tzinfo=None)

            report_date_str = dt.strftime('%Y-%m-%d')
            is_premarket = dt.hour < MARKET_OPEN_HOUR_UTC

            if is_premarket:
                prev_day       = get_prev_trading_day(report_date_str)
                ref_close_date = prev_day
                ref_open_date  = report_date_str
                timing_label   = "Before market open"
                vix_val = safe_float(macro_data, ref_close_date, ("Open", "^VIX"))
                if vix_val is None:
                    past_data = macro_data[macro_data.index <= ref_close_date]
                    vix_val = round(float(past_data.iloc[-1].loc["Open", "^VIX"]), 2) \
                        if not past_data.empty else None
            else:
                next_day       = get_next_trading_day(report_date_str)
                ref_close_date = report_date_str
                ref_open_date  = next_day
                timing_label   = "After market close"
                vix_val = safe_float(macro_data, ref_close_date, ("Close", "^VIX"))
                if vix_val is None:
                    past_data = macro_data[macro_data.index <= ref_close_date]
                    vix_val = round(float(past_data.iloc[-1].loc["Close", "^VIX"]), 2) \
                        if not past_data.empty else None

            price_close = round(safe_float(price_data, ref_close_date, "Close"), 2)
            price_open  = round(safe_float(price_data, ref_open_date,  "Open"), 2)

            # Sector ETF uses the same date anchors as the price data
            sector_close = round(safe_float(macro_data, ref_close_date, ("Close", sector_etf_ticker)), 2)
            sector_open  = round(safe_float(macro_data, ref_open_date, ("Open",  sector_etf_ticker)), 2)
            sector_change = round((sector_open - sector_close) / sector_close * 100, 2) \
                if sector_close and sector_open else None

            record = {
                "ticker":            ticker,
                "earnings_date":     earnings_dt,
                "earnings_timing":   timing_label,
                "eps_estimate":      None if pd.isna(eps_estimate) else float(eps_estimate),
                "eps_actual":        None if pd.isna(eps_actual)   else float(eps_actual),
                "surprise_pct":      None if pd.isna(surprise_pct) else float(surprise_pct),
                "company_name":      company_name,
                "sector":            sector,
                "sector_etf":        sector_etf_ticker,
                "industry":          industry,
                "fetched_at":        datetime.now(timezone.utc).replace(tzinfo=None),
                "ref_close_date":    ref_close_date,
                "ref_open_date":     ref_open_date,
                "price_ref_close":   price_close if price_close is not None else None,
                "price_ref_open":    price_open if price_open is not None else None,
                "sector_ref_close":  sector_close if sector_close is not None else None,
                "sector_ref_open":   sector_open if sector_open is not None else None,
                "sector_etf_change": sector_change,
                "vix_val":           float(vix_val) if vix_val and pd.notna(vix_val) else None,
            }

            records.append(record)

        NORMALIZED_EBITDA_ROW = income_stmt.index.get_loc("Normalized EBITDA")
        TOTAL_REVENUE_ROW     = income_stmt.index.get_loc("Total Revenue")
        OPERATING_INCOME_ROW  = income_stmt.index.get_loc("Operating Income")

        for i in range(min(5, len(records))):
            record = records[i]
            record.update({
                "normalized_EBITA": float(income_stmt.iloc[NORMALIZED_EBITDA_ROW, i]) if pd.notna(income_stmt.iloc[NORMALIZED_EBITDA_ROW, i]) else None,
                "total_revenue":    float(income_stmt.iloc[TOTAL_REVENUE_ROW, i]) if pd.notna(income_stmt.iloc[TOTAL_REVENUE_ROW, i]) else None,
                "operating_income": float(income_stmt.iloc[OPERATING_INCOME_ROW, i]) if pd.notna(income_stmt.iloc[OPERATING_INCOME_ROW, i]) else None,
            })

    except Exception as exc:
        logger.warning("%s - error fetching earnings: %s", ticker, exc)

    return records

def run_backfill(repo: PastEarningsRepository):
    tickers = get_sp500_tickers()
    
    total_upserted    = 0
    total_modified    = 0
    total_errors      = 0
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
    
    run_backfill(PastEarningsRepository(collection=get_company_data_db()))