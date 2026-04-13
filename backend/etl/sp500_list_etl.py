import logging

from io import StringIO
import pandas as pd
import requests

from utils import SP500_WIKI_URL
from repository.sp500_company_repository import SP500CompanyRepository
from core.dependencies import get_company_data_db
from utils import upsert_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backfill_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_company_info() -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(SP500_WIKI_URL, headers=headers)
    
    if response.status_code != 200:
        logger.error("Failed to fetch S&P 500 companies: HTTP %d", response.status_code)
        return []
    
    try:
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        
        companies = []
        for _, row in df.iterrows():
            ticker = row["Symbol"].replace(".", "-")
            name   = row["Security"]
            companies.append({"ticker": ticker, "name": name})
        
        return companies
    except Exception as exc:
        logger.error("Error parsing S&P 500 companies: %s", exc)
        return []

def run_backfill(companies: list[dict], repo: SP500CompanyRepository):
    tickers_upserted  = 0
    tickers_modified  = 0
    total_errors      = 0
    tickers_with_data = 0
    
    summary = upsert_records(repo, companies)
    tickers_upserted += summary["upserted"]
    tickers_modified += summary["modified"]
    total_errors += summary["errors"]
    
    
    logger.info("=== Backfill Complete ===")
    logger.info("Tickers processed : %d", len(companies))
    logger.info("Tickers with data : %d", tickers_with_data)
    logger.info("Total upserted    : %d", tickers_upserted)
    logger.info("Total modified    : %d", tickers_modified)
    logger.info("Total errors      : %d", total_errors)

        
if __name__ == "__main__":
    companies = get_company_info()
    
    run_backfill(companies, SP500CompanyRepository(collection=get_company_data_db()))