import logging
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

from repository.historical_market_data_repository import HistoricalMarketDataRepository
from etl.utils import upsert_records
from core.dependencies import get_general_market_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backfill_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_historical_market_data(ticker: str) -> list[dict]:
    # get market data for the last 2 years to ensure we capture at least 5 quarters of earnings history, even for companies with infrequent reporting
    end_date = datetime.now()
    date_range_years = 2
    start_date = end_date - timedelta(days=365 * date_range_years)
    
    market_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False, auto_adjust=False)
    market_data.columns = market_data.columns.get_level_values(0)  # flatten columns if they are multi-indexed
    market_data.reset_index(inplace=True)  # move date from index to column
    
    daily_records = []
    for entry in market_data.to_dict('records'):
        open_val = entry.get("Open")
        close_val = entry.get("Close")
        if pd.isna(open_val) or pd.isna(close_val):
            continue
        record = {
            "ticker": ticker,
            "trading_day": entry.get("Date").strftime('%Y-%m-%d'),
            "open": round(float(open_val), 2),
            "close": round(float(close_val), 2)
        }
        daily_records.append(record)
    return daily_records
    

def run_backfill(repo: HistoricalMarketDataRepository) -> None:
    # The VIX, SPY, and standard Sector ETFs
    TARGET_SYMBOLS = [
        "^VIX", "SPY", "XLK", "XLF", "XLV", "XLE", 
        "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC"
    ]
    for symbol in TARGET_SYMBOLS:
        logger.info("Fetching historical market data for %s", symbol)
        market_data = fetch_historical_market_data(symbol)
        results = upsert_records(repo, market_data)
        logger.info("Finished processing ticker : %s", symbol)
        logger.info("Total upserted             : %d", results.get("upserted", 0))
        logger.info("Total modified             : %d", results.get("modified", 0))
        logger.info("Total errors               : %d", results.get("errors", 0))

    
if __name__ == "__main__":
    repo = HistoricalMarketDataRepository(collection=get_general_market_data())
    run_backfill(repo)
    