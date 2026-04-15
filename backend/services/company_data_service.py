from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf
from models.API_responses import EarningsData
from repository.past_earnings_repository import PastEarningsRepository
from analysis.engine import compute_impact_factors

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
    
    def get_upcoming_earnings(self, sp500_companies: list[str]):
        earnings_calendar = yf.Calendars(end=datetime.now() + pd.Timedelta(days=7))
        upcoming_earnings = []
        for ticker, row in earnings_calendar.get_earnings_calendar().iterrows():
            if ticker not in sp500_companies:
                continue
            earnings_date = row["Event Start Date"].strftime(DATE_FORMAT)
            earnings = {
                "ticker": ticker,
                "eps_estimate": row["EPS Estimate"],
                "earnings_date": earnings_date,
                "timing": "Before Market Open" if row["Event Start Date"].hour < 10 else "After Market Close"
            }
            upcoming_earnings.append(earnings)
        
        upcoming_earnings.sort(key=lambda x: x["earnings_date"])
        return upcoming_earnings
    
    def get_historical_earnings(self, ticker: str):
        if self.repo is None:
            raise ValueError("PastEarningsRepository is not initialized.")
        earnings_data = self.repo.get_earnings_by_ticker(ticker)
        compute_impact_factors(earnings_data)
        return earnings_data