from repository.base_repository import BaseRepository
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

class SP500CompanyRepository(BaseRepository):
    def __init__(self, collection: Collection) -> None:
        super().__init__(collection)
        self.collection = collection["sp500_companies"]
 
    def upsert_data(self, record: dict) -> None:
        self.collection.update_one(
            {"ticker": record["ticker"]},
            {"$set": {"name": record["name"]}},
            upsert=True,
        )
        
    def bulk_upsert_data(self, records: list[dict]) -> dict:
        if not records:
            return {"upserted": 0, "modified": 0, "errors": 0}
        ops = [
            UpdateOne(
                {"ticker": r["ticker"]},
                {"$set": {"name": r["name"]}},
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
    
    def get_all_companies(self) -> list[dict]:
        res = self.collection.find({}, {"_id": 0}).sort("ticker", 1)
        return list(res)