import numpy as np
import yfinance as yf
from models.API_responses import EarningsData
from repository.past_earnings_repository import PastEarningsRepository
from analysis.engine import compute_impact_factors

# Module that implements services related to company data, such as fetching and processing earnings data.

DATE_FORMAT = "%Y-%m-%d"
SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

class CompanyDataService:
    def __init__(self, company_data_repository: PastEarningsRepository = None):
        self._data = {}
        self.repo = company_data_repository

    def fetch_company_data(self, ticker: str):
        if ticker not in self._data:
            self._data[ticker] = yf.Ticker(ticker).info
        return self._data[ticker]
    
    def fetch_upcoming_earnings_data(self, ticker: str):
        data = yf.Ticker(ticker).get_earnings_dates()
        earnings_list = []
        for date, row in data.iterrows():
            try: 
                earnings_list.append(EarningsData(
                    earnings_date=date.strftime(DATE_FORMAT),
                    eps_estimate=row['EPS Estimate'],
                    eps_actual=row['Reported EPS'] if not np.isnan(row['Reported EPS']) else None,
                ))
            except ValueError as exc:
                print(f"Error processing earnings data for {ticker} on {date}: {exc}")
                continue
        return earnings_list
    
    def get_upcoming_earnings_estimates(self, ticker: str):
        data = yf.Ticker(ticker).get_earnings_estimate(as_dict=True)
        print("Raw earnings estimates data: ", data)
        # only extract next quarter estimates 
        estimates = {
            "avg": data["avg"]["+1q"],
            "low": data["low"]["+1q"],
            "high": data["high"]["+1q"],
        }
        
        return estimates
    
    def get_historical_earnings(self, ticker: str):
        if self.repo is None:
            raise ValueError("PastEarningsRepository is not initialized.")
        earnings_data = self.repo.get_earnings_by_ticker(ticker)
        compute_impact_factors(earnings_data)
        return earnings_data

    def get_sp500_companies(self) -> list[str]:
        pass