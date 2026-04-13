from pydantic import BaseModel

class YFinanceRequest(BaseModel):
    ticker: str
    limit: int

