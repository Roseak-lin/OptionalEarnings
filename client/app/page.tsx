"use client";

import React, { useState } from "react";

export default function Home() {
  const [searchInput, setSearchInput] = useState("");
  const [companyInfo, setCompanyInfo] = useState<any>(null);
  const [earningsHistory, setEarningsHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput.trim()) return;

    setLoading(true);
    setError("");
    setCompanyInfo(null);
    setEarningsHistory([]);
    setExpandedRow(null);

    try {
      const [infoRes, earningsRes] = await Promise.all([
        fetch(
          `http://localhost:8000/api/company-info?ticker=${searchInput.toUpperCase()}`,
        ),
        fetch(
          `http://localhost:8000/api/earnings-history?ticker=${searchInput.toUpperCase()}`,
        ),
      ]);

      if (!infoRes.ok || !earningsRes.ok) {
        throw new Error(
          "Failed to fetch data. Please check the ticker and try again.",
        );
      }

      const infoData = await infoRes.json();
      const earningsData = await earningsRes.json();

      setCompanyInfo(infoData);
      setEarningsHistory(earningsData.earnings || []);
      console.log("Fetched Earnings History:", earningsData.earnings);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrencyLarge = (num: number | null | undefined) => {
    if (num === null || num === undefined) return "N/A";
    if (Math.abs(num) >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (Math.abs(num) >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString('en-US', {timeZone: "UTC"});
  };

  const formatDateTime = (dateString: string | null | undefined) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString('en-US', {timeZone: "UTC"});
  };

  const formatPercentage = (num: number | null | undefined) => {
    if (num === null || num === undefined) return "N/A";
    return `${num.toFixed(2)}%`;
  };

  const toggleRow = (idx: number) => {
    setExpandedRow(expandedRow === idx ? null : idx);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-zinc-900 dark:text-zinc-50">
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">Market Dashboard</h1>
      </header>

      <main className="p-6 max-w-7xl mx-auto space-y-8">
        <form onSubmit={handleSearch} className="flex max-w-md gap-2">
          <input
            type="text"
            placeholder="Enter Ticker (e.g., AAPL)"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="flex-1 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-zinc-900 dark:bg-white px-4 py-2 text-sm font-medium text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </form>

        {error && <div className="text-red-500 font-medium">{error}</div>}

        {companyInfo && (
          <section className="p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
            <h2 className="text-2xl font-bold mb-2">
              {companyInfo.company_name} ({companyInfo.ticker})
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
              <div>
                <span className="text-zinc-500 block">Sector</span>
                <span className="font-medium">
                  {companyInfo.sector || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 block">Industry</span>
                <span className="font-medium">
                  {companyInfo.industry || "N/A"}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 block">Location</span>
                <span className="font-medium">
                  {companyInfo.city}, {companyInfo.country}
                </span>
              </div>
              <div>
                <span className="text-zinc-500 block">Market Cap</span>
                <span className="font-medium">
                  {formatCurrencyLarge(companyInfo.marketCap)}
                </span>
              </div>
            </div>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-4 leading-relaxed">
              {companyInfo.longBusinessSummary}
            </p>
          </section>
        )}

        {earningsHistory.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold mb-4">
              Comprehensive Earnings History
            </h2>
            <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950">
                  <tr>
                    <th className="p-4 font-medium w-8"></th>
                    <th className="p-4 font-medium">Earnings Date</th>
                    <th className="p-4 font-medium">EPS Est</th>
                    <th className="p-4 font-medium">EPS Actual</th>
                    <th className="p-4 font-medium">Surprise</th>
                    <th className="p-4 font-medium">Total Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                  {earningsHistory.map((earning, idx) => (
                    <React.Fragment key={idx}>
                      <tr
                        onClick={() => toggleRow(idx)}
                        className="hover:bg-zinc-50 dark:hover:bg-zinc-950/50 transition-colors cursor-pointer"
                      >
                        <td className="p-4 text-zinc-400">
                          {expandedRow === idx ? "▼" : "▶"}
                        </td>
                        <td className="p-4 font-medium">
                          {formatDate(earning.earnings_date)}
                        </td>
                        <td className="p-4">
                          {earning.eps_estimate !== null
                            ? earning.eps_estimate
                            : "N/A"}
                        </td>
                        <td className="p-4">
                          {earning.eps_actual !== null
                            ? earning.eps_actual
                            : "N/A"}
                        </td>
                        <td
                          className={`p-4 ${earning.surprise_pct && earning.surprise_pct > 0 ? "text-green-600 dark:text-green-400" : earning.surprise_pct && earning.surprise_pct < 0 ? "text-red-600 dark:text-red-400" : ""}`}
                        >
                          {formatPercentage(earning.surprise_pct)}
                        </td>
                        <td className="p-4">
                          {formatCurrencyLarge(earning.total_revenue)}
                        </td>
                      </tr>
                      {expandedRow === idx && (
                        <tr className="bg-zinc-50/50 dark:bg-zinc-950/30">
                          <td
                            colSpan={6}
                            className="p-6 border-b border-zinc-200 dark:border-zinc-800"
                          >
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                              <div>
                                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                                  Details & Timing
                                </h4>
                                <div className="space-y-2 mb-4 text-sm">
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Name:
                                    </span>{" "}
                                    {earning.company_name || "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Industry:
                                    </span>{" "}
                                    {earning.industry || "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Sector:
                                    </span>{" "}
                                    {earning.sector || "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Sector ETF:
                                    </span>{" "}
                                    {earning.sector_etf || "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Timing:
                                    </span>{" "}
                                    {earning.earnings_timing === "after_market_close" ? "After Market Close" : "Before Market Open" || "N/A"}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                                  Price Action
                                </h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Ref Close Date:
                                    </span>{" "}
                                    {formatDate(earning.ref_close_date)}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Price Ref Close:
                                    </span>{" "}
                                    {earning.price_ref_close
                                      ? `$${earning.price_ref_close.toFixed(2)}`
                                      : "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Sector Ref Close:
                                    </span>{" "}
                                    {earning.sector_ref_close
                                      ? `$${earning.sector_ref_close.toFixed(2)}`
                                      : "N/A"}
                                  </p>
                                  <div className="h-2"></div>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Ref Open Date:
                                    </span>{" "}
                                    {formatDate(earning.ref_open_date)}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Price Ref Open:
                                    </span>{" "}
                                    {earning.price_ref_open
                                      ? `$${earning.price_ref_open.toFixed(2)}`
                                      : "N/A"}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Sector Ref Open:
                                    </span>{" "}
                                    {earning.sector_ref_open
                                      ? `$${earning.sector_ref_open.toFixed(2)}`
                                      : "N/A"}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                                  Extended Financials
                                </h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Operating Income:
                                    </span>{" "}
                                    {formatCurrencyLarge(
                                      earning.operating_income,
                                    )}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Norm. EBITA:
                                    </span>{" "}
                                    {formatCurrencyLarge(
                                      earning.normalized_EBITA,
                                    )}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                                  Market & System
                                </h4>
                                <div className="space-y-2 mb-4 text-sm">
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      ETF Change ({earning.sector_etf || "N/A"}):
                                    </span>{" "}
                                    {formatPercentage(
                                      earning.sector_etf_change,
                                    )}
                                  </p>
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      VIX Close:
                                    </span>{" "}
                                    {earning.vix_close
                                      ? earning.vix_close.toFixed(2)
                                      : "N/A"}
                                  </p>
                                </div>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="text-zinc-500 mr-2">
                                      Fetched At:
                                    </span>{" "}
                                    {formatDateTime(earning.fetched_at)}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
