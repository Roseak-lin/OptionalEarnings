from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from bson import ObjectId
from datetime import datetime


class PastEarningsRepository:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection["company_earnings_history"]
        self.collection.create_index(
            [("ticker", 1), ("earnings_date", 1)],
            unique=True,
            name="ticker_date_unique",
        )

    # ------------------------------------------------------------------
    # ETL operations
    # ------------------------------------------------------------------

    def upsert_earnings(self, record: dict) -> None:
        """Upsert a single earnings record by ticker + date."""
        self.collection.update_one(
            {
                "ticker": record["ticker"],
                "earnings_date": record["earnings_date"],
            },
            {"$set": record},
            upsert=True,
        )

    def bulk_upsert_earnings(self, records: list[dict]) -> dict:
        """Bulk upsert a list of earnings records. Returns a summary dict."""
        if not records:
            return {"upserted": 0, "modified": 0, "errors": 0}

        ops = [
            UpdateOne(
                {
                    "ticker": r["ticker"],
                    "earnings_date": r["earnings_date"],
                },
                {"$set": r},
                upsert=True,
            )
            for r in records
        ]

        try:
            result = self.collection.bulk_write(ops, ordered=False)
            return {
                "upserted": result.upserted_count,
                "modified": result.modified_count,
                "errors": 0,
            }
        except BulkWriteError as bwe:
            return {
                "upserted": bwe.details.get("nUpserted", 0),
                "modified": bwe.details.get("nModified", 0),
                "errors": len(bwe.details.get("writeErrors", [])),
            }

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def get_earnings_by_ticker(self, ticker: str) -> list[dict]:
        """Get all earnings history for a ticker, sorted by date descending."""
        results = self.collection.find(
            {"ticker": ticker},
            {"_id": 0}
        ).sort("earnings_date", -1)
        return list(results)

    def get_earnings_by_date(self, date: datetime) -> list[dict]:
        """Get all companies that reported earnings on a given date."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = date.replace(hour=23, minute=59, second=59)
        results = self.collection.find(
            {"earnings_date": {"$gte": start, "$lte": end}},
            {"_id": 0}
        )
        return list(results)

    def get_earnings_by_ticker_and_date_range(
        self, ticker: str, start: datetime, end: datetime
    ) -> list[dict]:
        """Get earnings for a ticker within a date range."""
        results = self.collection.find(
            {
                "ticker": ticker,
                "earnings_date": {"$gte": start, "$lte": end},
            },
            {"_id": 0}
        ).sort("earnings_date", -1)
        return list(results)

    # ------------------------------------------------------------------
    # Legacy / user-based operations (kept from original)
    # ------------------------------------------------------------------

    def add_earnings_data(self, user_id: str, ticker: str, earnings_data: dict) -> dict | None:
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {f"earnings_data.{ticker}": earnings_data}},
        )
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def temp(self, _id: str):
        return None