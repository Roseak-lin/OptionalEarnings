export type CompanyInfo = {
  name: string;
  ticker: string;
}

export type UpcomingEarnings = {
  ticker: string;
  name: string;
  eps_estimate: number;
  earnings_date: string;
  market_cap: number;
  timing: string;
}