
import os

from fastapi import APIRouter
from massive import RESTClient
from config import POLYGON_IO_KEY
from models.YFinanance import EarningsData, YFinanceResponse, CompanyInfoResponse
import yfinance as yf

router = APIRouter(prefix="/api")
polygon_client = RESTClient(POLYGON_IO_KEY)

DATE_FORMAT = "%Y-%m-%d"

@router.get("/upcoming-earnings")
# def get_upcoming_earnings(ticker: YFinanceRequest) -> YFinanceResponse:
def get_upcoming_earnings(ticker: str) -> YFinanceResponse:
    data = yf.Ticker(ticker).get_earnings_dates()
    earnings_list = []
    for date, row in data.iterrows():
        earnings_list.append(EarningsData(
            earnings_date=date.strftime(DATE_FORMAT),
            eps_estimate=row['EPS Estimate'],
            eps_actual=row['Reported EPS']
        ))
    return YFinanceResponse(ticker=ticker, earnings=earnings_list)

@router.get("/company-info") 
def get_company_info(ticker: str) -> CompanyInfoResponse:
    data = yf.Ticker(ticker).info
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

@router.get("/test")
def test_endpoint():
    data = yf.Ticker("AAPL").info
    return {"data": data}