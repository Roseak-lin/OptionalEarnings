from datetime import datetime

from pydantic import BaseModel

class EarningsData(BaseModel):
    ticker: str
    earnings_date: datetime
    company_name: str
    eps_estimate: float
    eps_actual: float
    fetched_at: datetime
    industry: str | None = None
    normalized_EBITA: float | None = None
    operating_income: float | None = None
    sector: str | None = None
    surprise_pct: float | None = None
    total_revenue: float | None = None

class YFinanceRequest(BaseModel):
    ticker: str
    limit: int

class YFinanceResponse(BaseModel):
    ticker: str
    earnings: list[EarningsData]
    
class CompanyInfoResponse(BaseModel):
    ticker: str
    industry: str
    sector: str
    city: str
    state: str
    country: str
    longBusinessSummary: str
    marketCap: int