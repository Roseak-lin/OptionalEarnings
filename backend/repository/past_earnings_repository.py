from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from datetime import datetime

from .base_repository import BaseRepository

class PastEarningsRepository(BaseRepository):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)
        self.collection = collection["company_earnings_history"]
        self.collection.create_index(
            [("ticker", 1), ("earnings_date", 1)],
            unique=True,
            name="ticker_date_unique",
        )

    def upsert_data(self, record: dict) -> None:
        self.collection.update_one(
            {
                "ticker": record["ticker"],
                "earnings_date": record["earnings_date"],
            },
            {"$set": record},
            upsert=True,
        )

    def bulk_upsert_data(self, records: list[dict]) -> dict:
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

    def get_earnings_by_ticker(self, ticker: str) -> list[dict]:
        """Get all earnings history for a ticker, sorted by date descending."""
        results = self.collection.find(
            {"ticker": ticker},
        )
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