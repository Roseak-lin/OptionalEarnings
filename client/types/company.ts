export type CompanyInfo = {
  name: string;
  ticker: string;
}

export type UpcomingEarnings = {
  ticker: string;
  eps_estimate: number;
  earnings_date: string;
  timing: string;
}