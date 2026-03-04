from pydantic import BaseModel

class EarningsData(BaseModel):
    earnings_date: str
    eps_estimate: float
    eps_actual: float

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