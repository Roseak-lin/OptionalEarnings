from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from repository.base_repository import BaseRepository

class HistoricalMarketDataRepository(BaseRepository):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)
        self.collection = collection["historical_market_data"]
        self.collection.create_index(
            [("ticker", 1), ("trading_day", -1)],
            unique=True,
        )
        
    def upsert_data(self, record: dict) -> None:
        self.collection.update_one(
            {
                "ticker": record["ticker"],
                "trading_day": record["trading_day"],
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
                    "trading_day": r["trading_day"],
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