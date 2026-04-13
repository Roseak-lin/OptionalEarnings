import logging
from datetime import datetime, timedelta, timezone

import certifi
import pandas as pd
import yfinance as yf
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

from utils import get_sp500_tickers
from core.config import MONGO_URI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class EarningsExtractor:
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
        self.collection = self.client["company_data"]["earnings_history"]
        self._ensure_indexes()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _ensure_indexes(self):
        """Create a unique compound index so re-runs never duplicate rows."""
        self.collection.create_index(
            [("ticker", 1), ("earnings_date", 1)],
            unique=True,
            name="ticker_date_unique",
        )
        logger.info("Indexes ensured.")

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    def get_previous_trading_day(self) -> datetime.date:
        """Return yesterday's date (Mon-Fri). Skips back over the weekend."""
        today = datetime.now(timezone.utc).date()
        offset = 1
        if today.weekday() == 0:   # Monday → go back to Friday
            offset = 3
        elif today.weekday() == 6: # Sunday → go back to Friday
            offset = 2
        prev_day = today - timedelta(days=offset)
        logger.info("Previous trading day: %s", prev_day)
        return prev_day

    def fetch_earnings_for_ticker(
        self, ticker: str, target_date: datetime.date
    ) -> dict | None:
        """
        Pull earnings_dates from yfinance and return a record if an
        earnings report falls on target_date, otherwise None.
        """
        try:
            t = yf.Ticker(ticker)
            dates_df = t.earnings_dates  # DataFrame indexed by earnings datetime
            if dates_df is None or dates_df.empty:
                return None

            # Normalise index to date for comparison
            dates_df.index = pd.to_datetime(dates_df.index).date
            print("DATES_DF: ", dates_df, "TARGET: ", target_date)
            if target_date not in dates_df.index:
                logger.info("No earnings found for %s on %s", ticker, target_date)
                return None

            row = dates_df.loc[target_date]
            # earnings_dates can have multiple rows for the same date; take first
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            eps_estimate = row.get("EPS Estimate")
            eps_actual   = row.get("Reported EPS")
            surprise_pct = row.get("Surprise(%)")

            record = {
                "ticker":        ticker,
                "earnings_date": datetime.combine(target_date, datetime.min.time()),
                "eps_estimate":  None if pd.isna(eps_estimate) else float(eps_estimate),
                "eps_actual":    None if pd.isna(eps_actual)   else float(eps_actual),
                "surprise_pct":  None if pd.isna(surprise_pct) else float(surprise_pct),
                "fetched_at":    datetime.now(timezone.utc),
            }

            # Enrich with basic company info
            info = t.fast_info
            record["company_name"] = getattr(info, "company_name", None) or ticker
            record["sector"]       = t.info.get("sector")
            record["industry"]     = t.info.get("industry")
            record["market_cap"]   = t.info.get("marketCap")

            return record

        except Exception as exc:
            logger.warning("Could not fetch earnings for %s: %s", ticker, exc)
            return None

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def build_operations(self, records: list[dict]) -> list[UpdateOne]:
        ops = []
        for rec in records:
            filter_q = {
                "ticker":        rec["ticker"],
                "earnings_date": rec["earnings_date"],
            }
            ops.append(UpdateOne(filter_q, {"$set": rec}, upsert=True))
        return ops

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self, operations: list[UpdateOne]) -> dict:
        if not operations:
            logger.info("No earnings records to load.")
            return {"upserted": 0, "modified": 0, "errors": 0}

        try:
            result = self.collection.bulk_write(operations, ordered=False)
            summary = {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "errors":   0,
            }
        except BulkWriteError as bwe:
            summary = {
                "upserted": bwe.details.get("nUpserted", 0),
                "modified": bwe.details.get("nModified", 0),
                "errors":   len(bwe.details.get("writeErrors", [])),
            }
            logger.error("Bulk write errors: %s", bwe.details.get("writeErrors"))

        logger.info(
            "Load complete — upserted: %d, modified: %d, errors: %d",
            summary["upserted"], summary["modified"], summary["errors"],
        )
        return summary

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    def run(self) -> dict:
        logger.info("=== EarningsExtractor starting ===")

        tickers      = get_sp500_tickers()
        target_date  = self.get_previous_trading_day()
        records      = []

        for i, ticker in enumerate(tickers, 1):
            logger.debug("[%d/%d] Checking %s …", i, len(tickers), ticker)
            record = self.fetch_earnings_for_ticker(ticker, target_date)
            if record:
                logger.info("Earnings found for %s on %s", ticker, target_date)
                records.append(record)

        logger.info(
            "Extraction complete — %d earnings reports found for %s.",
            len(records), target_date,
        )

        operations = self.build_operations(records)
        summary    = self.load(operations)

        logger.info("=== EarningsExtractor finished ===")
        return {
            "target_date":    str(target_date),
            "tickers_checked": len(tickers),
            "earnings_found": len(records),
            **summary,
        }

    def close(self):
        self.client.close()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    etl = EarningsExtractor(mongo_uri=MONGO_URI)
    try:
        # result = etl.run()
        calendar = yf.Calendars()
        print(calendar.get_earnings_calendar(start="2026-03-24", end="2026-03-27"))
    finally:
        etl.close()