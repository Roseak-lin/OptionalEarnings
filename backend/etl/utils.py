from io import StringIO
import os
import sys
from pathlib import Path
import pandas as pd
from pymongo.errors import BulkWriteError
import requests

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # add backend/ to path for imports
from backend.repository.historical_market_data_repository import HistoricalMarketDataRepository
from backend.repository.past_earnings_repository import PastEarningsRepository

SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_sp500_tickers() -> list[str]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(SP500_WIKI_URL, headers=headers)
    
    # extract the first table from the Wikipedia page, which contains the list of S&P 500 companies
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    
    # the 'Symbol' column contains the tickers, but some have dots (e.g. BRK.B) which yfinance expects as dashes (BRK-B)
    tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
    return tickers

def upsert_records(
    repo: PastEarningsRepository | HistoricalMarketDataRepository,
    records: list[dict]
) -> dict:
    if not records:
        return {"upserted": 0, "modified": 0, "errors": 0}

    try:
        result = repo.bulk_upsert_data(records)
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