from fastapi import APIRouter, Depends

from backend.services.sp500_info_service import SP500InfoService
from backend.analysis.engine import generate_earnings_summary

from backend.models.API_responses import CompanyInfoResponse, BulkCompanyEarningsResponse
from backend.services.company_data_service import CompanyDataService
from backend.core.dependencies import get_company_data_service, get_sp500_info_service

router = APIRouter(prefix="/api")

@router.get("/company-info", description="Fetches company information such as industry, sector, location, market cap, and business summary.") 
def get_company_info(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)) -> CompanyInfoResponse:
    data = company_data_service.fetch_company_data(ticker.upper())
    return CompanyInfoResponse(
        ticker=ticker,
        company_name=data.get("shortName", "N/A"),
        industry=data.get("industry", ""),
        sector=data.get("sector", ""),
        city=data.get("city", ""),
        state=data.get("state", ""),
        country=data.get("country", ""),
        marketCap=data.get("marketCap", 0),
        longBusinessSummary=data.get("longBusinessSummary", "")
    )

@router.get("/get-upcoming-earnings", description="Fetches earnings estimates for a given ticker. Returns EPS estimates for the next quarter, including average, low, and high estimates.")
def get_earnings_estimates(company_data_service: CompanyDataService = Depends(get_company_data_service), sp500_info_service: SP500InfoService = Depends(get_sp500_info_service)):
    sp500_tickers = sp500_info_service.get_all_companies()
    sp500_tickers = list(map(lambda x: x["ticker"], sp500_tickers))
    
    return company_data_service.get_upcoming_earnings(sp500_companies=sp500_tickers)

@router.get("/earnings-history", description="Fetches historical earnings data for a given ticker, including past earnings dates, EPS estimates, and actual EPS values.")
def get_earnings_history(ticker: str, company_data_service: CompanyDataService = Depends(get_company_data_service)):
    earnings_list = company_data_service.get_historical_earnings(ticker.upper())
    summary = generate_earnings_summary(ticker, earnings_list)
    return BulkCompanyEarningsResponse(ticker=ticker, earnings=earnings_list, earnings_summary=summary)

@router.get("/sp500-companies", description="Fetches the list of S&P 500 companies along with their tickers and sectors.")
def get_sp500_companies(sp500_info_service: SP500InfoService = Depends(get_sp500_info_service)):
    sp500_data = sp500_info_service.get_all_companies()
    return sp500_data