from fastapi import Depends

from repository.past_earnings_repository import PastEarningsRepository
from services.company_data_service import CompanyDataService
from core.database import get_company_data, get_general_market_data

def get_past_earnings_db():
    return get_company_data()

def get_general_market_db():
    return get_general_market_data()

def get_past_earnings_repository(collection = Depends(get_past_earnings_db)):
    return PastEarningsRepository(collection)

def get_company_data_service(company_data_repository = Depends(get_past_earnings_repository)):
    return CompanyDataService(company_data_repository)