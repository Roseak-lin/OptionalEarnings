import yfinance as yf
from models.YFinanance import EarningsData
from repository.past_earnings_repository import PastEarningsRepository

# Module that implements services related to company data, such as fetching and processing earnings data.

DATE_FORMAT = "%Y-%m-%d"

class CompanyDataService:
    def __init__(self, company_data_repository: PastEarningsRepository = None):
        self._data = {}
        self.repo = company_data_repository

    def fetch_company_data(self, ticker: str):
        if ticker not in self._data:
            self._data[ticker] = yf.Ticker(ticker).info
        return self._data[ticker]
    
    def fetch_earnings_data(self, ticker: str):
        data = yf.Ticker(ticker).get_earnings_dates()
        earnings_list = []
        for date, row in data.iterrows():
            earnings_list.append(EarningsData(
                earnings_date=date.strftime(DATE_FORMAT),
                eps_estimate=row['EPS Estimate'],
                eps_actual=row['Reported EPS']
            ))
        return earnings_list
    
    def get_upcoming_earnings_estimates(self, ticker: str):
        data = yf.Ticker(ticker).get_earnings_estimate(as_dict=True)
        # only extract next quarter estimates 
        estimates = {
            "avg": data["avg"]["+1q"],
            "low": data["low"]["+1q"],
            "high": data["high"]["+1q"],
        }
        
        return estimates
    
    def temp(self, _id: str):
        print("REPO: ", self.repo)
        return self.repo.temp(_id)