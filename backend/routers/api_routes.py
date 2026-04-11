from fastapi import APIRouter, Depends
from massive import RESTClient
from core.config import POLYGON_IO_KEY
from backend.models.YFinanance import EarningsData, YFinanceResponse, CompanyInfoResponse
from backend.services.company_data_service import CompanyDataService
from backend.core.dependencies import get_company_data_service

router = APIRouter(prefix="/api")
polygon_client = RESTClient(POLYGON_IO_KEY)

@router.get("/upcoming-earnings", description="Fetches upcoming earnings data for a given ticker, including earnings date, EPS estimate, and actual EPS if available.")
def get_upcoming_earnings(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)) -> YFinanceResponse:
    earnings_list = company_data_service.fetch_earnings_data(ticker)
    return YFinanceResponse(ticker=ticker, earnings=earnings_list)

@router.get("/company-info", description="Fetches company information such as industry, sector, location, market cap, and business summary.") 
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

@router.get("/earnings-estimates", description="Fetches earnings estimates for a given ticker. Returns EPS estimates for the next quarter, including average, low, and high estimates.")
def get_earnings_estimates(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)):
    estimates = company_data_service.get_upcoming_earnings_estimates(ticker)
    return estimates

@router.get("/earnings-history", description="Fetches historical earnings data for a given ticker, including past earnings dates, EPS estimates, and actual EPS values.")
def get_earnings_history(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)):
    earnings_list = company_data_service.get_historical_earnings(ticker)
    return YFinanceResponse(ticker=ticker, earnings=earnings_list)