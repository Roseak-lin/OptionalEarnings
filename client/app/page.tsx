"use client";

import React, { useState } from "react";

export default function Home() {
  const [searchInput, setSearchInput] = useState("");
  const [companyInfo, setCompanyInfo] = useState<any>(null);
  const [earningsHistory, setEarningsHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput.trim()) return;

    setLoading(true);
    setError("");
    setCompanyInfo(null);
    setEarningsHistory([]);

    try {
      const [infoRes, earningsRes] = await Promise.all([
        fetch(`http://localhost:8000/api/company-info?ticker=${searchInput}`),
        fetch(`http://localhost:8000/api/earnings-history?ticker=${searchInput}`)
      ]);

      if (!infoRes.ok || !earningsRes.ok) {
        throw new Error("Failed to fetch data. Please check the ticker and try again.");
      }

      const infoData = await infoRes.json();
      const earningsData = await earningsRes.json();

      setCompanyInfo(infoData);
      setEarningsHistory(earningsData.earnings || []);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const formatMarketCap = (num: number) => {
    if (!num) return "N/A";
    return `$${(num / 1e9).toFixed(2)}B`;
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-zinc-900 dark:text-zinc-50">
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-6 py-4">
        <h1 className="text-xl font-bold tracking-tight">Market Dashboard</h1>
      </header>

      <main className="p-6 max-w-6xl mx-auto space-y-8">
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
            <h2 className="text-2xl font-bold mb-2">{companyInfo.company_name}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
              <div>
                <span className="text-zinc-500 block">Sector</span>
                <span className="font-medium">{companyInfo.sector || "N/A"}</span>
              </div>
              <div>
                <span className="text-zinc-500 block">Industry</span>
                <span className="font-medium">{companyInfo.industry || "N/A"}</span>
              </div>
              <div>
                <span className="text-zinc-500 block">Location</span>
                <span className="font-medium">{companyInfo.city}, {companyInfo.country}</span>
              </div>
              <div>
                <span className="text-zinc-500 block">Market Cap</span>
                <span className="font-medium">{formatMarketCap(companyInfo.marketCap)}</span>
              </div>
            </div>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-4 leading-relaxed line-clamp-3">
              {companyInfo.longBusinessSummary}
            </p>
          </section>
        )}

        {earningsHistory.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold mb-4">Earnings History</h2>
            <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950">
                  <tr>
                    <th className="p-4 font-medium">Date</th>
                    <th className="p-4 font-medium">EPS Estimate</th>
                    <th className="p-4 font-medium">EPS Actual</th>
                    <th className="p-4 font-medium">Surprise %</th>
                    <th className="p-4 font-medium">Total Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                  {earningsHistory.map((earning, idx) => (
                    <tr key={idx}>
                      <td className="p-4">{formatDate(earning.earnings_date)}</td>
                      <td className="p-4">{earning.eps_estimate !== null ? earning.eps_estimate : "N/A"}</td>
                      <td className="p-4">{earning.eps_actual !== null ? earning.eps_actual : "N/A"}</td>
                      <td className={`p-4 ${earning.surprise_pct && earning.surprise_pct > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                        {earning.surprise_pct !== null ? `${(earning.surprise_pct).toFixed(2)}%` : "N/A"}
                      </td>
                      <td className="p-4">{earning.total_revenue ? `$${(earning.total_revenue / 1e9).toFixed(2)}B` : "N/A"}</td>
                    </tr>
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