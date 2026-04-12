from abc import ABC, abstractmethod

class BaseRepository(ABC):
    def __init__(self, db):
        self.db = db
        self.collection = None

    # Upsert a single record. The specific implementation will depend on the repository type (e.g., earnings, market data).
    @abstractmethod
    def upsert_data(self, record: dict) -> None:
        pass

    # Upsert a list of records. Returns a summary dict with counts of upserted, modified, and errored records.
    @abstractmethod
    def bulk_upsert_data(self, records: list[dict]) -> dict:
        pass
    