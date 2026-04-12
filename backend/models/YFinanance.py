from datetime import date, datetime

from pydantic import BaseModel

class EarningsData(BaseModel):
    ticker: str
    earnings_date: datetime
    company_name: str
    eps_estimate: float | None = None
    eps_actual: float | None = None
    fetched_at: datetime
    industry: str | None = None
    normalized_EBITA: float | None = None
    operating_income: float | None = None
    sector: str | None = None
    surprise_pct: float | None = None
    total_revenue: float | None = None
    earnings_timing: str | None = None
    sector_etf: str | None = None
    sector_etf_change: float | None = None
    ref_close_date: date | None = None
    ref_open_date: date | None = None
    price_ref_close: float | None = None
    price_ref_open: float | None = None
    sector_ref_close: float | None = None
    sector_ref_open: float | None = None
    vix_close: float | None = None

class YFinanceRequest(BaseModel):
    ticker: str
    limit: int

class YFinanceResponse(BaseModel):
    ticker: str
    earnings: list[EarningsData]
    
class CompanyInfoResponse(BaseModel):
    ticker: str
    company_name: str
    industry: str
    sector: str
    city: str
    state: str
    country: str
    longBusinessSummary: str
    marketCap: int