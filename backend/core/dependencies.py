from fastapi import Depends

from repository.sp500_company_repository import SP500CompanyRepository
from services.sp500_info_service import SP500InfoService
from repository.past_earnings_repository import PastEarningsRepository
from services.company_data_service import CompanyDataService
from core.database import get_company_data, get_general_market_data

SECTOR_ETF_MAP = {
    "Technology": "XLK",
    "Financial Services": "XLF",
    "Healthcare": "XLV",
    "Energy": "XLE",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Industrials": "XLI",
    "Utilities": "XLU",
    "Basic Materials": "XLB",
    "Real Estate": "XLRE",
    "Communication Services": "XLC"
}

def get_company_data_db():
    return get_company_data()

def get_general_market_db():
    return get_general_market_data()

def get_past_earnings_repository(collection = Depends(get_company_data_db)):
    return PastEarningsRepository(collection)

def get_company_data_service(company_data_repository = Depends(get_past_earnings_repository)):
    return CompanyDataService(company_data_repository)

def get_sp500_info_repo(sp500_repo = Depends(get_company_data_db)):
    return SP500CompanyRepository(sp500_repo)

def get_sp500_info_service(sp500_repo = Depends(get_sp500_info_repo)):
    return SP500InfoService(sp500_repo)