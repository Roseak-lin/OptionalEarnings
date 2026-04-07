
import os

from fastapi import APIRouter, Depends
from massive import RESTClient
from core.config import POLYGON_IO_KEY
from models.YFinanance import EarningsData, YFinanceResponse, CompanyInfoResponse
from services.company_data_service import CompanyDataService
from core.dependencies import get_company_data_service

router = APIRouter(prefix="/api")
polygon_client = RESTClient(POLYGON_IO_KEY)

@router.get("/upcoming-earnings")
def get_upcoming_earnings(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)) -> YFinanceResponse:
    earnings_list = company_data_service.fetch_earnings_data(ticker)
    return YFinanceResponse(ticker=ticker, earnings=earnings_list)

@router.get("/company-info") 
def get_company_info(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)) -> CompanyInfoResponse:
    data = company_data_service.fetch_company_data(ticker)
    return CompanyInfoResponse(
        ticker=ticker,
        industry=data.get("industry", ""),
        sector=data.get("sector", ""),
        city=data.get("city", ""),
        state=data.get("state", ""),
        country=data.get("country", ""),
        marketCap=data.get("marketCap", 0),
        longBusinessSummary=data.get("longBusinessSummary", "")
    )

@router.get("/earnings-estimates")
def get_earnings_estimates(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)):
    estimates = company_data_service.get_upcoming_earnings_estimates(ticker)
    return estimates

@router.get("/test")
def test_endpoint(_id: str, company_data_service: CompanyDataService = Depends(get_company_data_service)):
    data = company_data_service.temp(_id)
    return {"data": data}